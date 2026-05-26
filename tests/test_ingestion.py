"""T1: Can the system process CSV, Excel, and PDF files without crashing?"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import SUPPORTED_EXTENSIONS, get_input_files, validate_file


class TestIngestion:
    def test_supported_extensions(self):
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".xlsx" in SUPPORTED_EXTENSIONS
        assert ".xls" in SUPPORTED_EXTENSIONS
        assert ".csv" in SUPPORTED_EXTENSIONS

    def test_validate_file_valid(self, tmp_path):
        pdf_file = tmp_path / "test.pdf"
        pdf_file.touch()
        assert validate_file(pdf_file) is True

    def test_validate_file_invalid_extension(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.touch()
        assert validate_file(txt_file) is False

    def test_validate_file_nonexistent(self):
        assert validate_file(Path("/nonexistent/file.pdf")) is False

    def test_get_input_files(self, tmp_path):
        (tmp_path / "doc1.pdf").touch()
        (tmp_path / "doc2.xlsx").touch()
        (tmp_path / "doc3.csv").touch()
        (tmp_path / "ignore.txt").touch()

        files = get_input_files(tmp_path)
        assert len(files) == 3

    def test_get_input_files_empty_dir(self, tmp_path):
        files = get_input_files(tmp_path)
        assert len(files) == 0

    def test_get_input_files_nonexistent_dir(self):
        files = get_input_files(Path("/nonexistent/dir"))
        assert files == []
