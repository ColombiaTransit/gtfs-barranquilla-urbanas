#!/usr/bin/env python3
"""Evaluate time-limited AMB route pilots for a requested GTFS service date.

A missing extension means the pilot expires, never that its underlying route vanishes.
End dates tagged provisional are not legally verified.
"""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path

DEFAULT_INPUT = Path("sources/amb/legal_validity_ocr_review/amb_pilots.csv")

def evaluate(row, date):
    start = dt.date.fromisoformat(row["pilot_start"])
    end = dt.date.fromisoformat(row["pilot_end_exclusive"])
    if end <= start:
        raise ValueError(f"Invalid pilot dates for {row['resolution']}")
    extension = row["extension_resolution"].strip()
    if date < start:
        status = "scheduled"
    elif date >= end:
        status = "extension_requires_article_review" if extension else "ended_no_extension_found"
    else:
        status = "active_under_recorded_period"
    return {
        "agency": row["agency"],
        "route_codes": row["route_codes"],
        "resolution": row["resolution"],
        "service_date": date.isoformat(),
        "pilot_status": status,
        "end_date_confidence": row["end_date_confidence"],
        "pilot_end_exclusive": row["pilot_end_exclusive"],
        "extension_resolution": extension or None,
        "base_resolution_to_reassess": row["base_resolution"],
        "legal_finalized": row["end_date_confidence"] == "verified" and (
            status != "extension_requires_article_review"),
        "route_cancelled": False,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=dt.date.fromisoformat, default=dt.date.today())
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8-sig", newline="") as f:
        records = list(csv.DictReader(f))
    result = {"service_date": args.date.isoformat(),
              "pilots": [evaluate(row, args.date) for row in records]}
    content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    print(content, end="")

if __name__ == "__main__":
    main()
