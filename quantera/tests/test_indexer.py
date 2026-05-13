"""T4: Is data correctly stored and retrieved? All indexed documents retrievable by company and category."""

import pytest
import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indexer import (
    init_db,
    insert_document,
    get_all_documents,
    get_documents_by_company,
    get_documents_by_category,
    get_document_count,
    delete_document,
    close_db,
)


class TestIndexer:
    @pytest.fixture
    def db_conn(self, tmp_path):
        db_path = tmp_path / "test.db"
        conn = init_db(db_path)
        yield conn
        close_db(conn)

    def test_init_db(self, tmp_path):
        db_path = tmp_path / "test.db"
        conn = init_db(db_path)
        assert db_path.exists()
        close_db(conn)

    def test_insert_and_get_all(self, db_conn):
        insert_document(db_conn, "TechCorp", ["financial report", "earnings"], "/path/to/tech.md")
        docs = get_all_documents(db_conn)
        assert len(docs) == 1
        assert docs[0]["company"] == "TechCorp"
        assert docs[0]["categories"] == ["financial report", "earnings"]

    def test_insert_duplicate(self, db_conn):
        insert_document(db_conn, "TechCorp", ["report"], "/path/to/tech.md")
        insert_document(db_conn, "TechCorp", ["updated"], "/path/to/tech.md")
        docs = get_all_documents(db_conn)
        assert len(docs) == 1
        assert docs[0]["categories"] == ["updated"]

    def test_get_by_company(self, db_conn):
        insert_document(db_conn, "TechCorp", ["report"], "/path/tech.md")
        insert_document(db_conn, "RetailCo", ["analysis"], "/path/retail.md")
        results = get_documents_by_company(db_conn, "TechCorp")
        assert len(results) == 1
        assert results[0]["company"] == "TechCorp"

    def test_get_by_category(self, db_conn):
        insert_document(db_conn, "TechCorp", ["financial report"], "/path/tech.md")
        insert_document(db_conn, "RetailCo", ["market analysis"], "/path/retail.md")
        results = get_documents_by_category(db_conn, "financial")
        assert len(results) == 1

    def test_document_count(self, db_conn):
        assert get_document_count(db_conn) == 0
        insert_document(db_conn, "TechCorp", ["report"], "/path/tech.md")
        assert get_document_count(db_conn) == 1

    def test_delete_document(self, db_conn):
        insert_document(db_conn, "TechCorp", ["report"], "/path/tech.md")
        assert delete_document(db_conn, "/path/tech.md") is True
        assert get_document_count(db_conn) == 0

    def test_delete_nonexistent(self, db_conn):
        assert delete_document(db_conn, "/nonexistent.md") is False
