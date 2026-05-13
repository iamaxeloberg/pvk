"""T3: Does the AI model extract correct company names and categories?"""

import pytest
from pathlib import Path
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
