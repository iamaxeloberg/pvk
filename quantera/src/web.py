"""FastAPI web server for Quantera."""

import logging
import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.ingestion import get_input_files
from src.converter import convert_to_markdown
from src.categoriser import extract_metadata
from src.indexer import (
    init_db,
    insert_document,
    get_all_documents,
    get_document_count,
    is_document_indexed,
    delete_document,
    close_db,
)
from src.retriever import retrieve_relevant_docs
from src.generator import generate_response
from src.agents.router import route_query, classify_query, VALID_AGENTS
from src.agents.kpi_agent import extract_kpis, format_kpi_response
from src.kpi_store import init_kpi_table, get_kpi_trend, get_all_kpis_for_company, get_companies_with_kpis, get_available_metrics
from src.vector_search import init_vector_table, semantic_search, has_embeddings
from src.utils import setup_logging, validate_config, ensure_dir
from config.settings import settings

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quantera",
    description="AI-driven financial document indexing and query system",
    version="0.1.0",
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check server logs for details."},
    )


@contextmanager
def get_db():
    conn = init_db()
    try:
        yield conn
    finally:
        close_db(conn)


@contextmanager
def get_kpi_db():
    conn = init_kpi_table()
    try:
        yield conn
    finally:
        close_db(conn)


class QueryRequest(BaseModel):
    question: str
    agent: str | None = None


class IngestResponse(BaseModel):
    total_input: int
    converted: int
    skipped_conversion: int
    conversion_failures: list[str]
    newly_indexed: int
    skipped_index: int
    indexing_failures: list[str]
    total_in_database: int


class QueryResponse(BaseModel):
    question: str
    answer: str
    agent_used: str
    relevant_documents: list[str]


class ClassifyResponse(BaseModel):
    question: str
    recommended_agent: str


class KPITrendResponse(BaseModel):
    company: str
    metric: str | None = None
    data: list[dict]


class KPICompanyResponse(BaseModel):
    company: str
    kpis: dict[str, list[dict]]


class KPIListResponse(BaseModel):
    companies: list[str]
    metrics: list[str]


class DocumentInfo(BaseModel):
    id: int
    company: str
    categories: list[str]
    markdown_file_path: str


class DocumentListResponse(BaseModel):
    total: int
    documents: list[DocumentInfo]


