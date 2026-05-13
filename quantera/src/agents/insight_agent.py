"""Insight Sub-Agent - Provides deep financial analysis from documents."""

import logging
from pathlib import Path
from litellm import completion
from config.settings import settings
from src.utils import read_prompt

logger = logging.getLogger(__name__)


def generate_insights(user_query: str, relevant_documents: list[str]) -> str:
    """Generate financial insights and analysis from relevant documents.

    Args:
        user_query: The user's analytical query
        relevant_documents: List of Markdown file paths to analyse

    Returns:
        Detailed financial analysis as a string
    """
    prompt = read_prompt("financial_insights")

    doc_contents = []
    for doc_path in relevant_documents:
        path = Path(doc_path)
        if path.exists():
            content = path.read_text(encoding="utf-8")
            doc_contents.append(f"--- Document: {path.name} ---\n{content}")
        else:
            logger.warning(f"Document not found: {doc_path}")

    if not doc_contents:
        return "No relevant documents found to generate insights."

    combined_docs = "\n\n".join(doc_contents)

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Analyse these financial documents and provide insights:\n\n{combined_docs}\n\nQuery: {user_query}"},
    ]

    response = completion(
        model=settings.high_capacity_llm_model,
        messages=messages,
        api_key=settings.high_capacity_llm_api_key or None,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )

    result = response.choices[0].message.content.strip()
    logger.info(f"Generated financial insights for query: {user_query}")
    return result
