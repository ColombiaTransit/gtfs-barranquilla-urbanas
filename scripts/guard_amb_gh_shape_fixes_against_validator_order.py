#!/usr/bin/env python3
"""Keep only GH shape fixes that also pass MobilityData stop order checks.

The 240m GH rerouting fixes many stop-to-shape warnings, but its first full
MobilityData run revealed new stop-order warnings on source route loops.
This optimizer starts with a safe set: all targeted improvements EXCEPT
those on routes with newly introduced order warnings. For those routes,
reintroduce each candidate section one by one, validating the complete
synthetic GTFS with the *real* MobilityData CLI each time.

A candidate is accepted ONLY if it reduces that route's shape-distance
warnings and does not increase route-level order warnings or GTFS ERRORS.
The original 9,020 SIU study stop visits and production GTFS never change.
"""
from __future__ import annotations
import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sources/amb/GH_combined_bus_road_geometry"
CANDIDATE=ROOT/"build/amb-gtfs-geometry-stop-aware-retry"
VALIDATOR_ORIGINAL=ROOT/"build/amb-gtfs-mobilitydata-PILOT-NOT-PUBLISHABLE/validator/report.json"
VALIDATOR_ALL=ROOT/"build/amb-gtfs-mobilitydata-STOP-AWARE-NOT-PUBLISHABLE/validator/report.json"
OUT=ROOT/"build/amb-gtfs-geometry-stop-aware-SAFE"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def occurrences(report,code):
    matching=[g for g in report["notices"] if g["code"]==code]
    if not matching:return []
    if len(matching)!=1:raise ValueError("Repeated validator notice group")
    group=matching[0]
    if int(group["totalNotices"])!=len(group.get("sampleNotices",[])):
        raise ValueError("Validator report is sampled")
    return group["sampleNotices"]

def grouped(report,code):
    return Counter(x["tripId"].removeprefix("QA_") for x in occurrences(report,code))

