#!/usr/bin/env python3
"""Reroute MobilityData stop-to-shape warnings only where evidence improves.

Uses official AMB KMZ (or explicitly historical ArcGIS fallback), the private
org GraphHopper bus profile, and the REAL MobilityData validator report.

For each impacted <=9 km GH bus-road section, try 2.0 km sub-sections with
~240m KMZ waypoints (9-11 per request), compare before/after stop distances
for *all* source stop visits in that section, check both-direction route
alignment and section join continuity. Promote only safer GH road candidates.

NO stop removal, stop reorder, fake bus-stop service assertion, or published
GTFS edit. Also exports exact 4 order notices as unmodified research issues.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
from collections import Counter,defaultdict
from pathlib import Path

from shapely.geometry import LineString, Point
from shapely.ops import substring
from pyproj import Transformer

from audit_amb_full_route_graphhopper_bus_geometry import (
    ROOT, PATTERNS, ARCGIS, TO_METERS, TO_WGS, load_geometries, coverage
)
from query_graphhopper_bus_gap_directions import Client

ORIGIN=ROOT/"sources/amb/GH_combined_bus_road_geometry"
STOP_QA=ROOT/"sources/amb/GH_combined_stop_order_QA/GH_refined_stop_sequence_passage_QA.csv"
SIU=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
DEFAULT_REPORT=ROOT/"build/amb-gtfs-mobilitydata-PILOT-NOT-PUBLISHABLE/validator/report.json"
DEFAULT_PILOT=ROOT/"build/amb-gtfs-mobilitydata-PILOT-NOT-PUBLISHABLE/gtfs_demo"
DEFAULT_OUT=ROOT/"build/amb-gtfs-geometry-stop-aware-retry"

def read_csv(path):
    with path.open("r",newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write_csv(path,records,headers):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=headers,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

def violations(report,code):
    matches=[x for x in report.get("notices",[]) if x["code"]==code]
    if not matches:return []
    if len(matches)!=1:raise ValueError("Repeated MobilityData notice group: "+code)
    notice=matches[0]
    samples=notice.get("sampleNotices",[])
    if int(notice["totalNotices"])!=len(samples):
        raise ValueError("MobilityData JSON report is sampled; must not silently drop issues")
    return samples

def segment_key(uid,n):
    return uid,int(n)

def as_line(feat):
    return LineString([TO_METERS.transform(float(v[0]),float(v[1]))
                       for v in feat["geometry"]["coordinates"]])

def coords_from_line(line):
    return [[round(lon,7),round(lat,7)]
            for lon,lat in (TO_WGS.transform(*p) for p in line.coords)]

def concat_roads(paths):
    coords=[]
    join_gaps=[]
    for line in paths:
        for i,p in enumerate(line.coords):
            if coords:
                prev=Point(coords[-1])
                gap=prev.distance(Point(p))
                if i==0:join_gaps.append(gap)
                if gap<0.15:continue
            coords.append(tuple(p))
    if len(coords)<2:return None,join_gaps
    return LineString(coords),join_gaps

def reroute_section(client,reference,subsection_km=2.0,spacing_m=240):
    length=reference.length
    parts=max(1,math.ceil(length/(subsection_km*1000)))
    routed=[]
    for i in range(parts):
        begin=length*i/parts
        end=length*(i+1)/parts
        section=substring(reference,begin,end)
        if not isinstance(section,LineString) or section.length<1:
            return None,"invalid_source_section",0
        # On each <=2km section, ensure all compulsory KMZ intermediate anchors
        # are more frequent than the prior 950m/450m (which used a 14-point cap).
        count=max(1,math.ceil(section.length/spacing_m))
        if count>14:return None,"too_many_waypoints",0
        anchors=[list(TO_WGS.transform(*section.interpolate(section.length*j/count).coords[0]))
                 for j in range(count+1)]
        gh,status=client.route(anchors)
        if status!="ok":return None,status,len(routed)
        routed.append(gh["geometry"])
    road,joints=concat_roads(routed)
    if road is None or max(joints,default=0)>40:
        return None,"disconnected_consecutive_bus_road_segments",len(routed)
    return road,"ok",len(routed)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--report",type=Path,default=DEFAULT_REPORT)
    parser.add_argument("--pilot",type=Path,default=DEFAULT_PILOT)
    parser.add_argument("--out",type=Path,default=DEFAULT_OUT)
    parser.add_argument("--max-affected-sections",type=int,default=200)
    parser.add_argument("--spacing-m",type=int,default=240)
    args=parser.parse_args()
    if not 150<=args.spacing_m<=300 or not 1<=args.max_affected_sections<=300:
        raise ValueError("Invalid route research limits")
    args.out.mkdir(parents=True,exist_ok=True)
    payload=json.loads(args.report.read_text(encoding="utf-8"))
    too_far=violations(payload,"stop_too_far_from_shape")
    out_of_order=violations(payload,"stops_match_shape_out_of_order")
    if not too_far:
        raise ValueError("Expected a real stop/shape warning list; cannot reroute from assumptions")
    stops={r["stop_id"]:r for r in read_csv(SIU)}
    pattern={r["trip_pattern_id"]:r for r in read_csv(PATTERNS)}
    original=read_csv(ORIGIN/"GH_full_route_bus_segment_alignment.csv")
    if len(original)!=352:raise ValueError("Expected the established 352 GH road sections")
    existing=json.loads((ORIGIN/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").read_text(encoding="utf-8"))
    features={}
    for feat in existing["features"]:
        prop=feat["properties"]
        key=segment_key(prop["trip_pattern_id"],prop["section"])
        if key in features:raise ValueError("Duplicate source GH section")
        features[key]=feat
    segments={segment_key(r["trip_pattern_id"],r["segment_number"]):r for r in original}
    if set(features)!=set(segments):raise ValueError("Source GH shape and metadata mismatch")
    sid_route={}
    oldvisits=read_csv(STOP_QA)
    for row in oldvisits:
        key=(row["trip_pattern_id"],int(row["source_stop_sequence"]))
        if key in sid_route:raise ValueError("Duplicate source stop passage")
        sid_route[key]=row
    if len(oldvisits)!=9020:raise ValueError("GTFS research source changed")
    pilot_st=read_csv(args.pilot/"stop_times.txt")
    sample_map={}
    sections_affected=Counter()
    for issue in too_far:
        uid=issue["tripId"].removeprefix("QA_")
        offset=int(issue["stopTimeCsvRowNumber"])-2
        if not 0<=offset<len(pilot_st):
            raise ValueError("MobilityData stop_times row number outside source")
        source=pilot_st[offset]
        if source["trip_id"]!=issue["tripId"] or source["stop_id"]!=issue["stopId"]:
            raise ValueError("MobilityData row number does not match generated GTFS")
        key=(uid,int(source["stop_sequence"]))
        if key not in sid_route:raise ValueError("No source route visit for "+str(key))
        orig=sid_route[key]
        if orig["SIU_physical_stop_id"]!=source["stop_id"]:
            raise ValueError("QA source ID differs from actual validator issue")
        region=segment_key(uid,orig["GH_segment_number"])
        sections_affected[region]+=1
        sample_map[key]=issue
    if len(sample_map)!=len(too_far):
        raise ValueError("Duplicate stop visit notice in MobilityData report")
    source_shape,metadata=load_geometries(pattern)
    byregion=defaultdict(list)
    for row in oldvisits:
        byregion[segment_key(row["trip_pattern_id"],row["GH_segment_number"])].append(row)
    for rows in byregion.values():
        rows.sort(key=lambda x:int(x["source_stop_sequence"]))
    client=Client(os.environ.get("GRAPHHOPPER_URL",""),timeout=30)
    server,info_status=client.info()
    if info_status!="ok":
        raise SystemExit("GraphHopper private /info unreachable: "+info_status)
    if "bus" not in [x.get("name") for x in server.get("profiles",[]) if isinstance(x,dict)]:
        raise SystemExit("GraphHopper does not advertise required bus profile")
    changes={}
    checks=[]
    all_affected=sorted(sections_affected,key=lambda k:(-sections_affected[k],k))
    if len(all_affected)>args.max_affected_sections:
        print("capacity: examining "+str(args.max_affected_sections)+" of "+
              str(len(all_affected))+" affected sections",flush=True)
    for index,key in enumerate(all_affected[:args.max_affected_sections],1):
        segment=segments[key]
        uid,n=key
        p=pattern[uid]
        original_key=(p["company"],p["official_route_label"],p["geometry_component"])
        base=source_shape[original_key]
        begin=float(segment["KMZ_segment_start_m"])
        end=float(segment["KMZ_segment_end_m"])
        source=substring(base,begin,end)
        oldroad=as_line(features[key])
        visits=byregion[key]
        locations=[Point(*TO_METERS.transform(
            float(stops[x["SIU_physical_stop_id"]]["stop_lon"]),
            float(stops[x["SIU_physical_stop_id"]]["stop_lat"]))) for x in visits]
        olddist=[z.distance(oldroad) for z in locations]
        old_far=sum(z>100 for z in olddist)
        newroad,status,queries=reroute_section(client,source,spacing_m=args.spacing_m)
        newdist=[z.distance(newroad) for z in locations] if newroad else []
        new_far=sum(z>100 for z in newdist) if newroad else -1
        new_warnings=sum((r["trip_pattern_id"],int(r["source_stop_sequence"])) in sample_map and d>100
                         for r,d in zip(visits,newdist)) if newroad else -1
        old_warnings=sum((r["trip_pattern_id"],int(r["source_stop_sequence"])) in sample_map
                         for r in visits)
        new_bad=sum(a<=100 and b>100 for a,b in zip(olddist,newdist)) if newroad else -1
        cov=coverage(source,newroad) if newroad else {}
        cover=min(cov.get("source_near_road",0),cov.get("road_near_source",0)) if newroad else 0
        ratio=newroad.length/source.length if newroad else None
        startgap=Point(source.coords[0]).distance(newroad) if newroad else None
        endgap=Point(source.coords[-1]).distance(newroad) if newroad else None
        # Only promote if all source stops improve or are no worse, source
        # corridor remains recognizably the same, and GH bus can route it.
        approve=bool(
            newroad is not None and
            new_far<old_far and
            new_bad==0 and
            cover>=0.68 and
            0.65<=ratio<=1.9 and
            startgap<=60 and endgap<=60 and
            new_warnings<old_warnings
        )
        if approve:
            changes[key]={
                "type":"Feature",
                "properties":{**features[key]["properties"],
                              "road_candidate_source":"MobilityData_targeted_240m_bus_retry",
                              "retry_preserved_all_existing_SIU_stop_ids":True,
                              "source_route_is_officially_verified":False},
                "geometry":{"type":"LineString","coordinates":coords_from_line(newroad)},
            }
        checks.append({
            "trip_pattern_id":uid,
            "company":p["company"],"route_label":p["official_route_label"],
            "section_number":n,
            "validator_stop_distance_notices_in_source_section":old_warnings,
            "source_stop_visits_in_section":len(visits),
            "old_stop_visits_above_100m_from_local_GH_section":old_far,
            "retry_stop_visits_above_100m_from_local_GH_section":new_far if newroad else "",
            "new_offroute_stops_introduced":new_bad if newroad else "",
            "source_KMZ_m":round(source.length,1),
            "old_GH_m":round(oldroad.length,1),
            "new_GH_m":round(newroad.length,1) if newroad else "",
            "new_GH_to_KMZ_ratio":round(ratio,3) if ratio else "",
            "new_GH_KMZ_bidirectional_coverage_min":round(cover,3),
            "GH_status":status,
            "GH_subsegment_requests_attempted":queries,
            "new_road_approved_as_RESEARCH_candidate":"yes" if approve else "no",
            "stop_time_sequence_modified":"no",
            "operator_stop_service_verified":"no",
        })
        print(f"section {index}/{min(len(all_affected),args.max_affected_sections)} "
              f"{uid} #{n}: flags={old_warnings} old_far={old_far} "
              f"new_far={new_far} candidate={'yes' if approve else 'no'}",flush=True)
    merged=[]
    for f in existing["features"]:
        k=segment_key(f["properties"]["trip_pattern_id"],f["properties"]["section"])
        merged.append(changes.get(k,f))
    merged_file=args.out/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson"
    merged_file.write_text(
        json.dumps({"type":"FeatureCollection","features":merged},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    # The generator uses the unchanged original source KMZ spans to convert
    # research stop positions to broad interpolated shape positions. The exact
    # shape_dist_traveled in stop_times was correctly omitted earlier.
    shutil.copy2(ORIGIN/"GH_full_route_bus_segment_alignment.csv",
                 args.out/"GH_full_route_bus_segment_alignment.csv")
    write_csv(args.out/"section_targeted_GH_bus_retry_review.csv",checks,list(checks[0]))
    changed=set(changes)
    # Assess actual stop-to-FULL shape distances, not only sectional distances.
    full=defaultdict(list)
    for f in merged:
        full[f["properties"]["trip_pattern_id"]].append(f)
    fullroads={}
    for uid,seq in full.items():
        seq.sort(key=lambda f:int(f["properties"]["section"]))
        points=[]
        for f in seq:
            points.extend(as_line(f).coords)
        fullroads[uid]=LineString(points)
    issues=[]
    for (uid,seq),issue in sorted(sample_map.items()):
        stop=stops[issue["stopId"]]
        pt=Point(*TO_METERS.transform(float(stop["stop_lon"]),float(stop["stop_lat"])))
        updated=round(pt.distance(fullroads[uid]),1)
        old=float(issue["geoDistanceToShape"])
        issues.append({
            "trip_pattern_id":uid,
            "stop_sequence":seq,
            "stop_id":issue["stopId"],
            "stop_name":issue.get("stopName",""),
            "old_MobilityData_distance_m":round(old,1),
            "new_GH_full_shape_distance_m":updated,
            "expected_MobilityData_100m_warning_resolved":"yes" if updated<=100 else "no",
            "source_route_segment":sid_route[uid,seq]["GH_segment_number"],
            "road_segment_replaced":"yes" if segment_key(uid,sid_route[uid,seq]["GH_segment_number"]) in changed else "no",
            "stop_was_removed_or_moved":"no",
            "needs_official_route_service_verification":"yes",
        })
    write_csv(args.out/"MobilityData_249_stop_shape_issues_before_after.csv",
              issues,list(issues[0]))
    # Don't rewrite any route direction just to silence a validator warning.
    order=[]
    for x in out_of_order:
        uid=x["tripId"].removeprefix("QA_")
        a=x["stopId1"];b=x["stopId2"]
        seqA=[r for r in oldvisits if r["trip_pattern_id"]==uid and r["SIU_physical_stop_id"]==a]
        seqB=[r for r in oldvisits if r["trip_pattern_id"]==uid and r["SIU_physical_stop_id"]==b]
        order.append({
            "trip_pattern_id":uid,"stop_id_1":a,"stop_name_1":x["stopName1"],
            "original_sequences_1":";".join(x["source_stop_sequence"] for x in seqA),
            "stop_id_2":b,"stop_name_2":x["stopName2"],
            "original_sequences_2":";".join(x["source_stop_sequence"] for x in seqB),
            "source_path_warning":"road_loop_nearest_match_may_be_ambiguous",
            "automatic_swap_or_drop":"no",
            "confirm_with_authoritative_SIU_order_and_GH_passage":"needed",
        })
    if order:
        write_csv(args.out/"MobilityData_4_source_stop_order_warnings_REVIEW_ONLY.csv",
                  order,list(order[0]))
    stats={
        "MobilityData_stop_shape_warnings_in_baseline":len(too_far),
        "MobilityData_stop_order_warnings_in_baseline":len(out_of_order),
        "source_GH_bus_road_sections":len(segments),
        "GH_bus_sections_impacted_by_stop_shape_warnings":len(all_affected),
        "GH_bus_sections_retried":len(checks),
        "GH_bus_sections_accepted_as_better_road_candidates":len(changes),
        "route_requests_through_private_GH_bus":client.route_queries,
        "baseline_MobilityData_249_warns_expected_resolved_after_reroute":sum(
            x["expected_MobilityData_100m_warning_resolved"]=="yes" for x in issues),
        "remaining_original_249_warnings_expected":sum(
            x["expected_MobilityData_100m_warning_resolved"]=="no" for x in issues),
        "number_of_SIU_physical_stops_deleted_or_moved":0,
        "number_of_source_stop_sequences_changed":0,
        "actual_SIU_stop_service_verified":False,
        "trip_boundaries_or_schedule_derived":False,
        "private_GraphHopper_endpoint_in_output":False,
    }
    (args.out/"summary.json").write_text(json.dumps(stats,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(stats,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
