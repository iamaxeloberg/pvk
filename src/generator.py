"""Stage 2 generation - sends relevant Markdown + prompt to Claude (RG1-RG2)."""

import logging

from config.settings import settings
from src.utils import get_llm_content, llm_completion, load_documents_for_prompt, read_prompt

logger = logging.getLogger(__name__)


def generate_response(user_query: str, relevant_documents: list[str]) -> str:
    """Generate a final response using the high-capacity LLM."""
    master_prompt = read_prompt("master_prompt")

    combined_docs = load_documents_for_prompt(relevant_documents, settings.max_doc_size_chars)

    if not combined_docs:
        return "No relevant documents found to answer your query."

    messages = [
        {"role": "system", "content": master_prompt},
        {"role": "user", "content": f"Based on the following documents, answer this query:\n\n{combined_docs}\n\nQuery: {user_query}"},
    ]

    logger.info("Generating response via LLM...")
    response = llm_completion(
        model=settings.high_capacity_llm_model,
        messages=messages,
        api_key=settings.high_capacity_llm_api_key or None,
        api_base=settings.high_capacity_llm_api_base or None,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )

    result = get_llm_content(response)
    logger.info(f"Generated response for query: {user_query}")
    return result
