"""API layer - terminal interface + callable Python API."""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import get_input_files
from src.converter import convert_batch
from src.categoriser import extract_metadata
from src.indexer import init_db, insert_document, get_all_documents, get_document_count, close_db
from src.retriever import retrieve_relevant_docs
from src.generator import generate_response
from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
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

    # Step 2: Convert to Markdown
    print("Converting to Markdown...")
    md_files = convert_batch(input_files)
    if not md_files:
        print("No files were successfully converted.")
        return
    print(f"Converted {len(md_files)} file(s).")

    # Step 3: Categorise and index
    print("Categorising documents...")
    conn = init_db()
    for md_path in md_files:
        try:
            content = md_path.read_text(encoding="utf-8")
            metadata = extract_metadata(content, md_path)
            insert_document(conn, metadata["company"], metadata["categories"], metadata["markdown_file_path"])
            print(f"  Indexed: {metadata['company']} - {metadata['categories']}")
        except Exception as e:
            print(f"  Failed to index {md_path}: {e}")
            logger.error(f"Failed to index {md_path}: {e}")

    count = get_document_count(conn)
    close_db(conn)
    print(f"\nPipeline complete. {count} document(s) indexed.")


def query(question: str):
    """Query the indexed documents and get an AI-generated response.

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

    # Step 1: Retrieve relevant documents
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

    # Step 2: Generate response
    print("Generating response...\n")
    try:
        response = generate_response(question, relevant_paths)
        print(response)
    except Exception as e:
        print(f"Error generating response: {e}")
        logger.error(f"Generation error: {e}")

    close_db(conn)


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
        print("  python src/api.py query <question> - Query indexed documents")
        print("  python src/api.py list             - List indexed documents")
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
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
