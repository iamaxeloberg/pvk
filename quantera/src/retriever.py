"""Stage 1 retrieval - filters SQLite index to find relevant docs (AL1-AL3)."""

import logging
from pathlib import Path
from config.settings import settings
from src.utils import read_prompt, get_llm_content, llm_completion

logger = logging.getLogger(__name__)


def retrieve_relevant_docs(conn, user_query: str) -> list[str]:
    """Use low-cost LLM to filter the index and return relevant file paths."""
    index_context = build_index_context(conn)
    prompt = read_prompt("retrieval")

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Document Index:\n{index_context}\n\nUser Query: {user_query}\n\nReturn the file paths of relevant documents:"},
    ]

    response = llm_completion(
        model=settings.low_cost_llm_model,
        messages=messages,
        api_key=settings.low_cost_llm_api_key or None,
        api_base=settings.low_cost_llm_api_base or None,
        temperature=0.0,
        max_tokens=1024,
    )

    result_text = get_llm_content(response)

    # Parse file paths from response (one per line)
    paths = [line.strip() for line in result_text.split("\n") if line.strip()]

    # Validate paths exist in the database
    valid_paths = []
    for path in paths:
        cursor = conn.execute("SELECT markdown_file_path FROM documents WHERE markdown_file_path = ?", (path,))
        if cursor.fetchone():
            valid_paths.append(path)
        else:
            logger.warning(f"LLM returned invalid path: {path}")

    logger.info(f"Retrieved {len(valid_paths)} relevant documents for query: {user_query}")
    return valid_paths


def build_index_context(conn) -> str:
    """Build a text representation of the SQLite index for the LLM to filter."""
    cursor = conn.execute("SELECT company, categories, markdown_file_path FROM documents")
    rows = cursor.fetchall()
    lines = []
    for company, categories, path in rows:
        lines.append(f"Company: {company} | Categories: {categories} | Path: {path}")
    return "\n".join(lines) if lines else "No documents indexed."
