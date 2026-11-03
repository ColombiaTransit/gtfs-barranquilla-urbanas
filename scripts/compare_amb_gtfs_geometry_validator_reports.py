#!/usr/bin/env python3
"""Compare actual MobilityData baseline and new stop-aware GH-shape reports.

Avoid claiming success from a hypothetical geometric estimate: use second
real validator invocation. Issue lists retain original stop IDs and any
out-of-order warning, without deleting or rearranging any source stop visit.
"""
import argparse
import csv
import json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"build/amb-gtfs-mobilitydata-PILOT-NOT-PUBLISHABLE/validator/report.json"
NEW=ROOT/"build/amb-gtfs-mobilitydata-STOP-AWARE-NOT-PUBLISHABLE/validator/report.json"
CHANGE=ROOT/"build/amb-gtfs-geometry-stop-aware-retry/summary.json"
OUT=ROOT/"build/amb-GTFS-MobilityData-geography-comparison"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def notices(report,code):
    groups=[n for n in report["notices"] if n["code"]==code]
    if not groups:return []
    if len(groups)!=1:raise ValueError("Duplicate notice grouping")
    if int(groups[0]["totalNotices"])!=len(groups[0].get("sampleNotices",[])):
        raise ValueError("Full MobilityData issue details absent; do not lose warnings")
    return groups[0]["sampleNotices"]

def counts(report):
    out=Counter()
    for n in report["notices"]:
        out[n["code"]]+=int(n["totalNotices"])
    return out