@app.on_event("startup")
async def startup_checks():
    logger.info("Quantera server starting up...")
    ensure_dir(Path(settings.input_dir))
    ensure_dir(Path(settings.markdown_dir))
    ensure_dir(Path(settings.db_path).parent)

    warnings = validate_config()
    if warnings:
        for w in warnings:
            logger.warning(f"Config warning: {w}")
    else:
        logger.info("All configuration validated successfully.")


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/ingest", response_model=IngestResponse)
def run_ingestion():
    """Run the ingestion pipeline on all files in the input directory."""
    input_files = get_input_files()

    md_files = []
    convert_skipped = 0
    conversion_failures = []
    for fp in input_files:
        md_path = settings.markdown_dir_obj / (fp.stem + ".md")
        if md_path.exists():
            convert_skipped += 1
            md_files.append(md_path)
        else:
            try:
                md_path = convert_to_markdown(fp)
                md_files.append(md_path)
            except Exception as e:
                conversion_failures.append(f"{fp.name}: {e}")
                logger.error(f"Failed to convert {fp}: {e}")

    with get_db() as conn:
        indexed = 0
        index_skipped = 0
        indexing_failures = []
        for md_path in md_files:
            try:
                if is_document_indexed(conn, str(md_path)):
                    index_skipped += 1
                    continue
                content = md_path.read_text(encoding="utf-8")
                metadata = extract_metadata(content, md_path)
                company = metadata.get("company", "Unknown")
                categories = metadata.get("categories", [])
                insert_document(conn, company, categories, metadata.get("markdown_file_path", str(md_path)))
                indexed += 1
            except Exception as e:
                indexing_failures.append(f"{md_path.name}: {e}")
                logger.error(f"Failed to index {md_path}: {e}")

        count = get_document_count(conn)

    return IngestResponse(
        total_input=len(input_files),
        converted=len(md_files),
        skipped_conversion=convert_skipped,
        conversion_failures=conversion_failures,
        newly_indexed=indexed,
        skipped_index=index_skipped,
        indexing_failures=indexing_failures,
        total_in_database=count,
    )


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    """Query indexed documents using the AI agent router with semantic search."""
    with get_db() as conn:
        count = get_document_count(conn)
        if count == 0:
            raise HTTPException(status_code=409, detail="No documents indexed. Run the ingestion pipeline first.")

        relevant_paths = []
        if has_embeddings(conn):
            with get_db() as vector_conn:
                try:
                    results = semantic_search(vector_conn, request.question, top_k=5)
                except Exception:
                    results = []
            if results:
                relevant_paths = [path for path, _score in results]

        if not relevant_paths:
            try:
                relevant_paths = retrieve_relevant_docs(conn, request.question)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Retrieval error: {e}")

        if not relevant_paths:
            return QueryResponse(question=request.question, answer="No relevant documents found.", agent_used="general", relevant_documents=[])

        try:
            agent = request.agent
            if agent and agent not in VALID_AGENTS:
                logger.warning(f"Invalid agent '{agent}' requested, defaulting to auto-routing")
                agent = None
            result = route_query(request.question, relevant_paths, agent=agent)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Query error: {e}")

        return QueryResponse(
            question=request.question,
            answer=result.get("response", "No response generated."),
            agent_used=result.get("agent_used", "unknown"),
            relevant_documents=result.get("relevant_documents", []),
        )


@app.post("/classify", response_model=ClassifyResponse)
def classify_question(request: QueryRequest):
    """Classify a query to determine which sub-agent should handle it."""
    try:
        agent = classify_query(request.question)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Classifier unavailable: {e}")
    return ClassifyResponse(question=request.question, recommended_agent=agent)


@app.get("/kpi/companies", response_model=KPIListResponse)
def list_kpi_companies():
    """List companies and metrics with stored KPI data."""
    try:
        with get_kpi_db() as kpi_conn:
            companies = get_companies_with_kpis(kpi_conn)
            metrics = get_available_metrics(kpi_conn)
        return KPIListResponse(companies=companies, metrics=metrics)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"KPI database error: {e}")


@app.get("/kpi/{company}", response_model=KPICompanyResponse)
def get_company_kpis(company: str):
    """Get all KPIs for a company."""
    try:
        with get_kpi_db() as kpi_conn:
            kpis = get_all_kpis_for_company(kpi_conn, company)
        return KPICompanyResponse(company=company, kpis=kpis)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"KPI database error: {e}")


@app.get("/kpi/{company}/{metric}", response_model=KPITrendResponse)
def get_kpi_trend_endpoint(company: str, metric: str):
    """Get time-series KPI data for a company and specific metric."""
    try:
        with get_kpi_db() as kpi_conn:
            trend = get_kpi_trend(kpi_conn, company, metric)
        return KPITrendResponse(company=company, metric=metric, data=trend)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"KPI database error: {e}")


@app.get("/documents", response_model=DocumentListResponse)
def list_documents():
    """List all indexed documents."""
    try:
        with get_db() as conn:
            docs = get_all_documents(conn)
            count = len(docs)
        return DocumentListResponse(
            total=count,
            documents=[DocumentInfo(**doc) for doc in docs],
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Document database error: {e}")


@app.delete("/documents/{markdown_path:path}")
def delete_doc(markdown_path: str):
    """Delete a document from the index."""
    if ".." in markdown_path:
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    try:
        with get_db() as conn:
            deleted = delete_document(conn, markdown_path)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {e}")

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document not found: {markdown_path}")

    return {"message": f"Deleted: {markdown_path}"}
