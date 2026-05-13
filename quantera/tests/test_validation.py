"""T13: Categorisation validation metrics tests."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validate_categorisation import compute_category_metrics, normalise_company


class TestCategoryMetrics:
    def test_perfect_match(self):
        result = compute_category_metrics(
            ["financial report", "earnings"],
            ["financial report", "earnings"],
        )
        assert result["precision"] == 1.0
        assert result["recall"] == 1.0
        assert result["f1"] == 1.0

    def test_partial_overlap(self):
        result = compute_category_metrics(
            ["financial report", "earnings", "bonus"],
            ["financial report", "earnings"],
        )
        assert result["precision"] == pytest.approx(2 / 3)
        assert result["recall"] == 1.0

    def test_no_overlap(self):
        result = compute_category_metrics(
            ["marketing", "sales"],
            ["financial report", "earnings"],
        )
        assert result["precision"] == 0.0
        assert result["recall"] == 0.0
        assert result["f1"] == 0.0

    def test_case_insensitive(self):
        result = compute_category_metrics(
            ["Financial Report", "EARNINGS"],
            ["financial report", "earnings"],
        )
        assert result["f1"] == 1.0

    def test_empty_both(self):
        result = compute_category_metrics([], [])
        assert result["f1"] == 1.0

    def test_predicted_empty(self):
        result = compute_category_metrics([], ["financial report"])
        assert result["precision"] == 0.0
        assert result["recall"] == 0.0

    def test_expected_empty(self):
        result = compute_category_metrics(["financial report"], [])
        assert result["precision"] == 0.0
        assert result["recall"] == 0.0


class TestNormaliseCompany:
    def test_exact_match(self):
        assert normalise_company("TechCorp AB") == normalise_company("TechCorp AB")

    def test_case_insensitive(self):
        assert normalise_company("TechCorp AB") == normalise_company("techcorp ab")

    def test_ignores_spaces(self):
        assert normalise_company("Tech Corp AB") == normalise_company("TechCorpAB")

    def test_different_companies(self):
        assert normalise_company("TechCorp AB") != normalise_company("RetailCo AB")
