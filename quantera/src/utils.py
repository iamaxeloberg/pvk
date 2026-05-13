"""Shared utility functions."""

import logging
from pathlib import Path

LOG_DIR = Path("logs")


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


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_prompt(name: str) -> str:
    """Read a prompt file from the prompts directory.

    Args:
        name: Prompt name without extension (e.g. 'categorisation')
              or a full file path.
    """
    path = Path(name) if Path(name).is_absolute() else Path("prompts") / f"{name}.txt"
    return path.read_text(encoding="utf-8")
