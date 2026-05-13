"""T6: Does the system return correct answers to predetermined questions?"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
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

    @patch("src.generator.completion")
    def test_generate_response_with_mock(self, mock_completion, tmp_path):
        """Test response generation using mocked LLM."""
        doc_path = tmp_path / "test.md"
        doc_path.write_text("# TechCorp\nRevenue: SEK 145.2M\n", encoding="utf-8")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "TechCorp reported revenue of SEK 145.2M."
        mock_completion.return_value = mock_response

        result = generate_response("What was the revenue?", [str(doc_path)])

        assert "145.2M" in result
        mock_completion.assert_called_once()

    @patch("src.generator.completion")
    def test_generate_response_uses_correct_model(self, mock_completion, tmp_path):
        """Test that the high-capacity LLM model is used."""
        doc_path = tmp_path / "test.md"
        doc_path.write_text("# Test\nData", encoding="utf-8")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Answer"
        mock_completion.return_value = mock_response

        generate_response("Query?", [str(doc_path)])

        call_kwargs = mock_completion.call_args.kwargs
        assert "claude" in call_kwargs["model"].lower() or "anthropic" in call_kwargs["model"].lower()

    @patch("src.generator.completion")
    def test_generate_response_combines_multiple_docs(self, mock_completion, tmp_path):
        """Test that multiple documents are combined in the prompt."""
        doc1 = tmp_path / "doc1.md"
        doc2 = tmp_path / "doc2.md"
        doc1.write_text("# Company A\nRevenue: 100M", encoding="utf-8")
        doc2.write_text("# Company B\nRevenue: 200M", encoding="utf-8")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Combined answer"
        mock_completion.return_value = mock_response

        generate_response("Compare revenues", [str(doc1), str(doc2)])

        call_kwargs = mock_completion.call_args.kwargs
        user_content = call_kwargs["messages"][1]["content"]
        assert "Company A" in user_content
        assert "Company B" in user_content
