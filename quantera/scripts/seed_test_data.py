#!/usr/bin/env python3
"""Generate synthetic test documents for development and testing."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


SAMPLE_COMPANIES = [
    {
        "name": "TechCorp AB",
        "document": "Q1 2025 Financial Report",
        "data": [
            ["Metric", "Value", "Change YoY"],
            ["Total Revenue", "SEK 145.2M", "+12%"],
            ["Recurring Revenue", "SEK 98.5M", "+18%"],
            ["Gross Margin", "62.3%", ""],
            ["EBITDA Margin", "24.1%", ""],
            ["Operating Margin", "18.7%", ""],
            ["Operating Cash Flow", "SEK 32.1M", ""],
            ["Free Cash Flow", "SEK 28.4M", ""],
            ["ARR", "SEK 410M", ""],
            ["NRR", "115%", ""],
            ["Customer Count", "342", ""],
        ],
    },
    {
        "name": "Nordic Retail Group",
        "document": "Annual Portfolio Review 2024",
        "data": [
            ["Metric", "Value", "Notes"],
            ["Revenue", "SEK 2.1B", "-3% YoY"],
            ["Gross Margin", "34.2%", ""],
            ["EBITDA", "SEK 185M", ""],
            ["Net Debt", "SEK 420M", ""],
            ["Store Count", "127", "Sweden, Norway, Denmark"],
            ["Planned Closures", "8-12", ""],
            ["Digital Investment", "SEK 45M", ""],
        ],
        "risks": [
            "Increasing competition from e-commerce",
            "Rising labor costs in Sweden",
            "Currency exposure in Norway and Denmark",
        ],
    },
    {
        "name": "GreenEnergy Solutions",
        "document": "Market Analysis 2025",
        "data": [
            ["Metric", "Value", "Notes"],
            ["Nordic Wind Market Share", "14%", ""],
            ["Installed Capacity", "890 MW", ""],
            ["Pipeline Projects", "340 MW", ""],
            ["Expected Revenue 2025", "SEK 680M", ""],
            ["Expected EBITDA Margin", "31-33%", ""],
            ["CapEx Requirement", "SEK 220M", ""],
        ],
        "competitors": ["Vattenfall", "Orsted", "Statkraft"],
    },
]


def generate_test_data():
    """Create synthetic CSV files and run the full ingestion pipeline."""
    input_dir = settings.input_dir_obj
    input_dir.mkdir(parents=True, exist_ok=True)

    for company in SAMPLE_COMPANIES:
        filename = f"{company['name'].lower().replace(' ', '_')}_report.csv"
        filepath = input_dir / filename

        rows = [["Company", "Document", "Metric", "Value", "Notes"]]
        for row in company["data"]:
            rows.append([company["name"], company["document"]] + row + [""] * (5 - len(row) - 2))

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        print(f"Created: {filepath}")

    print(f"\nGenerated {len(SAMPLE_COMPANIES)} test files in {input_dir}")
    print("\nRunning ingestion pipeline...\n")

    from src.api import run_pipeline
    run_pipeline()


if __name__ == "__main__":
    generate_test_data()
