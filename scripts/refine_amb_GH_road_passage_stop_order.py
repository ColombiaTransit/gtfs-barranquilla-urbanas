#!/usr/bin/env python3
"""Refine GH bus-stop order by matching each source stop to a POSSIBLE road pass.

Nearest-point projection on a whole 9km bus segment can select the *wrong*
pass when a route revisits the same street. This analysis enumerates all
spatially plausible projections to the GH bus road and uses an order-constrained
dynamic program (penalizing backward movement) to select a plausible chain.
A forced backwards jump is evidence for review, not an auto stop reorder.

No rerouting, no GTFS publication, no removal of SIU stops.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"sources/amb/full_GH_bus_geometry_quality"
STOPS=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
OUT=ROOT/"build/amb-full-route-refined-GH-order"
PROJECT=Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True)
NEAR_M=75.
CLUSTER_M=35.
BACKWARD_TOLERANCE_M=50.

def read(path):
    with path.open("r",newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write(path,rows,headers):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=headers,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def road_graph(line):
    points=list(line.coords)
    segments=[]
    prefixes=[]
    offset=0.
    for a,b in zip(points,points[1:]):
        seg=LineString((a,b))
        if seg.length<=1e-4:continue
        segments.append(seg)
        prefixes.append(offset)
        offset+=seg.length
    if not segments:return None
    return segments,prefixes,STRtree(segments),offset

def possibilities(p,road,expected):
    segs,prefixes,index,_=road
    projected=[]
    for idx in index.query(p.buffer(NEAR_M)):
        k=int(idx)
        seg=segs[k]
        distance=p.distance(seg)
        if distance>NEAR_M:continue
        position=prefixes[k]+seg.project(p)
        projected.append((position,distance))
    if not projected:return []
    projected.sort()
    clusters=[]
    for position,distance in projected:
        if not clusters or position-clusters[-1][-1][0]>CLUSTER_M:
            clusters.append([(position,distance)])
        else:clusters[-1].append((position,distance))
    out=[min(group,key=lambda xy:xy[1]*2+abs(xy[0]-expected)*.02)
         for group in clusters]
    # Keep candidate passes with close road location; prefer source chainage
    # expectation if more than 15 nearby road passes.
    return sorted(out,key=lambda v:(v[1]*2+abs(v[0]-expected)*.02))[:15]

def choose_monotone(groups):
    """DP minimizes nearest-street error and 9km segment backtracking penalty."""
    nodes=[]
    for i,entry in enumerate(groups):
        options=entry["options"]
        if not options:continue
        nodes.append((i,options,entry["expected"]))
    decisions={}
    if not nodes:return decisions
    dp=[]
    paths=[]
    for i,opts,expected in nodes:
        current=[]
        backlinks=[]
        for j,(pos,dist) in enumerate(opts):
            cost=2.0*dist+0.025*min(abs(pos-expected),4000)
            if not dp:
                current.append(cost)
                backlinks.append(-1)
            else:
                best_val=float("inf")
                best_index=-1
                prev_opts=nodes[len(dp)-1][1]
                for l,(prevpos,prevdist) in enumerate(prev_opts):
                    backwards=max(0,prevpos-pos-BACKWARD_TOLERANCE_M)
                    penalty=0.0 if backwards<=0 else 250.+backwards*2.5
                    total=dp[-1][l]+cost+penalty
                    if total<best_val:
                        best_val=total
                        best_index=l
                current.append(best_val)
                backlinks.append(best_index)
        dp.append(current)
        paths.append(backlinks)
    cursor=min(range(len(dp[-1])),key=lambda j:dp[-1][j])
    for n in range(len(nodes)-1,-1,-1):
        i,opts,expected=nodes[n]
        decisions[i]=(opts[cursor],len(opts))
        cursor=paths[n][cursor]
    return decisions

def main():
    global SOURCE, OUT
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,default=SOURCE)
    parser.add_argument("--out",type=Path,default=OUT)
    args=parser.parse_args()
    SOURCE=args.source
    OUT=args.out
    OUT.mkdir(parents=True,exist_ok=True)
    previous=read(SOURCE/"GH_stop_sequence_and_road_access_audit.csv")
    segments=read(SOURCE/"GH_full_route_bus_segment_alignment.csv")
    records=read(SOURCE/"GH_route_pattern_quality_register.csv")
    raw=json.loads((SOURCE/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").read_text(encoding="utf-8"))
    physical={x["stop_id"]:x for x in read(STOPS)}
    if len(previous)!=9020 or len(segments)!=352 or len(records)!=70:
        raise ValueError("Expected full 70-pattern GH QA with 352 segments and 9020 source visits")
    metrics={(s["trip_pattern_id"],int(s["segment_number"])):s for s in segments}
    geo={}
    for feat in raw["features"]:
        p=feat["properties"]
        key=(p["trip_pattern_id"],int(p["section"]))
        if key in geo:raise ValueError("Duplicated GraphHopper route segment")
        geo[key]=LineString([PROJECT.transform(*x[:2]) for x in feat["geometry"]["coordinates"]])
    if len(geo)!=352 or set(geo)!=set(metrics):
        raise ValueError("GraphHopper road segments and QA metrics do not match")
    bysegment=defaultdict(list)
    for r in previous:
        if r["SIU_physical_stop_id"] not in physical:
            raise ValueError("Unknown canonical SIU stop ID")
        bysegment[(r["trip_pattern_id"],int(r["GH_segment_number"]))].append(r)
    for rows in bysegment.values():
        rows.sort(key=lambda x:int(x["source_stop_sequence"]))
    output=[]
    priority=defaultdict(Counter)
    original_issues=0
    for key in sorted(metrics):
        segment=metrics[key]
        road_geom=geo[key]
        road=road_graph(road_geom)
        if road is None:raise ValueError("GraphHopper road has no usable edge")
        src_start=float(segment["KMZ_segment_start_m"])
        src_end=float(segment["KMZ_segment_end_m"])
        aligned=segment["road_geometry_candidate_status"]=="candidate_consistent_with_KMZ"
        group=bysegment[key]
        options=[]
        for r in group:
            p=physical[r["SIU_physical_stop_id"]]
            xy=Point(*PROJECT.transform(float(p["stop_lon"]),float(p["stop_lat"])))
            proportion=max(0.,min(1.,
                    (float(r["source_KMZ_chainage_m"])-src_start)/max(1.,src_end-src_start)))
            expected=road[3]*proportion
            opts=possibilities(xy,road,expected)
            options.append({"record":r,"options":opts,"expected":expected})
        decisions=choose_monotone(options)
        last=None
        for index,entry in enumerate(options):
            r=entry["record"]
            oldback=r["GH_stop_order_assessment"]=="GH_local_order_backwards_over_120m"
            if oldback:original_issues+=1
            choice=decisions.get(index)
            pos,dist=(choice[0] if choice else (None,None))
            count=choice[1] if choice else 0
            backwards=last is not None and pos is not None and pos+BACKWARD_TOLERANCE_M<last
            if pos is not None:last=pos
            if pos is None:
                review="no_GH_bus_road_pass_within_75m"
            elif backwards:
                review="road_order_backwards_unresolved"
            elif not aligned:
                review="road_route_deviates_from_KMZ_review"
            elif dist>45:
                review="stop_45_to_75m_from_GH_road"
            elif count>1:
                review="multiple_road_passages_order_resolved_tentative"
            else:
                review="road_order_compatible_tentative"
            if oldback and not backwards and pos is not None:
                priority[key[0]]["nearest_backtrack_resolved_or_nonsevere"]+=1
            if backwards:
                priority[key[0]]["backtrack_still_unresolved"]+=1
            if review not in ("road_order_compatible_tentative",
                              "multiple_road_passages_order_resolved_tentative"):
                priority[key[0]]["needs_review"]+=1
            if count>1:
                priority[key[0]]["multiple_possible_road_passes"]+=1
            priority[key[0]]["all_stops"]+=1
            output.append({
                **r,
                "refined_GH_projected_chainage_m":round(pos,1) if pos is not None else "",
                "refined_GH_stop_distance_to_bus_road_m":round(dist,1) if dist is not None else "",
                "possible_GH_road_passages_within_75m":count,
                "GH_nearest_projected_backtrack_in_original_QA":"yes" if oldback else "no",
                "refined_GH_road_order_backwards_over_50m":"yes" if backwards else "no",
                "GH_bus_road_geometry_KMZ_alignment":"consistent_candidate" if aligned else "needs_review",
                "refined_route_stop_assessment":review,
                "right_side_boarding_confirmed":"no",
                "operator_stop_service_confirmed":"no",
                "original_stop_sequence_changed":"no",
            })
    if len(output)!=9020 or sum(v["all_stops"] for v in priority.values())!=9020:
        raise ValueError("Lost stop visits during refined order audit")
    byroute={x["trip_pattern_id"]:x for x in records}
    detail=[]
    for uid,metrics_counter in priority.items():
        old=byroute[uid]
        detail.append({
            "trip_pattern_id":uid,
            "company":old["company"],
            "route_label":old["route_label"],
            "source_geometry":old["source_geometry"],
            "stop_visits":metrics_counter["all_stops"],
            "possible_multiple_GH_road_passages":metrics_counter["multiple_possible_road_passes"],
            "old_nearest_projection_backtracks_resolved_or_softened":metrics_counter["nearest_backtrack_resolved_or_nonsevere"],
            "refined_unresolved_order_backtracks":metrics_counter["backtrack_still_unresolved"],
            "stop_visits_requiring_GH_or_KMZ_review":metrics_counter["needs_review"],
            "source_sections_road_aligned":old["GH_sections_road_consistent"],
            "source_sections_checked":old["GH_sequential_sections_tested"],
            "research_priority":"P1_order_or_geometry_review" if metrics_counter["backtrack_still_unresolved"]>0
                or metrics_counter["needs_review"]>10 else
                "P2_partial_review" if metrics_counter["needs_review"]>0 else
                "P3_provisional_road_alignment",
            "GTFS_approved":"no",
        })
    detail.sort(key=lambda r:(r["research_priority"],-r["refined_unresolved_order_backtracks"],
                               -r["stop_visits_requiring_GH_or_KMZ_review"]))
    counts=Counter(x["refined_route_stop_assessment"] for x in output)
    # Map exactly the unresolved research exceptions; the physical SIU stop
    # catalog remains read-only and shared across all bus routes.
    resolved_classes={
        "road_order_compatible_tentative",
        "multiple_road_passages_order_resolved_tentative",
    }
    exceptions=[x for x in output if x["refined_route_stop_assessment"] not in resolved_classes]
    point_features=[]
    for x in exceptions:
        stop=physical[x["SIU_physical_stop_id"]]
        point_features.append({
            "type":"Feature",
            "properties":{
                "company":x["company"],
                "route_label":x["route_label"],
                "trip_pattern_id":x["trip_pattern_id"],
                "stop_sequence":x["source_stop_sequence"],
                "physical_SIU_stop_id":x["SIU_physical_stop_id"],
                "stop_name":x["stop_name"],
                "research_issue":x["refined_route_stop_assessment"],
                "GH_nearest_bus_road_distance_m":x["refined_GH_stop_distance_to_bus_road_m"],
                "GH_multiple_road_passages":x["possible_GH_road_passages_within_75m"],
                "confirmed_operator_stop":"no",
            },
            "geometry":{"type":"Point","coordinates":[float(stop["stop_lon"]),float(stop["stop_lat"])]},
        })
    (OUT/"GH_unresolved_stop_location_issues_REVIEW.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":point_features},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    jump_features=[x for x in point_features if
                   x["properties"]["research_issue"]=="road_order_backwards_unresolved"]
    (OUT/"GH_unresolved_stop_order_49_points.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":jump_features},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    mismatches=[]
    for feature in raw["features"]:
        p=feature["properties"]
        key=(p["trip_pattern_id"],int(p["section"]))
        if metrics[key]["road_geometry_candidate_status"]!="candidate_consistent_with_KMZ":
            mismatches.append(feature)
    (OUT/"GH_road_segments_differing_from_KMZ_REVIEW.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":mismatches},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")

    summary={
        "full_route_patterns_audited":len(records),
        "graphhopper_road_segments_reused_without_new_queries":len(segments),
        "physical_SIU_stop_visits_preserved":len(output),
        "old_nearest_projection_backtrack_signals":original_issues,
        "refined_unresolved_backwards_signals":sum(x["refined_GH_road_order_backwards_over_50m"]=="yes" for x in output),
        "old_backtrack_signals_resolved_or_softened":sum(x["GH_nearest_projected_backtrack_in_original_QA"]=="yes"
            and x["refined_GH_road_order_backwards_over_50m"]=="no" for x in output),
        "stops_with_multiple_graphhopper_road_passages":sum(
            int(x["possible_GH_road_passages_within_75m"])>1 for x in output),
        "refined_stop_assessment_counts":dict(counts),
        "road_order_compatible_tentative":counts["road_order_compatible_tentative"]+
            counts["multiple_road_passages_order_resolved_tentative"],
        "route_patterns_needing_priority_1_review":sum(r["research_priority"]=="P1_order_or_geometry_review"
                                                       for r in detail),
        "stop_review_point_features":len(point_features),
        "unresolved_stop_order_point_features":len(jump_features),
        "GH_bus_road_mismatch_sections_geojson":len(mismatches),
        "graphhopper_new_queries":0,
        "stop_times_or_trip_splitting_generated":False,
        "SIU_stops_created_or_removed":0,
        "GTFS_stop_sequence_changed":False,
        "actual_route_or_legal_stop_service_verified":False,
    }
    save_headers=list(output[0])
    write(OUT/"GH_refined_stop_sequence_passage_QA.csv",output,save_headers)
    write(OUT/"GH_route_review_priority_by_pattern.csv",detail,list(detail[0]))
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary_lines=[
        "# Betere controle van haltepassages bij terugkerende buswegtrajecten",
        "",
        "Alle routegeometrieën en stop_ID's komen uit bestaande SIU/KMZ-data plus de al berekende GraphHopper-busroutes.",
        "Een nearest-point projectie kan de verkeerde passage op een rondgaande weg kiezen. Daarom vergelijken",
        "we alle dichtbijliggende wegpassages en verkiezen een globale volgorde met een sterke straf voor achteruitlopen.",
        "Alle keuzes blijven voorlopige geografiebeoordelingen: geen hernummering, geen bewijs van haltebediening.",
        "",
        "## Resultaten",""
    ]
    for k,v in summary.items():
        if type(v) is int:summary_lines.append("- "+k+": **"+str(v)+"**")
    summary_lines.extend(["","## Classificaties",""])
    for k,v in sorted(counts.items()):
        summary_lines.append("- "+k+": "+str(v))
    summary_lines.extend([
        "",
        "## Volgende geometrische controles", "",
        "1. Beoordeel GH-buswegcorridors die afwijken van de originele AMB-KMZ; maak geen automatische concessieroutecorrecties.",
        "2. Beoordeel onopgeloste achteruitlopende stopprojecties op echte keerpunten, eenrichtingswegen en kruisingen.",
        "3. Beoordeel haltes boven 45 meter van de GH-busweg en bronroute (netwerk-/stopspecifiek), niet blind verwijderen.",
        "4. Zodra routegeometrie en haltevolgorde betrouwbaar genoeg zijn, kunnen reisduur en tripgrenzen apart komen.",
        "",
        "## Kaartbestanden voor broncontrole",
        "",
        "- GH_unresolved_stop_location_issues_REVIEW.geojson: alle haltebezoeken met nog onopgeloste weg-/volgordeafwijking.",
        "- GH_unresolved_stop_order_49_points.geojson: haltepunten waarbij de volgorde ook na mogelijke alternatieve wegpassages achteruitloopt.",
        "- GH_road_segments_differing_from_KMZ_REVIEW.geojson: buswegsegmenten die nog onvoldoende met het brontraject overeenstemmen.",
        "",
        "Bron: GraphHopper bus 11.1 via private organisatievariabele; publieke API: https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md",
        "Geen OSM-query's, nieuwe GraphHopper-query's of productie-GTFS-wijzigingen.",
        ""
    ])
    (OUT/"summary.md").write_text("\n".join(summary_lines),encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
