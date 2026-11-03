#!/usr/bin/env python3
"""Keep KMZ sparse-edge improvements only where MobilityData still agrees.

Compare actual baseline KMZ-first (1 stop-distance, 0 order, 0 ERROR) with
the partially GH-refined KMZ road proposal. The underlying GTFS files other
than shapes.txt MUST be byte-identical before the reports are produced.

This guard rejects whole route-pattern proposals with new stop distance,
stop order, or shape-related validator issues. If any new ERROR or unlocatable
new warning appears, it conservatively rejects all proposed changes.

The final safe research fixture is validated again in a separate CLI step.
No official KMZ or user stop data is edited.
"""
from __future__ import annotations
import argparse
import csv
import json
import shutil
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"build/amb-kmz-first-GH-fallback-research"
PROPOSED=ROOT/"build/amb-KMZ-dense-roads-research"
BASE_FEED=ROOT/"build/amb-KMZ-sparse-baseline-validation"
PROPOSED_FEED=ROOT/"build/amb-KMZ-sparse-proposal-validation"
OUT=ROOT/"build/amb-KMZ-road-refinement-safe"

def get(p):
    return json.loads(p.read_text(encoding="utf-8"))

def read_csv(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def save(p,rows):
    if not rows:return
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def fk(f):
    return f["properties"]["trip_pattern_id"],int(f["properties"]["section"])

def groups(report):
    return {r["code"]:r for r in report.get("notices",[])}

def total(report,severity):
    return sum(int(r["totalNotices"]) for r in report["notices"]
               if r["severity"]==severity)

def notice_key(n,code):
    uid=n.get("tripId","").removeprefix("QA_")
    if not uid and n.get("shapeId"):
        uid=n["shapeId"].removeprefix("GH_QA_")
    if not uid:
        return None
    if code=="stop_too_far_from_shape":
        return (uid,n.get("stopId"),n.get("stopTimeCsvRowNumber"))
    if code=="stops_match_shape_out_of_order":
        return (uid,n.get("stopId1"),n.get("stopId2"))
    # For other codes, GTFS row number may move when shapes.txt changes;
    # no stable identity. A new count for the same shape is a regression.
    return (uid,)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--base",type=Path,default=BASE)
    parser.add_argument("--proposed",type=Path,default=PROPOSED)
    parser.add_argument("--baseline-report",type=Path,
                        default=BASE_FEED/"validator/report.json")
    parser.add_argument("--proposed-report",type=Path,
                        default=PROPOSED_FEED/"validator/report.json")
    parser.add_argument("--out",type=Path,default=OUT)
    parser.add_argument("--rollback-all",action="store_true")
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    base=get(args.base/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson")
    proposed=get(args.proposed/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson")
    br=get(args.baseline_report)
    pr=get(args.proposed_report)
    basemap={fk(x):x for x in base["features"]}
    newmap={fk(x):x for x in proposed["features"]}
    if len(basemap)!=352 or set(basemap)!=set(newmap):
        raise ValueError("Expected identical 352 route segments between KMZ research variants")
    impacted={uid for (uid,sec),v in newmap.items()
              if v["properties"].get("accepted_local_sparse_edges",0)>0}
    changed_sections={k for k,v in newmap.items()
                      if v["properties"].get("accepted_local_sparse_edges",0)>0}
    summaries=read_csv(args.proposed/"KMZ_sparse_sections_review.csv")
    byuid=defaultdict(Counter)
    for row in summaries:
        byuid[row["trip_pattern_id"]]["sections"]+=1
        byuid[row["trip_pattern_id"]]["locally_accepted"]+=int(
            row["GH_locally_accepted_gap_count"])
    if not impacted:
        raise ValueError("No locally accepted GH bus road candidates to compare")
    bgroup=groups(br);pgroup=groups(pr)
    rejected=defaultdict(set)
    global_rollback_reasons=[]
    if args.rollback_all:global_rollback_reasons.append("explicit_failsafe_revert_all")
    if total(pr,"ERROR")>total(br,"ERROR"):
        global_rollback_reasons.append("new_GTFS_ERROR")
    bycode=[]
    for code in sorted(set(bgroup)|set(pgroup)):
        prev=bgroup.get(code)
        now=pgroup.get(code)
        old=int(prev["totalNotices"]) if prev else 0
        new=int(now["totalNotices"]) if now else 0
        change=new-old
        severity=(now or prev)["severity"]
        bycode.append({
            "notice_code":code,
            "severity":severity,
            "baseline":old,
            "proposed":new,
            "change":change,
        })
        if change<=0:continue
        if severity=="INFO":continue
        old_samples=prev.get("sampleNotices",[]) if prev else []
        new_samples=now.get("sampleNotices",[]) if now else []
        if len(new_samples)<new:
            global_rollback_reasons.append("validator_sample_truncated_"+code)
            continue
        if code in ("stop_too_far_from_shape","stops_match_shape_out_of_order"):
            oldids={notice_key(x,code) for x in old_samples}
            fresh=[x for x in new_samples if notice_key(x,code) not in oldids]
            for x in fresh:
                k=notice_key(x,code)
                if k and k[0] in impacted:
                    rejected[k[0]].add(code)
                else:
                    global_rollback_reasons.append("unlocated_new_"+code)
        else:
            # Warning counts about slight same-distance shape point changes
            # are still real new notices. Be conservative per shape pattern.
            for x in new_samples:
                k=notice_key(x,code)
                if k and k[0] in impacted:
                    rejected[k[0]].add("increased_"+code)
                elif k is None:
                    global_rollback_reasons.append("cannot_attribute_"+code)
    # Need independently catch new offroute / sequence instances even if a
    # different old warning vanished (total stays equal or decreases).
    for code in ("stop_too_far_from_shape","stops_match_shape_out_of_order"):
        prev=bgroup.get(code)
        now=pgroup.get(code)
        old_samples=prev.get("sampleNotices",[]) if prev else []
        new_samples=now.get("sampleNotices",[]) if now else []
        if now and len(new_samples)<int(now["totalNotices"]):
            global_rollback_reasons.append("validator_geometry_sample_truncated_"+code)
        oldids={notice_key(x,code) for x in old_samples}
        for item in new_samples:
            k=notice_key(item,code)
            if k not in oldids:
                if k and k[0] in impacted:
                    rejected[k[0]].add("new_"+code)
                else:
                    global_rollback_reasons.append("unattributed_"+code)
    if global_rollback_reasons:
        for uid in impacted:rejected[uid].update(global_rollback_reasons)
    selected={}
    decisions=[]
    for k in sorted(basemap):
        uid,sec=k
        is_changed=k in changed_sections
        keep_new=is_changed and uid not in rejected
        selected[k]=newmap[k] if keep_new else basemap[k]
        if is_changed:
            decisions.append({
                "trip_pattern_id":uid,
                "section_number":sec,
                "GH_locally_accepted_sparse_gaps":newmap[k]["properties"]["accepted_local_sparse_edges"],
                "all_locally_accepted_sparse_edges_for_pattern":byuid[uid]["locally_accepted"],
                "validator_guard_choice":"candidate_kept" if keep_new else "reverted_to_official_KMZ",
                "validator_guard_reason":"no_new_validator_notices" if keep_new
                    else ";".join(sorted(rejected[uid])),
                "SIU_physical_stop_ids_moved":"no",
                "source_stop_sequence_changed":"no",
            })
    safe={"type":"FeatureCollection",
          "features":[selected[fk(x)] for x in base["features"]]}
    (args.out/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").write_text(
        json.dumps(safe,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    shutil.copy2(args.base/"GH_full_route_bus_segment_alignment.csv",
                 args.out/"GH_full_route_bus_segment_alignment.csv")
    save(args.out/"KMZ_sparse_road_refinement_validator_guard.csv",decisions)
    save(args.out/"MobilityData_notice_difference_before_vs_unfiltered_refinement.csv",bycode)
    summary={
        "KMZ_source_sections_with_long_gaps":144,
        "GH_local_sparse_edge_candidates":sum(int(x["GH_locally_accepted_gap_count"]) for x in summaries),
        "KMZ_sections_locally_changed":len(changed_sections),
        "source_route_patterns_changed_before_validator":len(impacted),
        "source_route_patterns_rejected_by_validator":len(set(rejected)),
        "source_route_patterns_approved_by_validator":len(impacted-set(rejected)),
        "KMZ_sections_kept_with_road_densification":sum(
            x["validator_guard_choice"]=="candidate_kept" for x in decisions),
        "KMZ_sections_rolled_back_to_official":sum(
            x["validator_guard_choice"]=="reverted_to_official_KMZ" for x in decisions),
        "MobilityData_baseline_ERROR":total(br,"ERROR"),
        "MobilityData_unfiltered_proposal_ERROR":total(pr,"ERROR"),
        "MobilityData_baseline_WARNING":total(br,"WARNING"),
        "MobilityData_unfiltered_proposal_WARNING":total(pr,"WARNING"),
        "validator_global_rollback_reasons":sorted(set(global_rollback_reasons)),
        "source_SIU_stop_IDs_and_stop_order_modified":False,
        "official_AMB_KMZ_originally_modified":False,
        "actual_operator_stop_service_proven":False,
        "full_final_validator_recheck_required":True,
        "production_GTFS_modified":False,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
