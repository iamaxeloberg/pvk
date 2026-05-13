"""Document chunking - splits large documents into manageable chunks."""

import logging
from dataclasses import dataclass
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """A single chunk of document text with metadata."""

    text: str
    index: int
    source_file: str
    start_char: int
    end_char: int

    def token_estimate(self) -> int:
        """Rough token count estimate (1 token ~= 4 chars for English text)."""
        return len(self.text) // 4


def chunk_text(text: str, source_file: str = "", chunk_size: int | None = None, chunk_overlap: int | None = None) -> list[Chunk]:
    """Split text into overlapping chunks respecting paragraph boundaries.

    Strategy:
    1. Split by double newlines (paragraphs)
    2. Accumulate paragraphs until chunk_size is reached
    3. Overlap the last few paragraphs with the next chunk

    Args:
        text: The full document text
        source_file: Original file path for tracking
        chunk_size: Maximum characters per chunk (defaults to settings)
        chunk_overlap: Characters of overlap between chunks (defaults to settings)

    Returns:
        List of Chunk objects
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    if len(text) <= chunk_size:
        return [Chunk(text=text, index=0, source_file=source_file, start_char=0, end_char=len(text))]

    paragraphs = text.split("\n\n")
    chunks: list[Chunk] = []
    current_text = ""
    current_start = 0
    chunk_index = 0
    scan_pos = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_text) + len(para) + 2 > chunk_size and current_text:
            end_pos = current_start + len(current_text)
            chunks.append(Chunk(
                text=current_text.strip(),
                index=chunk_index,
                source_file=source_file,
                start_char=current_start,
                end_char=end_pos,
            ))
            chunk_index += 1

            overlap_paragraphs = _get_overlap_paragraphs(current_text, chunk_overlap)
            current_text = overlap_paragraphs
            current_start = max(0, end_pos - len(overlap_paragraphs))

        if current_text:
            current_text += "\n\n" + para
        else:
            para_pos = text.find(para, scan_pos)
            if para_pos == -1:
                para_pos = scan_pos
            current_text = para
            current_start = para_pos
            scan_pos = para_pos + len(para)

    if current_text:
        end_pos = current_start + len(current_text)
        chunks.append(Chunk(
            text=current_text.strip(),
            index=chunk_index,
            source_file=source_file,
            start_char=current_start,
            end_char=min(end_pos, len(text)),
        ))

    logger.info(f"Split '{source_file}' into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")
    return chunks


def _get_overlap_paragraphs(text: str, overlap_chars: int) -> str:
    """Get the trailing portion of text for overlap, aligned to paragraph boundaries."""
    if len(text) <= overlap_chars:
        return text

    tail = text[-overlap_chars:]
    first_newline = tail.find("\n\n")
    if first_newline != -1:
        return tail[first_newline + 2:]
    return tail
