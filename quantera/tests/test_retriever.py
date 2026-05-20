"""T5: Can the system return relevant results for a given company or topic query?"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retriever import build_index_context, retrieve_relevant_docs
from src.indexer import init_db, insert_document, close_db
from src.utils import read_prompt


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

    def test_read_prompt(self):
        prompt = read_prompt("retrieval")
        assert "query" in prompt.lower() or "relevant" in prompt.lower()

    def test_retrieve_relevant_docs_requires_llm(self, db_conn):
        """Full retrieval test requires LLM API."""
        pytest.skip("Requires LLM API configuration")

    @patch("src.retriever.llm_completion")
    def test_retrieve_relevant_docs_with_mock(self, mock_completion, db_conn):
        """Test retrieval using mocked LLM response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "/data/techcorp.md"
        mock_completion.return_value = mock_response

        result = retrieve_relevant_docs(db_conn, "What was TechCorp revenue?")

        assert len(result) == 1
        assert "/data/techcorp.md" in result
        mock_completion.assert_called_once()

    @patch("src.retriever.llm_completion")
    def test_retrieve_filters_invalid_paths(self, mock_completion, db_conn):
        """Test that paths not in the database are filtered out."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "/data/techcorp.md\n/data/nonexistent.md"
        mock_completion.return_value = mock_response

        result = retrieve_relevant_docs(db_conn, "query")

        assert len(result) == 1
        assert "/data/techcorp.md" in result
        assert "/data/nonexistent.md" not in result

    @patch("src.retriever.llm_completion")
    def test_retrieve_handles_empty_response(self, mock_completion, db_conn):
        """Test handling of empty LLM response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""
        mock_completion.return_value = mock_response

        result = retrieve_relevant_docs(db_conn, "query")

        assert result == []

    @patch("src.retriever.llm_completion")
    def test_retrieve_handles_multiple_paths(self, mock_completion, db_conn):
        """Test retrieval returning multiple valid documents."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "/data/techcorp.md\n/data/retailco.md"
        mock_completion.return_value = mock_response

        result = retrieve_relevant_docs(db_conn, "compare companies")

        assert len(result) == 2
        assert "/data/techcorp.md" in result
        assert "/data/retailco.md" in result
