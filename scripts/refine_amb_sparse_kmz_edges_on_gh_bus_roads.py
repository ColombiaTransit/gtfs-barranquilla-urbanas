#!/usr/bin/env python3
"""Conservatively trace sparse >400m AMB-KMZ vertex gaps onto bus roads.

The accepted research approach is official 2026 AMB KMZ first; existing
GraphHopper bus road shapes only for 7 patterns without usable 2026 KMZ.
This script replaces *only* long, un-detailed source edges with candidate
GraphHopper bus roads, never complete KMZ routes, and only when the returned
road follows the KMZ corridor and retains nearby SIU stop positions.

The actual MobilityData validator is run by the companion workflow. It may
reject these research candidates and revert whole patterns. Do not publish
the resulting geometry without operator route verification.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import LineString, Point
from pyproj import Transformer

from query_graphhopper_bus_gap_directions import Client

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"build/amb-kmz-first-GH-fallback-research"
OUT=ROOT/"build/amb-KMZ-dense-roads-research"
VISITS=ROOT/"sources/amb/provisional_trip_stop_order_v3_clean/candidate_trip_stop_sequences_v3_CLEAN_NO_TIMES_NOT_GTFS.csv"
STOPS=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
PROJECT=Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True)

def read_csv(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def write_csv(p,rows):
    if not rows:return
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def key(f):
    return (f["properties"]["trip_pattern_id"],int(f["properties"]["section"]))

def transform(coord):
    return Point(*PROJECT.transform(float(coord[0]),float(coord[1])))

def same(a,b,threshold_m=0.2):
    return a.distance(b)<=threshold_m

def append_nonduplicate(out,point):
    p=[round(float(point[0]),7),round(float(point[1]),7)]
    if not out or transform(out[-1]).distance(transform(p))>0.12:
        out.append(p)

def bidirectional_near_straight(road,source,tolerance_m=75):
    # A sparse KMZ edge only bounds a corridor, NOT a proven street centerline.
    # Test roads and source on equal metric samples in both directions.
    def frac_near(a,b):
        n=max(5,min(250,math.ceil(a.length/25)))
        ds=sorted(a.interpolate(a.length*i/n).distance(b) for i in range(n+1))
        return sum(d<=tolerance_m for d in ds)/len(ds),ds[int(.9*(len(ds)-1))]
    forward,p90_source=frac_near(source,road)
    reverse,p90_road=frac_near(road,source)
    return forward,reverse,max(p90_source,p90_road)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base",type=Path,default=BASE)
    p.add_argument("--out",type=Path,default=OUT)
    p.add_argument("--max-queries",type=int,default=2000)
    p.add_argument("--min-gap-m",type=float,default=400)
    p.add_argument("--max-end-snap-m",type=float,default=45)
    p.add_argument("--max-road-detour-ratio",type=float,default=1.55)
    args=p.parse_args()
    if not 390<=args.min_gap_m<=800 or not 25<=args.max_end_snap_m<=60:
        raise ValueError("Unsupported source-evidence thresholds")
    args.out.mkdir(parents=True,exist_ok=True)
    baseline=json.loads((args.base/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").read_text(encoding="utf-8"))
    if len(baseline["features"])!=352:
        raise ValueError("Expected 352 KMZ-first and GH-fallback sections")
    data=read_csv(args.base/"GH_full_route_bus_segment_alignment.csv")
    meta={(row["trip_pattern_id"],int(row["segment_number"])):row for row in data}
    if len(meta)!=352:raise ValueError("Missing GH source section metadata")
    physical={row["stop_id"]:row for row in read_csv(STOPS)}
    visitrows=read_csv(VISITS)
    if len(visitrows)!=9020:raise ValueError("Expected unchanged clean v3 stop visits")
    bypattern=defaultdict(list)
    for v in visitrows:
        bypattern[v["trip_pattern_id"]].append(v)
    client=Client(os.environ.get("GRAPHHOPPER_URL",""),timeout=35)
    info,status=client.info()
    if status!="ok":raise SystemExit("GraphHopper bus endpoint unavailable: "+status)
    if "bus" not in [x.get("name") for x in info.get("profiles",[]) if isinstance(x,dict)]:
        raise SystemExit("GraphHopper does not advertise bus profile")

    output_features=[]
    gap_rows=[]
    section_rows=[]
    new_gap_shapes=[]
    source_sparse_sections=set()
    changed_sections=set()
    gh_fallback_count=0
    stop_xy={sid:transform([x["stop_lon"],x["stop_lat"]]) for sid,x in physical.items()}
    for feature in baseline["features"]:
        props=feature["properties"]
        k=key(feature)
        uid,secno=k
        section=meta[k]
        source_kind=props["shape_source_actual"]
        coords=feature["geometry"]["coordinates"]
        if source_kind!="official_AMB_KMZ_2026":
            gh_fallback_count+=1
            output_features.append(feature)
            continue

        points=list(coords)
        local_positions=[0.]
        for a,b in zip(points,points[1:]):
            local_positions.append(local_positions[-1]+transform(a).distance(transform(b)))
        source_length=float(section["KMZ_segment_end_m"])-float(section["KMZ_segment_start_m"])
        if abs(local_positions[-1]-source_length)>22:
            raise ValueError("Source KMZ section and GH metadata length mismatch for "+str(k))
        sparse=[i for i in range(len(points)-1) if
                local_positions[i+1]-local_positions[i]>args.min_gap_m]
        if sparse:source_sparse_sections.add(k)
        visits=sorted(bypattern[uid],key=lambda v:int(v["stop_sequence"]))
        output=[]
        section_accepted=0
        gap_idx=0
        for i in range(len(points)-1):
            append_nonduplicate(output,points[i])
            dist=local_positions[i+1]-local_positions[i]
            if dist<=args.min_gap_m:continue
            gap_idx+=1
            source_a=transform(points[i])
            source_b=transform(points[i+1])
            source_line=LineString([source_a.coords[0],source_b.coords[0]])
            start=float(section["KMZ_segment_start_m"])+local_positions[i]
            end=float(section["KMZ_segment_start_m"])+local_positions[i+1]
            # Stop visits in this exact source edge. Include the same stop_id
            # repeatedly if the bus route traverses a road on both directions.
            affected=[v for v in visits if
                      start-0.02<=float(v["shape_dist_traveled_candidate_m"])<=end+0.02]
            selected_points=[stop_xy[v["stop_id"]] for v in affected]
            old_near=[pt.distance(source_line) for pt in selected_points]
            gh=None
            gh_status="not_queried_limit"
            if client.route_queries<args.max_queries:
                gh,gh_status=client.route([points[i],points[i+1]])
            if gh:
                road=gh["geometry"]
                start_offset=source_a.distance(Point(road.coords[0]))
                end_offset=source_b.distance(Point(road.coords[-1]))
                ratio=road.length/max(dist,1)
                cov_s,cov_g,p90=bidirectional_near_straight(road,source_line)
                new_near=[pt.distance(road) for pt in selected_points]
                newly_far=sum(a<=100 and b>100 for a,b in zip(old_near,new_near))
                local_source_stops=sum(a<=45 for a in old_near)
                local_lost_75=sum(a<=45 and b>75 for a,b in zip(old_near,new_near))
                # Both alignment and existing-stop criteria are required.
                accepted=(
                    start_offset<=args.max_end_snap_m and
                    end_offset<=args.max_end_snap_m and
                    .95<=ratio<=args.max_road_detour_ratio and
                    cov_s>=.82 and cov_g>=.82 and p90<=75 and
                    newly_far==0 and local_lost_75==0
                )
                if accepted:
                    # Add snapped endpoint connectors only where needed.
                    # Reinsert the ORIGINAL KMZ endpoint exactly to prevent
                    # sections and original source anchors from drifting.
                    for coord in gh["coordinates"]:
                        append_nonduplicate(output,coord)
                    append_nonduplicate(output,points[i+1])
                    section_accepted+=1
                    new_gap_shapes.append({
                        "type":"Feature",
                        "properties":{
                            "trip_pattern_id":uid,"section":secno,"gap_index":gap_idx,
                            "accepted":"research_only_passed_local_geometry_checks",
                            "company":props.get("company",""),
                            "route_label":props.get("route_label",""),
                            "kmz_gap_length_m":round(dist,1),
                        },
                        "geometry":{"type":"LineString","coordinates":gh["coordinates"]},
                    })
                verdict="GH_road_local_candidate" if accepted else "rejected_GH_corridor_or_stop_risk"
            else:
                accepted=False
                start_offset=end_offset=ratio=cov_s=cov_g=p90=""
                newly_far=local_lost_75=""
                local_source_stops=sum(a<=45 for a in old_near)
                verdict=gh_status
            gap_rows.append({
                "trip_pattern_id":uid,"company":props.get("company",""),
                "route_label":props.get("route_label",""),
                "section_number":secno,"gap_index":gap_idx,
                "KMZ_vertex_start":i,"KMZ_vertex_end":i+1,
                "original_KMZ_chord_m":round(dist,1),
                "KMZ_start_lon":round(float(points[i][0]),7),
                "KMZ_start_lat":round(float(points[i][1]),7),
                "KMZ_end_lon":round(float(points[i+1][0]),7),
                "KMZ_end_lat":round(float(points[i+1][1]),7),
                "SIU_source_visits_on_gap":len(affected),
                "SIU_source_visits_within_45m":local_source_stops,
                "GraphHopper_bus_status":gh_status,
                "GH_start_snap_m":round(start_offset,1) if gh else "",
                "GH_end_snap_m":round(end_offset,1) if gh else "",
                "GH_to_KMZ_straight_ratio":round(ratio,3) if gh else "",
                "KMZ_chord_near_road_fraction_75m":round(cov_s,3) if gh else "",
                "GH_road_near_KMZ_chord_fraction_75m":round(cov_g,3) if gh else "",
                "bidirectional_p90_source_road_m":round(p90,1) if gh else "",
                "SIU_visits_newly_over_100m":newly_far,
                "SIU_visits_became_over_75m":local_lost_75,
                "local_candidate_accepted":"yes" if accepted else "no",
                "decision":verdict,
                "actual_operator_2026_road_traversal_confirmed":"no",
                "official_KMZ_vertices_removed":"no",
            })
        append_nonduplicate(output,points[-1])
        section_changed=(section_accepted>0)
        if section_changed:changed_sections.add(k)
        result_feature={
            "type":"Feature","properties":{
                **props,
                "shape_source_actual":"official_AMB_KMZ_2026",
                "shape_refinement_method":("GH_bus_partial_sparse_edge_refinement"
                                           if section_changed else "original_2026_KMZ"),
                "accepted_local_sparse_edges":section_accepted,
                "operator_exact_street_tracing_proven":False,
                "GTFS_publication_ready":False,
            },
            "geometry":{"type":"LineString","coordinates":output},
        }
        if len(output)<2 or max(
                transform(a).distance(transform(b)) for a,b in zip(output,output[1:])
                )>max(args.min_gap_m*4,2100):
            # The longest possible original KMZ gaps are <=2.005km and
            # could remain unchanged if GH fails. Don't introduce new larger
            # gaps, but record already sparse KMZ source issues.
            old_max=max(transform(a).distance(transform(b)) for a,b in zip(points,points[1:]))
            new_max=max(transform(a).distance(transform(b)) for a,b in zip(output,output[1:]))
            if new_max>old_max+5:
                raise ValueError("Refinement made source geometry worse: "+str(k))
        output_features.append(result_feature)
        if sparse:
            section_rows.append({
                "trip_pattern_id":uid,
                "company":props.get("company",""),
                "route_label":props.get("route_label",""),
                "section_number":secno,
                "original_KMZ_gaps_over_400m":len(sparse),
                "GH_locally_accepted_gap_count":section_accepted,
                "GH_rejected_or_not_routed_gap_count":len(sparse)-section_accepted,
                "before_KMZ_coordinate_count":len(points),
                "after_candidate_coordinate_count":len(output),
                "source_is_official_KMZ_2026":"yes",
                "formal_GTFS_validator_acceptance":"pending",
            })
        print("KMZ section "+str(len(output_features))+"/352 "+uid+" #"+str(secno)+
              " gaps="+str(len(sparse))+
              " locally_ok="+str(section_accepted),flush=True)
    if len(output_features)!=352 or len(source_sparse_sections)!=144:
        raise ValueError("Expected exactly 144 official KMZ sections with >400m source gaps")
    if gh_fallback_count!=12:
        raise ValueError("Expected exactly 12 GH fallback sections for no-KMZ patterns")
    if len(gap_rows)==0:
        raise ValueError("No source KMZ sparse edges processed")
    result={"type":"FeatureCollection","features":output_features}
    (args.out/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").write_text(
        json.dumps(result,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    (args.out/"GH_full_route_bus_segment_alignment.csv").write_text(
        (args.base/"GH_full_route_bus_segment_alignment.csv").read_text(encoding="utf-8"),
        encoding="utf-8")
    write_csv(args.out/"KMZ_sparse_edges_GH_bus_decisions.csv",gap_rows)
    write_csv(args.out/"KMZ_sparse_sections_review.csv",section_rows)
    (args.out/"GraphHopper_accepted_KMZ_sparse_gap_road_candidates_RESEARCH_ONLY.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":new_gap_shapes},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    outcome=Counter(x["decision"] for x in gap_rows)
    summary={
        "input_route_patterns":70,
        "official_KMZ_source_sections_with_sparse_edges":len(source_sparse_sections),
        "all_KMZ_gaps_over_400m":len(gap_rows),
        "GraphHopper_bus_profile":"bus",
        "GH_bus_route_queries":client.route_queries,
        "locally_accepted_GH_road_substitutions":sum(x["local_candidate_accepted"]=="yes" for x in gap_rows),
        "not_locally_accepted_GH_road_substitutions":sum(x["local_candidate_accepted"]!="yes" for x in gap_rows),
        "source_sections_locally_refined":len(changed_sections),
        "existing_GH_no_KMZ_fallback_sections_unchanged":gh_fallback_count,
        "local_decision_reasons":dict(outcome),
        "validator_pass_required_before_research_candidate_approval":True,
        "source_KMZ_original_vertices_preserved":True,
        "source_v3_stop_visit_sequences_changed":False,
        "real_stop_service_or_route_direction_confirmed":False,
        "production_GTFS_modified":False,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
