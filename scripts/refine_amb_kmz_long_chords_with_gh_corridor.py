#!/usr/bin/env python3
"""Conservatively refine long straight official AMB KMZ chords using GH bus roads.

Each KMZ chord >400m is a candidate, not proof of a broken road. For every
candidate, extract the corresponding portion of the already vetted GH bus road
and use it ONLY if it has consistent forward projection, endpoints match, and
the replacement stays within a strict corridor around the official KMZ chord.
This never moves SIU stops, never changes their sequence, and never promotes
GH-only shortcuts. The complete GTFS is revalidated by the workflow.
"""
import argparse,csv,json,math,shutil
from pathlib import Path
from collections import defaultdict
from pyproj import Transformer,Geod
from shapely.geometry import LineString,Point
from shapely.ops import substring

ROOT=Path(__file__).resolve().parents[1]
KMZ=ROOT/"build/amb-kmz-first-GH-fallback-research"
GH=ROOT/"sources/amb/GTFS_7_largest_shape_offset_review"
OUT=ROOT/"build/amb-KMZ-refined-GH-corridor-NOT-PUBLISHABLE"
M=Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True)
W=Transformer.from_crs("EPSG:32618","EPSG:4326",always_xy=True)
GEOD=Geod(ellps="WGS84")
def key(f):
    return f["properties"]["trip_pattern_id"],int(f["properties"]["section"])
def projected(f):
    return LineString([M.transform(*xy) for xy in f["geometry"]["coordinates"]])
def coords(line):
    return [[round(x,7),round(y,7)] for x,y in (W.transform(*p) for p in line.coords)]
def join(segments):
    out=[]
    for s in segments:
        for p in s:
            if not out or Point(out[-1]).distance(Point(p))>.05:
                out.append(tuple(p))
    return out
def writecsv(p,rows,cols):
    with p.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=cols,extrasaction="ignore")
        w.writeheader();w.writerows(rows)
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--max-corridor-m",type=float,default=35)
    a.add_argument("--endpoint-m",type=float,default=12)
    a.add_argument("--min-chord-m",type=float,default=400)
    a.add_argument("--out",type=Path,default=OUT)
    args=a.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    src=json.loads((KMZ/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").read_text())
    roads=json.loads((GH/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").read_text())
    bygh={key(f):f for f in roads["features"]}
    if len(src["features"])!=352 or set(bygh)!={key(f) for f in src["features"]}:
        raise ValueError("Mismatch in source geometry segment population")
    out=[];audit=[];total=0;accepted=0;patterns=set();changed=set()
    for f in src["features"]:
        k=key(f)
        if f["properties"]["shape_source_actual"]!="official_AMB_KMZ_2026":
            out.append(f);continue
        original=projected(f)
        road=projected(bygh[k])
        source_pts=list(original.coords)
        assembled=[]
        modified=False
        for i,(p,q) in enumerate(zip(source_pts,source_pts[1:])):
            chord=LineString([p,q])
            if chord.length<args.min_chord_m:
                assembled.append([p,q]);continue
            total+=1
            ppoint,qpoint=Point(p),Point(q)
            start=road.project(ppoint)
            end=road.project(qpoint)
            p_error=road.distance(ppoint)
            q_error=road.distance(qpoint)
            reason=""
            replacement=None
            if p_error>args.endpoint_m or q_error>args.endpoint_m:
                reason="GH_endpoints_not_aligned"
            elif end-start<chord.length*.85:
                reason="GH_progress_incompatible_or_shortcut"
            elif end-start>chord.length*1.7:
                reason="GH_detour_excessive"
            else:
                candidate=substring(road,start,end)
                if not isinstance(candidate,LineString) or len(candidate.coords)<3:
                    reason="GH_no_intermediate_road_vertices"
                elif candidate.hausdorff_distance(chord)>args.max_corridor_m:
                    reason="GH_deviates_from_official_KMZ_corridor"
                elif candidate.length>chord.length*1.35:
                    reason="GH_length_excessive"
                else:
                    # Preserve original KMZ endpoints precisely; only insert
                    # road interior vertices. Their positions stay close to
                    # the original official KMZ corridor.
                    replacement=[p]+list(candidate.coords)[1:-1]+[q]
                    if any(Point(x).distance(chord)>args.max_corridor_m for x in replacement):
                        reason="GH_road_vertex_off_source_corridor"
                        replacement=None
                    else:
                        reason="GH_intermediate_vertices_accepted"
            if replacement is None:
                assembled.append([p,q])
            else:
                assembled.append(replacement)
                accepted+=1
                modified=True
                patterns.add(k[0])
                changed.add(k)
            audit.append({
                "trip_pattern_id":k[0],"section":k[1],"chord_index":i,
                "source_chord_m":round(chord.length,1),
                "GH_endpoint_error_start_m":round(p_error,1),
                "GH_endpoint_error_end_m":round(q_error,1),
                "GH_road_chainage_delta_m":round(end-start,1),
                "candidate_decision":reason,
                "accepted":"yes" if replacement is not None else "no",
                "official_KMZ_endpoints_retained":"yes",
                "SIU_stops_changed":"no"
            })
        result=dict(f)
        result["properties"]={**f["properties"],
            "KMZ_corridor_refinement_applied":modified,
            "refinement_method":"insert_GH_bus_road_vertices_only_where_official_KMZ_corridor_matches"}
        result["geometry"]={"type":"LineString","coordinates":coords(LineString(join(assembled)))}
        out.append(result)
    if len(out)!=352 or len(audit)<100:
        raise ValueError("Source input missing expected long chords")
    path=args.out/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson"
    path.write_text(json.dumps({"type":"FeatureCollection","features":out},
                               ensure_ascii=False,separators=(",",":"))+"\n")
    shutil.copy2(KMZ/"GH_full_route_bus_segment_alignment.csv",
                 args.out/"GH_full_route_bus_segment_alignment.csv")
    writecsv(args.out/"KMZ_long_chord_GH_road_refinement_decisions.csv",audit,list(audit[0]))
    summary={
        "total_official_KMZ_chords_over_400m":total,
        "long_chords_with_GH_road_vertices_accepted":accepted,
        "long_chords_rejected_and_original_KMZ_retained":total-accepted,
        "distinct_official_KMZ_sections_refined":len(changed),
        "distinct_route_patterns_refined":len(patterns),
        "official_KMZ_sections_total":340,
        "fallback_GH_sections_untouched":12,
        "source_SIU_stops_or_order_modified":False,
        "GTFS_production_modified":False,
        "actual_bus_road_service_verified":False,
        "requires_full_MobilityData_validator_and_geometry_comparison":True
    }
    (args.out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
