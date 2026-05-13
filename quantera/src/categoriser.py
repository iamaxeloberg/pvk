"""Low-cost LLM metadata extraction (DP3-DP4) - extracts company name and categories."""

import json
import logging
from pathlib import Path
from litellm import completion
from config.settings import settings
from src.utils import read_prompt

logger = logging.getLogger(__name__)


def extract_metadata(markdown_content: str, markdown_path: Path) -> dict:
    """Use low-cost LLM to extract company, categories, and file path from Markdown.

    Args:
        markdown_content: The Markdown text to analyse
        markdown_path: Path to the Markdown file

    Returns:
        Dict with keys: company, categories, markdown_file_path
    """
    prompt = read_prompt("categorisation")

    # Truncate very long documents to control token costs
    max_chars = 8000
    if len(markdown_content) > max_chars:
        content = markdown_content[:max_chars] + "\n\n[Document truncated for analysis...]"
    else:
        content = markdown_content

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Analyse this document and extract metadata:\n\n{content}"},
    ]

    response = completion(
        model=settings.low_cost_llm_model,
        messages=messages,
        api_key=settings.low_cost_llm_api_key or None,
        api_base=settings.low_cost_llm_api_base or None,
        temperature=0.0,
        max_tokens=512,
    )

    result_text = response.choices[0].message.content.strip()

    # Parse JSON from response (handle potential markdown code blocks)
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:]
    result_text = result_text.strip()

    metadata = json.loads(result_text)

    # Ensure markdown_file_path is set correctly
    metadata["markdown_file_path"] = str(markdown_path)

    logger.info(f"Extracted metadata: {metadata}")
    return metadata
