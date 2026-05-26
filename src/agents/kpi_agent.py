"""KPI Sub-Agent - Extracts and tracks financial metrics from documents."""

import logging
import sqlite3

from config.settings import settings
from src.utils import get_llm_content, llm_completion, load_documents_for_prompt, read_prompt, safe_parse_llm_json

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

    combined_docs = load_documents_for_prompt(relevant_documents, settings.max_doc_size_chars)

    if not combined_docs:
        return {"company": "", "period": "", "kpis": [], "error": "No relevant documents found"}

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Extract all financial KPIs from these documents:\n\n{combined_docs}\n\nUser query: {user_query}"},
    ]

    logger.info("Extracting KPIs via LLM...")
    response = llm_completion(
        model=settings.high_capacity_llm_model,
        messages=messages,
        api_key=settings.high_capacity_llm_api_key or None,
        api_base=settings.high_capacity_llm_api_base or None,
        temperature=0.0,
        max_tokens=settings.max_tokens,
    )

    result_text = get_llm_content(response)

    parsed = safe_parse_llm_json(result_text)

    if "error" in parsed:
        logger.error(f"Failed to parse KPI JSON: {parsed['error']}")
        return {"company": "", "period": "", "kpis": [], "error": f"Failed to parse KPI data: {parsed['error']}"}

    kpis = parsed[0] if isinstance(parsed, list) and parsed else parsed
    logger.info(f"Extracted {len(kpis.get('kpis', []))} KPIs for query: {user_query}")

    if db_conn is not None:
        from src.kpi_store import store_kpis

        source = relevant_documents[0] if relevant_documents else ""
        stored = store_kpis(db_conn, kpis, source)
        kpis["kpis_stored"] = stored

    return kpis


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
