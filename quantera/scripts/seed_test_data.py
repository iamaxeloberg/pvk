#!/usr/bin/env python3
"""Generate synthetic test documents for development and testing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


SAMPLE_COMPANIES = [
    {
        "name": "TechCorp AB",
        "document": "Q1 2025 Financial Report",
        "content": """# TechCorp AB - Q1 2025 Financial Report

## Revenue
- Total Revenue: SEK 145.2M (+12% YoY)
- Recurring Revenue: SEK 98.5M (+18% YoY)

## Margins
- Gross Margin: 62.3%
- EBITDA Margin: 24.1%
- Operating Margin: 18.7%

## Cash Flow
- Operating Cash Flow: SEK 32.1M
- Free Cash Flow: SEK 28.4M

## Key Metrics
- ARR: SEK 410M
- NRR: 115%
- Customer Count: 342
""",
    },
    {
        "name": "Nordic Retail Group",
        "document": "Annual Portfolio Review 2024",
        "content": """# Nordic Retail Group - Annual Portfolio Review 2024

## Company Overview
Nordic Retail Group operates 127 stores across Sweden, Norway, and Denmark.

## Financial Summary
- Revenue: SEK 2.1B (-3% YoY)
- Gross Margin: 34.2%
- EBITDA: SEK 185M
- Net Debt: SEK 420M

## Risks
- Increasing competition from e-commerce
- Rising labor costs in Sweden
- Currency exposure in Norway and Denmark

## Outlook
- Planned store closures: 8-12 locations
- Digital transformation investment: SEK 45M
""",
    },
    {
        "name": "GreenEnergy Solutions",
        "document": "Market Analysis 2025",
        "content": """# GreenEnergy Solutions - Market Analysis 2025

## Market Position
- Market share in Nordic wind energy: 14%
- Installed capacity: 890 MW
- Pipeline projects: 340 MW

## Financial Projections
- Expected Revenue 2025: SEK 680M
- Expected EBITDA Margin: 31-33%
- CapEx requirement: SEK 220M

## Competitive Landscape
- Main competitors: Vattenfall, Orsted, Statkraft
- Regulatory tailwinds from EU Green Deal
""",
    },
]


def generate_test_data():
    """Create synthetic Markdown files in the markdown directory."""
    md_dir = settings.markdown_dir_obj
    md_dir.mkdir(parents=True, exist_ok=True)

    for company in SAMPLE_COMPANIES:
        filename = f"{company['name'].lower().replace(' ', '_')}.md"
        filepath = md_dir / filename
        filepath.write_text(company["content"], encoding="utf-8")
        print(f"Created: {filepath}")

    print(f"\nGenerated {len(SAMPLE_COMPANIES)} test documents in {md_dir}")


if __name__ == "__main__":
    generate_test_data()
