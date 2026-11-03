#!/usr/bin/env python3
"""Reuse existing canonical SIU stop IDs on potential new AMB KMZ route patterns.

The physical stops are NOT duplicated per route. Route membership remains unverified.
Existing SIU-route incidence is recorded separately from proximity-based candidate routes.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/amb-shared-stop-reuse"

def read(path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write(path,items,headers):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=headers,extrasaction="ignore")
        w.writeheader()
        w.writerows(items)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    physical=read(ROOT/"sources/siu/gtfs_staging/candidate_stops.csv")
    byid={x["stop_id"]:x for x in physical}
    if len(byid)!=len(physical):
        raise ValueError("Duplicate physical stop_id")
    occurrences=read(ROOT/"sources/siu/gtfs_staging/siu_stop_occurrence_crosswalk.csv")
    known=defaultdict(set)
    for row in occurrences:
        sid=row["candidate_stop_id"]
        if sid not in byid:
            raise ValueError("SIU itinerary references nonexistent physical stop")
        known[sid].add(row["siu_itinerary_uuid"])
    candidates=read(ROOT/"sources/amb/kmz_stop_gaps/nearby_stop_candidates_NOT_CONFIRMED.csv")
    coverage=read(ROOT/"sources/amb/kmz_stop_gaps/kmz_siu_route_stop_coverage.csv")
    missing={(row["company"],row["kmz_route_label"]):row for row in coverage
             if row["siu_coverage_status"]=="no_siu_route_stop_candidate"}
    pairs={}
    omitted_osm=0
    for row in candidates:
        if not row["source"].startswith("SIU"):
            omitted_osm+=1
            continue
        sid=row["source_stop_id"]
        key=(row["company"],row["kmz_route_label"])
        if key not in missing:raise ValueError("KMZ candidate not in missing list")
        if sid not in byid:raise ValueError("SIU stop not in physical stop catalog: "+sid)
        n=(key[0],key[1],sid)
        previous=pairs.get(n)
        if previous is None or float(previous["distance_m"])>float(row["distance_m"]):
            pairs[n]=row
    incidence=defaultdict(list)
    cross=[]
    for (company,label,sid),row in sorted(pairs.items()):
        meta=missing[company,label]
        info=byid[sid]
        cross.append({
            "existing_physical_SIU_stop_id":sid,
            "existing_physical_SIU_stop_name":info["stop_name"],
            "existing_stop_lat":info["stop_lat"],
            "existing_stop_lon":info["stop_lon"],
            "already_used_by_n_SIU_itineraries":len(known[sid]),
            "candidate_additional_KMZ_company":company,
            "candidate_additional_KMZ_route_label":label,
            "candidate_base_route_id":meta["kmz_base_route_code"],
            "candidate_variant":meta["kmz_variant"],
            "source_KMZ_url_conflict":meta["source_url_collision"],
            "distance_to_route_m":row["distance_m"],
            "projection_along_line_m_not_stop_order":row["position_along_line_m_not_stop_sequence"],
            "nearest_KMZ_linestring":row["source_line_index"],
            "reuse_existing_stop_id":"yes",
            "new_physical_stop_created":"no",
            "route_service_confirmed":"no",
            "boarding_side_direction_checked":"no",
            "GTFS_stop_times_eligible":"no"
        })
        incidence[sid].append((company,label,float(row["distance_m"])))
    shared=[]
    for sid,uses in sorted(incidence.items()):
        info=byid[sid]
        shared.append({
            "physical_SIU_stop_id":sid,
            "physical_stop_name":info["stop_name"],
            "stop_lat":info["stop_lat"],
            "stop_lon":info["stop_lon"],
            "existing_SIU_itineraries_using_stop":len(known[sid]),
            "additional_KMZ_route_variant_candidates":len(uses),
            "candidate_KMZ_route_labels":";".join(sorted(f"{a}/{b}" for a,b,d in uses)),
            "smallest_distance_to_any_new_route_m":round(min(x[2] for x in uses),1),
            "stop_id_unique_across_routes":"yes",
            "candidate_route_service_confirmed":"no"
        })
    sobusa=[row for row in cross if row["candidate_additional_KMZ_company"]=="SOBUSA"]
    write(OUT/"shared_physical_SIU_stop_index.csv",shared,list(shared[0]))
    write(OUT/"missing_route_to_existing_stop_id_candidates.csv",cross,list(cross[0]))
    write(OUT/"sobusa_route_to_existing_stop_id_candidates.csv",sobusa,list(cross[0]))
    summary={
        "physical_SIU_stop_catalog":len(physical),
        "SIU_source_stop_occurrences":len(occurrences),
        "physical_SIU_stops_with_nearby_missing_KMZ_route":len(shared),
        "SIU_stop_ID_route_candidate_references":len(cross),
        "SOBUSA_stop_ID_route_candidate_references":len(sobusa),
        "unique_physical_SIU_stop_ids_near_SOBUSA":len({x["existing_physical_SIU_stop_id"] for x in sobusa}),
        "source_OSM_proximity_entries_skipped_no_new_physical_ID":omitted_osm,
        "new_physical_stops_created":0,
        "automatic_new_route_stop_service_approved":0
    }
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report=[
      "# Eén fysiek SIU stop_id voor meerdere route- en trip-kandidaten",
      "",
      "Fysieke SIU-stopcatalogus wordt éénmalig gebruikt. Alle verbindingen met de "
      "60 routevariant-KMZ's gebruiken dezelfde oorspronkelijke stop_id. Er wordt "
      "GEEN aparte halte per route aangemaakt. OSM-punten zijn hier expres niet aangemaakt als fysieke haltes.",
      "",
      "## Tellingen",
      ""
    ]
    for k,v in summary.items():report.append(f"- {k}: **{v}**")
    report+=["",
      "**Belangrijk:** dit koppelt bestaande locaties geografisch aan kandidaat-routes. "
      "SIU heeft niet vastgelegd dat de kandidaat-route hier stopt. Controleer de "
      "juiste straatkant, haltebediening, rijrichting en geordende haltepassages "
      "vóór opname in definitieve GTFS stop_times.txt.",
      "",
      "Bestanden: shared_physical_SIU_stop_index.csv, "
      "missing_route_to_existing_stop_id_candidates.csv, "
      "sobusa_route_to_existing_stop_id_candidates.csv.",
      ""]
    (OUT/"summary.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
