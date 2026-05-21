#!/usr/bin/env python3
"""Demo preparation script – run this before the live demo to reset everything.

Usage:
    python scripts/demo_prep.py

What it does:
    1. Removes old database and markdown files
    2. Removes old input files
    3. Generates fresh synthetic demo files (Volvo, Ericsson, Atlas Copco, Investor AB)
    4. Converts CSV -> Markdown
    5. Seeds the SQLite database with correct metadata
    6. Verifies everything is ready
"""

import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


def clean():
    """Remove generated files and old database."""
    print("Cleaning old demo data...")
    db = Path(settings.db_path)
    if db.exists():
        db.unlink()
        print(f"  Removed {db}")

    md_dir = settings.markdown_dir_obj
    for f in md_dir.glob("*.md"):
        f.unlink()
        print(f"  Removed {f}")

    input_dir = settings.input_dir_obj
    for f in input_dir.glob("*.csv"):
        f.unlink()
        print(f"  Removed {f}")
    for f in input_dir.glob("*.pdf"):
        f.unlink()
        print(f"  Removed {f}")
    for f in input_dir.glob("*.xlsx"):
        f.unlink()
        print(f"  Removed {f}")


def seed_files():
    """Generate fresh synthetic test files."""
    print("\nGenerating fresh demo files...")
    from scripts.seed_test_data import generate_test_data
    generate_test_data()


def seed_db():
    """Pre-populate database with known metadata."""
    print("\nSeeding database with demo metadata...")
    from scripts.seed_database import seed_demo_database
    seed_demo_database()


def verify():
    """Check that everything is in place."""
    print("\nVerifying demo setup...")
    ok = True

    input_files = list(settings.input_dir_obj.glob("*.csv"))
    if len(input_files) != 4:
        print(f"  WARNING: Expected 4 CSV files, found {len(input_files)}")
        ok = False
    else:
        print(f"  OK: {len(input_files)} input files found")

    md_files = list(settings.markdown_dir_obj.glob("*.md"))
    if len(md_files) != 4:
        print(f"  WARNING: Expected 4 Markdown files, found {len(md_files)}")
        ok = False
    else:
        print(f"  OK: {len(md_files)} Markdown files found")

    from src.indexer import init_db, get_document_count, close_db
    conn = init_db()
    count = get_document_count(conn)
    close_db(conn)
    if count != 4:
        print(f"  WARNING: Expected 4 documents in DB, found {count}")
        ok = False
    else:
        print(f"  OK: {count} documents indexed in SQLite")

    return ok


def main():
    print("=" * 50)
    print("DEMO PREPARATION")
    print("=" * 50)

    clean()
    # Note: seed_files runs the full pipeline including ingestion,
    # but since the LLM may not be available, we skip it and do manual steps.
    # Actually, seed_test_data.py also calls run_pipeline(). Let's just generate files manually.
    
    # Better: just use seed_test_data to generate CSVs, then manually convert and seed DB
    import csv
    from scripts.seed_test_data import SAMPLE_COMPANIES
    
    input_dir = settings.input_dir_obj
    input_dir.mkdir(parents=True, exist_ok=True)
    
    for company in SAMPLE_COMPANIES:
        filename = f"{company['name'].lower().replace(' ', '_')}_report.csv"
        filepath = input_dir / filename
        rows = [["Company", "Document", "Metric", "Value", "Notes"]]
        for row in company["data"]:
            rows.append([company["name"], company["document"]] + row + [""] * (5 - len(row) - 2))
        for risk in company.get("risks", []):
            rows.append([company["name"], company["document"], "Risk Factor", risk, ""])
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print(f"  Created: {filepath}")
    
    # Convert to markdown manually
    from src.converter import convert_to_markdown
    for csv_file in input_dir.glob("*.csv"):
        md_path = settings.markdown_dir_obj / (csv_file.stem + ".md")
        if not md_path.exists():
            convert_to_markdown(csv_file)
            print(f"  Converted: {csv_file.name} -> {md_path.name}")
    
    seed_db()
    
    if verify():
        print("\n" + "=" * 50)
        print("DEMO READY!")
        print("=" * 50)
        print("\nNext steps:")
        print("  1. Start FreeLLMAPI on localhost:3001")
        print("  2. Run: make list")
        print("  3. Run: make query Q='...'")
    else:
        print("\nWARNING: Demo setup verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
