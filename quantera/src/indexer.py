"""SQLite storage and indexing (DP5) - stores metadata and file paths."""

import json
import sqlite3
import logging
from pathlib import Path
from config.settings import settings

logger = logging.getLogger(__name__)


def _escape_like(value: str) -> str:
    """Escape SQL LIKE wildcard characters in a search value."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Initialise SQLite database and create tables if they don't exist."""
    path = db_path or settings.db_path_obj
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            categories TEXT NOT NULL,
            markdown_file_path TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_company ON documents(company)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_categories ON documents(categories)
    """)
    conn.commit()
    logger.info(f"Database initialised at {path}")
    return conn


def insert_document(conn: sqlite3.Connection, company: str, categories: list[str], markdown_path: str) -> None:
    """Insert a document record into the index."""
    categories_json = json.dumps(categories)
    conn.execute(
        """INSERT OR REPLACE INTO documents (company, categories, markdown_file_path)
           VALUES (?, ?, ?)""",
        (company, categories_json, markdown_path),
    )
    conn.commit()
    logger.info(f"Indexed document: {company} - {categories}")


def get_all_documents(conn: sqlite3.Connection) -> list[dict]:
    """Retrieve all indexed documents."""
    cursor = conn.execute("SELECT id, company, categories, markdown_file_path FROM documents")
    rows = cursor.fetchall()
    return [
        {
            "id": r["id"],
            "company": r["company"],
            "categories": json.loads(r["categories"]),
            "markdown_file_path": r["markdown_file_path"],
        }
        for r in rows
    ]


def get_documents_by_company(conn: sqlite3.Connection, company: str) -> list[dict]:
    """Retrieve documents for a specific company."""
    cursor = conn.execute(
        "SELECT id, company, categories, markdown_file_path FROM documents WHERE company LIKE ? ESCAPE '\\'",
        (f"%{_escape_like(company)}%",),
    )
    rows = cursor.fetchall()
    return [
        {
            "id": r["id"],
            "company": r["company"],
            "categories": json.loads(r["categories"]),
            "markdown_file_path": r["markdown_file_path"],
        }
        for r in rows
    ]


def get_documents_by_category(conn: sqlite3.Connection, category: str) -> list[dict]:
    """Retrieve documents matching a specific category."""
    cursor = conn.execute(
        "SELECT id, company, categories, markdown_file_path FROM documents WHERE categories LIKE ? ESCAPE '\\'",
        (f"%{_escape_like(category)}%",),
    )
    rows = cursor.fetchall()
    return [
        {
            "id": r["id"],
            "company": r["company"],
            "categories": json.loads(r["categories"]),
            "markdown_file_path": r["markdown_file_path"],
        }
        for r in rows
    ]


def get_document_count(conn: sqlite3.Connection) -> int:
    """Get the total number of indexed documents."""
    cursor = conn.execute("SELECT COUNT(*) FROM documents")
    return cursor.fetchone()[0]


def is_document_indexed(conn: sqlite3.Connection, markdown_path: str) -> bool:
    """Check if a document is already in the index."""
    cursor = conn.execute("SELECT 1 FROM documents WHERE markdown_file_path = ?", (markdown_path,))
    return cursor.fetchone() is not None


def delete_document(conn: sqlite3.Connection, markdown_path: str) -> bool:
    """Delete a document from the index."""
    cursor = conn.execute("DELETE FROM documents WHERE markdown_file_path = ?", (markdown_path,))
    conn.commit()
    return cursor.rowcount > 0


def close_db(conn: sqlite3.Connection) -> None:
    """Close the database connection."""
    conn.close()
