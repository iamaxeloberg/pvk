"""T8: Document chunking tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chunker import chunk_text, Chunk


class TestChunker:
    def test_small_text_not_split(self):
        """Text shorter than chunk_size should return a single chunk."""
        text = "This is a short document."
        chunks = chunk_text(text, "test.md", chunk_size=4000, chunk_overlap=200)

        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].source_file == "test.md"
        assert chunks[0].index == 0

    def test_large_text_is_split(self):
        """Text longer than chunk_size should be split into multiple chunks."""
        paragraphs = [f"Paragraph {i}: " + "x" * 500 for i in range(20)]
        text = "\n\n".join(paragraphs)

        chunks = chunk_text(text, "large.md", chunk_size=1000, chunk_overlap=100)

        assert len(chunks) > 1
        total_chars = sum(len(c.text) for c in chunks)
        assert total_chars >= len(text)

    def test_chunk_metadata(self):
        """Each chunk should have correct metadata."""
        text = "Para 1\n\nPara 2\n\nPara 3"
        chunks = chunk_text(text, "doc.md", chunk_size=20, chunk_overlap=5)

        for chunk in chunks:
            assert chunk.source_file == "doc.md"
            assert isinstance(chunk.index, int)
            assert isinstance(chunk.start_char, int)
            assert isinstance(chunk.end_char, int)

    def test_chunk_indices_are_sequential(self):
        """Chunk indices should start at 0 and increment."""
        text = "\n\n".join([f"P{i}" for i in range(10)])
        chunks = chunk_text(text, "doc.md", chunk_size=10, chunk_overlap=2)

        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_empty_text(self):
        """Empty text should return a single empty chunk."""
        chunks = chunk_text("", "empty.md", chunk_size=100, chunk_overlap=10)

        assert len(chunks) == 1
        assert chunks[0].text == ""

    def test_token_estimate(self):
        """Token estimate should be roughly chars / 4."""
        chunk = Chunk(text="A" * 400, index=0, source_file="test.md", start_char=0, end_char=400)

        assert chunk.token_estimate() == 100

    def test_overlap_preserves_content(self):
        """Overlapping chunks should not lose content between them."""
        paragraphs = [f"Important paragraph {i}" for i in range(10)]
        text = "\n\n".join(paragraphs)

        chunks = chunk_text(text, "doc.md", chunk_size=100, chunk_overlap=30)

        combined = " ".join(c.text for c in chunks)
        for para in paragraphs:
            assert para in combined
