#!/usr/bin/env python3
"""Validate research-stage agency.txt and routes.txt without publishing a feed."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

def read_csv(name, required):
    path = ROOT / "gtfs" / name
    if not path.is_file():
        errors.append(f"Missing gtfs/{name}")
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        for col in required:
            if col not in cols:
                errors.append(f"{name}: missing column {col}")
        rows = list(reader)
    for n, row in enumerate(rows, 2):
        for col in required:
            if not (row.get(col) or "").strip():
                errors.append(f"{name}:{n}: empty {col}")
    print(f"{name}: {len(rows)} records")
    return rows

agencies = read_csv("agency.txt", ["agency_id", "agency_name", "agency_url", "agency_timezone"])
routes = read_csv("routes.txt", ["route_id", "agency_id", "route_type"])

def unique(rows, field, filename):
    seen = set()
    for n, row in enumerate(rows, 2):
        val = (row.get(field) or "").strip()
        if val in seen:
            errors.append(f"{filename}:{n}: duplicate {field}={val}")
        seen.add(val)
    return seen

agency_ids = unique(agencies, "agency_id", "agency.txt")
unique(routes, "route_id", "routes.txt")
for n, row in enumerate(agencies, 2):
    if row.get("agency_timezone") != "America/Bogota":
        errors.append(f"agency.txt:{n}: unexpected timezone")
for n, row in enumerate(routes, 2):
    if row.get("agency_id") not in agency_ids:
        errors.append(f"routes.txt:{n}: unknown agency_id {row.get('agency_id')}")
    if row.get("route_type") != "3":
        errors.append(f"routes.txt:{n}: expected bus route_type=3")

if errors:
    print("\nVALIDATION FAILED:")
    for error in errors:
        print(" -", error)
    sys.exit(1)
print("\nResearch-stage agency/routes checks passed. This is NOT full GTFS validation.")