def write_csv(path,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def key(feature):
    p=feature["properties"]
    return p["trip_pattern_id"],int(p["section"])

def run_check(features,uid,jar,folder):
    road=folder/"road"
    road.mkdir(parents=True)
    (road/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":list(features.values())},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    shutil.copy2(BASE/"GH_full_route_bus_segment_alignment.csv",
                 road/"GH_full_route_bus_segment_alignment.csv")
    output=folder/"fixture"
    generated=subprocess.run(
        [sys.executable,str(ROOT/"archive/research_2026/scripts/build_amb_gtfs_geometry_validation_pilot.py"),
         "--road-dir",str(road),"--out",str(output)],
        cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=75
    )
    if generated.returncode!=0:
        raise RuntimeError("GTFS fixture generation failed with status "+str(generated.returncode)+
                           " "+generated.stderr[-500:])
    report_path=output/"validator"
    report_path.mkdir(parents=True,exist_ok=True)
    validated=subprocess.run(
        ["java","-Xmx3g","-jar",str(jar),
         "-i",str(output/"barranquilla_geometry_ONLY_TEST_NOT_FOR_PUBLICATION.zip"),
         "-o",str(report_path),"-c","co","-t","2"],
        cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=90
    )
    if validated.returncode!=0 or not (report_path/"report.json").is_file():
        raise RuntimeError("MobilityData validator failed during safe-shape selection")
    report=read(report_path/"report.json")
    errors=sum(int(x["totalNotices"]) for x in report["notices"] if x["severity"]=="ERROR")
    if errors>0:
        return False,float("inf"),float("inf"),errors
    far=grouped(report,"stop_too_far_from_shape")[uid]
    order=grouped(report,"stops_match_shape_out_of_order")[uid]
    return True,far,order,errors

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--jar",type=Path,required=True)
    parser.add_argument("--out",type=Path,default=OUT)
    parser.add_argument("--max-probes",type=int,default=100)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    original=read(BASE/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson")
    improved=read(CANDIDATE/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson")
    before=read(VALIDATOR_ORIGINAL)
    after=read(VALIDATOR_ALL)
    baseline_ord=grouped(before,"stops_match_shape_out_of_order")
    new_ord=grouped(after,"stops_match_shape_out_of_order")
    baseline_far=grouped(before,"stop_too_far_from_shape")
    new_far=grouped(after,"stop_too_far_from_shape")
    orig_map={key(f):f for f in original["features"]}
    proposed_map={key(f):f for f in improved["features"]}
    if len(orig_map)!=352 or len(proposed_map)!=352 or set(orig_map)!=set(proposed_map):
        raise ValueError("Expected matching 352 GH source road segments")
    modified={k for k,v in proposed_map.items()
              if v["properties"].get("road_candidate_source")=="MobilityData_targeted_240m_bus_retry"}
    new_order={trip for trip,count in new_ord.items() if count>baseline_ord[trip]}
    affected={key[0] for key in modified}
    if not modified or not new_order:
        raise ValueError("No candidate improvements / new order warnings to optimize")
    safe=dict(proposed_map)
    cautious=[k for k in modified if k[0] in new_order]
    for k in cautious:safe[k]=orig_map[k]
    current_far=Counter(baseline_far)
    for uid in affected-new_order:
        current_far[uid]=new_far[uid]
    decisions=[]
    attempts=0
    # Try highest-impact section first; consider only segments that were
    # actually accepted by the initial distance/official-corridor QA stage.
    rows=[]
    with (CANDIDATE/"section_targeted_GH_bus_retry_review.csv").open(
            newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    impact={(r["trip_pattern_id"],int(r["section_number"])):int(
        r["validator_stop_distance_notices_in_source_section"]) for r in rows}
    todo=sorted(cautious,key=lambda k:(-impact.get(k,0),k[0],k[1]))
    for k in todo:
        uid,n=k
        if attempts>=args.max_probes:
            decisions.append({"trip_pattern_id":uid,"section_number":n,
                              "candidate_GH_road_selected":"no",
                              "reason":"probe_limit_safe_rollback","source_stop_order_changed":"no"})
            continue
        attempts+=1
        safe[k]=proposed_map[k]
        with tempfile.TemporaryDirectory(prefix="GH-order-check-",dir=args.out) as folder:
            try:
                valid,far,order,errors=run_check(safe,uid,args.jar,Path(folder))
            except (RuntimeError,subprocess.TimeoutExpired) as exc:
                valid=False
                far=float("inf")
                order=float("inf")
                errors=-1
                print("probe "+str(attempts)+" source route="+uid+
                      " section="+str(n)+" rejected: runtime_error",flush=True)
        accepted=bool(valid and order<=baseline_ord[uid] and far<current_far[uid])
        if accepted:
            current_far[uid]=far
        else:
            safe[k]=orig_map[k]
        decisions.append({
            "trip_pattern_id":uid,
            "section_number":n,
            "source_MobilityData_far_warning_count_before":baseline_far[uid],
            "route_stop_too_far_count_if_candidate_tested":far if far!=float("inf") else "",
            "new_source_stop_order_warnings_if_selected":order if order!=float("inf") else "",
            "maximum_baseline_order_warnings_allowed":baseline_ord[uid],
            "candidate_GH_road_selected":"yes" if accepted else "no",
            "reason":"reduces_far_without_new_order" if accepted else "would_add_order_or_not_improve_far",
            "source_stop_order_changed":"no",
        })
        print("probe="+str(attempts)+"/"+str(min(len(todo),args.max_probes))+
              " "+uid+"#"+str(n)+
              " far="+str(far)+" order="+str(order)+
              " accepted="+str(accepted),flush=True)
    chosen_count=sum(k in modified and safe[k] is proposed_map[k] for k in orig_map)
    if chosen_count==0:
        raise ValueError("No road improvements were retained")
    output_geo={"type":"FeatureCollection",
                "features":[safe[key(f)] for f in original["features"]]}
    (args.out/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").write_text(
        json.dumps(output_geo,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    shutil.copy2(BASE/"GH_full_route_bus_segment_alignment.csv",
                 args.out/"GH_full_route_bus_segment_alignment.csv")
    if decisions:
        write_csv(args.out/"GH_reintroduced_road_candidates_under_order_guard.csv",decisions)
    summary={
        "original_MobilityData_route_order_warnings":sum(baseline_ord.values()),
        "unsafe_MobilityData_route_order_warnings":sum(new_ord.values()),
        "route_patterns_with_new_warnings_guarded":len(new_order),
        "original_GH_bus_road_sections":352,
        "initial_GH_road_sections_that_improved_stop_shape":len(modified),
        "initial_GH_road_sections_on_problem_routes":len(cautious),
        "individual_MobilityData_probe_runs":attempts,
        "stop_aware_road_sections_still_approved":chosen_count,
        "road_sections_reverted_for_order_safety":len(modified)-chosen_count,
        "GH_bus_sections_accepted_as_better_road_candidates":chosen_count,
        "source_GTFS_stop_sequence_unchanged":True,
        "actual_route_stop_service_confirmed":False,
        "unverified_GH_geometry_automatically_published":False,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
