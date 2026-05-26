"""T12: KPI Store time-series tests."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indexer import close_db
from src.kpi_store import (
    delete_kpis_for_company,
    get_all_kpis_for_company,
    get_available_metrics,
    get_companies_with_kpis,
    get_kpi_trend,
    init_kpi_table,
    store_kpis,
)


class TestKPIStore:
    @pytest.fixture
    def kpi_conn(self, tmp_path):
        db_path = tmp_path / "test.db"
        conn = init_kpi_table(db_path)
        yield conn
        close_db(conn)

    def test_init_kpi_table(self, tmp_path):
        db_path = tmp_path / "test.db"
        conn = init_kpi_table(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kpi_store'")
        assert cursor.fetchone() is not None
        close_db(conn)

    def test_store_kpis(self, kpi_conn):
        kpi_data = {
            "company": "TechCorp",
            "period": "Q1 2025",
            "kpis": [
                {"metric": "Revenue", "value": 145.2, "unit": "SEK M", "context": "Up 12% YoY"},
                {"metric": "Gross Margin", "value": 62.3, "unit": "%", "context": ""},
            ],
        }
        stored = store_kpis(kpi_conn, kpi_data, "/data/techcorp.md")
        assert stored == 2

    def test_get_kpi_trend(self, kpi_conn):
        for period, value in [("Q1 2025", 100.0), ("Q2 2025", 120.0), ("Q3 2025", 115.0)]:
            store_kpis(kpi_conn, {
                "company": "TechCorp",
                "period": period,
                "kpis": [{"metric": "Revenue", "value": value, "unit": "SEK M", "context": ""}],
            }, "/data/techcorp.md")

        trend = get_kpi_trend(kpi_conn, "TechCorp", "Revenue")
        assert len(trend) == 3
        assert trend[0]["period"] == "Q1 2025"
        assert trend[0]["value"] == 100.0
        assert trend[1]["value"] == 120.0

    def test_get_all_kpis_for_company(self, kpi_conn):
        store_kpis(kpi_conn, {
            "company": "TechCorp",
            "period": "Q1 2025",
            "kpis": [
                {"metric": "Revenue", "value": 100, "unit": "M", "context": ""},
                {"metric": "EBITDA", "value": 25, "unit": "M", "context": ""},
            ],
        }, "/data/techcorp.md")

        all_kpis = get_all_kpis_for_company(kpi_conn, "TechCorp")
        assert "Revenue" in all_kpis
        assert "EBITDA" in all_kpis
        assert len(all_kpis["Revenue"]) == 1

    def test_get_companies_with_kpis(self, kpi_conn):
        store_kpis(kpi_conn, {
            "company": "TechCorp",
            "period": "Q1",
            "kpis": [{"metric": "Revenue", "value": 100, "unit": "M", "context": ""}],
        }, "/data/tech.md")
        store_kpis(kpi_conn, {
            "company": "RetailCo",
            "period": "Q1",
            "kpis": [{"metric": "Revenue", "value": 50, "unit": "M", "context": ""}],
        }, "/data/retail.md")

        companies = get_companies_with_kpis(kpi_conn)
        assert "RetailCo" in companies
        assert "TechCorp" in companies

    def test_get_available_metrics(self, kpi_conn):
        store_kpis(kpi_conn, {
            "company": "TechCorp",
            "period": "Q1",
            "kpis": [
                {"metric": "Revenue", "value": 100, "unit": "M", "context": ""},
                {"metric": "EBITDA", "value": 25, "unit": "M", "context": ""},
            ],
        }, "/data/tech.md")

        metrics = get_available_metrics(kpi_conn)
        assert "Revenue" in metrics
        assert "EBITDA" in metrics

    def test_delete_kpis_for_company(self, kpi_conn):
        store_kpis(kpi_conn, {
            "company": "TechCorp",
            "period": "Q1",
            "kpis": [{"metric": "Revenue", "value": 100, "unit": "M", "context": ""}],
        }, "/data/tech.md")

        deleted = delete_kpis_for_company(kpi_conn, "TechCorp")
        assert deleted == 1

        trend = get_kpi_trend(kpi_conn, "TechCorp", "Revenue")
        assert trend == []

    def test_store_kpis_with_non_numeric_value(self, kpi_conn):
        kpi_data = {
            "company": "TechCorp",
            "period": "Q1 2025",
            "kpis": [{"metric": "Outlook", "value": "Positive", "unit": "", "context": "Strong demand"}],
        }
        stored = store_kpis(kpi_conn, kpi_data, "/data/techcorp.md")
        assert stored == 1

        trend = get_kpi_trend(kpi_conn, "TechCorp", "Outlook")
        assert len(trend) == 1
        assert trend[0]["value"] is None
        assert trend[0]["value_raw"] == "Positive"

    def test_kpi_trend_ordered_by_period(self, kpi_conn):
        for period in ["Q3 2025", "Q1 2025", "Q2 2025"]:
            store_kpis(kpi_conn, {
                "company": "TechCorp",
                "period": period,
                "kpis": [{"metric": "Revenue", "value": 100, "unit": "M", "context": ""}],
            }, "/data/tech.md")

        trend = get_kpi_trend(kpi_conn, "TechCorp", "Revenue")
        periods = [e["period"] for e in trend]
        assert periods == sorted(periods)

    def test_kpi_trend_ordered_across_years(self, kpi_conn):
        """Periods must sort chronologically across year boundaries, not lexicographically."""
        for period in ["Q1 2026", "Q4 2025", "Q2 2025", "Q1 2025", "FY 2024"]:
            store_kpis(kpi_conn, {
                "company": "TechCorp",
                "period": period,
                "kpis": [{"metric": "Revenue", "value": 100, "unit": "M", "context": ""}],
            }, "/data/tech.md")

        trend = get_kpi_trend(kpi_conn, "TechCorp", "Revenue")
        periods = [e["period"] for e in trend]
        assert periods == ["FY 2024", "Q1 2025", "Q2 2025", "Q4 2025", "Q1 2026"]
