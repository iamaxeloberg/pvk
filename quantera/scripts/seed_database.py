#!/usr/bin/env python3
"""Pre-populate the SQLite database with demo metadata for the live demo.

This skips the LLM categorisation step and inserts known-good metadata
so the demo can run smoothly even if the LLM API is slow or unstable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indexer import init_db, insert_document, close_db
from config.settings import settings

DEMO_DOCUMENTS = [
    {
        "company": "Volvo Group",
        "categories": ["financial report", "Q1 2025", "earnings", "trucks"],
        "markdown_path": str(settings.markdown_dir_obj / "volvo_group_report_csv.md"),
    },
    {
        "company": "Ericsson",
        "categories": ["financial report", "Q1 2025", "earnings", "telecom"],
        "markdown_path": str(settings.markdown_dir_obj / "ericsson_report_csv.md"),
    },
    {
        "company": "Atlas Copco",
        "categories": ["financial report", "Q1 2025", "earnings", "industrial"],
        "markdown_path": str(settings.markdown_dir_obj / "atlas_copco_report_csv.md"),
    },
    {
        "company": "Investor AB",
        "categories": ["portfolio update", "Q1 2025", "investment", "holding company"],
        "markdown_path": str(settings.markdown_dir_obj / "investor_ab_report_csv.md"),
    },
]


def seed_demo_database():
    """Insert demo documents into the SQLite index."""
    conn = init_db()
    try:
        for doc in DEMO_DOCUMENTS:
            insert_document(conn, doc["company"], doc["categories"], doc["markdown_path"])
            print(f"Indexed: {doc['company']} -> {doc['markdown_path']}")

        from src.indexer import get_document_count
        count = get_document_count(conn)
        print(f"\nTotal documents in database: {count}")
    finally:
        close_db(conn)


if __name__ == "__main__":
    seed_demo_database()
