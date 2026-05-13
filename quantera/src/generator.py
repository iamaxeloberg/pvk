"""Stage 2 generation - sends relevant Markdown + prompt to Claude (RG1-RG2)."""

import logging
from pathlib import Path
from litellm import completion
from config.settings import settings

logger = logging.getLogger(__name__)


def generate_response(user_query: str, relevant_documents: list[str]) -> str:
    """Generate a final response using the high-capacity LLM.

    Args:
        user_query: The original user query
        relevant_documents: List of Markdown file paths relevant to the query

    Returns:
        Generated response from the LLM
    """
    master_prompt = load_prompt()

    # Load document contents
    doc_contents = []
    for doc_path in relevant_documents:
        path = Path(doc_path)
        if path.exists():
            content = path.read_text(encoding="utf-8")
            doc_contents.append(f"--- Document: {path.name} ---\n{content}")
        else:
            logger.warning(f"Document not found: {doc_path}")

    if not doc_contents:
        return "No relevant documents found to answer your query."

    combined_docs = "\n\n".join(doc_contents)

    messages = [
        {"role": "system", "content": master_prompt},
        {"role": "user", "content": f"Based on the following documents, answer this query:\n\n{combined_docs}\n\nQuery: {user_query}"},
    ]

    response = completion(
        model=settings.high_capacity_llm_model,
        messages=messages,
        api_key=settings.high_capacity_llm_api_key or None,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )

    result = response.choices[0].message.content.strip()
    logger.info(f"Generated response for query: {user_query}")
    return result


def load_prompt(prompt_path: str | None = None) -> str:
    """Load the master prompt from file."""
    path = Path(prompt_path or "prompts/master_prompt.txt")
    return path.read_text(encoding="utf-8")