def write(path,rows,columns):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--base",type=Path,default=BASE)
    parser.add_argument("--new",type=Path,default=NEW)
    parser.add_argument("--retry",type=Path,default=CHANGE)
    parser.add_argument("--out",type=Path,default=OUT)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    baseline=read(args.base)
    updated=read(args.new)
    effort=read(args.retry)
    bs=counts(baseline)
    ns=counts(updated)
    before_far=notices(baseline,"stop_too_far_from_shape")
    after_far=notices(updated,"stop_too_far_from_shape")
    before_order=notices(baseline,"stops_match_shape_out_of_order")
    after_order=notices(updated,"stops_match_shape_out_of_order")
    basetotal=Counter()
    newtotal=Counter()
    for s in baseline["notices"]:basetotal[s["severity"]]+=int(s["totalNotices"])
    for s in updated["notices"]:newtotal[s["severity"]]+=int(s["totalNotices"])
    rows=[]
    for code in sorted(set(bs)|set(ns)):
        severity=next((r["severity"] for r in updated["notices"] if r["code"]==code),
                      next((r["severity"] for r in baseline["notices"] if r["code"]==code),"UNKNOWN"))
        rows.append({"notice_code":code,"severity":severity,
                     "before":bs[code],"after":ns[code],"difference":ns[code]-bs[code]})
    write(args.out/"MobilityData_notice_counts_before_after.csv",
          rows,["notice_code","severity","before","after","difference"])
    all_far=[]
    by_pattern=defaultdict(Counter)
    for v in after_far:
        uid=v["tripId"].removeprefix("QA_")
        by_pattern[uid]["remaining_shape_warnings"]+=1
        all_far.append({
            "trip_pattern_id":uid,
            "trip_id":v["tripId"],
            "stop_id":v["stopId"],
            "stop_name":v["stopName"],
            "distance_from_GH_shape_m":round(float(v["geoDistanceToShape"]),1),
            "GTFS_stop_time_row":v["stopTimeCsvRowNumber"],
            "actual_route_stop_service_confirmed":"no",
            "review":"KMZ_vs_road_or_stop_source_investigation",
        })
    all_far.sort(key=lambda x:(x["trip_pattern_id"],-x["distance_from_GH_shape_m"]))
    write(args.out/"MobilityData_remaining_stop_shape_warning_details.csv",
          all_far,["trip_pattern_id","trip_id","stop_id","stop_name",
                   "distance_from_GH_shape_m","GTFS_stop_time_row",
                   "actual_route_stop_service_confirmed","review"])
    all_order=[]
    for r in after_order:
        uid=r["tripId"].removeprefix("QA_")
        by_pattern[uid]["remaining_stop_order_warnings"]+=1
        all_order.append({
            "trip_pattern_id":uid,"stop_1":r["stopId1"],
            "stop_1_name":r["stopName1"],
            "stop_2":r["stopId2"],
            "stop_2_name":r["stopName2"],
            "source_stop_order_auto_changed":"no",
            "review":"revisited_street_or_real_sequence_conflict",
        })
    write(args.out/"MobilityData_remaining_stop_order_warning_details.csv",
          all_order,["trip_pattern_id","stop_1","stop_1_name","stop_2",
                     "stop_2_name","source_stop_order_auto_changed","review"])
    for r in before_far:
        by_pattern[r["tripId"].removeprefix("QA_")]["original_shape_warnings"]+=1
    for r in before_order:
        by_pattern[r["tripId"].removeprefix("QA_")]["original_order_warnings"]+=1
    priorities=[{
        "trip_pattern_id":uid,
        "original_stop_shape_warnings":x["original_shape_warnings"],
        "remaining_stop_shape_warnings":x["remaining_shape_warnings"],
        "shape_warning_reduction":x["original_shape_warnings"]-x["remaining_shape_warnings"],
        "original_stop_order_warnings":x["original_order_warnings"],
        "remaining_stop_order_warnings":x["remaining_stop_order_warnings"],
        "reference_route_stop_service_confirmed":"no",
    } for uid,x in by_pattern.items()]
    priorities.sort(key=lambda x:(-x["remaining_stop_shape_warnings"],
                                 -x["remaining_stop_order_warnings"],x["trip_pattern_id"]))
    write(args.out/"MobilityData_shape_stop_review_by_route.csv",
          priorities,list(priorities[0]))
    improved=(len(after_far)<=len(before_far) and
              len(after_order)<=len(before_order) and
              newtotal["ERROR"]==0)
    summary={
        "validator_version_before":baseline["summary"]["validatorVersion"],
        "validator_version_after":updated["summary"]["validatorVersion"],
        "baseline_validation_errors":basetotal["ERROR"],
        "new_validation_errors":newtotal["ERROR"],
        "baseline_warnings_total":basetotal["WARNING"],
        "new_warnings_total":newtotal["WARNING"],
        "before_stop_to_shape_over_100m_count":len(before_far),
        "after_stop_to_shape_over_100m_count":len(after_far),
        "resolved_stop_to_shape_over_100m_warnings":len(before_far)-len(after_far),
        "before_stop_match_out_of_order_warnings":len(before_order),
        "after_stop_match_out_of_order_warnings":len(after_order),
        "road_sections_selected_as_improved_candidates":
            effort["GH_bus_sections_accepted_as_better_road_candidates"],
        "validated_reduction_without_new_order_warnings":improved,
        "stop_id_or_stop_sequence_modified":False,
        "full_final_real_operator_feed_created":False,
        "fully_publishable":False,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report=["# MobilityData GTFS geometriecontrole: vóór en na gerichte GraphHopper-herroutering","",
            "**Uitsluitend test-GTFS met synthetische dienstregeling; niet publiceren.**",
            "Echte validator 8.0.1 tweemaal uitgevoerd op afzonderlijke GTFS-test-ZIP's.",
            "",
            "## Uitkomsten", ""]
    for k,v in summary.items():
        if type(v) in (int,float,bool):
            report.append("- "+k+": **"+str(v)+"**")
    report+=["","## Warning-codes","",
             "| Code | Ernst | Eerst | Nu | Verschil |",
             "|---|---|---:|---:|---:|"]
    for x in rows:
        report.append("| "+x["notice_code"]+" | "+x["severity"]+" | "+
                      str(x["before"])+" | "+str(x["after"])+" | "+
                      str(x["difference"])+" |")
    report+=["",
        "## Onopgeloste routevragen","",
        "1. Stopafstanden boven de MobilityData grens van 100m vragen een route- of stopbroncontrole, geen kunstmatige lijn naar halte.",
        "2. Stops match shape out of order kan veroorzaakt worden door hetzelfde wegdeel bij een rondrit; zonder bewijs niet omwisselen.",
        "3. Geen daadwerkelijke haltebediening, keerpunten, echte ritten of dienstregeling vastgesteld.",
        "4. Twee MobilityData HTML/JSON rapporten en beide demonstratie-ZIP's zijn als workflow-artifact beschikbaar.",
        ""
    ]
    (args.out/"summary.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if newtotal["ERROR"]>0:
        raise SystemExit("New GTFS specification errors appeared: do not promote revised road candidates")
    if not improved:
        raise SystemExit("New shape warnings or order warnings increased: manual review, no automatic promotion")

if __name__=="__main__":
    main()
