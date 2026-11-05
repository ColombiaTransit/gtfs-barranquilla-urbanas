#!/usr/bin/env python3
"""Detailed geographic exception register for LAS PALMAS and VILLA CAROLINA ZOOLOGICO.
Never changes route mapping or legal status.
"""
import argparse,csv,json
from pathlib import Path
from collections import defaultdict
from shapely.geometry import Point
from pyproj import Transformer
from audit_siu_kmz_loop_aware import read,lines
from review_four_siu_kmz_routes import solve,norm
TARGET={"LAS PALMAS":"C5-4135","VILLA CAROLINA ZOOLOGICO":"B11-4166"}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo",type=Path,default=Path("."))
    ap.add_argument("--out",type=Path,default=Path("build/two-route-exceptions.csv"))
    ap.add_argument("--summary",type=Path,default=Path("build/two-route-summary.csv"))
    a=ap.parse_args();root=a.repo.resolve()
    scores=read(root/"sources/amb/kmz_stop_research/siu_crosswalk/all_siu_kmz_spatial_scores_NOT_CONFIRMED.csv")
    manifest=read(root/"sources/amb/kmz/manifest.csv")
    stops=read(root/"sources/siu/public_extract/siu_route_stop_sequences.csv")
    byid=defaultdict(list)
    for s in stops:
        if s.get("likely_test_itinerary")!="true":byid[s["siu_itinerary_uuid"]].append(s)
    for v in byid.values():v.sort(key=lambda x:int(x["siu_stop_sequence"]))
    lookup={(norm(m["company"]),m["route_label"]):m for m in manifest}
    proj=Transformer.from_crs(4326,32618,always_xy=True)
    exceptions=[];summary=[]
    for score in scores:
        name=score["siu_name"]
        if name not in TARGET or score["kmz_route_label"]!=TARGET[name]:continue
        m=lookup[(norm(score["kmz_company"]),score["kmz_route_label"])]
        sections=lines(root/"sources/amb/kmz"/m["geojson_path"],proj)
        source=byid[score["siu_itinerary_uuid"]]
        points=[Point(*proj.transform(float(s["stop_lon"]),float(s["stop_lat"]))) for s in source]
        candidates=[(i,rev,solve(points,line,rev,True)) for i,line in enumerate(sections,1) for rev in (False,True)]
        idx,rev,best=min(candidates,key=lambda x:(-x[2]["covered"],x[2]["backward_gt20m"]+x[2]["implausible_forward_gt_max500m_or_5x"],x[2]["backward_gt20m"]))
        line=sections[idx-1];chosen=best["_chosen"]
        uncovered=0;backward=0;jumps=0
        for i,(s,p) in enumerate(zip(source,points)):
            distance=round(line.distance(p),1)
            issues=[]
            if distance>50:issues.append("outside_50m");uncovered+=1
            if i==0:issues.append("first_stop")
            if i==len(points)-1:issues.append("last_stop")
            delta=None;straight=None
            if i and chosen[i] is not None and chosen[i-1] is not None:
                delta=round(chosen[i]-chosen[i-1],1)
                straight=round(points[i].distance(points[i-1]),1)
                if delta < -20:issues.append("backward_gt20m");backward+=1
                if delta>max(500,straight*5):issues.append("implausible_forward");jumps+=1
            if issues:
                exceptions.append({"siu_name":name,"kmz_candidate":TARGET[name],
                    "stop_sequence":s["siu_stop_sequence"],"stop_name":s.get("stop_name",""),
                    "stop_lon":s["stop_lon"],"stop_lat":s["stop_lat"],
                    "distance_to_kmz_m":distance,"chosen_along_m":round(chosen[i],1) if chosen[i] is not None else "",
                    "previous_to_current_along_delta_m":delta if delta is not None else "",
                    "previous_to_current_straight_m":straight if straight is not None else "",
                    "issue":";".join(issues),"assessment":"requires_manual_geographic_review"})
        summary.append({"siu_name":name,"kmz_candidate":TARGET[name],
            "total_stops":len(points),"outside_50m":uncovered,
            "backward_gt20m":backward,"implausible_forward":jumps,
            "first_stop_distance_m":round(line.distance(points[0]),1),
            "last_stop_distance_m":round(line.distance(points[-1]),1),
            "selected_orientation":"reverse" if rev else "forward",
            "geographic_mapping_status":"provisional_exception_open",
            "legal_mapping_confirmed":"no","gtfs_approved":"no"})
    if len(summary)!=2:raise SystemExit("Expected exactly two reviewed routes")
    for path,rows in ((a.out,exceptions),(a.summary,summary)):
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps({"summary":summary,"exception_rows":len(exceptions)},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
