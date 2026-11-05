#!/usr/bin/env python3
"""Geographic screening of AMB continuous-boarding anchor candidates.

Geometry endpoints are never promoted to verified GTFS stops.
"""
import csv
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/gtfs-source-consolidation"
# Broad metropolitan screening envelope; NOT an administrative boundary.
LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = 10.55, 11.25, -75.20, -74.55

def distance_km(a, b):
    p1, l1 = map(math.radians, a)
    p2, l2 = map(math.radians, b)
    dlat, dlon = p2 - p1, l2 - l1
    x = math.sin(dlat / 2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlon / 2)**2
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(x)))

def inside(point):
    return LAT_MIN <= point[0] <= LAT_MAX and LON_MIN <= point[1] <= LON_MAX

def main():
    with (OUT / "continuous_pickup_anchor_candidates.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    reviewed = []
    for row in rows:
        status = row["anchor_status"]
        reasons = []
        separation = ""
        if status != "geometry_endpoints_only_not_stops" or row["linestring_count"] != "1":
            reasons.append("source_or_geometry_review_required")
        else:
            try:
                start = tuple(map(float, row["geometry_start_lat_lon"].split(",")))
                end = tuple(map(float, row["geometry_end_lat_lon"].split(",")))
                separation = round(distance_km(start, end), 3)
                if not inside(start) or not inside(end):
                    reasons.append("outside_broad_metro_envelope")
                if separation < 0.15:
                    reasons.append("near_coincident_endpoints_loop_or_digitization")
                elif separation > 65:
                    reasons.append("unusually_distant_endpoints")
            except (ValueError, TypeError):
                reasons.append("invalid_endpoint_coordinates")
        if reasons:
            priority = "MANUAL_GEOMETRY_REVIEW"
        else:
            priority = "PRIORITY_GEOGRAPHIC_TERMINAL_REVIEW"
        reviewed.append({
            **row,
            "endpoint_separation_km": separation,
            "metro_envelope_check": "pass" if not reasons else "review",
            "review_priority": priority,
            "review_reasons": ";".join(reasons),
            "terminal_verification": "PENDING_INDEPENDENT_EVIDENCE",
            "gtfs_anchor_approved": "no",
        })
    path = OUT / "continuous_pickup_geographic_review.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(reviewed[0]))
        writer.writeheader()
        writer.writerows(sorted(reviewed, key=lambda x: (x["review_priority"] != "PRIORITY_GEOGRAPHIC_TERMINAL_REVIEW", x["operator"], x["amb_route_code"], x["kmz_variant"])))
    counts = dict(Counter(row["review_priority"] for row in reviewed))
    summary = {
        "screened": len(reviewed), "priorities": counts,
        "method": "single-LineString and non-colliding KMZ; broad envelope and endpoint separation screening",
        "caveat": "This is geographic plausibility screening only; route termini and boarding safety are not confirmed.",
        "next_step": "Cross-check candidate points against operator terminals, route names, OSM and independent imagery; verify direction and turnarounds before creating stops.txt."
    }
    (OUT / "continuous_pickup_geographic_review_summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
