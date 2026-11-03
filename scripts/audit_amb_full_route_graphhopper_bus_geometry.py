#!/usr/bin/env python3
"""Audit AMB route geography + stop order with GraphHopper's bus road network.

Uses the official KMZ (historic ArcGIS fallback only when explicitly labeled)
and the cleaned v3 physical-SIU-stop visit order. Divides entire source lines
into consecutive sections, constrains GraphHopper bus routing through interior
KMZ points, and checks road alignment and stop order in EACH section.

No assumption about GTFS trip boundaries, schedules, or actual operator
boarding service. No OSM/Overpass requests. No modification of source staging
or gtfs/*. Private URL from ColombiaTransit Actions GRAPHHOPPER_URL only.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import substring

from map_missing_siu_route_stops_to_trips import (
    ROOT, ARCGIS_INVENTORY, COVERAGE, load_arcgis, read_csv,
    source_selection
)
from query_graphhopper_bus_gap_directions import Client

SOURCE=ROOT/"sources/amb/provisional_trip_stop_order_v3_clean"
PATTERNS=ROOT/"sources/amb/missing_siu_trip_stop_patterns/trip_patterns_MISSING_SIU_NO_TIMES.csv"
STOPS=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
ARCGIS=ROOT/"build/amb-arcgis-fallback/arcgis_routes_original.geojson"
OUT=ROOT/"build/amb-graphhopper-full-route-geometry-QA"
TO_METERS=Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True)
TO_WGS=Transformer.from_crs("EPSG:32618","EPSG:4326",always_xy=True)

def save_csv(path,rows,columns):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def metric_distance(p,geometry):
    return p.distance(geometry)

def coverage(source_line,road_line,interval_m=75.0,tolerance_m=50.0):
    if road_line.length<=0 or source_line.length<=0:
        return {"source_near_road":0.0,"road_near_source":0.0,
                "source_p90_deviation_m":float("inf"),
                "road_p90_deviation_m":float("inf")}
    def scan(a,b):
        n=max(4,min(450,math.ceil(a.length/interval_m)))
        ds=sorted(a.interpolate(a.length*i/n).distance(b) for i in range(n+1))
        return round(sum(d<=tolerance_m for d in ds)/len(ds),3),round(ds[int(.90*(len(ds)-1))],1)
    sr,sp=scan(source_line,road_line)
    rs,rp=scan(road_line,source_line)
    return {"source_near_road":sr,"road_near_source":rs,
            "source_p90_deviation_m":sp,"road_p90_deviation_m":rp}

def load_geometries(manifest):
    coverage_rows=[r for r in read_csv(COVERAGE)
                   if r["siu_coverage_status"]=="no_siu_route_stop_candidate"]
    if len(coverage_rows)!=60:
        raise ValueError("Expected 60 AMB source route variants requiring GIS fallback handling")
    arc=load_arcgis(ARCGIS)
    inv=read_csv(ARCGIS_INVENTORY)
    shapes={}
    sources={}
    for r in coverage_rows:
        source,lines,url,warning=source_selection(r,arc,inv)
        for part,shape in enumerate(lines,1):
            key=(r["company"],r["kmz_route_label"],str(part))
            if key in shapes:raise ValueError("Duplicate route geometry")
            shapes[key]=shape
            sources[key]={"source":source,"warning":warning,
                          "source_url":url,"company":r["company"],
                          "route_label":r["kmz_route_label"]}
    for uid,p in manifest.items():
        key=(p["company"],p["official_route_label"],p["geometry_component"])
        if key not in shapes:
            raise ValueError("Missing source geometry for "+uid)
    return shapes,sources

def divide(length,max_segment_m):
    count=max(1,math.ceil(length/max_segment_m))
    return [(length*i/count,length*(i+1)/count) for i in range(count)]

def request_points(line,spacing_m):
    n=max(1,min(14,math.ceil(line.length/spacing_m)))
    return [list(TO_WGS.transform(*line.interpolate(line.length*i/n).coords[0]))
            for i in range(n+1)]

def match_visits(visits,shape,sections,section_records,route_lines,canonical):
    matched=[]
    for r in visits:
        original_pos=float(r["shape_dist_traveled_candidate_m"])
        if original_pos<-1 or original_pos>shape.length+3:
            raise ValueError("Stop shape projection outside route line")
        segment_index=min(len(sections)-1,max(0,
            next((i for i,(start,end) in enumerate(sections)
                  if original_pos<=end+0.02),len(sections)-1)))
        region=section_records[segment_index]
        road=route_lines.get(segment_index)
        stop=canonical[r["stop_id"]]
        p=Point(*TO_METERS.transform(float(stop["stop_lon"]),float(stop["stop_lat"])))
        geom_at_pos=shape.interpolate(min(shape.length,max(0,original_pos)))
        official_distance=round(p.distance(geom_at_pos),1)
        if road is None:
            road_distance=""
            gh_projected=""
            label="GH_bus_road_unavailable"
        else:
            road_distance=round(p.distance(road),1)
            gh_projected=round(road.project(p),1)
            if road_distance<=25:
                label="candidate_near_GH_bus_road"
            elif road_distance<=45:
                label="candidate_needs_close_GH_review"
            else:
                label="candidate_far_from_GH_bus_road"
        matched.append({
            "trip_pattern_id":r["trip_pattern_id"],
            "company":r["company"],"route_label":r["official_route_label"],
            "source_stop_sequence":r["stop_sequence"],
            "SIU_physical_stop_id":r["stop_id"],
            "stop_name":r["stop_name"],
            "stop_visit_source_kind":r["source_row_kind"],
            "source_KMZ_chainage_m":round(original_pos,1),
            "source_KMZ_distance_to_stop_projected_point_m":official_distance,
            "GH_segment_number":segment_index+1,
            "GH_road_snapped_nearest_distance_m":road_distance,
            "GH_local_chainage_m":gh_projected,
            "GH_bus_segment_status":region["GH_bus_status"],
            "GH_segment_source_near_road_fraction":region["source_road_coverage_50m"],
            "GH_segment_road_near_source_fraction":region["road_source_coverage_50m"],
            "GH_road_stop_assessment":label,
            "GH_stop_order_assessment":"awaiting_segment_order_check",
            "actual_operator_stop_service_proven":"no",
            "source_stop_sequence_modified":"no",
        })
    # Compare GH local chainage ONLY within each distinct source section. Do not
    # globally project to a self-overlapping full route; it would map a later
    # pass back onto an earlier visit on the same physical street.
    groups=defaultdict(list)
    for r in matched:
        groups[int(r["GH_segment_number"])].append(r)
    for group in groups.values():
        previous=None
        for r in group:
            if r["GH_local_chainage_m"]=="":
                r["GH_stop_order_assessment"]="GH_road_unavailable"
                continue
            pos=float(r["GH_local_chainage_m"])
            if previous is not None and pos<previous-120:
                r["GH_stop_order_assessment"]="GH_local_order_backwards_over_120m"
            else:
                r["GH_stop_order_assessment"]="GH_local_order_compatible"
            previous=pos
    return matched

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=OUT)
    parser.add_argument("--max-patterns",type=int,default=70)
    parser.add_argument("--segment-km",type=float,default=9.0)
    parser.add_argument("--anchor-spacing-m",type=int,default=950)
    parser.add_argument("--timeout",type=int,default=30)
    args=parser.parse_args()
    if not 1<=args.max_patterns<=70 or not 2<=args.segment_km<=12 or not 400<=args.anchor_spacing_m<=1400:
        raise ValueError("Invalid safe GraphHopper route audit parameters")
    args.out.mkdir(parents=True,exist_ok=True)
    patterns={x["trip_pattern_id"]:x for x in read_csv(PATTERNS)}
    stops={x["stop_id"]:x for x in read_csv(STOPS)}
    visits=read_csv(SOURCE/"candidate_trip_stop_sequences_v3_CLEAN_NO_TIMES_NOT_GTFS.csv")
    if len(visits)!=9020 or len(patterns)<70:
        raise ValueError("Input v3 or route manifest changed since accepted source")
    bypattern=defaultdict(list)
    for r in visits:
        if r["stop_id"] not in stops:raise ValueError("Unknown physical SIU ID")
        bypattern[r["trip_pattern_id"]].append(r)
    for uid,part in bypattern.items():
        part.sort(key=lambda r:int(r["stop_sequence"]))
        if [int(x["stop_sequence"]) for x in part]!=list(range(1,len(part)+1)):
            raise ValueError("v3 stop_sequence is not contiguous")
        if any(float(a["shape_dist_traveled_candidate_m"])>
               float(b["shape_dist_traveled_candidate_m"])+2 for a,b in zip(part,part[1:])):
            raise ValueError("Source stop order is nonmonotonic")
    shapes,sources=load_geometries(patterns)
    client=Client(os.environ.get("GRAPHHOPPER_URL",""),timeout=args.timeout)
    info,status=client.info()
    if status!="ok":
        raise SystemExit("Private GraphHopper /info not available: "+status)
    if "bus" not in [p.get("name") for p in info.get("profiles",[]) if isinstance(p,dict)]:
        raise SystemExit("GraphHopper /info does not advertise the required bus profile")
    segment_rows=[]
    stop_rows=[]
    trip_rows=[]
    features=[]
    reviewed=0
    for uid,part in sorted(bypattern.items()):
        if reviewed>=args.max_patterns:break
        p=patterns[uid]
        key=(p["company"],p["official_route_label"],p["geometry_component"])
        source=shapes[key]
        info=sources[key]
        sections=divide(source.length,args.segment_km*1000)
        region_rows=[]
        region_lines={}
        for i,(start,end) in enumerate(sections):
            section=substring(source,start,end)
            if not isinstance(section,LineString) or section.length<0.5:
                raise ValueError("Invalid source route component slice")
            points=request_points(section,args.anchor_spacing_m)
            response,route_status=client.route(points)
            metric=coverage(section,response["geometry"]) if response else {}
            ratio=round(response["distance_m"]/section.length,3) if response else ""
            road_start_snapped=""
            road_end_snapped=""
            if response:
                region_lines[i]=response["geometry"]
                road_start_snapped=round(Point(*TO_METERS.transform(*points[0])).distance(
                    response["geometry"]),1)
                road_end_snapped=round(Point(*TO_METERS.transform(*points[-1])).distance(
                    response["geometry"]),1)
                features.append({
                    "type":"Feature",
                    "properties":{
                        "trip_pattern_id":uid,"company":p["company"],
                        "route_label":p["official_route_label"],
                        "component":p["geometry_component"],"section":i+1,
                        "source":info["source"],
                        "GH_profile":"bus",
                        "GH_road_candidate_only":True,
                        "road_near_source_fraction":metric["road_near_source"],
                        "source_near_road_fraction":metric["source_near_road"],
                    },
                    "geometry":{"type":"LineString","coordinates":response["coordinates"]}
                })
            aligned=(bool(response) and metric["source_near_road"]>=.72 and
                     metric["road_near_source"]>=.72 and
                     ratio>=.65 and ratio<=1.9 and
                     road_start_snapped<=60 and road_end_snapped<=60)
            region={
                "trip_pattern_id":uid,"company":p["company"],
                "route_label":p["official_route_label"],
                "geometry_component":p["geometry_component"],
                "segment_number":i+1,
                "KMZ_segment_start_m":round(start,1),
                "KMZ_segment_end_m":round(end,1),
                "KMZ_segment_length_m":round(section.length,1),
                "source_geometry":info["source"],
                "source_geometry_warning":info["warning"],
                "GH_bus_status":route_status,
                "GH_bus_road_distance_m":response["distance_m"] if response else "",
                "GH_road_to_KMZ_ratio":ratio,
                "source_road_coverage_50m":metric.get("source_near_road",""),
                "road_source_coverage_50m":metric.get("road_near_source",""),
                "KMZ_p90_m_to_GH_road":metric.get("source_p90_deviation_m",""),
                "GH_road_p90_m_to_KMZ":metric.get("road_p90_deviation_m",""),
                "start_waypoint_road_distance_m":road_start_snapped,
                "end_waypoint_road_distance_m":road_end_snapped,
                "road_geometry_candidate_status":"candidate_consistent_with_KMZ"
                     if aligned else "review_roads_or_source_route",
                "GH_sampled_KMZ_anchor_count":len(points),
                "official_route_is_confirmed_by_GH":"no",
            }
            segment_rows.append(region)
            region_rows.append(region)
        match=match_visits(part,source,sections,region_rows,region_lines,stops)
        stop_rows.extend(match)
        mismatch=sum(x["GH_road_stop_assessment"]=="candidate_far_from_GH_bus_road" for x in match)
        backwards=sum(x["GH_stop_order_assessment"]=="GH_local_order_backwards_over_120m" for x in match)
        failed=sum(x["GH_bus_status"]!="ok" for x in region_rows)
        aligned=sum(x["road_geometry_candidate_status"]=="candidate_consistent_with_KMZ" for x in region_rows)
        matched=sum(x["GH_road_stop_assessment"]=="candidate_near_GH_bus_road" for x in match)
        trip_status=(
            "road_geometry_candidate_with_order_review" if failed==0 and aligned==len(region_rows)
              and mismatch==0 and backwards==0 else
            "road_geometry_or_stop_order_needs_review"
        )
        trip_rows.append({
            "trip_pattern_id":uid,
            "company":p["company"],"route_label":p["official_route_label"],
            "source_geometry":info["source"],
            "source_geometry_warning":info["warning"],
            "source_component_count_for_this_pattern":1,
            "KMZ_component_length_m":round(source.length,1),
            "GH_sequential_sections_tested":len(region_rows),
            "GH_sections_road_consistent":aligned,
            "GH_sections_failed_routing":failed,
            "concept_v3_SIU_stop_visits":len(match),
            "GH_stops_within_25m_road":matched,
            "GH_stop_visits_beyond_45m_from_road":mismatch,
            "GH_stop_visits_showing_order_backward_over_120m":backwards,
            "road_and_order_research_status":trip_status,
            "trip_direction_or_turning_point_confirmed":"no",
            "operator_stop_service_confirmed":"no",
            "GTFS_ready":"no",
        })
        reviewed+=1
        print("pattern="+str(reviewed)+"/"+str(min(len(bypattern),args.max_patterns))+
              " "+uid+" segments="+str(len(region_rows))+
              " good_segments="+str(aligned)+
              " stop_over45m="+str(mismatch)+
              " backwards="+str(backwards),flush=True)
    if not trip_rows:
        raise ValueError("No source patterns were reviewed")
    save_csv(args.out/"GH_full_route_bus_segment_alignment.csv",segment_rows,list(segment_rows[0]))
    save_csv(args.out/"GH_stop_sequence_and_road_access_audit.csv",stop_rows,list(stop_rows[0]))
    save_csv(args.out/"GH_route_pattern_quality_register.csv",trip_rows,list(trip_rows[0]))
    (args.out/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":features},ensure_ascii=False,separators=(",",":"))+"\n",
        encoding="utf-8")
    count=Counter(x["road_and_order_research_status"] for x in trip_rows)
    summary={
        "GH_profile":"bus",
        "GH_version":str(info.get("version","")) if False else
            str(client.info_queries)+"_info_query_completed",
        "patterns_selected":len(trip_rows),
        "total_v3_patterns_available":len(bypattern),
        "GH_segment_route_requests":client.route_queries,
        "GH_sequential_sections":len(segment_rows),
        "GH_segments_succeeded":sum(x["GH_bus_status"]=="ok" for x in segment_rows),
        "GH_road_segments_with_source_alignment":sum(
            x["road_geometry_candidate_status"]=="candidate_consistent_with_KMZ" for x in segment_rows),
        "candidate_road_shapes_geojson_features":len(features),
        "v3_source_stop_visits_audited":len(stop_rows),
        "GH_stops_over_45m_from_bus_road":sum(
            x["GH_road_stop_assessment"]=="candidate_far_from_GH_bus_road" for x in stop_rows),
        "GH_stop_order_backwards_over_120m":sum(
            x["GH_stop_order_assessment"]=="GH_local_order_backwards_over_120m" for x in stop_rows),
        "route_pattern_statuses":dict(count),
        "GH_bus_oneway_compliant_road_net_hypothesis":True,
        "actual_2026_legal_bus_tracings_confirmed":False,
        "GTFS_trip_stop_sequences_changed":False,
        "new_stop_ids_created":0,
        "times_generated":0,
        "OSM_Overpass_queries":0,
        "endpoint_or_token_in_output":False,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    md=[
        "# AMB routegeometrie en haltevolgorde langs GraphHopper bus-wegennet",
        "",
        "GraphHopper wordt uitsluitend via ColombiaTransit GRAPHHOPPER_URL benaderd; de privé-URL staat niet in deze uitvoer.",
        "Officiële AMB-KMZ is de uitgangsroute; historisch ArcGIS blijft expliciet als onbevestigde fallback.",
        "De route is opgedeeld in opeenvolgende delen met KMZ-tussenpunten, zodat GH niet eenvoudig de busroute inkort.",
        "Elke route-passagescore vergelijkt **beide richtingen van de geometrieafstand** (bron→busweg en busweg→bron).",
        "SIU stop_ID en bronvolgorde blijven identiek; iedere passage wordt alleen op het passende routedeel beoordeeld.",
        "",
        "## Resultaten",""
    ]
    for k,v in summary.items():
        if type(v) is int:md.append("- "+k+": **"+str(v)+"**")
    md.extend([
        "",
        "## Belangrijk",
        "",
        "- GraphHopper maakt een bus-berijdbare kandidaat-shape; niet automatisch het werkelijk gereden concessietraject.",
        "- De segmenten blijven afzonderlijk opgeslagen. Bij terugkerende routes en rondritten wordt niet op een volledige zelf-overlappende lijn geprojecteerd.",
        "- Voor zover GH-segment en KMZ niet overeenstemmen, blijven officiële brongeometrie en stopvolgorde de onbevestigde referentie; geen overschrijven.",
        "- Bus haltebediening, triprichtingen en keerpunten zijn niet geverifieerd. Geen aankomst- of vertrektijden.",
        "",
        "## Onderzoeksbestanden",
        "",
        "- GH_full_route_bus_segment_alignment.csv — alle GH-bussegmenten versus KMZ, met afwijkingen.",
        "- GH_stop_sequence_and_road_access_audit.csv — elke SIU-stoppassage gekoppeld aan eigen bron- en GH-routedeel, plus lokale volgordecontrole.",
        "- GH_route_pattern_quality_register.csv — controleoverzicht per bronroutedeel / concept-patroon.",
        "- GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson — wegenvolgende geometrie om tegen de AMB-KMZ te leggen.",
        "",
        "Geen nieuwe fysieke stops, geen hernummering, geen publicatie-GTFS gewijzigd.",
        ""
    ])
    (args.out/"summary.md").write_text("\n".join(md),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
