"""Marker integration - converts PDF/Excel/CSV to Markdown (DP2)."""

import csv
import logging
from pathlib import Path
from config.settings import settings

logger = logging.getLogger(__name__)

_pdf_model_dict = None


def _get_pdf_model_dict():
    """Lazy-load and cache the Marker model dict to avoid reloading on every PDF."""
    global _pdf_model_dict
    if _pdf_model_dict is None:
        from marker.models import create_model_dict

        _pdf_model_dict = create_model_dict()
    return _pdf_model_dict


def _to_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Convert headers and rows into a Markdown table string."""
    if not headers:
        return ""
    header_row = "| " + " | ".join(str(h) for h in headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    data_rows = []
    for row in rows:
        padded = row + [""] * (len(headers) - len(row))
        data_rows.append("| " + " | ".join(str(c) for c in padded[: len(headers)]) + " |")
    return "\n".join([header_row, separator] + data_rows)


def convert_excel(file_path: Path, output_dir: Path | None = None) -> Path:
    """Convert an Excel file (.xlsx/.xls) to Markdown tables per sheet."""
    import openpyxl

    output_dir = output_dir or settings.markdown_dir_obj
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Converting Excel file {file_path} to Markdown...")
    wb = openpyxl.load_workbook(file_path, data_only=True)

    sections = [f"# {file_path.stem}\n"]
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue
        headers = [str(c) if c is not None else "" for c in rows[0]]
        data_rows = [[str(c) if c is not None else "" for c in row] for row in rows[1:]]
        sections.append(f"## {sheet_name}\n")
        sections.append(_to_markdown_table(headers, data_rows))
        sections.append("")

    md_filename = file_path.stem + ".md"
    md_path = output_dir / md_filename
    md_path.write_text("\n".join(sections), encoding="utf-8")
    logger.info(f"Markdown saved to {md_path}")
    return md_path


def convert_csv_file(file_path: Path, output_dir: Path | None = None) -> Path:
    """Convert a CSV file to a Markdown table."""
    output_dir = output_dir or settings.markdown_dir_obj
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Converting CSV file {file_path} to Markdown...")

    with open(file_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        md_content = f"# {file_path.stem}\n\n*Empty file*\n"
    else:
        headers = rows[0]
        data_rows = rows[1:]
        md_content = f"# {file_path.stem}\n\n{_to_markdown_table(headers, data_rows)}\n"

    md_filename = file_path.stem + ".md"
    md_path = output_dir / md_filename
    md_path.write_text(md_content, encoding="utf-8")
    logger.info(f"Markdown saved to {md_path}")
    return md_path


def convert_to_markdown(file_path: Path, output_dir: Path | None = None) -> Path:
    """Convert a single file to Markdown.

    PDFs use Marker; Excel/CSV files use native Python libraries.

    Args:
        file_path: Path to the input file (PDF/Excel/CSV)
        output_dir: Optional output directory override

    Returns:
        Path to the generated Markdown file
    """
    ext = file_path.suffix.lower()

    if ext == ".pdf":
        return _convert_pdf(file_path, output_dir)
    elif ext in (".xlsx", ".xls"):
        return convert_excel(file_path, output_dir)
    elif ext == ".csv":
        return convert_csv_file(file_path, output_dir)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def _convert_pdf(file_path: Path, output_dir: Path | None = None) -> Path:
    """Convert a PDF file to Markdown using Marker."""
    from marker.converters.pdf import PDFConverter
    from marker.output import text_from_rendered

    output_dir = output_dir or settings.markdown_dir_obj
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Converting PDF {file_path} to Markdown...")

    converter = PDFConverter(artifacts=_get_pdf_model_dict())
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
