"""KPI Store - Time-series storage for extracted financial metrics."""

import logging
import re
import sqlite3
from pathlib import Path

from config.settings import settings
from src.utils import escape_like

logger = logging.getLogger(__name__)

_QUARTER_MAP = {"q1": 1, "q2": 2, "q3": 3, "q4": 4}
_HALF_MAP = {"h1": 1, "h2": 2}


def _period_sort_key(period: str) -> tuple:
    """Parse a period string into a sortable (year, sub_period) tuple.

    Handles: "Q1 2025", "Q4 2024", "H1 2025", "FY 2024", "2025", etc.
    Unknown formats sort to (9999, 0).
    """
    period_lower = period.lower().strip()

    match = re.match(r"q([1-4])\s*(\d{4})", period_lower)
    if match:
        return (int(match.group(2)), int(match.group(1)))

    match = re.match(r"h([1-2])\s*(\d{4})", period_lower)
    if match:
        return (int(match.group(2)), int(match.group(1)) + 4)

    match = re.match(r"fy\s*(\d{4})", period_lower)
    if match:
        return (int(match.group(1)), 9)

    match = re.match(r"(\d{4})", period_lower)
    if match:
        return (int(match.group(1)), 0)

    return (9999, 0)


def init_kpi_table(db_path: Path | None = None) -> sqlite3.Connection:
    """Initialise the KPI store table in the database."""
    conn = sqlite3.connect(str(db_path or settings.db_path_obj))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kpi_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            metric TEXT NOT NULL,
            value REAL,
            value_raw TEXT,
            unit TEXT,
            period TEXT,
            context TEXT,
            source_file TEXT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_kpi_company ON kpi_store(company)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_kpi_metric ON kpi_store(metric)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_kpi_period ON kpi_store(period)
    """)
    conn.commit()
    logger.info(f"KPI store table initialised at {db_path or settings.db_path_obj}")
    return conn


def store_kpis(conn: sqlite3.Connection, kpi_data: dict, source_file: str = "") -> int:
    """Store extracted KPIs in the time-series database.

    Args:
        conn: SQLite connection
        kpi_data: Dict from KPI agent with company, period, kpis list
        source_file: Source document path

    Returns:
        Number of KPIs stored
    """
    company = kpi_data.get("company", "Unknown")
    period = kpi_data.get("period", "")
    kpis = kpi_data.get("kpis", [])

    stored = 0
    for kpi in kpis:
        metric = kpi.get("metric", "")
        value_raw = str(kpi.get("value", "")) if kpi.get("value") is not None else ""

        try:
            value = float(kpi.get("value"))
        except (ValueError, TypeError):
            value = None

        unit = kpi.get("unit", "")
        context = kpi.get("context", "")

        conn.execute(
            """INSERT INTO kpi_store (company, metric, value, value_raw, unit, period, context, source_file)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (company, metric, value, value_raw, unit, period, context, source_file),
        )
        stored += 1

    conn.commit()
    logger.info(f"Stored {stored} KPIs for {company} ({period})")
    return stored


def get_kpi_trend(
    conn: sqlite3.Connection,
    company: str,
    metric: str,
) -> list[dict]:
    """Retrieve time-series data for a specific company and metric.

    Args:
        conn: SQLite connection
        company: Company name
        metric: KPI metric name (e.g. Revenue, Gross Margin)

    Returns:
        List of dicts with period, value, unit, context, source_file
    """
    cursor = conn.execute(
        """SELECT period, value, value_raw, unit, context, source_file, extracted_at
           FROM kpi_store
           WHERE company LIKE ? ESCAPE '\\' AND metric LIKE ? ESCAPE '\\'""",
        (f"%{escape_like(company)}%", f"%{escape_like(metric)}%"),
    )
    rows = cursor.fetchall()
    results = [
        {
            "period": r["period"],
            "value": r["value"],
            "value_raw": r["value_raw"],
            "unit": r["unit"],
            "context": r["context"],
            "source_file": r["source_file"],
            "extracted_at": r["extracted_at"],
        }
        for r in rows
    ]
    results.sort(key=lambda x: _period_sort_key(x["period"]))
    return results


def get_all_kpis_for_company(conn: sqlite3.Connection, company: str) -> dict[str, list[dict]]:
    """Get all KPIs for a company, grouped by metric.

    Args:
        conn: SQLite connection
        company: Company name

    Returns:
        Dict mapping metric name to list of time-series entries
    """
    cursor = conn.execute(
        """SELECT metric, period, value, value_raw, unit, context, source_file
           FROM kpi_store
           WHERE company LIKE ? ESCAPE '\\'""",
        (f"%{escape_like(company)}%",),
    )
    rows = cursor.fetchall()

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        metric = row["metric"]
        if metric not in grouped:
            grouped[metric] = []
        grouped[metric].append({
            "period": row["period"],
            "value": row["value"],
            "value_raw": row["value_raw"],
            "unit": row["unit"],
            "context": row["context"],
            "source_file": row["source_file"],
        })

    for entries in grouped.values():
        entries.sort(key=lambda x: _period_sort_key(x["period"]))

    return grouped


def get_companies_with_kpis(conn: sqlite3.Connection) -> list[str]:
    """Get list of unique companies that have stored KPIs."""
    cursor = conn.execute("SELECT DISTINCT company FROM kpi_store ORDER BY company")
    return [r["company"] for r in cursor.fetchall()]


def get_available_metrics(conn: sqlite3.Connection) -> list[str]:
    """Get list of unique metrics in the KPI store."""
    cursor = conn.execute("SELECT DISTINCT metric FROM kpi_store ORDER BY metric")
    return [r["metric"] for r in cursor.fetchall()]


def delete_kpis_for_company(conn: sqlite3.Connection, company: str) -> int:
    """Delete all KPIs for a specific company.

    Returns:
        Number of rows deleted
    """
    cursor = conn.execute("DELETE FROM kpi_store WHERE company LIKE ? ESCAPE '\\'", (f"%{escape_like(company)}%",))
    conn.commit()
    return cursor.rowcount
