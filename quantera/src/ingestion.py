"""File detection and preparation (DP1) - scans input folder for supported file types."""

from pathlib import Path
from config.settings import settings

SUPPORTED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".csv"}


def get_input_files(input_dir: Path | None = None) -> list[Path]:
    """Scan input directory and return list of supported files."""
    dir_path = input_dir or settings.input_dir_obj
    if not dir_path.exists():
        return []
    return [
        f for f in dir_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def validate_file(file_path: Path) -> bool:
    """Check if a file has a supported extension and exists."""
    return file_path.exists() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
