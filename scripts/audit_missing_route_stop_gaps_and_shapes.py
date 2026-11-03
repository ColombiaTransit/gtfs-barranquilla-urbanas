#!/usr/bin/env python3
"""Audit >2 km stop gaps and multi-part KMZ/ArcGIS geometry without inventing stops.

Reuses outputs produced by map_missing_siu_route_stops_to_trips.py. All GPS stop
IDs stay unchanged; 'suggestions' are merely locations needing human/source
review, never extra selected stops or GTFS stop_times.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import Point

from map_missing_siu_route_stops_to_trips import (
    ROOT, ARCGIS_INVENTORY, COVERAGE, load_arcgis, read_csv, source_selection
)

BASE = ROOT / "build/amb-missing-route-stop-trip-patterns"
ARCGIS = ROOT / "build/amb-arcgis-fallback/arcgis_routes_original.geojson"
GAP_ALERT_M = 2000
INNER_MARGIN_M = 115
JOIN_REVIEW_M = 80
LONG_GEOMETRY_EDGE_M = 800

def export(name, rows, fields):
    with (BASE / name).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def f(row, key):
    return float(row[key])

def main():
    patterns = read_csv(BASE / "trip_patterns_MISSING_SIU_NO_TIMES.csv")
    stops = read_csv(BASE / "candidate_stop_order_per_trip_NO_TIMES.csv")
    rejected = read_csv(BASE / "all_projected_SIU_stop_candidates_WITH_DECISIONS.csv")
    missing = [row for row in read_csv(COVERAGE)
               if row["siu_coverage_status"] == "no_siu_route_stop_candidate"]
    by_id = {r["trip_pattern_id"]: r for r in patterns}
    by_stop = defaultdict(list)
    by_raw = defaultdict(list)
    for row in stops:
        if row["trip_pattern_id"] not in by_id:
            raise ValueError("Orphan selected stop: " + row["trip_pattern_id"])
        by_stop[row["trip_pattern_id"]].append(row)
    for row in rejected:
        if row["trip_pattern_id"] not in by_id:
            raise ValueError("Orphan projected candidate: " + row["trip_pattern_id"])
        by_raw[row["trip_pattern_id"]].append(row)

    gap_rows = []
    review = []
    gap_count = Counter()
    for pattern in patterns:
        uid = pattern["trip_pattern_id"]
        ordered = sorted(by_stop[uid], key=lambda r:int(r["stop_sequence"]))
        candidates = sorted(by_raw[uid], key=lambda r:f(r,"distance_along_shape_m"))
        for idx, (a, b) in enumerate(zip(ordered,ordered[1:]),1):
            start,end=f(a,"shape_dist_traveled_candidate_m"),f(b,"shape_dist_traveled_candidate_m")
            gap=end-start
            if gap < GAP_ALERT_M:
                continue
            interior = [r for r in candidates
                        if r["selected_for_model_trip"]=="no"
                        and start+INNER_MARGIN_M < f(r,"distance_along_shape_m") < end-INNER_MARGIN_M]
            within25 = [r for r in interior
                        if f(r,"distance_to_route_m")<=25 and
                        r["source_vs_shape_direction"]!="direction_conflict"]
            band25to35 = [r for r in interior
                          if 25<f(r,"distance_to_route_m")<=35 and
                          r["source_vs_shape_direction"]!="direction_conflict"]
            opposing = [r for r in interior
                        if r["source_vs_shape_direction"]=="direction_conflict"]
            if within25:
                kind="check_initial_selection_and_occurrence"
            elif band25to35:
                kind="nearby_existing_SIU_stops_outside_25m_limit"
            elif opposing:
                kind="only_opposite_direction_source_stops_nearby"
            else:
                kind="no_source_SIU_stop_on_this_corridor"
            key=(pattern["company"],pattern["official_route_label"])
            record={
                "company":key[0],"route_label":key[1],"trip_pattern_id":uid,
                "geometry_source":pattern["source_geometry"],
                "gap_index":idx,
                "from_stop_sequence":a["stop_sequence"],
                "to_stop_sequence":b["stop_sequence"],
                "from_stop_id":a["stop_id"],"to_stop_id":b["stop_id"],
                "distance_along_shape_start_m":round(start,1),
                "distance_along_shape_end_m":round(end,1),
                "gap_m":round(gap,1),
                "unselected_same_direction_candidates_within_25m":len(within25),
                "unselected_same_direction_candidates_25to35m":len(band25to35),
                "unselected_opposing_direction_candidates":len(opposing),
                "gap_review_class":kind,
                "model_stop_order_modified":"no",
                "new_stop_id_created":"no",
                "is_bus_stop_absence_proven":"no",
                "actual_operator_boarding_verified":"no",
            }
            gap_rows.append(record)
            gap_count[kind]+=1
            for group,flag in ((within25,"within_25m_not_selected"),
                               (band25to35,"25_to_35m_needs_manual_validation"),
                               (opposing,"opposite_direction_do_not_auto_add")):
                for r in sorted(group,key=lambda z:f(z,"distance_to_route_m"))[:5]:
                    review.append({
                        "company":key[0],"route_label":key[1],
                        "trip_pattern_id":uid,"gap_index":idx,
                        "gap_m":round(gap,1),
                        "existing_physical_SIU_stop_id":r["physical_stop_id"],
                        "stop_name":r["physical_stop_name"],
                        "stop_lat":r["stop_lat"],"stop_lon":r["stop_lon"],
                        "projection_along_shape_m":r["distance_along_shape_m"],
                        "distance_to_route_m":r["distance_to_route_m"],
                        "local_direction_assessment":r["source_vs_shape_direction"],
                        "reason_for_review":flag,
                        "added_to_model_trip":"no",
                        "real_stop_service_verified":"no",
                    })

    # Load authoritative KMZ route components or explicitly marked older ArcGIS
    # fallback exactly as the mapping step did (don't silently stitch fragments).
    arc = load_arcgis(ARCGIS)
    inv = read_csv(ARCGIS_INVENTORY)
    source_by_key = {}
    nodes = []
    edges = []
    geometry_jumps = []
    fragmentation = []
    for item in missing:
        key=(item["company"],item["kmz_route_label"])
        source,lines,url,warning=source_selection(item,arc,inv)
        source_by_key[key]=source
        selected=[p for p in patterns if
                  (p["company"],p["official_route_label"])==key]
        if len(selected)!=len(lines):
            raise ValueError("Geometry components changed since mapping for " + "/".join(key))
        out=[]
        for i,line in enumerate(lines,1):
            ends=(Point(line.coords[0]),Point(line.coords[-1]))
            out.append((i,line,ends))
            nodes.append({
                "company":key[0],"route_label":key[1],
                "component_index":i,"component_length_m":round(line.length,1),
                "first_lon_lat":str(tuple(round(x,7) for x in line.coords[0])),
                "last_lon_lat":str(tuple(round(x,7) for x in line.coords[-1])),
                "source_geometry":source,"source_warning":warning,
                "correct_component_order_known":"no",
            })
            # Route geometry coordinate jumps may signal missing intermediate
            # polyline vertices, not a true uninterrupted public road.
            coords=list(line.coords)
            jump=[((a[0]-b[0])**2+(a[1]-b[1])**2)**.5
                  for a,b in zip(coords,coords[1:])]
            for j,size in enumerate(jump,1):
                if size>=LONG_GEOMETRY_EDGE_M:
                    geometry_jumps.append({
                        "company":key[0],"route_label":key[1],
                        "component_index":i,"source":source,
                        "vertex_edge_number":j,"straight_edge_m":round(size,1),
                        "may_be_legitimate_straight_road":"yes",
                        "requires_graphhopper_or_road_network_review":"yes",
                    })
        if len(out)>1:
            for aidx,aline,(as_,ae) in out:
                for bidx,bline,(bs,be) in out:
                    if bidx<=aidx:continue
                    choices=[
                        ("end_to_start",ae.distance(bs)),
                        ("end_to_end_reverse_B",ae.distance(be)),
                        ("start_to_start_reverse_A",as_.distance(bs)),
                        ("start_to_end_reverse_A",as_.distance(be)),
                    ]
                    endtype,mind=min(choices,key=lambda v:v[1])
                    edges.append({
                        "company":key[0],"route_label":key[1],
                        "component_A":aidx,"component_B":bidx,
                        "smallest_endpoint_gap_m":round(mind,1),
                        "candidate_connection":endtype,
                        "connectable_within_80m":"yes" if mind<=JOIN_REVIEW_M else "no",
                        "automatic_shape_merge_approved":"no",
                        "bus_trip_order_verified":"no",
                    })
        if len(out)>1:
            edge_count=sum(e["connectable_within_80m"]=="yes" for e in edges
                           if (e["company"],e["route_label"])==key)
            fragmentation.append({
                "company":key[0],"route_label":key[1],
                "geometry_source":source,
                "source_warning":warning,
                "component_count":len(out),
                "near_endpoint_pair_links_80m":edge_count,
                "directed_component_sequence_verified":"no",
                "auto_merge_performed":"no",
                "next_step":"review_segment_order_and_roundtrip_against_official_shape",
            })

    if len(source_by_key)!=60:
        raise ValueError("All 60 missing-SIU route variants must be audited")
    # Determine routes with at least one large between-stop gap.
    gap_routes={(r["company"],r["route_label"]) for r in gap_rows}
    gap_count_by_route=Counter((r["company"],r["route_label"]) for r in gap_rows)
    max_by_route=defaultdict(float)
    for r in gap_rows:
        k=(r["company"],r["route_label"])
        max_by_route[k]=max(max_by_route[k],r["gap_m"])
    jump_by_route=Counter((r["company"],r["route_label"]) for r in geometry_jumps)
    summary={
        "source_route_variants":len(missing),
        "route_variants_with_geometric_stop_gaps_over_2km":len(gap_routes),
        "individual_stop_sequence_gaps_over_2km":len(gap_rows),
        "gap_classification_counts":dict(gap_count),
        "possible_nearby_SIU_candidates_for_review":len(review),
        "routes_with_geometry_edges_longer_than_800m":len(jump_by_route),
        "geometry_edges_longer_than_800m":len(geometry_jumps),
        "route_variants_with_multiple_shape_components":len(fragmentation),
        "component_near_endpoint_pairs_within_80m":sum(r["connectable_within_80m"]=="yes" for r in edges),
        "new_boarding_stops_or_stop_times_generated":0,
        "existing_trip_stop_orders_modified":False,
        "autoroute_component_stitching_performed":False,
    }
    # Full dataset and QA table support route-by-route progression without
    # keeping all candidate SVG/shape data in the top-level report.
    route_qa=[]
    for item in missing:
        k=(item["company"],item["kmz_route_label"])
        n=gap_count_by_route.get(k,0)
        large=max_by_route.get(k,0)
        n_frag=next((i["component_count"] for i in fragmentation if
                     (i["company"],i["route_label"])==k),1)
        flags=[]
        if n_frag>1:flags.append("fragmented_route_geometry")
        if large>5000:flags.append("gap_exceeds_5km")
        elif n:flags.append("gap_exceeds_2km")
        if jump_by_route[k]:flags.append("long_shape_coordinate_edges")
        if k==("SOBUSA","B18-4175 A") or k==("SOBUSA","B18-4175 B"):
            flags.append("official_B18_AB_lengths_suggest_source_label_swap")
        if item["source_url_collision"]=="yes":
            flags.append("official_AMB_source_URL_collision")
        route_qa.append({
            "company":k[0],"route_label":k[1],
            "route_shape_source":source_by_key[k],
            "gaps_over_2km":n,
            "largest_between_stop_shape_gap_m":round(large,1),
            "long_raw_geometry_edges_over_800m":jump_by_route[k],
            "component_count":n_frag,
            "priority":"P1_source_or_segment_problem" if n_frag>1 or large>5000 else
                       "P2_gap_review" if n else "P3_routine_geography_review",
            "qa_flags":";".join(flags),
            "model_ready_for_graphhopper_without_manual_validation":"no",
            "stop_service_is_confirmed":"no",
        })
    route_qa.sort(key=lambda r:(
        {"P1_source_or_segment_problem":0,"P2_gap_review":1,
         "P3_routine_geography_review":2}[r["priority"]],
        -r["largest_between_stop_shape_gap_m"],r["company"],r["route_label"]))
    if gap_rows:
        export("stop_gaps_over_2km_review.csv",gap_rows,list(gap_rows[0]))
    if review:
        export("existing_SIU_stop_candidates_inside_gaps_REVIEW_ONLY.csv",review,list(review[0]))
    if nodes:
        export("shape_component_endpoints.csv",nodes,list(nodes[0]))
    if edges:
        export("shape_fragment_join_candidates_REVIEW_ONLY.csv",edges,list(edges[0]))
    if geometry_jumps:
        export("shape_long_geometry_edge_QA.csv",geometry_jumps,list(geometry_jumps[0]))
    if fragmentation:
        export("fragmented_shape_route_summary.csv",fragmentation,list(fragmentation[0]))
    export("route_gap_priority_queue_60.csv",route_qa,list(route_qa[0]))
    (BASE/"gap_and_geometry_audit_summary.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report=[
        "# AMB: grote haltegaten en gefragmenteerde lijngeometrie",
        "",
        "Bron: 60 ontbrekende SIU-routevarianten, officiële KMZ en expliciete historische ArcGIS-fallback.",
        "**Een lange halteafstand bewijst géén ontbrekende halte.** Er kan een snelwegtraject zijn.",
        "Een nabije SIU-halte op een andere route bewijst bovendien niet dat de nieuwe lijn daar stopt.",
        "",
        "## Samenvatting","",
    ]
    for k,v in summary.items():
        if k!="gap_classification_counts":
            report.append("- "+k+": **"+str(v)+"**")
    report+=["","## Classificatie van gaten", ""]
    for k,v in sorted(gap_count.items(),key=lambda a:-a[1]):
        report.append("- "+k+": "+str(v))
    report+=["","## Gefragmenteerde routes",""]
    for x in fragmentation:
        report.append(
            "- "+x["company"]+" "+x["route_label"]+": "+
            str(x["component_count"])+" componenten, "+
            str(x["near_endpoint_pair_links_80m"])+" kandidaat-eindpuntverbindingen binnen 80 m; NIET automatisch samengevoegd")
    report+=["","## Volgende controles","",
        "1. Loop P1-routes na met KMZ/ArcGIS en officiële straattracés; controleer of lange lijnen echte doorgaande wegdelen zijn.",
        "2. Beoordeel bestaande SIU-haltes binnen grote gaten inclusief rijrichting; voeg deze niet zonder aanvullend bewijs automatisch toe.",
        "3. Bij gefragmenteerde shapes: inspecteer eventuele eindpuntverbindingen en de volgorde; verbind alleen met bronbewijs.",
        "4. Pas nadat route-trips en instapplaatsen gevalideerd zijn, GraphHopper voor reistijden gebruiken. Geen tijden berekend.",
        "",
    ]
    (BASE/"gap_and_geometry_audit_summary.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
