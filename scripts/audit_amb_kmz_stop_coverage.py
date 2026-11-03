#!/usr/bin/env python3
"""Audit official AMB KMZ routes against SIU itinerary evidence and identify nearby stop candidates.

Research-only: geometric proximity is NOT a stop-service assertion or an ordered GTFS stop list.
Reads the already versioned SIU, KMZ and OSM inputs. Does not make network requests.
"""
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[1]
KMZ = ROOT / "sources/amb/kmz"
SIU = ROOT / "sources/siu"
OSM = ROOT / "sources/osm"
OUT = ROOT / "build/amb-kmz-stop-gaps"
MAX_METERS = 50

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def norm(x):
    x = unicodedata.normalize("NFKD", (x or "").upper())
    return re.sub("[^A-Z0-9]", "", "".join(a for a in x if not unicodedata.combining(a)))

def company_key(x):
    k = norm(x)
    return "MONTERREY" if k in ("TRANSPORTESMONTERREY", "MONTERREY") else k

def company_matches(kmz_company, names):
    return company_key(kmz_company) in {company_key(name) for name in names.split(";")}

def main():
    manifest = read_csv(KMZ / "manifest.csv")
    siu = read_csv(SIU / "gtfs_staging/siu_amb_route_crosswalk_review.csv")
    prov = read_csv(SIU / "open_route_review/provisional_base_route_code_candidates.csv")
    prov_ids = {x["siu_itinerary_uuid"] for x in prov}
    stop_catalog = read_csv(SIU / "gtfs_staging/candidate_stops.csv")
    osm_candidates = read_csv(OSM / "analysis/possible_boarding_platforms.csv")

    coverage = []
    for m in manifest:
        matches = [s for s in siu
                   if norm(s["candidate_amb_route_code"]) == norm(m["base_route_id_candidate"])
                   and company_matches(m["company"], s["siu_companies"])]
        extra = []
        # The KMZ site labels C5-4135, but 358-2024 and SIU reference C5-4136.
        if m["company"] == "COOTRAB" and m["base_route_id_candidate"] == "C5-4135":
            extra = [s for s in siu if s["siu_name"] == "LAS PALMAS"
                     and company_matches(m["company"], s["siu_companies"])]
        # PT4/PT5 public SIU names conflict with the latest legal terminal descriptions.
        if m["company"] == "COOLITORAL" and m["base_route_id_candidate"] == "PT5-4105":
            extra = [s for s in siu if s["siu_name"] in ("VIA 40 CIRCUNVALAR", "CIRCUNVALAR VIA 40")
                     and company_matches(m["company"], s["siu_companies"])]
        for s in extra:
            if s not in matches:
                matches.append(s)

        strong = [s for s in matches if s["route_match_status"] == "high_confidence_provisional"]
        provisional = [s for s in matches if s["siu_itinerary_uuid"] in prov_ids]
        specific_issue = ("route_code_conflict_C5_4135_vs_C5_4136"
                          if m["company"] == "COOTRAB" and m["base_route_id_candidate"] == "C5-4135" else
                          "PT4_PT5_unresolved_SIU_route_name_vs_terminal"
                          if m["company"] == "COOLITORAL" and m["base_route_id_candidate"] in ("PT4-4104", "PT5-4105") else "")
        # Known code/route conflict cannot be treated as final SIU matching.
        if specific_issue.startswith("PT4_"):
            category = "siu_link_ambiguous"
        elif strong:
            category = "siu_staged_strong_candidate"
        elif provisional:
            category = "siu_staged_provisional_candidate"
        elif matches:
            category = "siu_link_ambiguous"
        else:
            category = "no_siu_route_stop_candidate"

        notes = [specific_issue] if specific_issue else []
        if m.get("source_url_collision") == "yes":
            notes.append("official_KMZ_URL_reused_for_different_route_label")
        if category == "siu_link_ambiguous":
            notes.append("do_not_duplicate_SIU_stops_to_AB_patterns")
        coverage.append({
            "company":m["company"], "kmz_route_label":m["route_label"],
            "kmz_base_route_code":m["base_route_id_candidate"], "kmz_variant":m["variant"],
            "siu_coverage_status":category,
            "siu_itinerary_names":";".join(dict.fromkeys(x["siu_name"] for x in matches)),
            "siu_itinerary_uuids":";".join(dict.fromkeys(x["siu_itinerary_uuid"] for x in matches)),
            "source_url_collision":m.get("source_url_collision",""),
            "source_kmz_url":m["kmz_url"], "source_geojson_path":m["geojson_path"],
            "notes":";".join(notes), "route_stop_mapping_confirmed":"no",
            "needs_new_candidate_stop_search":"yes" if category == "no_siu_route_stop_candidate" else "no",
        })

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "kmz_siu_route_stop_coverage.csv", coverage, list(coverage[0]))
    counts = Counter(x["siu_coverage_status"] for x in coverage)

    # SIU candidate stops are real recorded locations, NOT evidence that another route serves them.
    # OSM source filters out explicit Transmetro/regional objects; remaining objects are not TPC-confirmed.
    stops = []
    for row in stop_catalog:
        try:
            stops.append({
                "source":"SIU_other_itinerary_nearby_unverified",
                "id":row["stop_id"], "name":row["stop_name"],
                "lat":float(row["stop_lat"]), "lon":float(row["stop_lon"])
            })
        except (KeyError, ValueError):
            continue
    for row in osm_candidates:
        try:
            stops.append({
                "source":"OSM_unclassified_boarding_candidate_unverified",
                "id":str(row["osm_type"])+"/"+str(row["osm_id"]),
                "name":row["name"], "lat":float(row["lat"]), "lon":float(row["lon"])
            })
        except (KeyError, ValueError):
            continue
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)
    point_geoms = [Point(*transformer.transform(s["lon"],s["lat"])) for s in stops]
    tree = STRtree(point_geoms)
    candidates = []
    per_route = []
    for c in coverage:
        if c["needs_new_candidate_stop_search"] != "yes":
            continue
        src = KMZ / c["source_geojson_path"]
        if not src.is_file():
            per_route.append({**c,"siu_near_30m":0, "osm_near_30m":0,
                              "nearby_points_50m":0, "matching_status":"missing_KMZ_file"})
            continue
        features = json.loads(src.read_text(encoding="utf-8")).get("features",[])
        best = {}
        for segment_index, feature in enumerate(features,1):
            geom = feature.get("geometry") or {}
            if geom.get("type") != "LineString":
                continue
            coords = geom.get("coordinates") or []
            if len(coords) < 2:
                continue
            line = LineString([transformer.transform(p[0],p[1]) for p in coords])
            if line.is_empty or line.length < 1:
                continue
            for raw_idx in tree.query(line.buffer(MAX_METERS)):
                idx = int(raw_idx)
                p = point_geoms[idx]
                distance = p.distance(line)
                if distance > MAX_METERS:
                    continue
                prev = best.get(idx)
                if prev is None or distance < prev["distance_m"]:
                    best[idx] = {
                        "company":c["company"], "kmz_route_label":c["kmz_route_label"],
                        "kmz_base_route_code":c["kmz_base_route_code"],
                        "kmz_variant":c["kmz_variant"],"source":stops[idx]["source"],
                        "source_stop_id":stops[idx]["id"],"source_stop_name":stops[idx]["name"],
                        "stop_lat":stops[idx]["lat"],"stop_lon":stops[idx]["lon"],
                        "distance_m":round(distance,2),
                        "source_line_index":segment_index,
                        "position_along_line_m_not_stop_sequence":round(line.project(p),1),
                        "source_url_collision":c["source_url_collision"],
                        "tpc_service_verified":"no",
                        "legal_route_variant_verified":"no",
                        "stop_sequence_verified":"no",
                    }
        ordered = sorted(best.values(),key=lambda x:(x["source_line_index"],
                       x["position_along_line_m_not_stop_sequence"],x["distance_m"]))
        candidates.extend(ordered)
        siu30 = sum(x["distance_m"] <=30 and x["source"].startswith("SIU") for x in ordered)
        osm30 = sum(x["distance_m"] <=30 and x["source"].startswith("OSM") for x in ordered)
        per_route.append({**c,"siu_near_30m":siu30,"osm_near_30m":osm30,
                         "nearby_points_50m":len(ordered),
                         "matching_status":"proximity_research_only_not_route_service_or_order"})
    if candidates:
        write_csv(OUT/"nearby_stop_candidates_NOT_CONFIRMED.csv",candidates,list(candidates[0]))
    if per_route:
        write_csv(OUT/"uncovered_route_stop_search_summary.csv",per_route,list(per_route[0]))

    summary = {
        "kmz_route_variant_records":len(coverage),
        "siu_itineraries_regular":len(siu),
        "source_siu_candidate_stop_locations":len(stop_catalog),
        "source_osm_unclassified_boarding_candidates":len(osm_candidates),
        "coverage_counts":dict(counts),
        "uncovered_route_variant_records":len(per_route),
        "uncovered_variants_with_osm_candidate_30m":sum(int(x["osm_near_30m"])>0 for x in per_route),
        "uncovered_variants_with_siu_candidate_30m":sum(int(x["siu_near_30m"])>0 for x in per_route),
        "nearby_50m_route_stop_candidates":len(candidates),
        "legal_mapping_final_confirmed":0,
        "tpc_route_stops_confirmed_from_geographic_proximity":0,
        "no_stop_times_or_gtfs_shapes_generated":True,
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    grouped=defaultdict(list)
    for row in coverage:
        grouped[row["company"]].append(row)
    lines=["# AMB KMZ → SIU-haltedekking en geografische onderzoekskandidaten","",
           "Bronnen: openbare AMB KMZ-routeviewer (93 vermelde bestanden), "
           "SIU-itineraries (33 reguliere), OSM Overpass (34 niet-geclassificeerde instapplaatskandidaten).","",
           "## Status",""]
    for k,v in counts.items():
        lines.append(f"- {k}: **{v}** KMZ-vermeldingen")
    lines += ["", "**Geografische nabijheid geeft GEEN bewezen haltebediening of stop_sequence.**",
              "SIU-basisroutekoppelingen zijn nog niet juridisch definitief geverifieerd.",
              "De SIU-bron is niet het complete AMB-netwerk; licentie/actuele vergunningstatus apart toetsen.",
              "De KMZ-site kent 4 dubbele verwijzingen voor verschillende routelabels.","",
              "## Welke KMZ-routevermeldingen missen SIU?","",
              "| Bedrijf | Geen SIU-routekandidaat | SIU-koppeling onbeslist |","|---|---|---|"]
    for company, items in grouped.items():
        missing=", ".join(x["kmz_route_label"] for x in items if x["siu_coverage_status"]=="no_siu_route_stop_candidate")
        amb=", ".join(x["kmz_route_label"] for x in items if x["siu_coverage_status"]=="siu_link_ambiguous")
        lines.append(f"| {company} | {missing or '—'} | {amb or '—'} |")
    lines += ["","## Reconstructie-onderzoek","",
              f"- {len(per_route)} routevarianten zonder SIU-kandidaat op maximaal 50m van bestaande SIU-halteplaatsen en OSM-punten getest.",
              f"- {summary['uncovered_variants_with_siu_candidate_30m']} van die varianten hebben minstens één SIU-punt binnen 30m (geen route-toewijzing).",
              f"- {summary['uncovered_variants_with_osm_candidate_30m']} varianten hebben minstens één OSM-kandidaat binnen 30m (geen bewezen TPC-halte).",
              "- Posities langs een KML LineString zijn alleen geometrisch gesorteerd; volledige wettelijke rijrichting en haltevolgorde onbekend.",
              "- Prioriteit: SOBUSA B18/C12/C16; overige bedrijven zonder SIU; varianten met KMZ-linkconflicten apart.",
              "- Outputs: kmz_siu_route_stop_coverage.csv, uncovered_route_stop_search_summary.csv, nearby_stop_candidates_NOT_CONFIRMED.csv.",
              "- Geen wijzigingen aan gtfs/trips.txt, gtfs/stop_times.txt of gtfs/shapes.txt.", ""]
    (OUT/"summary.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
