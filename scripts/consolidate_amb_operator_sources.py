#!/usr/bin/env python3
"""Supplemental route-level source gap matrix; preserves provisional status."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/gtfs-source-consolidation"

def read(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    kmz = read("sources/amb/kmz_stop_gaps/kmz_siu_route_stop_coverage.csv")
    siu = read("sources/siu/open_route_review/siu_amb_crosswalk_visual_decisions_2026-11-05.csv")
    dispatch = []
    for op, path in [
        ("COOCHOFAL", "sources/operators/coochofal/dispatch_windows.csv"),
        ("TRANSURBAR", "sources/operators/transurbar/dispatch_windows.csv"),
    ]:
        dispatch.extend([{"operator": op, **row} for row in read(path)])
    matches = defaultdict(list)
    for row in siu:
        code = row["amb_base_candidate"].strip()
        if code and "|" not in code:
            matches[(row["amb_operator"].strip(), code)].append(row)
    windows = defaultdict(list)
    for row in dispatch:
        if row["amb_route_candidate"].strip():
            windows[(row["operator"], row["amb_route_candidate"].strip())].append(row)
    output = []
    for k in kmz:
        op, code = k["company"].strip(), k["kmz_base_route_code"].strip()
        sm = matches[(op, code)]
        ws = windows[(op, code)]
        flags = []
        if not sm: flags.append("no_accepted_siu_itinerary")
        if k.get("route_stop_mapping_confirmed", "").lower() != "yes":
            flags.append("stop_mapping_not_confirmed")
        if not ws: flags.append("no_operator_dispatch_window_in_loaded_registers")
        if k.get("source_url_collision", "").lower() == "yes": flags.append("kmz_url_collision")
        if any(x["decision_status"].startswith(("accepted_provisional", "selected_")) for x in sm):
            flags.append("provisional_crosswalk")
        output.append({
            "operator": op, "amb_route_code": code,
            "kmz_route_label": k["kmz_route_label"], "kmz_variant": k["kmz_variant"],
            "amb_kmz_url": k["source_kmz_url"],
            "amb_geojson_path": k["source_geojson_path"],
            "siu_itineraries": ";".join(x["siu_name"] for x in sm),
            "siu_decisions": ";".join(x["decision_status"] for x in sm),
            "stop_mapping_confirmed": k.get("route_stop_mapping_confirmed", ""),
            "operator_dispatch_windows": ";".join(
                f"{w['day_group']}:{w['first_departure']}-{w['last_departure']}" for w in ws
            ),
            "headway_status": "not_assessed_in_supplement",
            "source_geometry_validation": "not_revalidated_in_supplement",
            "gaps": ";".join(flags)
        })
    with (OUT / "amb_route_geometry_stops_dispatch_gaps.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    unresolved = [x for x in siu if not x["amb_base_candidate"] or "|" in x["amb_base_candidate"]]
    with (OUT / "unresolved_siu_crosswalks.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(siu[0]))
        writer.writeheader()
        writer.writerows(unresolved)
    summary = {
        "kmz_rows": len(kmz), "siu_itineraries": len(siu),
        "siu_single_route_candidates": len(siu)-len(unresolved),
        "siu_unresolved": len(unresolved),
        "operator_dispatch_records_included": len(dispatch),
        "kmz_rows_with_siu_match": sum(bool(x["siu_itineraries"]) for x in output),
        "kmz_rows_with_dispatch_windows": sum(bool(x["operator_dispatch_windows"]) for x in output),
        "gap_counts": dict(Counter(g for x in output for g in x["gaps"].split(";") if g)),
        "scope_notes": [
            "Supplement to existing route_source_consolidation.csv, not a replacement",
            "COOLITORAL waypoint and dispatch artifact not yet joined",
            "LA CAROLINA original KML archive not yet verified in this pass",
            "Headways and legal resolutions remain in existing separate registers",
            "No inferred stops, headways or new GTFS route mappings"
        ]
    }
    (OUT / "geometry_stops_dispatch_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    main()
