"""T6: Does the system return correct answers to predetermined questions?"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator import generate_response
from src.utils import read_prompt


class TestGenerator:
    def test_read_prompt(self):
        prompt = read_prompt("master_prompt")
        assert "financial" in prompt.lower() or "analysis" in prompt.lower()

    def test_generate_response_no_docs(self):
        response = generate_response("What is the revenue?", [])
        assert "No relevant documents" in response

    def test_generate_response_with_docs(self, tmp_path):
        """Test response generation with actual document content."""
        doc_path = tmp_path / "test.md"
        doc_path.write_text("# Test Company\nRevenue: SEK 100M\n", encoding="utf-8")
        pytest.skip("Requires LLM API configuration")

    def test_generate_response_missing_doc(self, tmp_path):
        """Test handling of missing document files."""
        doc_path = tmp_path / "nonexistent.md"
        response = generate_response("Query?", [str(doc_path)])
        assert "No relevant documents" in response
