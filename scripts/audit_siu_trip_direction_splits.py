#!/usr/bin/env python3
"""Flag SIU itinerary lists that may include both directions/return loops.

No automatic GTFS direction_id or split is made: a circular line can legitimately
be one trip. Proposed turning indices are geometric investigation anchors only.
"""
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"sources/siu/open_route_review/combined_20_route_stop_candidates_NO_TIMES.csv"
STOPS=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
OUT=ROOT/"build/gtfs-trip-timing-staging"

def read(path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write(path,rows,fields):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader();w.writerows(rows)

def metres(a,b):
    lat1,lon1=a;lat2,lon2=b
    dlat=math.radians(lat2-lat1);dlon=math.radians(lon2-lon1)
    q=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 12742000*math.asin(min(1,math.sqrt(q)))

def main():
    physical={r["stop_id"]:r for r in read(STOPS)}
    source=read(SOURCE)
    groups=defaultdict(list)
    for r in source:groups[r["siu_itinerary_uuid"]].append(r)
    out=[]
    for uid,rows in sorted(groups.items()):
        rows.sort(key=lambda r:int(r["siu_stop_sequence"]))
        points=[(float(physical[r["candidate_stop_id"]]["stop_lat"]),
                 float(physical[r["candidate_stop_id"]]["stop_lon"])) for r in rows]
        distances=[metres(points[0],p) for p in points]
        farthest_idx=max(range(len(points)),key=lambda i:distances[i])
        farthest=distances[farthest_idx]
        first_last=metres(points[0],points[-1])
        near_closed=first_last<=300 and farthest>=1500
        midpoint_ratio=round((farthest_idx+1)/len(points),3)
        named_directions=Counter()
        for r in rows:
            for item in re.findall(r"(?<![A-Z])(?:NS|SN|EO|OE)(?![A-Z])",r["siu_canonical_name"].upper()):
                named_directions[item]+=1
        opposite_axes=(named_directions["NS"]>0 and named_directions["SN"]>0) or (
            named_directions["EO"]>0 and named_directions["OE"]>0)
        flags=[]
        if near_closed:flags.append("returns_near_first_stop")
        if opposite_axes:flags.append("opposing_street_direction_markers")
        if len(points)>250:flags.append("large_itinerary_may_join_roundtrip")
        if farthest<500:flags.append("all_stops_near_start_possible_short_loop")
        out.append({
            "siu_itinerary_uuid":uid,
            "base_route_id_candidate":rows[0]["gtfs_route_id_candidate"],
            "stop_count":len(points),
            "first_to_last_stop_m":round(first_last,1),
            "maximum_distance_from_first_stop_m":round(farthest,1),
            "farthest_from_start_source_stop_sequence":farthest_idx+1,
            "fraction_of_route_stops_before_farthest_point":midpoint_ratio,
            "near_closed_route_possible":"yes" if near_closed else "no",
            "NS_marker_count":named_directions["NS"],
            "SN_marker_count":named_directions["SN"],
            "EO_marker_count":named_directions["EO"],
            "OE_marker_count":named_directions["OE"],
            "opposite_direction_markers_found":"yes" if opposite_axes else "no",
            "unverified_midpoint_turning_candidate":"yes" if near_closed and .2<=midpoint_ratio<=.8 else "no",
            "review_flags":";".join(flags),
            "actual_trip_direction_count_known":"no",
            "automatic_outbound_return_split_performed":"no",
            "GTFS_direction_id_assigned":"no",
            "GTFS_stop_times_publication_approved":"no",
        })
    write(OUT/"itinerary_direction_split_review.csv",out,list(out[0]))
    summary={
        "SIU_itineraries_checked":len(out),
        "possible_closed_itineraries":sum(x["near_closed_route_possible"]=="yes" for x in out),
        "itineraries_with_both_compass_direction_markers":sum(x["opposite_direction_markers_found"]=="yes" for x in out),
        "unverified_midpoint_turning_candidates":sum(x["unverified_midpoint_turning_candidate"]=="yes" for x in out),
        "auto_direction_split":0,
        "all_direction_assignments_require_review":True,
    }
    (OUT/"direction_split_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    lines=[
      "# SIU itineraries: review before treating one ordered itinerary as one physical trip",
      "",
      "The 20 frequency trip templates are RESEARCH TEMPLATES, not 20 verified single outbound journeys. "
      "A SIU itinerary may include outbound and inbound sections or a legal circular route.",
      "Do not infer direction_id 0/1 from A/B variants or split solely at a geographic farthest point.",
      "",
      f"- Checked: {len(out)} SIU itineraries",
      f"- Possible closed circuits (first-last <=300m and max radial distance >=1.5km): {summary['possible_closed_itineraries']}",
      f"- Both street-side direction abbreviations on at least one axis: {summary['itineraries_with_both_compass_direction_markers']}",
      f"- Midpoint turnaround review candidates: {summary['unverified_midpoint_turning_candidates']}",
      "",
      "The farthest-from-start point is an investigation candidate, not an automatically approved segment boundary. "
      "Compare with original route geometry and legal terminal(s), then manually approve trip patterns and calibrate "
      "duration separately per direction, time-of-day and applicable service.",
      "",
    ]
    (OUT/"direction_split_review.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
