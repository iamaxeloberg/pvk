"""Insight Sub-Agent - Provides deep financial analysis from documents."""

import logging

from config.settings import settings
from src.utils import get_llm_content, llm_completion, load_documents_for_prompt, read_prompt

logger = logging.getLogger(__name__)


def generate_insights(user_query: str, relevant_documents: list[str]) -> str:
    """Generate financial insights and analysis from relevant documents."""
    prompt = read_prompt("financial_insights")

    combined_docs = load_documents_for_prompt(relevant_documents, settings.max_doc_size_chars)

    if not combined_docs:
        return "No relevant documents found to generate insights."

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Analyse these financial documents and provide insights:\n\n{combined_docs}\n\nQuery: {user_query}"},
    ]

    logger.info("Generating financial insights via LLM...")
    response = llm_completion(
        model=settings.high_capacity_llm_model,
        messages=messages,
        api_key=settings.high_capacity_llm_api_key or None,
        api_base=settings.high_capacity_llm_api_base or None,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )

    result = get_llm_content(response)
    logger.info(f"Generated financial insights for query: {user_query}")
    return result
