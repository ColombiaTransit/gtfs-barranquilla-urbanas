#!/usr/bin/env python3
"""Audit AMB legal status CSV without inventing legal closure."""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

SOURCE = Path("sources/amb/legal_validity_ocr_review/gtfs_legal_status_2026-11-04.csv")
OUTPUT = Path("sources/amb/legal_validity_ocr_review/gtfs_legal_status_audit.json")
REQUIRED = ("agency", "route_codes", "decisions", "verified_legal_evidence",
            "unresolved_issue", "current_operation_verified", "gtfs_release_approved", "next_action")

def main():
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = set(REQUIRED) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Missing fields: {sorted(missing)}")
        rows = list(reader)
    errors = []
    for n, row in enumerate(rows, 2):
        for key in REQUIRED:
            if not row[key].strip():
                errors.append(f"line {n}: empty {key}")
        for key in ("current_operation_verified", "gtfs_release_approved"):
            if row[key] not in ("yes", "no"):
                errors.append(f"line {n}: invalid {key}")
        if row["gtfs_release_approved"] == "yes" and (
            row["current_operation_verified"] != "yes" or
            row["unresolved_issue"].strip().lower() not in ("none", "resolved")
        ):
            errors.append(f"line {n}: unsafe GTFS approval")
    counts = Counter(row["agency"] for row in rows)
    output = {"route_groups": len(rows), "agencies": dict(sorted(counts.items())),
              "open_legal_issues": sum(r["unresolved_issue"].strip().lower() not in ("none", "resolved") for r in rows),
              "current_operation_verified": sum(r["current_operation_verified"] == "yes" for r in rows),
              "gtfs_release_approved": sum(r["gtfs_release_approved"] == "yes" for r in rows),
              "errors": errors}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
