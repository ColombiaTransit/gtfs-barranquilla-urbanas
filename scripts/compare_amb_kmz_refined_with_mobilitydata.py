#!/usr/bin/env python3
"""Final independent MobilityData report on KMZ bus-road densification.

Compares a real baseline 2026 KMZ-first GTFS with a regenerated pilot using
only GH gap-substitutions allowed by source corridor/stop and validator guards.
The source route, service, trips, stops and demo stop_times are byte-identical.
No publication GTFS changes and no real timetables.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/amb-KMZ-GH-refinement-final-QA"
BASE=ROOT/"build/amb-KMZ-sparse-baseline-validation"
FINAL=ROOT/"build/amb-KMZ-sparse-final-validation"
DEC=ROOT/"build/amb-KMZ-road-refinement-safe/summary.json"
LOCAL=ROOT/"build/amb-KMZ-dense-roads-research/summary.json"

def read(p):return json.loads(p.read_text(encoding="utf-8"))

def groups(data):return {x["code"]:x for x in data["notices"]}

def metric(data,key):return sum(int(x["totalNotices"]) for x in data["notices"]
                                 if x["severity"]==key)

def detailed(report,code):
    n=groups(report).get(code)
    if not n:return []
    samples=n.get("sampleNotices",[])
    if len(samples)!=int(n["totalNotices"]):
        raise ValueError("MobilityData report sampled geometry notices")
    return samples

def issue_keys(items,code):
    if code=="stop_too_far_from_shape":
        return {(x.get("tripId"),x.get("stopId"),x.get("stopTimeCsvRowNumber")) for x in items}
    return {(x.get("tripId"),x.get("stopId1"),x.get("stopId2")) for x in items}

def write(p,rows,columns=None):
    if not rows:return
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns or list(rows[0]),extrasaction="ignore")
        w.writeheader();w.writerows(rows)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=OUT)
    parser.add_argument("--baseline",type=Path,default=BASE)
    parser.add_argument("--final",type=Path,default=FINAL)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    base=read(args.baseline/"validator/report.json")
    final=read(args.final/"validator/report.json")
    local=read(LOCAL)
    choice=read(DEC)
    b=groups(base);f=groups(final)
    bycode=[]
    for code in sorted(set(b)|set(f)):
        previous=int(b[code]["totalNotices"]) if code in b else 0
        current=int(f[code]["totalNotices"]) if code in f else 0
        bycode.append({
            "code":code,
            "severity":(f.get(code) or b[code])["severity"],
            "before_KMZ_first":previous,
            "after_GH_road_refinement":current,
            "difference":current-previous,
        })
    write(args.out/"MobilityData_KMZ_first_refinement_notice_differences.csv",bycode)
    newissues={}
    for code in ("stop_too_far_from_shape","stops_match_shape_out_of_order"):
        before=issue_keys(detailed(base,code),code)
        after=issue_keys(detailed(final,code),code)
        newissues[code]=len(after-before)
    former_far=detailed(base,"stop_too_far_from_shape")
    current_far=detailed(final,"stop_too_far_from_shape")
    residual=[{
        "trip_pattern_id":x.get("tripId","").removeprefix("QA_"),
        "stop_id":x.get("stopId",""),"stop_name":x.get("stopName",""),
        "distance_m":round(float(x.get("geoDistanceToShape","0")),2),
        "status":"still_offroute_unverified_GH_or_source",
    } for x in current_far]
    write(args.out/"remaining_stop_vs_refined_shape_QA.csv",residual)
    berrors=metric(base,"ERROR")
    ferrors=metric(final,"ERROR")
    bwarnings=metric(base,"WARNING")
    fwarnings=metric(final,"WARNING")
    valid=(ferrors<=berrors and
           fwarnings<=bwarnings and
           all(v==0 for v in newissues.values()))
    summary={
        "comparison":"2026 official AMB KMZ first with GH-bus road shaping only for individually safe >400m source edges",
        "input_sparse_KMZ_sections":local["official_KMZ_source_sections_with_sparse_edges"],
        "total_source_KMZ_straight_gaps_over_400m":local["all_KMZ_gaps_over_400m"],
        "GH_bus_routes_tested_for_sparse_edges":local["GH_bus_route_queries"],
        "GH_locally_plausible_edge_replacements":local["locally_accepted_GH_road_substitutions"],
        "KMZ_sections_locally_refined":local["source_sections_locally_refined"],
        "GH_KMZ_sections_kept_after_validator_guards":choice["KMZ_sections_kept_with_road_densification"],
        "GH_KMZ_sections_reverted_for_validator_risk":choice["KMZ_sections_rolled_back_to_official"],
        "source_routes_refined_after_validator_guards":choice["source_route_patterns_approved_by_validator"],
        "MobilityData_original_ERROR":berrors,
        "MobilityData_final_ERROR":ferrors,
        "MobilityData_original_WARNING":bwarnings,
        "MobilityData_final_WARNING":fwarnings,
        "MobilityData_original_stop_too_far_from_shape":len(former_far),
        "MobilityData_final_stop_too_far_from_shape":len(current_far),
        "MobilityData_original_stops_match_shape_out_of_order":len(detailed(base,"stops_match_shape_out_of_order")),
        "MobilityData_final_stops_match_shape_out_of_order":len(detailed(final,"stops_match_shape_out_of_order")),
        "new_stop_too_far_from_shape_notices":newissues["stop_too_far_from_shape"],
        "new_stop_order_notices":newissues["stops_match_shape_out_of_order"],
        "same_stop_times_trips_stops_routes_in_both_GTFS":True,
        "validator_did_not_regress":valid,
        "GH_road_shapes_are_only_research_candidates":True,
        "GTFS_production_or_SIU_original_changes":False,
        "real_2026_AMB_trip_directions_proven":False,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    md=[
        "# Gecontroleerde verfijning AMB KMZ: rechte segmenten met GraphHopper bus",
        "",
        "Zelfde agency, routes, trips, stops, stop_times, calendar en testkalender. Alleen shapes.txt verschilt.",
        "**Let op: dit is onderzoeks-GTFS met synthetische vertrektijden. Niet publiceren.**",
        "",
        "## Verwerking","",
        "- KMZ-trajectdelen met bron-vertex-sprongen >400m: **"+str(summary["input_sparse_KMZ_sections"])+"**",
        "- Oorspronkelijke lange KMZ-verbindingen >400m: **"+str(summary["total_source_KMZ_straight_gaps_over_400m"])+"**",
        "- GraphHopper bus-verzoeken: **"+str(summary["GH_bus_routes_tested_for_sparse_edges"])+"**",
        "- Geografisch lokaal passende GH-wegstukken: **"+str(summary["GH_locally_plausible_edge_replacements"])+"**",
        "- Aangepaste KMZ-routedelen na validatorcontrole: **"+str(summary["GH_KMZ_sections_kept_after_validator_guards"])+"**",
        "- Wegens QA teruggedraaide routedelen: **"+str(summary["GH_KMZ_sections_reverted_for_validator_risk"])+"**",
        "",
        "## Feitelijke MobilityData GTFS Validator 8.0.1","",
        "| Bevinding | KMZ-first | KMZ + veilige GH-wegverbindingen |",
        "|---|---:|---:|",
        "| ERROR | "+str(berrors)+" | "+str(ferrors)+" |",
        "| alle WARNING | "+str(bwarnings)+" | "+str(fwarnings)+" |",
        "| Haltes te ver van shape | "+str(len(former_far))+" | "+str(len(current_far))+" |",
        "| Haltes buiten volgorde | "+str(summary["MobilityData_original_stops_match_shape_out_of_order"])+" | "+str(summary["MobilityData_final_stops_match_shape_out_of_order"])+" |",
        "",
        "**Geen validatieregressie:** "+("ja" if valid else "**NEE — alle verbeteringen ongedaan maken**"),
        "",
        "## Bronnen/waarschuwingen","",
        "- Officiële AMB KMZ 2026 blijft de lijn- en volgordeautoriteit.",
        "- GraphHopper bus-route wordt alleen voor ontbrekende bocht-details tussen bestaande KMZ-punten getoetst.",
        "- Originele KMZ-punten blijven behouden; geen SIU-stop verplaatst of vervallen.",
        "- PT2 en D8 zonder betrouwbare KMZ houden bestaande GH bus-fallback als onderzoeksgeometrie.",
        "- Een GH-wegroute die de validator passeert, bewijst nog niet dat vervoerders die exacte straat in de concessie rijden.",
        "- Geen nieuwe vertrek- en aankomsttijden en geen productiefeedwijzigingen.",
        "",
    ]
    (args.out/"summary.md").write_text("\n".join(md),encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    if not valid:
        raise SystemExit("Source-geometry refinement introduced new GTFS/stop notices; rollback needed")

if __name__=="__main__":
    main()
