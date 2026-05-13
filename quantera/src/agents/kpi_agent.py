"""KPI Sub-Agent - Extracts and tracks financial metrics from documents."""

import json
import logging
import sqlite3
from pathlib import Path
from litellm import completion
from config.settings import settings
from src.utils import read_prompt

logger = logging.getLogger(__name__)


def extract_kpis(
    user_query: str,
    relevant_documents: list[str],
    db_conn: sqlite3.Connection | None = None,
) -> dict:
    """Extract key performance indicators from relevant documents.

    Args:
        user_query: The user's query about financial metrics
        relevant_documents: List of Markdown file paths to analyse
        db_conn: Optional SQLite connection to store KPIs for time-series tracking

    Returns:
        Dict with company, period, and list of KPI objects
    """
    prompt = read_prompt("kpi_extraction")

    doc_contents = []
    for doc_path in relevant_documents:
        path = Path(doc_path)
        if path.exists():
            content = path.read_text(encoding="utf-8")
            doc_contents.append(f"--- Document: {path.name} ---\n{content}")
        else:
            logger.warning(f"Document not found: {doc_path}")

    if not doc_contents:
        return {"company": "", "period": "", "kpis": [], "error": "No relevant documents found"}

    combined_docs = "\n\n".join(doc_contents)

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Extract all financial KPIs from these documents:\n\n{combined_docs}\n\nUser query: {user_query}"},
    ]

    response = completion(
        model=settings.high_capacity_llm_model,
        messages=messages,
        api_key=settings.high_capacity_llm_api_key or None,
        temperature=0.0,
        max_tokens=2048,
    )

    result_text = response.choices[0].message.content.strip()

    parts = result_text.split("```")
    if len(parts) > 1:
        result_text = parts[1]
        if result_text.startswith("json"):
            result_text = result_text[4:]
    result_text = result_text.strip()

    try:
        kpis = json.loads(result_text)
        logger.info(f"Extracted {len(kpis.get('kpis', []))} KPIs for query: {user_query}")

        if db_conn is not None:
            from src.kpi_store import store_kpis

            source = relevant_documents[0] if relevant_documents else ""
            stored = store_kpis(db_conn, kpis, source)
            kpis["kpis_stored"] = stored

        return kpis
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse KPI JSON: {e}")
        return {"company": "", "period": "", "kpis": [], "error": f"Failed to parse KPI data: {e}"}


def format_kpi_response(kpi_data: dict) -> str:
    """Format extracted KPI data into a human-readable response.

    Args:
        kpi_data: Dict from extract_kpis()

    Returns:
        Formatted string response
    """
    if kpi_data.get("error"):
        return kpi_data["error"]

    lines = []
    company = kpi_data.get("company", "Unknown")
    period = kpi_data.get("period", "N/A")

    lines.append(f"# KPI Report: {company}")
    lines.append(f"Period: {period}\n")

    kpis = kpi_data.get("kpis", [])
    if not kpis:
        lines.append("No KPIs extracted from the documents.")
        return "\n".join(lines)

    for kpi in kpis:
        metric = kpi.get("metric", "Unknown")
        value = kpi.get("value", "N/A")
        unit = kpi.get("unit", "")
        context = kpi.get("context", "")

        value_str = f"{value} {unit}".strip()
        lines.append(f"- **{metric}**: {value_str}")
        if context:
            lines.append(f"  _{context}_")

    return "\n".join(lines)
