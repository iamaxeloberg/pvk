"""T5: Can the system return relevant results for a given company or topic query?"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retriever import build_index_context, load_prompt
from src.indexer import init_db, insert_document, close_db


class TestRetriever:
    @pytest.fixture
    def db_conn(self, tmp_path):
        db_path = tmp_path / "test.db"
        conn = init_db(db_path)
        insert_document(conn, "TechCorp", ["financial report", "earnings"], "/data/techcorp.md")
        insert_document(conn, "RetailCo", ["market analysis"], "/data/retailco.md")
        yield conn
        close_db(conn)

    def test_build_index_context(self, db_conn):
        context = build_index_context(db_conn)
        assert "TechCorp" in context
        assert "RetailCo" in context
        assert "/data/techcorp.md" in context

    def test_build_index_context_empty(self, tmp_path):
        db_path = tmp_path / "empty.db"
        conn = init_db(db_path)
        context = build_index_context(conn)
        assert "No documents" in context
        close_db(conn)

    def test_load_prompt(self):
        prompt = load_prompt()
        assert "query" in prompt.lower() or "relevant" in prompt.lower()

    def test_retrieve_relevant_docs_requires_llm(self, db_conn):
        """Full retrieval test requires LLM API."""
        pytest.skip("Requires LLM API configuration")
