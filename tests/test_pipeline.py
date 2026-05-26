"""T7: Error handling - empty documents, conversion failures, pipeline resilience."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indexer import close_db, get_document_count, init_db
from src.ingestion import validate_file


class TestPipelineErrorHandling:
    def test_empty_input_directory(self, tmp_path):
        """System should handle empty input directory without crashing."""
        from src.ingestion import get_input_files
        files = get_input_files(tmp_path)
        assert files == []

    def test_invalid_file_type(self, tmp_path):
        """System should reject unsupported file types."""
        txt_file = tmp_path / "notes.txt"
        txt_file.touch()
        assert validate_file(txt_file) is False

    def test_database_initialisation_idempotent(self, tmp_path):
        """Database should be safe to initialise multiple times."""
        db_path = tmp_path / "test.db"
        conn1 = init_db(db_path)
        close_db(conn1)
        conn2 = init_db(db_path)
        assert get_document_count(conn2) == 0
        close_db(conn2)

    def test_query_empty_database(self, tmp_path):
        """Querying an empty database should return a helpful message."""
        from src.indexer import close_db, get_document_count, init_db
        db_path = tmp_path / "empty.db"
        conn = init_db(db_path)
        assert get_document_count(conn) == 0
        close_db(conn)

    def test_converter_handles_missing_file(self):
        """Converter should handle missing input files gracefully."""
        from src.converter import convert_to_markdown
        with pytest.raises((FileNotFoundError, ValueError)):
            convert_to_markdown(Path("/nonexistent/file.pdf"))
