#!/usr/bin/env python3
"""Focused review of ambiguous/low-coverage SIU-KMZ candidates. Research only."""
import argparse,csv,json
from collections import defaultdict
from pathlib import Path

def read(p):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write(p,rows,fields):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo",type=Path,default=Path("."));a=ap.parse_args()
    root=a.repo.resolve();folder=root/"build/siu_kmz_all_matches"
    overview=read(folder/"route_overview.csv");ranked=read(folder/"ranked_candidates.csv")
    scores=read(root/"sources/amb/kmz_stop_research/siu_crosswalk/all_siu_kmz_spatial_scores_NOT_CONFIRMED.csv")
    names={r["siu_itinerary_uuid"]:r["siu_name"] for r in scores if r.get("siu_name")}
    byid=defaultdict(list)
    for row in ranked:byid[row["siu_itinerary_uuid"]].append(row)
    output=[];summary=[]
    for row in overview:
        uid=row["siu_itinerary_uuid"];cov=float(row["best_coverage_50_pct"])
        if row["status"]!="ambiguous" and cov>=90:continue
        candidates=sorted(byid[uid],key=lambda x:(int(x["rank"]),x["kmz_route_label"]))
        first=candidates[0] if candidates else None
        for c in candidates:
            if int(c["rank"])>5:continue
            coverage=float(c["coverage_50_pct"])
            if first and coverage<float(first["coverage_50_pct"])-10:continue
            issue=("low_coverage_and_ambiguous" if row["status"]=="ambiguous" and cov<90 else
                   "ambiguous_candidates" if row["status"]=="ambiguous" else "low_coverage")
            # Geometric coincidence cannot establish direction or variant identity.
            recommendation=("review_loop_direction" if c["kmz_route_label"].startswith(("PT4","PT5")) else
                            "compare_variant_geometry_and_source" if c["kmz_route_label"].startswith(("PT1","PT2","A16","B13","C9","C18")) else
                            "inspect_unmatched_stop_clusters")
            output.append(dict(siu_itinerary_uuid=uid,siu_name=names.get(uid,""),
                siu_stop_count=row["siu_stop_count"],issue=issue,kmz_company=c["kmz_company"],
                kmz_route_label=c["kmz_route_label"],candidate_rank=c["rank"],
                coverage_50_pct=c["coverage_50_pct"],sequence_coverage_pct=c["sequence_coverage_pct"],
                orientation=c["orientation"],is_ring=c.get("is_ring",""),
                ring_wrap_count=c.get("ring_wrap_count",""),
                sequence_violations=c.get("sequence_violations",""),
                backward_gt20m=c["backward_gt20m"],
                implausible_forward=c["implausible_forward"],recommendation=recommendation,
                operational_mapping_status="pending_geographic_review",
                legal_confirmation_required="no"))
        summary.append(dict(siu_itinerary_uuid=uid,siu_name=names.get(uid,""),
            stop_count=row["siu_stop_count"],best_kmz=row["best_kmz"],
            coverage_50_pct=row["best_coverage_50_pct"],review_reason=row["status"],
            candidate_count=len([x for x in output if x["siu_itinerary_uuid"]==uid])))
    write(folder/"focused_review_candidates.csv",output,list(output[0]) if output else ["siu_itinerary_uuid"])
    write(folder/"focused_review_routes.csv",summary,list(summary[0]) if summary else ["siu_itinerary_uuid"])
    print(json.dumps({"routes_requiring_review":len(summary),"candidate_rows":len(output),
      "legal_confirmation_required":False,"review_routes":[{"name":r["siu_name"],"best_kmz":r["best_kmz"],
      "coverage":r["coverage_50_pct"]} for r in summary]},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
