"""T2: Does Marker produce correct Markdown files for the file types?"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.converter import convert_to_markdown, convert_batch


class TestConverter:
    def test_convert_batch_empty(self):
        results = convert_batch([])
        assert results == []

    def test_convert_batch_invalid_file(self, tmp_path):
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.touch()
        results = convert_batch([invalid_file], tmp_path)
        assert results == []
