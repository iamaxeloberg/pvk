"""Marker integration - converts PDF/Excel/CSV to Markdown (DP2)."""

import logging
from pathlib import Path
from config.settings import settings

logger = logging.getLogger(__name__)


def convert_to_markdown(file_path: Path, output_dir: Path | None = None) -> Path:
    """Convert a single file to Markdown using Marker.

    Args:
        file_path: Path to the input file (PDF/Excel/CSV)
        output_dir: Optional output directory override

    Returns:
        Path to the generated Markdown file
    """
    from marker.converters.pdf import PDFConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered

    output_dir = output_dir or settings.markdown_dir_obj
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Converting {file_path} to Markdown...")

    converter = PDFConverter(artifacts=create_model_dict())
    rendered = converter(file_path)
    text, _, images = text_from_rendered(rendered)

    md_filename = file_path.stem + ".md"
    md_path = output_dir / md_filename
    md_path.write_text(text, encoding="utf-8")

    logger.info(f"Markdown saved to {md_path}")
    return md_path


def convert_batch(file_paths: list[Path], output_dir: Path | None = None) -> list[Path]:
    """Convert multiple files to Markdown.

    Returns:
        List of paths to generated Markdown files
    """
    results = []
    for fp in file_paths:
        try:
            md_path = convert_to_markdown(fp, output_dir)
            results.append(md_path)
        except Exception as e:
            logger.error(f"Failed to convert {fp}: {e}")
            print(f"Failed to convert {fp}: {e}")
    return results
