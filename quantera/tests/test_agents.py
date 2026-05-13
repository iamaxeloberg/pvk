"""T10: Sub-agent and AI router tests."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.router import classify_query, VALID_AGENTS
from src.agents import router as router_module
from src.agents.kpi_agent import extract_kpis, format_kpi_response
from src.agents.insight_agent import generate_insights
from src.agents.briefing_agent import generate_briefing


class TestAgentRouter:
    @patch("src.agents.router.completion")
    def test_classify_kpi_query(self, mock_completion):
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = "kpi"

        result = classify_query("What was TechCorp's revenue in Q1?")
        assert result == "kpi"

    @patch("src.agents.router.completion")
    def test_classify_insight_query(self, mock_completion):
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = "insight"

        result = classify_query("Analyse the profitability trends")
        assert result == "insight"

    @patch("src.agents.router.completion")
    def test_classify_briefing_query(self, mock_completion):
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = "briefing"

        result = classify_query("Give me a briefing on Nordic Retail")
        assert result == "briefing"

    @patch("src.agents.router.completion")
    def test_classify_general_query(self, mock_completion):
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = "general"

        result = classify_query("What documents do we have?")
        assert result == "general"

    @patch("src.agents.router.completion")
    def test_classify_invalid_agent_defaults_to_general(self, mock_completion):
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = "invalid_agent"

        result = classify_query("test query")
        assert result == "general"

    @patch("src.agents.router.completion")
    def test_classify_handles_whitespace(self, mock_completion):
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = "  KPI  "

        result = classify_query("test query")
        assert result == "kpi"

    @patch("src.agents.kpi_agent.completion")
    def test_route_with_explicit_kpi_agent(self, mock_completion):
        """Test that passing agent='kpi' routes to the KPI agent."""
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = json.dumps({
            "company": "TestCo",
            "period": "Q1",
            "kpis": [{"metric": "Revenue", "value": 100, "unit": "M", "context": ""}],
        })

        result = router_module.route_query("What is revenue?", ["/doc.md"], agent="kpi")
        assert result["agent_used"] == "kpi"
        assert "TestCo" in result["response"]


class TestKPIAgent:
    @patch("src.agents.kpi_agent.completion")
    def test_extract_kpis_returns_structured_data(self, mock_completion):
        kpi_json = json.dumps({
            "company": "TechCorp",
            "period": "Q1 2025",
            "kpis": [
                {"metric": "Revenue", "value": 145.2, "unit": "SEK M", "context": "Up 12% YoY"},
                {"metric": "Gross Margin", "value": 62.3, "unit": "%", "context": ""},
            ],
        })
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = kpi_json

        result = extract_kpis("What are the KPIs?", ["/doc.md"])

        assert result["company"] == "TechCorp"
        assert len(result["kpis"]) == 2
        assert result["kpis"][0]["metric"] == "Revenue"

    @patch("src.agents.kpi_agent.completion")
    def test_extract_kpis_handles_code_fences(self, mock_completion):
        kpi_json = '```json\n{"company": "Test", "period": "FY", "kpis": []}\n```'
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = kpi_json

        result = extract_kpis("KPIs?", ["/doc.md"])
        assert result["company"] == "Test"

    def test_extract_kpis_no_documents(self):
        result = extract_kpis("KPIs?", [])
        assert result["error"] == "No relevant documents found"

    def test_format_kpi_response(self):
        kpi_data = {
            "company": "TechCorp",
            "period": "Q1 2025",
            "kpis": [
                {"metric": "Revenue", "value": 145.2, "unit": "SEK M", "context": "Up 12% YoY"},
            ],
        }
        formatted = format_kpi_response(kpi_data)
        assert "TechCorp" in formatted
        assert "Revenue" in formatted
        assert "145.2 SEK M" in formatted

    def test_format_kpi_response_error(self):
        formatted = format_kpi_response({"error": "Something went wrong"})
        assert "Something went wrong" in formatted

    def test_format_kpi_response_no_kpis(self):
        formatted = format_kpi_response({"company": "Test", "period": "Q1", "kpis": []})
        assert "No KPIs extracted" in formatted


class TestInsightAgent:
    @patch("src.agents.insight_agent.completion")
    def test_generate_insights_returns_text(self, mock_completion):
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = "## Analysis\nRevenue is strong."

        result = generate_insights("Analyse trends", ["/doc.md"])
        assert "Revenue" in result

    def test_generate_insights_no_documents(self):
        result = generate_insights("Analyse", [])
        assert "No relevant documents" in result


class TestBriefingAgent:
    @patch("src.agents.briefing_agent.completion")
    def test_generate_briefing_returns_text(self, mock_completion):
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = "## Executive Summary\nCompany is doing well."

        result = generate_briefing("Brief me", ["/doc.md"])
        assert "Executive Summary" in result or "Company" in result

    def test_generate_briefing_no_documents(self):
        result = generate_briefing("Brief me", [])
        assert "No relevant documents" in result


class TestAgentIntegration:
    @patch("src.agents.router.completion")
    @patch("src.agents.kpi_agent.completion")
    def test_full_kpi_route(self, mock_kpi, mock_router, tmp_path):
        doc = tmp_path / "test.md"
        doc.write_text("# TechCorp\nRevenue: 100M", encoding="utf-8")

        mock_router.return_value.choices = [MagicMock()]
        mock_router.return_value.choices[0].message.content = "kpi"

        mock_kpi.return_value.choices = [MagicMock()]
        mock_kpi.return_value.choices[0].message.content = json.dumps({
            "company": "TechCorp",
            "period": "Q1",
            "kpis": [{"metric": "Revenue", "value": 100, "unit": "M", "context": ""}],
        })

        result = route_query("What is revenue?", [str(doc)])

        assert result["agent_used"] == "kpi"
        assert "TechCorp" in result["response"]
