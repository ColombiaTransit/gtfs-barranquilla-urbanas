#!/usr/bin/env python3
"""Combine 310 initially aligned and 21 newly aligned GH bus road segments.

Only newer GH bus-road shapes that PASSED stricter repeat routing against KMZ
are promoted to a new, separate RESEARCH candidate geometry dataset. Sources
and stop IDs are immutable. The combined 352-segment dataset is used as input
for another non-destructive stop-order match with repeated passage handling.

Retains the 21 unresolved source/road mismatches as flagged, NOT certified.
"""
from __future__ import annotations
import csv
import json
from collections import Counter,defaultdict
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString,Point

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/"sources/amb/full_GH_bus_geometry_quality"
RETRY=ROOT/"sources/amb/GH_dense_KMZ_shape_retry"
STOPS=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
OUT=ROOT/"build/amb-GH-best-geometry"
TO_METERS=Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True)

def read(path):
    with path.open("r",newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write(path,rows,columns):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def ident(row):
    return (row["trip_pattern_id"],int(row["segment_number"]))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    segment_rows=read(OLD/"GH_full_route_bus_segment_alignment.csv")
    stops=read(OLD/"GH_stop_sequence_and_road_access_audit.csv")
    patterns=read(OLD/"GH_route_pattern_quality_register.csv")
    retry=read(RETRY/"GH_dense_anchor_road_segment_before_after_QA.csv")
    source_shapes=json.loads((OLD/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").read_text(encoding="utf-8"))
    retry_shapes=json.loads((RETRY/"GH_dense_KMZ_constrained_bus_road_candidates_RESEARCH_ONLY.geojson").read_text(encoding="utf-8"))
    physical={x["stop_id"]:x for x in read(STOPS)}
    if len(segment_rows)!=352 or len(stops)!=9020 or len(patterns)!=70 or len(retry)!=42:
        raise ValueError("GH baseline / dense retry input counts changed")
    retry_idx={ident(x):x for x in retry}
    if len(retry_idx)!=42:raise ValueError("Repeated dense-retry segment identity")
    first={}
    for f in source_shapes["features"]:
        p=f["properties"]
        key=(p["trip_pattern_id"],int(p["section"]))
        if key in first:raise ValueError("Duplicate baseline GH shape")
        first[key]=f
    newer={}
    for f in retry_shapes["features"]:
        p=f["properties"]
        key=(p["trip_pattern_id"],int(p["segment_number"]))
        if key in newer:raise ValueError("Duplicate revised GH geometry")
        newer[key]=f
    if len(first)!=352 or len(newer)!=42:raise ValueError("Incomplete GH source shapes")
    initial={ident(x):x for x in segment_rows}
    if set(retry_idx)-set(initial):raise ValueError("Retry references unknown section")
    chosen_shapes={}
    merged=[]
    provenance=[]
    for row in segment_rows:
        key=ident(row)
        new=dict(row)
        should_switch=(key in retry_idx and
                       retry_idx[key]["retry_research_status"]=="new_road_candidate_consistent")
        if should_switch:
            v=retry_idx[key]
            f=newer[key]
            new["source_road_coverage_50m"]=v["retry_source_near_GH_fraction_50m"]
            new["road_source_coverage_50m"]=v["retry_GH_near_source_fraction_50m"]
            new["GH_bus_road_distance_m"]=v["retry_GH_distance_m"]
            new["GH_road_to_KMZ_ratio"]=v["retry_GH_to_KMZ_distance_ratio"]
            new["start_waypoint_road_distance_m"]=v["retry_source_anchor_start_m_to_GH_road"]
            new["end_waypoint_road_distance_m"]=v["retry_source_anchor_end_m_to_GH_road"]
            new["road_geometry_candidate_status"]="candidate_consistent_with_KMZ"
            new["GH_sampled_KMZ_anchor_count"]=""
        else:
            f=first[key]
        new["best_candidate_road_source"]="dense_450m_GH_retry" if should_switch else "baseline_950m_GH"
        new["source_geometry_is_legally_proven"]="no"
        merged.append(new)
        geom={"type":"Feature",
              "properties":{
                  **f["properties"],
                  "trip_pattern_id":row["trip_pattern_id"],
                  "section":int(row["segment_number"]),
                  "road_candidate_source":new["best_candidate_road_source"],
                  "road_candidate_status":new["road_geometry_candidate_status"],
                  "is_real_2026_bus_route_confirmed":False,
              },
              "geometry":f["geometry"]}
        chosen_shapes[key]=geom
        provenance.append({
            "trip_pattern_id":row["trip_pattern_id"],
            "company":row["company"],"route_label":row["route_label"],
            "segment_number":row["segment_number"],
            "KMZ_shape_length_m":row["KMZ_segment_length_m"],
            "road_candidate_source":new["best_candidate_road_source"],
            "selected_as_research_corrected_geometry":"yes" if should_switch else "no",
            "new_source_near_road_fraction_50m":new["source_road_coverage_50m"],
            "new_road_near_source_fraction_50m":new["road_source_coverage_50m"],
            "road_candidate_status":new["road_geometry_candidate_status"],
            "actual_bus_route_verified":"no",
        })
    if len(chosen_shapes)!=352 or sum(p["selected_as_research_corrected_geometry"]=="yes" for p in provenance)!=21:
        raise ValueError("Expected 21 validated research bus road geometry replacements")

    line={}
    for key,f in chosen_shapes.items():
        line[key]=LineString([TO_METERS.transform(*x[:2]) for x in f["geometry"]["coordinates"]])
    byregion=defaultdict(list)
    for old in stops:
        key=(old["trip_pattern_id"],int(old["GH_segment_number"]))
        if key not in line:raise ValueError("Unmapped stop in new GH road geometry")
        byregion[key].append(old)
    recalculated=[]
    for key,items in sorted(byregion.items()):
        items.sort(key=lambda s:int(s["source_stop_sequence"]))
        geometry=line[key]
        section=next(x for x in merged if ident(x)==key)
        last=None
        for row in items:
            stop=physical[row["SIU_physical_stop_id"]]
            point=Point(*TO_METERS.transform(float(stop["stop_lon"]),float(stop["stop_lat"])))
            distance=round(point.distance(geometry),1)
            projection=round(geometry.project(point),1)
            if last is not None and projection<last-120:
                order_status="GH_local_order_backwards_over_120m"
            else:
                order_status="GH_local_order_compatible"
            last=projection
            state=("candidate_near_GH_bus_road" if distance<=25 else
                   "candidate_needs_close_GH_review" if distance<=45 else
                   "candidate_far_from_GH_bus_road")
            update=dict(row)
            update["GH_road_snapped_nearest_distance_m"]=distance
            update["GH_local_chainage_m"]=projection
            update["GH_segment_source_near_road_fraction"]=section["source_road_coverage_50m"]
            update["GH_segment_road_near_source_fraction"]=section["road_source_coverage_50m"]
            update["GH_road_stop_assessment"]=state
            update["GH_stop_order_assessment"]=order_status
            update["best_candidate_road_source"]=section["best_candidate_road_source"]
            recalculated.append(update)
    if len(recalculated)!=9020:raise ValueError("Lost SIU stop rows in merged road candidate")

    bypattern=defaultdict(list)
    for r in recalculated:bypattern[r["trip_pattern_id"]].append(r)
    revised_pattern=[]
    for p in patterns:
        uid=p["trip_pattern_id"]
        xs=bypattern[uid]
        counters=Counter(x["GH_road_stop_assessment"] for x in xs)
        backwards=sum(x["GH_stop_order_assessment"]=="GH_local_order_backwards_over_120m" for x in xs)
        y=dict(p)
        y["GH_stops_within_25m_road"]=counters["candidate_near_GH_bus_road"]
        y["GH_stop_visits_beyond_45m_from_road"]=counters["candidate_far_from_GH_bus_road"]
        y["GH_stop_visits_showing_order_backward_over_120m"]=backwards
        y["GH_sections_road_consistent"]=sum(
            x["road_geometry_candidate_status"]=="candidate_consistent_with_KMZ" for x in merged
            if x["trip_pattern_id"]==uid)
        y["road_and_order_research_status"]=(
            "road_geometry_candidate_with_order_review" if
            y["GH_sections_road_consistent"]==int(y["GH_sequential_sections_tested"]) and
            counters["candidate_far_from_GH_bus_road"]==0 and backwards==0
            else "road_geometry_or_stop_order_needs_review")
        y["improved_GH_dense_geometry_used"]="yes" if any(
            x["best_candidate_road_source"]=="dense_450m_GH_retry" for x in merged
            if x["trip_pattern_id"]==uid) else "no"
        revised_pattern.append(y)

    write(OUT/"GH_full_route_bus_segment_alignment.csv",merged,list(merged[0]))
    write(OUT/"GH_stop_sequence_and_road_access_audit.csv",recalculated,list(recalculated[0]))
    write(OUT/"GH_route_pattern_quality_register.csv",revised_pattern,list(revised_pattern[0]))
    write(OUT/"GH_road_candidate_selection_provenance.csv",provenance,list(provenance[0]))
    collection={"type":"FeatureCollection","features":[chosen_shapes[ident(x)] for x in segment_rows]}
    (OUT/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").write_text(
        json.dumps(collection,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    metric={
        "GH_road_segments_total":len(merged),
        "GH_improved_450m_route_sections_selected":21,
        "GH_road_sections_aligned_after_merge":sum(
            x["road_geometry_candidate_status"]=="candidate_consistent_with_KMZ" for x in merged),
        "GH_source_geometry_sections_still_unresolved":sum(
            x["road_geometry_candidate_status"]!="candidate_consistent_with_KMZ" for x in merged),
        "SIU_stops_audited_against_selected_roads":len(recalculated),
        "SIU_stops_over_45m_from_best_candidate_road":sum(
            x["GH_road_stop_assessment"]=="candidate_far_from_GH_bus_road" for x in recalculated),
        "old_first_pass_SIU_stops_over_45m":sum(
            x["GH_road_stop_assessment"]=="candidate_far_from_GH_bus_road" for x in stops),
        "selected_geometries_count":len(collection["features"]),
        "OSM_queries":0,"additional_GH_requests":0,
        "SIU_physical_stop_ids_changed":False,
        "GTFS_stop_sequence_changed":False,
        "actual_AMB_operator_road_service_verified":False,
    }
    (OUT/"summary.json").write_text(json.dumps(metric,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    doc=[
        "# AMB bronconforme wegengeometrie (geconsolideerde GraphHopper-buskandidaten)",
        "",
        "Uit de 352 eerste KMZ-gebonden GH-wegroutes worden uitsluitend de 21 hergetoetste",
        "wegengeometrieën ingevoegd die met dichtere KMZ-tussenpunten nu **voldoende overeenkomen**.",
        "Alle andere GH-wegroutes blijven uit de oorspronkelijke 950m-ankerrouteanalyse behouden.",
        "De 21 resterende afwijkingen blijven expliciet als onbevestigde brontrajecten gemarkeerd.",
        "",
        "## Resultaat","",
    ]
    for k,v in metric.items():
        if type(v) is int:doc.append("- "+k+": **"+str(v)+"**")
    doc+=["",
        "## Grenzen",
        "",
        "- Alle 9.020 SIU-fysieke haltebezoeken en hun stop_sequence blijven intact.",
        "- Een route die overeenkomt met GraphHopper is **niet noodzakelijk de door de vervoerder werkelijk gereden route**.",
        "- De resultaten zijn input voor een tweede controle van herhaalde wegpassages en bronhaltevolgorde.",
        "- Geen GTFS stop_times, route-trips, reistijden of publieke shapes worden overschreven.",
        "- Private GH via organisatievariabele; publieke API: https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md",
        "",
    ]
    (OUT/"summary.md").write_text("\n".join(doc),encoding="utf-8")
    print(json.dumps(metric,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
