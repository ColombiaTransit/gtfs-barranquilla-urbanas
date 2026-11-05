#!/usr/bin/env python3
"""Four disputed SIU->AMB KMZ matches: inspect directional path distances.

Research-only. Multiple projections and loops remain ambiguous. Never changes
GTFS routes, legal register, shapes or stop_times.
"""
import argparse,csv,json,statistics,sys
from pathlib import Path
from collections import defaultdict
from pyproj import Transformer
from shapely.geometry import Point
from audit_siu_kmz_loop_aware import read,lines,occurrences

TARGETS={
 "LAS PALMAS":"C5-4135",
 "VILLA CAROLINA ZOOLOGICO":"B11-4166",
 "ROJA RIOMAR":"B14-4174",
 "SOLEDAD CALLE 84":"A10-4114 B",
}
def norm(s):
    return "".join(c for c in str(s).upper() if c.isalnum()).replace("TRANSPORTESMONTERREY","MONTERREY")

def solve(points,line,reverse,include_trace=False):
    choices=occurrences(points,line,buffer_m=50,max_options=20)
    # State transitions score path distance against straight-line stop distance.
    # Strongly penalize backward travel and unrealistic long forward jumps.
    positions=[[(line.length-p if reverse else p,d) for p,d in opts] for opts in choices]
    # Closed rings can cross the geometry origin once. Duplicate each position
    # into a second lap so a valid cyclic sequence stays monotonic.
    is_ring=Point(line.coords[0]).distance(Point(line.coords[-1]))<=50
    if is_ring:
        positions=[sorted(opts+[(p+line.length,d) for p,d in opts]) for opts in positions]
    blocks=[];block=[]
    for i,opts in enumerate(positions):
        if opts:block.append(i)
        elif block:blocks.append(block);block=[]
    if block:blocks.append(block)
    chosen=[None]*len(points)
    for block in blocks:
        costs=[d for _,d in positions[block[0]]]
        parents=[[-1]*len(costs)]
        for prev_i,i in zip(block,block[1:]):
            straight=points[prev_i].distance(points[i])
            new=[];parent=[]
            for pos,d in positions[i]:
                transitions=[]
                for j,(old,_) in enumerate(positions[prev_i]):
                    delta=pos-old
                    # Not a trip planner: only test monotonicity and
                    # displacement plausibility, allowing detours.
                    backward_penalty=1000+10*abs(delta) if delta < -20 else 0
                    excessive_forward=max(0,delta-max(500,straight*5))*2
                    shortfall=max(0,straight-delta-80)*2
                    transitions.append(costs[j]+d+backward_penalty+excessive_forward+shortfall)
                j=min(range(len(transitions)),key=transitions.__getitem__)
                new.append(transitions[j]);parent.append(j)
            costs=new;parents.append(parent)
        j=min(range(len(costs)),key=costs.__getitem__)
        for k in range(len(block)-1,-1,-1):
            i=block[k];chosen[i]=positions[i][j][0]
            j=parents[k][j]
    ratios=[];excessive=0;backwards=0;total=0;distances=[]
    for i in range(len(chosen)-1):
        if chosen[i] is None or chosen[i+1] is None:continue
        total+=1
        delta=chosen[i+1]-chosen[i]
        straight=points[i].distance(points[i+1])
        distances.append(round(delta,1))
        if delta < -20:backwards+=1
        if delta>max(500,straight*5):excessive+=1
        if straight>30 and delta>=0:ratios.append(delta/straight)
    first=next((round(p,1) for p in chosen if p is not None),None)
    last=next((round(p,1) for p in reversed(chosen) if p is not None),None)
    result={"direction":"reverse" if reverse else "forward",
        "covered":sum(p is not None for p in chosen),"pairs":total,
        "backward_gt20m":backwards,"implausible_forward_gt_max500m_or_5x":excessive,
        "median_path_to_direct_ratio":round(statistics.median(ratios),2) if ratios else "",
        "first_along_m":first,"last_along_m":last,
        "first_stop_to_shape_m":round(points[0].distance(line),1),
        "last_stop_to_shape_m":round(points[-1].distance(line),1),
        "ambiguous_stops":sum(len(x)>1 for x in choices),
        "is_ring":is_ring,
        "ring_wrap_count":sum(1 for a,b in zip(chosen,chosen[1:]) if a is not None and b is not None and a<line.length<=b) if is_ring else 0,
        "sequence_violations":backwards+excessive,
        "section_length_m":round(line.length,1)}
    if include_trace:result["_chosen"]=chosen
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,default=Path("."))
    p.add_argument("--out",type=Path,default=Path("build/siu-kmz-four-route-review.csv"))
    args=p.parse_args();root=args.repo.resolve()
    manifest=read(root/"sources/amb/kmz/manifest.csv")
    scores=read(root/"sources/amb/kmz_stop_research/siu_crosswalk/all_siu_kmz_spatial_scores_NOT_CONFIRMED.csv")
    stops=read(root/"sources/siu/public_extract/siu_route_stop_sequences.csv")
    by_it=defaultdict(list)
    for row in stops:
        if row.get("likely_test_itinerary")!="true":by_it[row["siu_itinerary_uuid"]].append(row)
    for g in by_it.values():g.sort(key=lambda x:int(x["siu_stop_sequence"]))
    lookup={(norm(m["company"]),m["route_label"]):m for m in manifest}
    proj=Transformer.from_crs(4326,32618,always_xy=True)
    out=[]
    for score in scores:
        name=score["siu_name"]
        if name not in TARGETS or score["kmz_route_label"]!=TARGETS[name]:continue
        m=lookup[(norm(score["kmz_company"]),score["kmz_route_label"])]
        path=root/"sources/amb/kmz"/m["geojson_path"]
        sections=lines(path,proj)
        points=[Point(*proj.transform(float(s["stop_lon"]),float(s["stop_lat"]))) for s in by_it[score["siu_itinerary_uuid"]]]
        results=[(section_id,solve(points,line,reverse)) for section_id,line in enumerate(sections,1) for reverse in (False,True)]
        # Compare both directions; choose by coverage then violations.
        section_id,best=min(results,key=lambda z:(-z[1]["covered"],z[1]["backward_gt20m"]+z[1]["implausible_forward_gt_max500m_or_5x"],z[1]["backward_gt20m"],z[1]["ambiguous_stops"]))
        out.append({"siu_name":name,"siu_uuid":score["siu_itinerary_uuid"],
            "old_gis_code":score["prior_GIS_base_code_candidate"],
            "kmz_candidate":score["kmz_route_label"],
            "operator":score["kmz_company"],"coverage50_pct":score["share_of_SIU_stops_within_50m_pct"],
            "section_count":len(sections),"chosen_section":section_id,**best,
            "source_url_collision":score["official_source_KMZ_URL_collision"],
            "decision":"retain_geographic_candidate_pending_legal_and_sequence_review",
            "legal_route_confirmed":"no","gtfs_approved":"no"})
    if len(out)!=4:raise SystemExit(f"Expected 4 distinct SIU routes; found {len(out)}")
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
