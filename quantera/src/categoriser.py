"""Low-cost LLM metadata extraction (DP3-DP4) - extracts company name and categories."""

import logging
from pathlib import Path
from config.settings import settings
from src.utils import read_prompt, get_llm_content, llm_completion, safe_parse_llm_json

logger = logging.getLogger(__name__)


def extract_metadata(markdown_content: str, markdown_path: Path) -> dict:
    """Use low-cost LLM to extract company, categories, and file path from Markdown."""
    prompt = read_prompt("categorisation")

    max_chars = 8000
    if len(markdown_content) > max_chars:
        content = markdown_content[:max_chars] + "\n\n[Document truncated for analysis...]"
    else:
        content = markdown_content

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Analyse this document and extract metadata:\n\n{content}"},
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
    metadata = safe_parse_llm_json(result_text)

    if "error" in metadata:
        logger.error(f"Failed to parse categorisation metadata: {metadata['error']}")
        return {"company": "Unknown", "categories": ["Uncategorised"], "markdown_file_path": str(markdown_path)}

    metadata["markdown_file_path"] = str(markdown_path)
    logger.info(f"Extracted metadata: {metadata}")
    return metadata
