"""Briefing Sub-Agent - Creates executive briefings from financial documents."""

import logging
from pathlib import Path

from config.settings import settings
from src.utils import get_llm_content, llm_completion, read_prompt

logger = logging.getLogger(__name__)


def generate_briefing(user_query: str, relevant_documents: list[str]) -> str:
    """Generate an executive briefing from relevant documents."""
    prompt = read_prompt("executive_briefing")

    doc_contents = []
    for doc_path in relevant_documents:
        path = Path(doc_path)
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError, OSError) as e:
                logger.warning(f"Could not read {doc_path}: {e}")
                continue
            if len(content) > settings.max_doc_size_chars:
                content = content[: settings.max_doc_size_chars] + "\n\n[Document truncated due to size...]"
            doc_contents.append(f"--- Document: {path.name} ---\n{content}")
        else:
            logger.warning(f"Document not found: {doc_path}")

    if not doc_contents:
        return "No relevant documents found to generate a briefing."

    combined_docs = "\n\n".join(doc_contents)

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Create an executive briefing based on these documents:\n\n{combined_docs}\n\nQuery: {user_query}"},
    ]

    logger.info("Generating executive briefing via LLM...")
    response = llm_completion(
        model=settings.high_capacity_llm_model,
        messages=messages,
        api_key=settings.high_capacity_llm_api_key or None,
        api_base=settings.high_capacity_llm_api_base or None,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )

    result = get_llm_content(response)
    logger.info(f"Generated executive briefing for query: {user_query}")
    return result
