#!/usr/bin/env python3
"""Consolidate existing GTFS route sources without inventing mappings or service."""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "build" / "gtfs-source-consolidation"

def load(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    routes = load("gtfs/routes.txt")
    headways = load("sources/amb/gtfs_staging/route_headway_candidates.csv")
    siu = load("sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv")
    shapes = load("sources/amb/KMZ_first_GH_fallback_validation/source_shape_source_by_pattern.csv")
    closure = load("sources/amb/research_closure_and_gtfs_handoff_2026-11-04.csv")
    by_headway = defaultdict(list)
    by_siu = defaultdict(list)
    by_shape = defaultdict(list)
    for row in headways:
        by_headway[row["gtfs_route_id"]].append(row)
    for row in siu:
        # Do not treat a suggested route code as a confirmed mapping.
        key = row.get("suggested_gtfs_route_id", "").strip()
        if key:
            by_siu[key].append(row)
        for token in row.get("same_company_gtfs_ids", "").split(";"):
            token = token.strip()
            if token and token != key:
                by_siu[token].append(row)
    for row in shapes:
        key = (row.get("company", "").strip().upper().replace(" ", "_"),
               row.get("official_route_label", "").strip().upper())
        by_shape[key].append(row)
    output = []
    for route in routes:
        rid = route["route_id"]
        company = route["agency_id"].removeprefix("AMB_")
        short = route["route_short_name"]
        hs = by_headway[rid]
        ss = by_siu[rid]
        sh = by_shape[(company, short)]
        valid_h = [x for x in hs if x.get("peak_headway_secs") and x.get("offpeak_headway_secs")]
        confirmed_siu = [x for x in ss if x.get("final_gtfs_route_mapping_confirmed", "").lower() == "yes"]
        kmz = [x for x in sh if x.get("genuine_2026_KMZ_used", "").lower() == "yes"]
        reasons = []
        if len(hs) != 1:
            reasons.append("headway_join_missing_or_duplicate")
        if len(valid_h) != 1:
            reasons.append("headway_values_missing_or_ambiguous")
        if not confirmed_siu:
            reasons.append("siu_route_mapping_not_confirmed")
        if not sh:
            reasons.append("shape_pattern_not_joined")
        if len(sh) > 1:
            reasons.append("shape_variants_require_direction_review")
        if not kmz and sh:
            reasons.append("shape_uses_fallback_or_non_2026_source")
        reasons.append("service_calendar_and_real_trip_times_not_confirmed")
        source = hs[0] if len(hs) == 1 else {}
        output.append({
            "gtfs_route_id": rid,
            "agency_id": route["agency_id"],
            "route_short_name": short,
            "headway_rows": len(hs),
            "headway_status": "candidate_with_values" if len(valid_h) == 1 and len(hs) == 1 else "missing_or_ambiguous",
            "peak_headway_secs": source.get("peak_headway_secs", "") if len(hs) == 1 else "",
            "offpeak_headway_secs": source.get("offpeak_headway_secs", "") if len(hs) == 1 else "",
            "headway_source": source.get("source_file", "") if len(hs) == 1 else "",
            "siu_candidate_count": len({x.get("siu_itinerary_uuid") for x in ss}),
            "siu_confirmed_count": len({x.get("siu_itinerary_uuid") for x in confirmed_siu}),
            "siu_candidate_uuids": ";".join(sorted({x.get("siu_itinerary_uuid", "") for x in ss if x.get("siu_itinerary_uuid")})),
            "shape_pattern_count": len(sh),
            "kmz_2026_pattern_count": len(kmz),
            "shape_pattern_ids": ";".join(sorted({x.get("trip_pattern_id", "") for x in sh if x.get("trip_pattern_id")})),
            "calendar_status": "model_only_not_verified",
            "gtfs_build_ready": "no",
            "reason": ";".join(reasons),
            "research_phase": "closed_gtfs_handoff",
        })
    fields = list(output[0]) if output else []
    write(args.out / "route_source_consolidation.csv", output, fields)
    summary = {
        "gtfs_route_rows": len(routes),
        "unique_gtfs_route_ids": len({x["route_id"] for x in routes}),
        "headway_rows": len(headways),
        "siu_crosswalk_rows": len(siu),
        "shape_pattern_rows": len(shapes),
        "research_closure_rows": len(closure),
        "route_headway_candidates_with_values": sum(x["headway_status"] == "candidate_with_values" for x in output),
        "routes_with_siu_candidates": sum(int(x["siu_candidate_count"]) > 0 for x in output),
        "routes_with_confirmed_siu": sum(int(x["siu_confirmed_count"]) > 0 for x in output),
        "routes_with_shape_pattern_join": sum(int(x["shape_pattern_count"]) > 0 for x in output),
        "routes_with_2026_kmz_pattern": sum(int(x["kmz_2026_pattern_count"]) > 0 for x in output),
        "gtfs_release_ready": False,
        "notes": "Candidate joins are not legal route/variant confirmation; historical model windows are not current service."
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
