#!/usr/bin/env python3
"""End-to-end pipeline runner."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import run_pipeline, query


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Quantera AI financial document pipeline")
    parser.add_argument("command", choices=["ingest", "query"], help="Command to run")
    parser.add_argument("--question", "-q", type=str, help="Query string (for 'query' command)")
    args = parser.parse_args()

    if args.command == "ingest":
        run_pipeline()
    elif args.command == "query":
        if not args.question:
            print("Error: --question is required for query command")
            sys.exit(1)
        query(args.question)


if __name__ == "__main__":
    main()
