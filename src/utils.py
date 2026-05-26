"""Shared utility functions."""

import json
import logging
import os
import re
from pathlib import Path

LOG_DIR = Path("logs")
_PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def setup_logging(level: str = "INFO", log_to_file: bool = True) -> None:
    """Configure centralized logging with console and optional file output.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to also write logs to a file
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers: list[logging.Handler] = [
        logging.StreamHandler(),
    ]

    if log_to_file:
        LOG_DIR.mkdir(exist_ok=True)
        log_file = LOG_DIR / "quantera.log"
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)

    logging.basicConfig(level=getattr(logging, level.upper()), format=log_format, handlers=handlers)


def llm_completion(
    model: str,
    messages: list[dict],
    api_key: str | None = None,
    api_base: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 1024,
    num_retries: int = 2,
    timeout: int = 60,
):
    """Wrapper around litellm.completion with retries and timeout.

    Args:
        model: LiteLLM model identifier
        messages: List of message dicts
        api_key: API key (or None)
        api_base: API base URL (or None)
        temperature: Sampling temperature
        max_tokens: Maximum output tokens
        num_retries: Number of retry attempts on transient errors
        timeout: Request timeout in seconds

    Returns:
        LiteLLM completion response

    Raises:
        Exception on failure after all retries
    """
    from litellm import completion

    os.environ.setdefault("LITELLM_REQUEST_TIMEOUT", str(timeout))

    last_error = None
    for attempt in range(num_retries + 1):
        try:
            return completion(
                model=model,
                messages=messages,
                api_key=api_key or None,
                api_base=api_base or None,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
        except Exception as e:
            last_error = e
            logger = logging.getLogger(__name__)
            if attempt < num_retries:
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{num_retries + 1}): {e}. Retrying...")
            else:
                logger.error(f"LLM call failed after {num_retries + 1} attempts: {e}")
    raise last_error


def get_llm_content(response) -> str:
    """Safely extract content from an LLM response.

    Args:
        response: LiteLLM completion response

    Returns:
        The message content string, or empty string if response is empty/missing
    """
    if not response or not response.choices:
        logging.getLogger(__name__).warning("LLM returned empty response (no choices)")
        return ""
    content = response.choices[0].message.content
    if content is None:
        logging.getLogger(__name__).warning("LLM returned None content")
        return ""
    return content.strip()


def safe_parse_llm_json(text: str) -> dict:
    """Parse JSON from an LLM response with multiple fallback strategies.

    Handles markdown code fences, surrounding text, and malformed JSON.

    Returns:
        Parsed dict, or dict with "error" key on failure
    """
    if not text:
        return {"error": "Empty response from LLM"}

    cleaned = text.strip()

    parsed = None
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    if parsed is None:
        parts = cleaned.split("```")
        if len(parts) > 1:
            candidate = parts[1]
            if candidate.startswith("json"):
                candidate = candidate[4:]
            candidate = candidate.strip()
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                pass

    if parsed is None:
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    if parsed is None:
        match = re.search(r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]', cleaned, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    if parsed is None:
        return {"error": "Failed to parse LLM JSON response"}

    return parsed


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_prompt(name: str) -> str:
    """Read a prompt file from the prompts directory.

    Uses absolute path relative to the source directory so it works
    regardless of the current working directory.

    Args:
        name: Prompt name without extension (e.g. 'categorisation')
              or a full file path.

    Raises:
        FileNotFoundError: If the prompt file does not exist
    """
    if Path(name).is_absolute():
        path = Path(name)
    else:
        path = _PROMPT_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def validate_config() -> list[str]:
    """Validate that required configuration is present. Returns list of warnings."""
    from config.settings import settings
    warnings = []
    if not settings.low_cost_llm_api_key:
        warnings.append("LOW_COST_LLM_API_KEY is not set")
    if not settings.high_capacity_llm_api_key:
        warnings.append("HIGH_CAPACITY_LLM_API_KEY is not set")
    if not settings.low_cost_llm_api_base:
        warnings.append("LOW_COST_LLM_API_BASE is not set")
    if not settings.high_capacity_llm_api_base:
        warnings.append("HIGH_CAPACITY_LLM_API_BASE is not set")
    input_dir = Path(settings.input_dir)
    if not input_dir.exists():
        warnings.append(f"Input directory does not exist: {input_dir}")
    markdown_dir = Path(settings.markdown_dir)
    if not markdown_dir.exists():
        warnings.append(f"Markdown directory does not exist: {markdown_dir}")
    db_dir = Path(settings.db_path).parent
    if not db_dir.exists():
        warnings.append(f"Database directory does not exist: {db_dir}")
    return warnings
