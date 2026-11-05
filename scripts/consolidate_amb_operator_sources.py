#!/usr/bin/env python3
"""Supplemental route-level source gap matrix; preserves provisional status."""
import csv
import json
import io
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/gtfs-source-consolidation"

def read(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def kmz_endpoint_candidates(url):
    """Inspect source KMZ and return geometry endpoints only, never validated stops.

    Multiple LineStrings or disjoint sections are deliberately left ambiguous.
    """
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "ColombiaTransit-GTFS-Source-Audit/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(12_000_001)
        if len(raw) > 12_000_000:
            return "source_too_large", "", "", 0
        if zipfile.is_zipfile(io.BytesIO(raw)):
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                names = [n for n in archive.namelist() if n.lower().endswith(".kml")]
                if not names:
                    return "no_kml_in_kmz", "", "", 0
                root = ET.fromstring(archive.read(names[0]))
        else:
            root = ET.fromstring(raw)
        lines = []
        for element in root.iter():
            if element.tag.split("}")[-1] != "LineString":
                continue
            for coords in element.iter():
                if coords.tag.split("}")[-1] != "coordinates" or not coords.text:
                    continue
                points = []
                for token in coords.text.split():
                    parts = token.split(",")
                    if len(parts) >= 2:
                        try:
                            lon, lat = float(parts[0]), float(parts[1])
                            if -180 <= lon <= 180 and -90 <= lat <= 90:
                                points.append((lat, lon))
                        except ValueError:
                            pass
                if len(points) >= 2:
                    lines.append(points)
        if not lines:
            return "no_linestring", "", "", 0
        if len(lines) != 1:
            return "multiple_linestrings_review_required", "", "", len(lines)
        start, end = lines[0][0], lines[0][-1]
        fmt = lambda p: f"{p[0]:.7f},{p[1]:.7f}"
        return "geometry_endpoints_only_not_stops", fmt(start), fmt(end), 1
    except Exception as exc:
        return "fetch_or_parse_failed:" + type(exc).__name__, "", "", 0

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
    anchor_rows = []
    endpoint_cache = {}
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
        anchor_status = "not_required_siu_candidate_exists" if sm else "not_checked"
        if not sm:
            url = k["source_kmz_url"].strip()
            if url not in endpoint_cache:
                endpoint_cache[url] = kmz_endpoint_candidates(url) if url else ("missing_url", "", "", 0)
            anchor_status, start, end, sections = endpoint_cache[url]
            if k.get("source_url_collision", "").lower() == "yes":
                anchor_status = "source_url_collision_review_required"
                start = end = ""
            anchor_rows.append({
                "operator": op, "amb_route_code": code, "kmz_variant": k["kmz_variant"],
                "kmz_url": url, "geometry_start_lat_lon": start,
                "geometry_end_lat_lon": end, "linestring_count": sections,
                "anchor_status": anchor_status,
                "terminal_stops_verified": "no",
                "note": "Geometry endpoints are candidates only; may be depot, loop closure, or arbitrary digitization start."
            })
        continuous_status = ("FIXED_STOPS_CONTINUOUS_ALLOWED" if sm
                             else "CONTINUOUS_ANCHORS_PENDING")
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
            "continuous_pickup_class": continuous_status,\n            "continuous_pickup_policy": "user_confirmed_for_applicable_urban_routes_scope_review_required",\n            "anchor_status": anchor_status,\n            "headway_status": "not_assessed_in_supplement",
            "source_geometry_validation": "not_revalidated_in_supplement",
            "gaps": ";".join(flags)
        })
    with (OUT / "amb_route_geometry_stops_dispatch_gaps.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    anchor_fields = ["operator", "amb_route_code", "kmz_variant", "kmz_url",
                     "geometry_start_lat_lon", "geometry_end_lat_lon", "linestring_count",
                     "anchor_status", "terminal_stops_verified", "note"]
    with (OUT / "continuous_pickup_anchor_candidates.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=anchor_fields)
        writer.writeheader()
        writer.writerows(anchor_rows)
    unresolved = [x for x in siu if not x["amb_base_candidate"] or "|" in x["amb_base_candidate"]]
    with (OUT / "unresolved_siu_crosswalks.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(siu[0]))
        writer.writeheader()
        writer.writerows(unresolved)
    summary = {
        "kmz_rows": len(kmz),
        "routes_needing_anchor_review": len(anchor_rows),
        "geometry_endpoint_candidates_found": sum(x["anchor_status"] == "geometry_endpoints_only_not_stops" for x in anchor_rows), "siu_itineraries": len(siu),
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
            "Geometry endpoints are NOT confirmed terminals or GTFS stops",
            "No inferred stops, headways or new GTFS route mappings"
        ]
    }
    (OUT / "geometry_stops_dispatch_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    main()
