"""Shared utility functions."""

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_prompt(name: str) -> str:
    """Read a prompt file from the prompts directory."""
    prompt_path = Path("prompts") / f"{name}.txt"
    return prompt_path.read_text(encoding="utf-8")
