#!/usr/bin/env python3
"""Rank route source coverage for a seven-pattern review queue; no automatic approval."""
import csv,json,argparse
from pathlib import Path
def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write(path,rows,fields):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,default=Path("build/gtfs-source-consolidation/route_source_consolidation.csv"));p.add_argument("--out",type=Path,default=Path("build/gtfs-source-consolidation"));a=p.parse_args()
    data=read(a.input);out=[]
    for x in data:
        freq=x["headway_status"]=="candidate_with_values"
        siu=int(x["siu_candidate_count"])>0
        shape=int(x["shape_pattern_count"])>0
        kmz=int(x["kmz_2026_pattern_count"])>0
        multi=int(x["shape_pattern_count"])>1
        score=4*freq+3*siu+3*shape+kmz-2*multi
        blockers=[]
        if not freq:blockers.append("headway_missing_or_ambiguous")
        if not siu:blockers.append("siu_itinerary_missing")
        if not shape:blockers.append("shape_pattern_missing")
        if multi:blockers.append("multiple_shape_patterns_need_review")
        if int(x["siu_confirmed_count"])==0:blockers.append("siu_mapping_not_final")
        blockers.append("calendar_and_trip_times_not_confirmed")
        out.append({"gtfs_route_id":x["gtfs_route_id"],"route_short_name":x["route_short_name"],"agency_id":x["agency_id"],"score":score,"headway_candidate":str(freq).lower(),"siu_candidate":str(siu).lower(),"shape_candidate":str(shape).lower(),"kmz_2026_candidate":str(kmz).lower(),"siu_candidate_uuids":x["siu_candidate_uuids"],"shape_pattern_ids":x["shape_pattern_ids"],"review_blockers":";".join(blockers),"approved_for_publication":"no"})
    out.sort(key=lambda x:(-x["score"],x["gtfs_route_id"]))
    complete=[x for x in out if x["headway_candidate"]=="true" and x["siu_candidate"]=="true" and x["shape_candidate"]=="true"]
    shortlist=complete[:7]
    a.out.mkdir(parents=True,exist_ok=True)
    fields=list(out[0])
    write(a.out/"route_pattern_review_ranking.csv",out,fields)
    write(a.out/"first_seven_review_queue.csv",shortlist,fields)
    summary={"total_routes":len(out),"all_three_source_candidates":len(complete),"selected_for_review":len(shortlist),"selection_rule":"Headway + SIU itinerary candidate + shape candidate; ranked by source coverage, not final route confirmation","publication_approved":False}
    (a.out/"first_seven_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    (a.out/"first_seven_summary.md").write_text("# Eerste zeven routepatronen: reviewqueue\n\n"+ "\n".join(f"- {k}: {v}" for k,v in summary.items())+"\n\n"+"\n".join(f"- {x['gtfs_route_id']}: {x['review_blockers']}" for x in shortlist)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
