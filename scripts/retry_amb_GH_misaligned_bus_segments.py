#!/usr/bin/env python3
"""Retry ONLY GH bus sections that diverged from official AMB KMZ route shapes.

The 352 first-pass sections were routed with ~950m KMZ anchor spacing. For
the 42 flagged sections, use ~450m source anchors to distinguish the impact
of GH shortcut routing from true road access / outdated geometry conflict.

Creates research-only revised road candidates and a before/after QA matrix.
No route, SIU stop order, stop ID, GTFS files or times are modified.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
from collections import Counter,defaultdict
from pathlib import Path
from shapely.geometry import Point
from shapely.ops import substring

from audit_amb_full_route_graphhopper_bus_geometry import (
    ROOT,PATTERNS,STOPS,ARCGIS,SOURCE,TO_METERS,
    read_csv,Client,load_geometries,request_points,coverage,save_csv
)

FIRST=ROOT/"sources/amb/full_GH_bus_geometry_quality"
OUT=ROOT/"build/amb-GH-dense-KMZ-segment-retry"

def number(s):
    try:return float(s)
    except (TypeError,ValueError):return None

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=OUT)
    parser.add_argument("--anchor-spacing-m",type=int,default=450)
    parser.add_argument("--max-sections",type=int,default=42)
    args=parser.parse_args()
    if not 300<=args.anchor_spacing_m<=600 or not 1<=args.max_sections<=42:
        raise ValueError("Invalid bounded GH route retry parameters")
    args.out.mkdir(parents=True,exist_ok=True)
    segments=read_csv(FIRST/"GH_full_route_bus_segment_alignment.csv")
    stops=read_csv(FIRST/"GH_stop_sequence_and_road_access_audit.csv")
    manifest={r["trip_pattern_id"]:r for r in read_csv(PATTERNS)}
    physical={r["stop_id"]:r for r in read_csv(STOPS)}
    if len(segments)!=352 or len(stops)!=9020:
        raise ValueError("First-pass GH source results changed since QA")
    needs=[s for s in segments if s["road_geometry_candidate_status"]!="candidate_consistent_with_KMZ"]
    if len(needs)!=42:
        raise ValueError("Expected 42 previously problematic source road sections")
    shape,sources=load_geometries(manifest)
    byseg=defaultdict(list)
    for s in stops:
        byseg[(s["trip_pattern_id"],int(s["GH_segment_number"]))].append(s)
    client=Client(os.environ.get("GRAPHHOPPER_URL",""),timeout=30)
    info,status=client.info()
    if status!="ok":
        raise SystemExit("GraphHopper private /info unavailable: "+status)
    if "bus" not in [x.get("name") for x in info.get("profiles",[]) if isinstance(x,dict)]:
        raise SystemExit("Private GraphHopper server has no bus profile")
    results=[]
    geodata=[]
    for s in needs[:args.max_sections]:
        uid=s["trip_pattern_id"]
        pat=manifest[uid]
        key=(pat["company"],pat["official_route_label"],pat["geometry_component"])
        kmz=shape[key]
        start=float(s["KMZ_segment_start_m"])
        end=float(s["KMZ_segment_end_m"])
        section=substring(kmz,start,end)
        points=request_points(section,args.anchor_spacing_m)
        response,ghstatus=client.route(points)
        cov=coverage(section,response["geometry"]) if response else {}
        ratio=response["distance_m"]/section.length if response else None
        startoffset=round(Point(*TO_METERS.transform(*points[0])).distance(response["geometry"]),1) if response else None
        endoffset=round(Point(*TO_METERS.transform(*points[-1])).distance(response["geometry"]),1) if response else None
        baseline_score=min(float(s["source_road_coverage_50m"]),float(s["road_source_coverage_50m"]))
        score=min(cov["source_near_road"],cov["road_near_source"]) if response else 0.
        improved=score>baseline_score+.03
        repaired=(bool(response) and score>=.72 and
                  ratio>=.65 and ratio<=1.9 and startoffset<=60 and endoffset<=60)
        before_after=[]
        for stop in byseg[(uid,int(s["segment_number"]))]:
            origin=physical[stop["SIU_physical_stop_id"]]
            p=Point(*TO_METERS.transform(float(origin["stop_lon"]),float(origin["stop_lat"])))
            old=number(stop["GH_road_snapped_nearest_distance_m"])
            new=round(p.distance(response["geometry"]),1) if response else None
            before_after.append((old,new))
        old_match=sum(a is not None and a<=45 for a,b in before_after)
        new_match=sum(b is not None and b<=45 for a,b in before_after)
        outcome=("new_road_candidate_consistent" if repaired else
                 "geometry_alignment_improves_but_not_sufficient" if improved else
                 "still_inconsistent_or_unroutable")
        record={
            "trip_pattern_id":uid,
            "company":pat["company"],"route_label":pat["official_route_label"],
            "segment_number":s["segment_number"],
            "source_geometry":s["source_geometry"],
            "KMZ_segment_length_m":s["KMZ_segment_length_m"],
            "original_anchor_spacing_nominal_m":950,
            "retry_anchor_spacing_nominal_m":args.anchor_spacing_m,
            "original_source_near_GH_fraction_50m":s["source_road_coverage_50m"],
            "retry_source_near_GH_fraction_50m":cov.get("source_near_road",""),
            "original_GH_near_source_fraction_50m":s["road_source_coverage_50m"],
            "retry_GH_near_source_fraction_50m":cov.get("road_near_source",""),
            "old_min_bidirectional_coverage":baseline_score,
            "new_min_bidirectional_coverage":score,
            "retry_GH_bus_profile_status":ghstatus,
            "retry_GH_distance_m":response["distance_m"] if response else "",
            "retry_GH_to_KMZ_distance_ratio":round(ratio,3) if ratio else "",
            "retry_source_anchor_start_m_to_GH_road":startoffset if startoffset is not None else "",
            "retry_source_anchor_end_m_to_GH_road":endoffset if endoffset is not None else "",
            "stop_visits_in_section":len(before_after),
            "stop_visits_near_old_road_within_45m":old_match,
            "stop_visits_near_retry_road_within_45m":new_match,
            "change_in_nearby_SIU_visits":new_match-old_match,
            "retry_research_status":outcome,
            "GH_bus_routing_creates_road_candidate_not_legal_certification":"yes",
            "SIU_stop_sequence_modified":"no",
        }
        results.append(record)
        if response:
            geodata.append({
                "type":"Feature",
                "properties":{
                    "trip_pattern_id":uid,"company":pat["company"],
                    "route_label":pat["official_route_label"],
                    "segment_number":int(s["segment_number"]),
                    "retry_status":outcome,
                    "old_min_bidirectional_coverage":baseline_score,
                    "retry_min_bidirectional_coverage":score,
                    "source_is_official_KMZ_or_explicit_old_ArcGIS":s["source_geometry"],
                },
                "geometry":{"type":"LineString","coordinates":response["coordinates"]},
            })
        print("section="+uid+"#"+s["segment_number"]+
              " old="+str(round(baseline_score,3))+
              " new="+str(round(score,3))+" "+outcome,flush=True)
    if not results:
        raise ValueError("No problematic route segments were retried")
    save_csv(args.out/"GH_dense_anchor_road_segment_before_after_QA.csv",
             results,list(results[0]))
    (args.out/"GH_dense_KMZ_constrained_bus_road_candidates_RESEARCH_ONLY.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":geodata},ensure_ascii=False,separators=(",",":"))+"\n",
        encoding="utf-8")
    outcomes=Counter(x["retry_research_status"] for x in results)
    summary={
        "source_GH_full_route_sections":len(segments),
        "previously_mismatching_sections":len(needs),
        "sections_retried":len(results),
        "GraphHopper_profile":"bus",
        "GH_version":info.get("version",""),
        "GH_route_queries":client.route_queries,
        "new_road_candidates_consistent_with_KMZ_after_dense_waypoints":
            outcomes["new_road_candidate_consistent"],
        "alignment_improved_but_still_inconsistent":
            outcomes["geometry_alignment_improves_but_not_sufficient"],
        "still_inconsistent_or_unroutable":
            outcomes["still_inconsistent_or_unroutable"],
        "additional_stop_visits_close_to_retried_GH_road_net":sum(
            x["change_in_nearby_SIU_visits"] for x in results),
        "road_candidates_mapped":len(geodata),
        "no_OSM_requests":True,
        "GTFS_stops_or_sequences_changed":False,
        "reached_legal_source_route_certainty":False,
        "private_endpoint_in_outputs":False,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    md=[
        "# Afwijkende AMB-routegeometrie opnieuw getoetst met dichter geplaatste KMZ-waypoints",
        "",
        "Een busroute die wegens 950m-waypoints afwijkt van het brontraject is opnieuw via het busprofiel gerouteerd",
        "met ongeveer 450m tussen de verplichte KMZ-punten. Dit voorkomt veel kortere omwegen over parallelwegen",
        "maar bewijst geen concessiebediening of exacte haltes. De eerdere GH-geometrie is niet overschreven.",
        "",
        "## Resultaat","",
    ]
    for k,v in summary.items():
        if type(v) is int:md.append("- "+k+": **"+str(v)+"**")
    md.extend([
        "",
        "## Bronnen / beperkingen","",
        "- Private GraphHopper via ColombiaTransit organisatievariabele GRAPHHOPPER_URL, profiel bus.",
        "- Publieke GraphHopper API-documentatie: https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md",
        "- Officiële KMZ-routes; historische ArcGIS-geometrie blijft als fallback gemarkeerd.",
        "- Geen stop_sequence, stop_id, routes.txt, trips.txt of stop_times.txt aangepast.",
        "",
        "## Output","",
        "- GH_dense_anchor_road_segment_before_after_QA.csv: per wegdeel eerdere/nieuwe match en aantal haltes binnen 45m.",
        "- GH_dense_KMZ_constrained_bus_road_candidates_RESEARCH_ONLY.geojson: dichter aan de bronroute gebonden kandidaat-weggeometrie.",
        ""
    ])
    (args.out/"summary.md").write_text("\n".join(md),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
