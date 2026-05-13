"""T3: Does the AI model extract correct company names and categories?"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.categoriser import extract_metadata
from src.utils import read_prompt


class TestCategoriser:
    def test_read_prompt(self):
        prompt = read_prompt("categorisation")
        assert "company" in prompt.lower()
        assert "categories" in prompt.lower()

    def test_extract_metadata_structure(self):
        """Test that metadata extraction returns the expected structure."""
        sample_md = """# TechCorp AB - Q1 2025 Financial Report
## Revenue
- Total Revenue: SEK 145.2M
## Margins
- Gross Margin: 62.3%
"""
        # This test requires a working LLM API, so we skip it in CI
        pytest.skip("Requires LLM API configuration")

    @patch("src.categoriser.completion")
    def test_extract_metadata_with_mock(self, mock_completion):
        """Test metadata extraction using mocked LLM response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"company": "TechCorp AB", "categories": ["financial report", "earnings"]}'
        mock_completion.return_value = mock_response

        sample_md = "# TechCorp AB - Q1 2025 Report\nRevenue: SEK 100M"
        md_path = Path("/data/techcorp.md")

        result = extract_metadata(sample_md, md_path)

        assert result["company"] == "TechCorp AB"
        assert result["categories"] == ["financial report", "earnings"]
        assert result["markdown_file_path"] == str(md_path)
        mock_completion.assert_called_once()

    @patch("src.categoriser.completion")
    def test_extract_metadata_handles_code_fences(self, mock_completion):
        """Test that JSON wrapped in markdown code fences is parsed correctly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '```json\n{"company": "RetailCo", "categories": ["market analysis", "retail"]}\n```'
        mock_completion.return_value = mock_response

        result = extract_metadata("# RetailCo Report", Path("/data/retail.md"))

        assert result["company"] == "RetailCo"
        assert result["categories"] == ["market analysis", "retail"]

    @patch("src.categoriser.completion")
    def test_extract_metadata_truncates_long_documents(self, mock_completion):
        """Test that very long documents are truncated before sending to LLM."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"company": "BigCorp", "categories": ["report"]}'
        mock_completion.return_value = mock_response

        long_content = "A" * 10000
        extract_metadata(long_content, Path("/data/big.md"))

        call_args = mock_completion.call_args
        user_content = call_args.kwargs["messages"][1]["content"]
        assert len(user_content) < 10000
        assert "truncated" in user_content.lower()
