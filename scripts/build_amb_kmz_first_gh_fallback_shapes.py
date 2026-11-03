#!/usr/bin/env python3
"""Build an official AMB-KMZ-first / GH-fallback shapes RESEARCH fixture.

The 70 provisional source trip patterns have already been mapped onto source
KMZ/ArcGIS chainages, and an independent 352-section GraphHopper bus road
collection exists. For a KMZ-sourced route component, copy its actual 2026
official KMZ polyline in the same section chainage positions. If the component
has NO usable genuine route KMZ, use the previously generated GH bus shape as
fallback; mark it as derived from older ArcGIS when applicable.

Output retains 352 sections so that the unchanged nonpublishing GTFS fixture
generator can produce exactly comparable stop_times/trips/agencies/routes.
This creates no fake SIU stop positions, no route directions, no OSM query,
no production output, and no real trip timetable.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from collections import Counter,defaultdict
from pathlib import Path

from shapely.geometry import LineString
from shapely.ops import substring
from pyproj import Geod

from audit_amb_full_route_graphhopper_bus_geometry import (
    ROOT,PATTERNS,TO_WGS,load_geometries
)

BASE = ROOT/"sources/amb/GTFS_7_largest_shape_offset_review"
SHAPES=BASE/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson"
META=BASE/"GH_full_route_bus_segment_alignment.csv"
OUT=ROOT/"build/amb-kmz-first-GH-fallback-research"
GEOD=Geod(ellps="WGS84")

def read_csv(path):
    with path.open("r",newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def haversine_series(coords):
    longest=0.
    for a,b in zip(coords,coords[1:]):
        length=abs(GEOD.inv(float(a[0]),float(a[1]),float(b[0]),float(b[1]))[2])
        longest=max(longest,length)
    return round(longest,1)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=OUT)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)

    source_manifest=read_csv(PATTERNS)
    patterns={r["trip_pattern_id"]:r for r in source_manifest}
    if len(patterns)!=70:
        raise ValueError(f"Unexpected source patterns: {len(patterns)}")
    source_lines,source_details=load_geometries(patterns)
    metadata=read_csv(META)
    if len(metadata)!=352:
        raise ValueError(f"Unexpected GH road segment count {len(metadata)}")
    prior=json.loads(SHAPES.read_text(encoding="utf-8"))
    if len(prior["features"])!=352:
        raise ValueError("Original GH shape collection is not the complete 352 section version")
    source_segments={(r["trip_pattern_id"],int(r["segment_number"])):r
                     for r in metadata}
    prior_segments={(f["properties"]["trip_pattern_id"],int(f["properties"]["section"])):f
                    for f in prior["features"]}
    if len(source_segments)!=352 or set(prior_segments)!=set(source_segments):
        raise ValueError("Metadata and GraphHopper shape sections do not align")

    built=[]
    route_rows=[]
    point_by_pattern=defaultdict(int)
    section_source=defaultdict(Counter)
    dubious=[]
    for key,f in prior_segments.items():
        uid,part=key
        row=source_segments[key]
        pattern=patterns[uid]
        original=(pattern["company"],pattern["official_route_label"],
                  pattern["geometry_component"])
        original_shape=source_lines[original]
        detail=source_details[original]
        actual_type=detail["source"]
        is_kmz=(actual_type=="AMB_KMZ_2026" and
                pattern["source_geometry"]=="AMB_KMZ_2026")
        if is_kmz:
            start=float(row["KMZ_segment_start_m"])
            end=float(row["KMZ_segment_end_m"])
            line=substring(original_shape,start,end)
            if not isinstance(line,LineString) or line.length<1:
                raise ValueError(f"Invalid KMZ section {key}")
            pts=[[round(float(lon),7),round(float(lat),7)]
                 for lon,lat in (TO_WGS.transform(*xy) for xy in line.coords)]
            origin="official_AMB_KMZ_2026"
        else:
            # No reliable KMZ: use the existing, already reviewed
            # GraphHopper bus road (not an invented 2026 official KMZ).
            pts=f["geometry"]["coordinates"]
            origin="GH_bus_fallback_no_usable_2026_KMZ"
        if len(pts)<2:
            raise ValueError(f"Missing usable geometry for {key}")
        if any(not(-76<float(x[0])<-73 and 9<float(x[1])<12) for x in pts):
            raise ValueError(f"Out-of-project shape coordinates for {key}")
        maximum=haversine_series(pts)
        geo={"type":"Feature","properties":{
            **f["properties"],
            "trip_pattern_id":uid,"section":part,
            "shape_source_precedence":"KMZ_2026_then_GH_fallback",
            "shape_source_actual":origin,
            "original_source_geometry":actual_type,
            "source_geometry_warning":detail["warning"],
            "operator_stop_service_confirmed":False,
            "gtfs_demo_only":True,
        },"geometry":{"type":"LineString","coordinates":pts}}
        built.append(geo)
        section_source[uid][origin]+=1
        point_by_pattern[uid]+=len(pts)
        if maximum>400:
            dubious.append({
                "trip_pattern_id":uid,"section_number":part,
                "source":origin,
                "maximum_geodesic_jump_between_source_vertices_m":maximum,
                "warning":"sparse_source_road_geometry_or_connector_review",
            })
        route_rows.append({
            "trip_pattern_id":uid,
            "company":pattern["company"],
            "route_label":pattern["official_route_label"],
            "section_number":part,
            "geometry_source":origin,
            "original_GEOMETRY":actual_type,
            "original_source_warning":detail["warning"],
            "source_vertices":len(pts),
            "max_single_vertex_step_m":maximum,
            "KMZ_chainage_start_m":row["KMZ_segment_start_m"],
            "KMZ_chainage_end_m":row["KMZ_segment_end_m"],
            "SIU_stops_moved_or_removed":"no",
            "real_2026_operator_route_confirmed":"no",
        })
    if len(built)!=352:
        raise ValueError("Lost sections")
    for uid in patterns:
        if not section_source[uid]:
            raise ValueError(f"Pattern has no geometry: {uid}")
        if len(section_source[uid])!=1:
            raise ValueError(f"Mixed source within same source-pattern: {uid}")
    pattern_rows=[]
    for uid,p in sorted(patterns.items()):
        source=next(iter(section_source[uid]))
        pattern_rows.append({
            "trip_pattern_id":uid,
            "company":p["company"],
            "official_route_label":p["official_route_label"],
            "shape_source_selected":source,
            "sections":sum(section_source[uid].values()),
            "total_coordinate_points":point_by_pattern[uid],
            "historical_fallback_warning":p["geometry_warning"],
            "exact_SIU_stop_order_preserved":"yes",
            "genuine_2026_KMZ_used":"yes" if source=="official_AMB_KMZ_2026" else "no",
        })
    n_kmz=sum(p["genuine_2026_KMZ_used"]=="yes" for p in pattern_rows)
    n_fallback=len(pattern_rows)-n_kmz
    if n_kmz<=0 or n_fallback<=0:
        raise ValueError("Expected both official KMZ and GH fallback patterns")
    zipped={"type":"FeatureCollection","features":built}
    (args.out/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").write_text(
        json.dumps(zipped,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    shutil.copy2(META,args.out/"GH_full_route_bus_segment_alignment.csv")
    write_csv(args.out/"shape_source_by_pattern.csv",pattern_rows)
    write_csv(args.out/"shape_source_by_section.csv",route_rows)
    if dubious:
        write_csv(args.out/"source_shape_sparse_vertex_or_connector_QA.csv",dubious)
    summary={
        "source_patterns":len(pattern_rows),
        "official_2026_KMZ_patterns":n_kmz,
        "GraphHopper_bus_fallback_patterns":n_fallback,
        "source_road_sections":len(built),
        "official_2026_KMZ_sections":sum(
            r["geometry_source"]=="official_AMB_KMZ_2026" for r in route_rows),
        "GH_fallback_sections":sum(
            r["geometry_source"]=="GH_bus_fallback_no_usable_2026_KMZ" for r in route_rows),
        "KMZ_source_vertex_steps_over_400m_warn_sections":sum(
            q["source"]=="official_AMB_KMZ_2026" for q in dubious),
        "all_patterns_used_exact_source_v3_SIU_stop_order":True,
        "no_new_GH_or_OSM_queries":True,
        "2026_KMZ_source_route_is_current_legal_operational_service_verified":False,
        "GTFS_production_modified":False,
        "GTFS_demo_only":True,
        "geometries_equal_pilot_baseline_population":True,
        "physical_SIU_stop_records_created":0,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
