#!/usr/bin/env python3
"""Research map of only the remaining real MobilityData 67+4 geometry notices.

Reads canonical physical SIU stops, original v3 KMZ stop sequence positions,
and actual post-repair validator notice CSV. No new GraphHopper/OSM queries.
No stop moves or reordering. Files are strictly QA, not GTFS publication.
"""
from __future__ import annotations
import csv
import json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"sources/amb/GTFS_shape_validator_recheck"
STOPS=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
ORDERS=ROOT/"sources/amb/provisional_trip_stop_order_v3_clean/candidate_trip_stop_sequences_v3_CLEAN_NO_TIMES_NOT_GTFS.csv"
PATTERNS=ROOT/"sources/amb/missing_siu_trip_stop_patterns/trip_patterns_MISSING_SIU_NO_TIMES.csv"
OUT=ROOT/"build/amb-GTFS-remaining-geography-review"

def read(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def write(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    stop={x["stop_id"]:x for x in read(STOPS)}
    source=read(ORDERS)
    manifests={x["trip_pattern_id"]:x for x in read(PATTERNS)}
    issue=read(SRC/"MobilityData_remaining_stop_shape_warning_details.csv")
    ordering=read(SRC/"MobilityData_remaining_stop_order_warning_details.csv")
    if len(issue)!=67 or len(ordering)!=4:
        raise ValueError("Expected 67 stop-shape and 4 order notices from validated repair; source changed")
    source_by_stop=defaultdict(list)
    source_by_seq={}
    for r in source:
        key=(r["trip_pattern_id"],r["stop_id"])
        source_by_stop[key].append(r)
        source_by_seq[(r["trip_pattern_id"],r["stop_sequence"])]=r
    cases=[]
    points=[]
    route_summary=defaultdict(Counter)
    for r in issue:
        uid=r["trip_pattern_id"]
        sid=r["stop_id"]
        s=stop[sid]
        matches=source_by_stop.get((uid,sid),[])
        if not matches:raise ValueError("Missing original SIU candidate stop in v3: "+uid+" / "+sid)
        distance=float(r["distance_from_GH_shape_m"])
        source_distance=min(float(x["distance_from_route_m"]) for x in matches)
        manifest=manifests[uid]
        near=source_distance<=35.
        priority="P1_big_GH_route_discrepancy" if distance>=250 else "P2_stop_vs_GH_road_review"
        reason=(
            "near_source_KMZ_but_far_from_GH_bus_road" if near else
            "stop_offset_from_KMZ_and_GH_both_need_review"
        )
        if manifest["source_geometry"].startswith("AMB_ARCGIS"):
            reason+=";historical_ArcGIS_fallback"
        row={
            "trip_pattern_id":uid,
            "company":manifest["company"],
            "route_label":manifest["official_route_label"],
            "physical_SIU_stop_id":sid,
            "physical_stop_name":s["stop_name"],
            "longitude":s["stop_lon"],"latitude":s["stop_lat"],
            "validator_distance_to_final_GH_shape_m":distance,
            "nearest_source_KMZ_distance_m":round(source_distance,1),
            "original_shape_chainage_candidates_m":";".join(
                x["shape_dist_traveled_candidate_m"] for x in matches),
            "original_concept_stop_sequences":";".join(x["stop_sequence"] for x in matches),
            "source_geometry":manifest["source_geometry"],
            "source_geometry_warning":manifest.get("geometry_warning",""),
            "review_priority":priority,
            "review_reason":reason,
            "current_stop_GTFS_move_approved":"no",
            "actual_route_stop_service_verified":"no",
        }
        cases.append(row)
        route_summary[uid]["remaining_stops"]+=1
        if near:route_summary[uid]["near_KMZ_but_far_GH"]+=1
        if priority.startswith("P1"):route_summary[uid]["P1_stops"]+=1
        points.append({
            "type":"Feature",
            "properties":{k:v for k,v in row.items() if k not in ("longitude","latitude")},
            "geometry":{"type":"Point","coordinates":[float(s["stop_lon"]),float(s["stop_lat"])]},
        })
    cases.sort(key=lambda x:(x["review_priority"],-x["validator_distance_to_final_GH_shape_m"],x["company"]))
    write(OUT/"67_remaining_stop_vs_shape_source_evidence.csv",cases,list(cases[0]))
    (OUT/"67_remaining_stop_vs_GH_shape.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":points},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    ordercases=[]
    orderlines=[]
    for n,x in enumerate(ordering,1):
        uid=x["trip_pattern_id"]
        a=stop[x["stop_1"]]
        b=stop[x["stop_2"]]
        asrc=source_by_stop[(uid,x["stop_1"])]
        bsrc=source_by_stop[(uid,x["stop_2"])]
        if not asrc or not bsrc:raise ValueError("Unmatched original stop order warning")
        a_sequence=";".join(y["stop_sequence"] for y in asrc)
        b_sequence=";".join(y["stop_sequence"] for y in bsrc)
        ordercases.append({
            "trip_pattern_id":uid,"company":manifests[uid]["company"],
            "route_label":manifests[uid]["official_route_label"],
            "stop_1_id":x["stop_1"],"stop_1_name":a["stop_name"],
            "stop_1_original_sequences":a_sequence,
            "stop_1_KMZ_positions_m":";".join(y["shape_dist_traveled_candidate_m"] for y in asrc),
            "stop_2_id":x["stop_2"],"stop_2_name":b["stop_name"],
            "stop_2_original_sequences":b_sequence,
            "stop_2_KMZ_positions_m":";".join(y["shape_dist_traveled_candidate_m"] for y in bsrc),
            "has_multiple_passages_over_same_stop_id":"yes" if len(asrc)>1 or len(bsrc)>1 else "no",
            "geometry_source":manifests[uid]["source_geometry"],
            "review":"check_source_KMZ_loop_SIU_sequence_and_GH_bus_road_passages",
            "automatic_stop_sequence_swap":"no",
            "stop_service_confirmed":"no",
        })
        orderlines.append({
            "type":"Feature",
            "properties":{
                "trip_pattern_id":uid,
                "company":manifests[uid]["company"],
                "route_label":manifests[uid]["official_route_label"],
                "marker":"validator_out_of_order_pair_reference_only_NOT_BUS_ROUTE",
                "stop_1_id":x["stop_1"],"stop_2_id":x["stop_2"],
                "auto_route_or_stop_order_change":"no",
            },
            "geometry":{"type":"LineString","coordinates":[
                [float(a["stop_lon"]),float(a["stop_lat"])],
                [float(b["stop_lon"]),float(b["stop_lat"])]
            ]},
        })
    write(OUT/"4_remaining_stop_order_source_evidence.csv",ordercases,list(ordercases[0]))
    (OUT/"4_remaining_order_warning_pairs_NOT_ROUTES.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":orderlines},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    byroute=[]
    for uid,cnt in route_summary.items():
        byroute.append({
            "trip_pattern_id":uid,
            "company":manifests[uid]["company"],
            "route_label":manifests[uid]["official_route_label"],
            "stop_distance_warnings":cnt["remaining_stops"],
            "stops_with_source_KMZ_within_35m_but_GH_over_100m":cnt["near_KMZ_but_far_GH"],
            "priority_1_large_GH_offset_stops":cnt["P1_stops"],
            "still_has_validator_stop_order_warning":"yes" if any(x["trip_pattern_id"]==uid for x in ordercases) else "no",
            "route_stop_service_verified":"no",
        })
    byroute.sort(key=lambda x:(-x["stop_distance_warnings"],-x["priority_1_large_GH_offset_stops"],x["route_label"]))
    write(OUT/"remaining_67_source_review_by_route.csv",byroute,list(byroute[0]))
    summary={
        "validator_stop_shape_warnings_remaining":len(issue),
        "validator_stop_order_warnings_remaining":len(ordering),
        "route_patterns_with_remaining_stop_shape_issues":len(byroute),
        "stops_within_35m_of_original_KMZ_but_more_than_100m_from_GH_road":
            sum(c["near_KMZ_but_far_GH"] for c in route_summary.values()),
        "priority_1_stop_offset_over_250m":sum(c["P1_stops"] for c in route_summary.values()),
        "new_SIU_stops_created":0,
        "stops_reordered_or_removed":0,
        "GTFS_production_feed_changed":False,
        "new_Overpass_or_GH_requests":0,
    }
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
