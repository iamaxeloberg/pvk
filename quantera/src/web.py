"""FastAPI web server for Quantera."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
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
from src.agents.router import route_query, classify_query
from src.agents.kpi_agent import extract_kpis, format_kpi_response
from src.utils import setup_logging
from config.settings import settings

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quantera",
    description="AI-driven financial document indexing and query system",
    version="0.1.0",
)


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


class DocumentInfo(BaseModel):
    id: int
    company: str
    categories: list[str]
    markdown_file_path: str


class DocumentListResponse(BaseModel):
    total: int
    documents: list[DocumentInfo]


@app.get("/health")
def health_check():
    return {"status": "ok"}


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
        else:
            try:
                md_path = convert_to_markdown(fp)
                md_files.append(md_path)
            except Exception as e:
                conversion_failures.append(f"{fp.name}: {e}")
                logger.error(f"Failed to convert {fp}: {e}")

    conn = init_db()
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
            insert_document(conn, metadata["company"], metadata["categories"], metadata["markdown_file_path"])
            indexed += 1
        except Exception as e:
            indexing_failures.append(f"{md_path.name}: {e}")
            logger.error(f"Failed to index {md_path}: {e}")

    count = get_document_count(conn)
    close_db(conn)

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
    """Query indexed documents using the AI agent router."""
    conn = init_db()

    count = get_document_count(conn)
    if count == 0:
        close_db(conn)
        raise HTTPException(status_code=404, detail="No documents indexed. Run the ingestion pipeline first.")

    try:
        relevant_paths = retrieve_relevant_docs(conn, request.question)
    except Exception as e:
        close_db(conn)
        raise HTTPException(status_code=500, detail=f"Retrieval error: {e}")

    if not relevant_paths:
        close_db(conn)
        return QueryResponse(question=request.question, answer="No relevant documents found.", agent_used="general", relevant_documents=[])

    try:
        result = route_query(request.question, relevant_paths, agent=request.agent)
    except Exception as e:
        close_db(conn)
        raise HTTPException(status_code=500, detail=f"Query error: {e}")

    close_db(conn)
    return QueryResponse(
        question=request.question,
        answer=result["response"],
        agent_used=result["agent_used"],
        relevant_documents=result["relevant_documents"],
    )


@app.post("/classify", response_model=ClassifyResponse)
def classify_question(request: QueryRequest):
    """Classify a query to determine which sub-agent should handle it."""
    agent = classify_query(request.question)
    return ClassifyResponse(question=request.question, recommended_agent=agent)


@app.get("/documents", response_model=DocumentListResponse)
def list_documents():
    """List all indexed documents."""
    conn = init_db()
    docs = get_all_documents(conn)
    count = len(docs)
    close_db(conn)

    return DocumentListResponse(
        total=count,
        documents=[DocumentInfo(**doc) for doc in docs],
    )


@app.delete("/documents/{markdown_path:path}")
def delete_doc(markdown_path: str):
    """Delete a document from the index."""
    conn = init_db()
    deleted = delete_document(conn, markdown_path)
    close_db(conn)

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document not found: {markdown_path}")

    return {"message": f"Deleted: {markdown_path}"}
