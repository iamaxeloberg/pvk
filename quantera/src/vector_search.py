"""Vector-based semantic search for documents.

Uses sentence-transformers for embeddings and cosine similarity for retrieval.
Falls back to LLM-based retrieval if the embedding model is unavailable.
"""

import json
import logging
import sqlite3
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None


def _get_model():
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")
        except ImportError:
            logger.warning("sentence-transformers not installed; vector search disabled")
            return None
    return _model


def embed_text(text: str) -> list[float] | None:
    """Generate an embedding vector for the given text.

    Returns None if the embedding model is unavailable.
    """
    model = _get_model()
    if model is None:
        return None
    embedding = model.encode(text)
    return embedding.tolist()


def init_vector_table(db_path: Path | None = None) -> sqlite3.Connection:
    """Initialise the vector embeddings table in the database."""
    conn = sqlite3.connect(str(db_path or settings.db_path_obj))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS document_embeddings (
            markdown_file_path TEXT PRIMARY KEY,
            embedding TEXT NOT NULL,
            content_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def store_embedding(
    conn: sqlite3.Connection,
    markdown_path: str,
    embedding: list[float],
    content_summary: str = "",
) -> None:
    """Store an embedding vector for a document."""
    embedding_json = json.dumps(embedding)
    conn.execute(
        """INSERT OR REPLACE INTO document_embeddings (markdown_file_path, embedding, content_summary)
           VALUES (?, ?, ?)""",
        (markdown_path, embedding_json, content_summary),
    )
    conn.commit()
    logger.info(f"Stored embedding for {markdown_path}")


def get_embedding(conn: sqlite3.Connection, markdown_path: str) -> list[float] | None:
    """Retrieve a stored embedding vector."""
    cursor = conn.execute(
        "SELECT embedding FROM document_embeddings WHERE markdown_file_path = ?",
        (markdown_path,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return json.loads(row[0])


def has_embeddings(conn: sqlite3.Connection) -> bool:
    """Check if any embeddings exist in the database."""
    cursor = conn.execute("SELECT COUNT(*) FROM document_embeddings")
    return cursor.fetchone()[0] > 0


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_search(
    conn: sqlite3.Connection,
    query: str,
    top_k: int = 5,
    threshold: float = 0.3,
) -> list[tuple[str, float]]:
    """Search for documents semantically similar to the query.

    Args:
        conn: SQLite connection
        query: The search query
        top_k: Maximum number of results to return
        threshold: Minimum similarity score (0.0-1.0)

    Returns:
        List of (markdown_file_path, similarity_score) tuples sorted by score.
        Returns empty list if embeddings are unavailable.
    """
    query_embedding = embed_text(query)
    if query_embedding is None:
        logger.warning("Cannot perform semantic search: embedding model unavailable")
        return []

    cursor = conn.execute("SELECT markdown_file_path, embedding FROM document_embeddings")
    rows = cursor.fetchall()

    results = []
    for path, embedding_json in rows:
        try:
            doc_embedding = json.loads(embedding_json)
        except json.JSONDecodeError:
            logger.warning(f"Corrupted embedding for {path}, skipping")
            continue
        score = _cosine_similarity(query_embedding, doc_embedding)
        if score >= threshold:
            results.append((path, round(score, 4)))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


def embed_document(conn: sqlite3.Connection, markdown_path: Path) -> bool:
    """Generate and store an embedding for a document.

    Returns True if successful, False if embedding model is unavailable.
    """
    if not markdown_path.exists():
        logger.warning(f"Document not found: {markdown_path}")
        return False

    content = markdown_path.read_text(encoding="utf-8")
    embedding = embed_text(content)
    if embedding is None:
        return False

    summary = content[:500].replace("\n", " ")
    store_embedding(conn, str(markdown_path), embedding, summary)
    return True
