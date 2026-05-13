"""T9: Vector-based semantic search tests."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_search import (
    init_vector_table,
    store_embedding,
    get_embedding,
    has_embeddings,
    semantic_search,
    _cosine_similarity,
)
from src.indexer import init_db, close_db


class TestVectorSearch:
    @pytest.fixture
    def db_conn(self, tmp_path):
        db_path = tmp_path / "test.db"
        conn = init_db(db_path)
        vector_conn = init_vector_table(db_path)
        yield vector_conn
        close_db(vector_conn)

    def test_init_vector_table(self, tmp_path):
        db_path = tmp_path / "test.db"
        conn = init_vector_table(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='document_embeddings'")
        assert cursor.fetchone() is not None
        close_db(conn)

    def test_store_and_get_embedding(self, db_conn):
        embedding = [0.1, 0.2, 0.3, 0.4]
        store_embedding(db_conn, "/path/doc.md", embedding, "Summary")

        result = get_embedding(db_conn, "/path/doc.md")
        assert result == embedding

    def test_get_embedding_missing(self, db_conn):
        result = get_embedding(db_conn, "/nonexistent.md")
        assert result is None

    def test_has_embeddings(self, db_conn):
        assert has_embeddings(db_conn) is False
        store_embedding(db_conn, "/path/doc.md", [0.1, 0.2])
        assert has_embeddings(db_conn) is True

    def test_cosine_similarity_identical(self):
        vec = [1.0, 0.0, 0.0]
        assert _cosine_similarity(vec, vec) == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal(self):
        assert _cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_cosine_similarity_opposite(self):
        assert _cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)

    def test_cosine_similarity_zero_vector(self):
        assert _cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0

    @patch("src.vector_search.embed_text")
    def test_semantic_search_returns_results(self, mock_embed, db_conn):
        mock_embed.return_value = [0.5, 0.5, 0.5]

        store_embedding(db_conn, "/doc1.md", [0.5, 0.5, 0.5], "Similar doc")
        store_embedding(db_conn, "/doc2.md", [0.1, 0.1, 0.1], "Different doc")

        results = semantic_search(db_conn, "test query")

        assert len(results) >= 1
        assert results[0][0] == "/doc1.md"
        assert results[0][1] == pytest.approx(1.0)

    @patch("src.vector_search.embed_text")
    def test_semantic_search_respects_threshold(self, mock_embed, db_conn):
        mock_embed.return_value = [1.0, 0.0, 0.0]

        store_embedding(db_conn, "/similar.md", [0.9, 0.1, 0.0], "Similar")
        store_embedding(db_conn, "/different.md", [0.0, 1.0, 0.0], "Different")

        results = semantic_search(db_conn, "query", threshold=0.5)

        paths = [p for p, _ in results]
        assert "/similar.md" in paths
        assert "/different.md" not in paths

    @patch("src.vector_search.embed_text")
    def test_semantic_search_respects_top_k(self, mock_embed, db_conn):
        mock_embed.return_value = [0.5, 0.5]

        for i in range(10):
            store_embedding(db_conn, f"/doc{i}.md", [0.5, 0.5], f"Doc {i}")

        results = semantic_search(db_conn, "query", top_k=3)

        assert len(results) == 3

    def test_semantic_search_no_model(self, db_conn):
        """Should return empty list when embedding model is unavailable."""
        with patch("src.vector_search.embed_text", return_value=None):
            results = semantic_search(db_conn, "query")
            assert results == []
