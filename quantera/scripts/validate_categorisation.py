#!/usr/bin/env python3
"""Categorisation Validation Script.

Compares AI-extracted categories and company names against a labelled dataset
to measure categorisation accuracy.

Usage:
    python scripts/validate_categorisation.py --labels path/to/labels.json
    python scripts/validate_categorisation.py --labels path/to/labels.json --input-dir path/to/files

Label file format (JSON):
[
    {
        "file": "techcorp_q1.pdf",
        "expected_company": "TechCorp AB",
        "expected_categories": ["financial report", "earnings"]
    },
    {
        "file": "retail_q2.xlsx",
        "expected_company": "Nordic Retail Group",
        "expected_categories": ["market analysis", "retail"]
    }
]

The script will:
1. Convert each labelled file to Markdown (if not already done)
2. Run the categoriser on each Markdown file
3. Compare extracted company/categories against expected values
4. Report accuracy metrics: company exact match, category precision/recall/F1
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import validate_file
from src.converter import convert_to_markdown
from src.categoriser import extract_metadata
from src.utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def compute_category_metrics(predicted: list[str], expected: list[str]) -> dict:
    """Compute precision, recall, and F1 for category sets."""
    pred_set = set(c.lower().strip() for c in predicted)
    exp_set = set(c.lower().strip() for c in expected)

    if not pred_set and not exp_set:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}

    tp = len(pred_set & exp_set)
    fp = len(pred_set - exp_set)
    fn = len(exp_set - pred_set)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {"precision": precision, "recall": recall, "f1": f1}


def normalise_company(name: str) -> str:
    """Normalise company name for comparison."""
    return name.lower().strip().replace(" ", "")


def run_validation(labels_path: str, input_dir: str | None = None) -> dict:
    """Run categorisation validation against a labelled dataset.

    Args:
        labels_path: Path to JSON label file
        input_dir: Optional input directory override

    Returns:
        Validation results dict
    """
    labels_file = Path(labels_path)
    if not labels_file.exists():
        print(f"Error: Labels file not found: {labels_path}")
        sys.exit(1)

    with open(labels_file, encoding="utf-8") as f:
        labels = json.load(f)

    if not labels:
        print("Error: Labels file is empty")
        sys.exit(1)

    print(f"Loaded {len(labels)} labelled entries from {labels_path}")
    print("=" * 60)

    results = []
    company_correct = 0
    category_metrics = {"precision": [], "recall": [], "f1": []}

    for i, label in enumerate(labels, 1):
        filename = label["file"]
        expected_company = label["expected_company"]
        expected_categories = label["expected_categories"]

        input_path = Path(input_dir or "data/input") / filename
        if not validate_file(input_path):
            md_path = Path("data/markdown") / (Path(filename).stem + ".md")
            if not md_path.exists():
                print(f"  [{i}/{len(labels)}] {filename}: SKIP (file not found)")
                continue
        else:
            try:
                md_path = convert_to_markdown(input_path)
            except Exception as e:
                print(f"  [{i}/{len(labels)}] {filename}: SKIP (conversion failed: {e})")
                continue

        try:
            content = md_path.read_text(encoding="utf-8")
            metadata = extract_metadata(content, md_path)
            actual_company = metadata.get("company", "")
            actual_categories = metadata.get("categories", [])
        except Exception as e:
            print(f"  [{i}/{len(labels)}] {filename}: ERROR ({e})")
            results.append({
                "file": filename,
                "status": "error",
                "error": str(e),
            })
            continue

        company_match = normalise_company(actual_company) == normalise_company(expected_company)
        if company_match:
            company_correct += 1

        cat_metrics = compute_category_metrics(actual_categories, expected_categories)
        category_metrics["precision"].append(cat_metrics["precision"])
        category_metrics["recall"].append(cat_metrics["recall"])
        category_metrics["f1"].append(cat_metrics["f1"])

        status = "OK" if company_match and cat_metrics["f1"] >= 0.5 else "PARTIAL" if company_match or cat_metrics["f1"] > 0 else "FAIL"

        print(f"  [{i}/{len(labels)}] {filename}: {status}")
        if not company_match:
            print(f"    Company: expected='{expected_company}', actual='{actual_company}'")
        if cat_metrics["f1"] < 1.0:
            print(f"    Categories: expected={expected_categories}, actual={actual_categories}")
            print(f"    Category F1: {cat_metrics['f1']:.2f}")

        results.append({
            "file": filename,
            "status": status,
            "company_match": company_match,
            "expected_company": expected_company,
            "actual_company": actual_company,
            "expected_categories": expected_categories,
            "actual_categories": actual_categories,
            "category_metrics": cat_metrics,
        })

    total = len(results)
    company_accuracy = company_correct / total if total > 0 else 0.0
    avg_precision = sum(category_metrics["precision"]) / len(category_metrics["precision"]) if category_metrics["precision"] else 0.0
    avg_recall = sum(category_metrics["recall"]) / len(category_metrics["recall"]) if category_metrics["recall"] else 0.0
    avg_f1 = sum(category_metrics["f1"]) / len(category_metrics["f1"]) if category_metrics["f1"] else 0.0

    print("\n" + "=" * 60)
    print("CATEGORISATION VALIDATION REPORT")
    print("=" * 60)
    print(f"  Total entries:            {total}")
    print(f"  Company exact match:      {company_accuracy:.0%} ({company_correct}/{total})")
    print(f"  Category precision:       {avg_precision:.2f}")
    print(f"  Category recall:          {avg_recall:.2f}")
    print(f"  Category F1:              {avg_f1:.2f}")

    failed = [r for r in results if r["status"] == "FAIL"]
    if failed:
        print(f"\n  Failed ({len(failed)}):")
        for r in failed:
            print(f"    - {r['file']}")

    report = {
        "total": total,
        "company_accuracy": company_accuracy,
        "category_precision": avg_precision,
        "category_recall": avg_recall,
        "category_f1": avg_f1,
        "results": results,
    }

    report_path = Path("data/validation_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n  Report saved to {report_path}")
    print("=" * 60)

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate categorisation accuracy against labelled data")
    parser.add_argument("--labels", required=True, help="Path to JSON labels file")
    parser.add_argument("--input-dir", default=None, help="Input directory override")
    args = parser.parse_args()

    run_validation(args.labels, args.input_dir)
