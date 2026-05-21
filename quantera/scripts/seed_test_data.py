#!/usr/bin/env python3
"""Generate synthetic test documents for development and testing."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


SAMPLE_COMPANIES = [
    {
        "name": "Volvo Group",
        "document": "Q1 2025 Financial Report",
        "data": [
            ["Metric", "Value", "Change YoY"],
            ["Net Sales", "SEK 132.4B", "+8%"],
            ["Adjusted Operating Income", "SEK 18.9B", "+12%"],
            ["Operating Margin", "14.3%", "+0.5pp"],
            ["EBITDA", "SEK 24.1B", "+10%"],
            ["EBITDA Margin", "18.2%", "+0.3pp"],
            ["Free Cash Flow", "SEK 8.7B", "+22%"],
            ["Net Financial Position", "SEK -42.1B", ""],
            ["Truck Deliveries", "55,400", "+6%"],
            ["Order Intake", "48,200", "-4%"],
            ["Employees", "102,000", "+1,200"],
        ],
        "risks": [
            "Slowdown in North American heavy-duty truck market",
            "European emission regulation changes increasing R&D costs",
            "Supply chain disruptions for battery components",
        ],
    },
    {
        "name": "Ericsson",
        "document": "Q1 2025 Financial Report",
        "data": [
            ["Metric", "Value", "Change YoY"],
            ["Net Sales", "SEK 53.3B", "-2%"],
            ["Gross Income", "SEK 20.1B", "-4%"],
            ["Gross Margin", "37.7%", "-0.8pp"],
            ["EBIT", "SEK 3.8B", "-18%"],
            ["EBIT Margin", "7.1%", "-1.4pp"],
            ["Net Income", "SEK 2.4B", "-25%"],
            ["Free Cash Flow", "SEK -1.2B", ""],
            ["R&D Spending", "SEK 10.8B", "+3%"],
            ["5G Contracts Signed", "142", "+8"],
            ["Employees", "96,000", "-4,000"],
        ],
        "risks": [
            "Slower 5G rollout in key markets (India, Europe)",
            "Increased competition from Huawei and Nokia",
            "Margin pressure from enterprise networking segment",
        ],
    },
    {
        "name": "Atlas Copco",
        "document": "Q1 2025 Financial Report",
        "data": [
            ["Metric", "Value", "Change YoY"],
            ["Revenues", "SEK 41.2B", "+11%"],
            ["EBIT", "SEK 9.1B", "+15%"],
            ["EBIT Margin", "22.1%", "+0.7pp"],
            ["Net Profit", "SEK 7.0B", "+14%"],
            ["Operating Cash Flow", "SEK 6.8B", "+9%"],
            ["Free Cash Flow", "SEK 5.4B", "+11%"],
            ["Orders Received", "SEK 43.5B", "+7%"],
            ["Acquisitions (YTD)", "SEK 2.1B", ""],
            ["Employees", "49,000", "+2,100"],
        ],
        "risks": [
            "Slowing industrial automation demand in China",
            "Currency headwinds from strong SEK vs USD",
            "Integration risk from recent compressor acquisitions",
        ],
    },
    {
        "name": "Investor AB",
        "document": "Q1 2025 Portfolio Update",
        "data": [
            ["Metric", "Value", "Change YoY"],
            ["Net Asset Value (NAV)", "SEK 685B", "+5%"],
            ["NAV per Share", "SEK 226.40", "+6%"],
            ["Portfolio Value", "SEK 712B", "+4%"],
            ["Dividend Income (Q1)", "SEK 4.2B", "+3%"],
            ["Net Cash Position", "SEK 28.5B", ""],
            ["Core Holdings", "12", ""],
            ["New Investments (Q1)", "SEK 8.3B", ""],
            ["Divestments (Q1)", "SEK 3.1B", ""],
            ["Share Buybacks (Q1)", "SEK 2.0B", ""],
        ],
        "risks": [
            "Concentration risk in Swedish large-cap holdings",
            "Private equity valuation uncertainty in higher-rate environment",
            "Currency exposure via unhedged international holdings",
        ],
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

        # Add risk factors if present
        for risk in company.get("risks", []):
            rows.append([company["name"], company["document"], "Risk Factor", risk, ""])

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
