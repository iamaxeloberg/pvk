"""T11: Accuracy and Relevance Assessment tests."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.assessment import (
    AssessmentResult,
    AssessmentReport,
    assess_response,
    run_assessment_suite,
    save_report,
)


class TestAssessmentResult:
    def test_passed_above_threshold(self):
        result = AssessmentResult(
            query="test",
            expected_answer="Revenue is 100M",
            actual_answer="Revenue is 100M",
            agent_used="kpi",
            overall_score=0.85,
        )
        assert result.passed() is True

    def test_passed_below_threshold(self):
        result = AssessmentResult(
            query="test",
            expected_answer="Revenue is 100M",
            actual_answer="Revenue is unknown",
            agent_used="kpi",
            overall_score=0.4,
        )
        assert result.passed() is False

    def test_passed_custom_threshold(self):
        result = AssessmentResult(
            query="test",
            expected_answer="Revenue is 100M",
            actual_answer="Revenue is 100M",
            agent_used="kpi",
            overall_score=0.6,
        )
        assert result.passed(threshold=0.5) is True
        assert result.passed(threshold=0.7) is False


class TestAssessmentReport:
    def test_empty_report(self):
        report = AssessmentReport()
        assert report.average_accuracy == 0.0
        assert report.pass_rate() == 0.0

    def test_average_scores(self):
        results = [
            AssessmentResult("q1", "exp", "act", "kpi", factual_accuracy=0.8, completeness=0.7, consistency=0.9, overall_score=0.8),
            AssessmentResult("q2", "exp", "act", "insight", factual_accuracy=0.6, completeness=0.5, consistency=0.7, overall_score=0.6),
        ]
        report = AssessmentReport(results=results)

        assert report.average_accuracy == pytest.approx(0.7)
        assert report.average_completeness == pytest.approx(0.6)
        assert report.average_consistency == pytest.approx(0.8)

    def test_pass_rate(self):
        results = [
            AssessmentResult("q1", "exp", "act", "kpi", overall_score=0.8),
            AssessmentResult("q2", "exp", "act", "insight", overall_score=0.9),
            AssessmentResult("q3", "exp", "act", "briefing", overall_score=0.4),
        ]
        report = AssessmentReport(results=results)
        assert report.pass_rate() == pytest.approx(2 / 3)

    def test_summary_contains_stats(self):
        results = [
            AssessmentResult("q1", "exp", "act", "kpi", overall_score=0.8, feedback="Good"),
        ]
        report = AssessmentReport(results=results)
        summary = report.summary()
        assert "1" in summary
        assert "0.80" in summary


class TestAssessResponse:
    @patch("src.assessment.completion")
    def test_assess_response_returns_scores(self, mock_completion):
        scores = json.dumps({
            "factual_accuracy": 0.9,
            "completeness": 0.8,
            "consistency": 0.95,
            "overall_score": 0.88,
            "feedback": "Good answer",
        })
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = scores

        result = assess_response(
            query="What is revenue?",
            expected_answer="Revenue is 100M",
            actual_answer="Revenue is 100M",
            agent_used="kpi",
        )

        assert result.factual_accuracy == 0.9
        assert result.completeness == 0.8
        assert result.consistency == 0.95
        assert result.overall_score == 0.88
        assert result.feedback == "Good answer"

    @patch("src.assessment.completion")
    def test_assess_response_handles_code_fences(self, mock_completion):
        scores = '```json\n{"factual_accuracy": 0.7, "completeness": 0.6, "consistency": 0.8, "overall_score": 0.7, "feedback": "OK"}\n```'
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = scores

        result = assess_response("Q", "exp", "act")
        assert result.factual_accuracy == 0.7

    @patch("src.assessment.completion")
    def test_assess_response_handles_api_error(self, mock_completion):
        mock_completion.side_effect = Exception("API error")

        result = assess_response("Q", "exp", "act")
        assert "API error" in result.feedback
        assert result.overall_score == 0.0


class TestRunAssessmentSuite:
    @patch("src.assessment.completion")
    def test_run_suite_multiple_cases(self, mock_completion):
        scores = json.dumps({
            "factual_accuracy": 0.8,
            "completeness": 0.7,
            "consistency": 0.9,
            "overall_score": 0.8,
            "feedback": "Good",
        })
        mock_completion.return_value.choices = [MagicMock()]
        mock_completion.return_value.choices[0].message.content = scores

        test_cases = [
            {"query": "Q1", "expected_answer": "A1", "actual_answer": "A1", "agent_used": "kpi"},
            {"query": "Q2", "expected_answer": "A2", "actual_answer": "A2", "agent_used": "insight"},
        ]

        report = run_assessment_suite(test_cases)
        assert len(report.results) == 2


class TestSaveReport:
    def test_save_report_creates_file(self, tmp_path):
        results = [
            AssessmentResult("q1", "exp", "act", "kpi", overall_score=0.8, feedback="Good"),
        ]
        report = AssessmentReport(results=results)
        output_path = tmp_path / "report.json"

        save_report(report, output_path)

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert data["summary"]["total_evaluations"] == 1
        assert len(data["results"]) == 1
