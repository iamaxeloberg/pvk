"""API layer - terminal interface + callable Python API."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import get_input_files
from src.converter import convert_to_markdown
from src.categoriser import extract_metadata
from src.indexer import init_db, insert_document, get_all_documents, get_document_count, is_document_indexed, close_db
from src.retriever import retrieve_relevant_docs
from src.generator import generate_response
from src.vector_search import init_vector_table, embed_document, semantic_search, has_embeddings
from src.agents.router import route_query, classify_query
from src.kpi_store import init_kpi_table, get_kpi_trend, get_all_kpis_for_company, get_companies_with_kpis, get_available_metrics
from src.utils import setup_logging
from config.settings import settings

setup_logging()
logger = logging.getLogger(__name__)


def run_pipeline():
    """Run the full ingestion pipeline: input -> markdown -> categorise -> index."""
    print("Starting ingestion pipeline...")

    # Step 1: Get input files
    input_files = get_input_files()
    if not input_files:
        print("No input files found in the input directory.")
        return

    print(f"Found {len(input_files)} input file(s).")

    # Step 2: Convert to Markdown (skip already converted)
    print("\nConverting to Markdown...")
    md_files = []
    convert_skipped = 0
    convert_failed = []
    for fp in input_files:
        md_path = settings.markdown_dir_obj / (fp.stem + ".md")
        if md_path.exists():
            convert_skipped += 1
            logger.info(f"Skipping already converted: {fp.name}")
        else:
            try:
                md_path = convert_to_markdown(fp)
                md_files.append(md_path)
            except Exception as e:
                convert_failed.append((fp.name, str(e)))
                logger.error(f"Failed to convert {fp}: {e}")

    # Step 3: Categorise and index (skip already indexed)
    print("Categorising and indexing documents...")
    conn = init_db()
    vector_conn = init_vector_table()
    indexed = 0
    index_skipped = 0
    index_failed = []
    embedded = 0
    for md_path in md_files:
        try:
            if is_document_indexed(conn, str(md_path)):
                index_skipped += 1
                logger.info(f"Skipping already indexed: {md_path.name}")
                continue
            content = md_path.read_text(encoding="utf-8")
            metadata = extract_metadata(content, md_path)
            insert_document(conn, metadata["company"], metadata["categories"], metadata["markdown_file_path"])
            indexed += 1

            if embed_document(vector_conn, md_path):
                embedded += 1
        except Exception as e:
            index_failed.append((md_path.name, str(e)))
            logger.error(f"Failed to index {md_path}: {e}")

    count = get_document_count(conn)
    close_db(conn)
    close_db(vector_conn)

    # Summary report
    print("\n" + "=" * 50)
    print("INGESTION SUMMARY")
    print("=" * 50)
    print(f"  Input files found:      {len(input_files)}")
    print(f"  Converted (new):        {len(md_files)}")
    print(f"  Skipped (already done): {convert_skipped}")
    print(f"  Conversion failures:    {len(convert_failed)}")
    print(f"  Newly indexed:          {indexed}")
    print(f"  Skipped (already done): {index_skipped}")
    print(f"  Indexing failures:      {len(index_failed)}")
    print(f"  Embeddings created:     {embedded}")
    print(f"  Total in database:      {count}")

    if convert_failed:
        print("\nConversion failures:")
        for name, err in convert_failed:
            print(f"  - {name}: {err}")

    if index_failed:
        print("\nIndexing failures:")
        for name, err in index_failed:
            print(f"  - {name}: {err}")

    print("=" * 50)


def query(question: str):
    """Query the indexed documents and get an AI-generated response.

    Uses semantic search if embeddings are available, falls back to LLM-based retrieval.

    Args:
        question: Natural language query about the indexed financial data
    """
    print(f"Query: {question}\n")

    conn = init_db()

    count = get_document_count(conn)
    if count == 0:
        print("No documents indexed. Run the ingestion pipeline first.")
        close_db(conn)
        return

    print(f"Searching {count} indexed documents...")

    # Step 1: Retrieve relevant documents (semantic search with LLM fallback)
    relevant_paths = []
    if has_embeddings(conn):
        vector_conn = init_vector_table()
        results = semantic_search(vector_conn, question, top_k=5)
        close_db(vector_conn)
        if results:
            relevant_paths = [path for path, _score in results]
            print(f"  (semantic search: {len(relevant_paths)} results)")
        else:
            print("  (semantic search returned no results, falling back to LLM retrieval)")

    if not relevant_paths:
        try:
            relevant_paths = retrieve_relevant_docs(conn, question)
        except Exception as e:
            print(f"Error during retrieval: {e}")
            logger.error(f"Retrieval error: {e}")
            close_db(conn)
            return

    if not relevant_paths:
        print("No relevant documents found for this query.")
        close_db(conn)
        return

    print(f"Found {len(relevant_paths)} relevant document(s).")

    # Step 2: Route to appropriate sub-agent and generate response
    print("Routing to specialised agent...\n")
    try:
        result = route_query(question, relevant_paths)
        print(f"Agent used: {result['agent_used']}")
        print(f"\n{result['response']}")
    except Exception as e:
        print(f"Error generating response: {e}")
        logger.error(f"Generation error: {e}")

    close_db(conn)


def kpi_trend(company: str, metric: str | None = None):
    """Query KPI time-series data for a company.

    Args:
        company: Company name to query
        metric: Optional specific metric (e.g. Revenue, EBITDA)
    """
    conn = init_db()
    kpi_conn = init_kpi_table()

    companies = get_companies_with_kpis(kpi_conn)
    if not companies:
        print("No KPIs stored yet. Run queries that extract KPIs first.")
        close_db(conn)
        close_db(kpi_conn)
        return

    if metric:
        trend = get_kpi_trend(kpi_conn, company, metric)
        if not trend:
            print(f"No KPI trend found for {company} / {metric}")
            close_db(conn)
            close_db(kpi_conn)
            return
        print(f"\nKPI Trend: {company} — {metric}")
        print("=" * 40)
        for entry in trend:
            value = entry["value"] if entry["value"] is not None else entry["value_raw"]
            unit = f" {entry['unit']}" if entry["unit"] else ""
            context = f" ({entry['context']})" if entry["context"] else ""
            print(f"  {entry['period']}: {value}{unit}{context}")
    else:
        all_kpis = get_all_kpis_for_company(kpi_conn, company)
        if not all_kpis:
            print(f"No KPIs stored for {company}")
            close_db(conn)
            close_db(kpi_conn)
            return
        print(f"\nKPIs for {company}")
        print("=" * 40)
        for metric_name, entries in all_kpis.items():
            print(f"\n  {metric_name}:")
            for entry in entries:
                value = entry["value"] if entry["value"] is not None else entry["value_raw"]
                unit = f" {entry['unit']}" if entry["unit"] else ""
                print(f"    {entry['period']}: {value}{unit}")

    close_db(conn)
    close_db(kpi_conn)


def list_documents():
    """List all indexed documents."""
    conn = init_db()
    docs = get_all_documents(conn)
    close_db(conn)

    if not docs:
        print("No documents indexed.")
        return

    print(f"Indexed documents ({len(docs)}):\n")
    for doc in docs:
        print(f"  Company: {doc['company']}")
        print(f"  Categories: {', '.join(doc['categories'])}")
        print(f"  Path: {doc['markdown_file_path']}")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python src/api.py ingest          - Run ingestion pipeline")
        print("  python src/api.py query <question> - Query indexed documents (auto-routed)")
        print("  python src/api.py list             - List indexed documents")
        print("  python src/api.py classify <q>     - Show which agent would handle the query")
        print("  python src/api.py kpi <company> [metric] - Show KPI trends")
        sys.exit(1)

    command = sys.argv[1]

    if command == "ingest":
        run_pipeline()
    elif command == "query":
        if len(sys.argv) < 3:
            print("Error: query requires a question")
            sys.exit(1)
        query(" ".join(sys.argv[2:]))
    elif command == "list":
        list_documents()
    elif command == "classify":
        if len(sys.argv) < 3:
            print("Error: classify requires a question")
            sys.exit(1)
        agent = classify_query(" ".join(sys.argv[2:]))
        print(f"Recommended agent: {agent}")
    elif command == "kpi":
        if len(sys.argv) < 3:
            print("Error: kpi requires a company name")
            sys.exit(1)
        company = sys.argv[2]
        metric = sys.argv[3] if len(sys.argv) > 3 else None
        kpi_trend(company, metric)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
