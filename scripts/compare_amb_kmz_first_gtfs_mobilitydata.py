#!/usr/bin/env python3
"""Compare two REAL MobilityData 8.0.1 reports for equal GTFS test populations.

Focus on geometry: KMZ official first + existing GH fallback versus the current
order-guarded GH-only trial. Both use the same synthetic GTFS stop visits,
routes, trips and service dates. This counts all validator notices and records
specific stop and route warnings for review, no automatic route promotion.
"""
from __future__ import annotations

import argparse,csv,json
from collections import Counter,defaultdict
from pathlib import Path

from build_amb_gtfs_geometry_validation_pilot import ROOT

BASE=ROOT/"build/amb-mobilitydata-GH-reference-NOT-PUBLISHABLE"
HYBRID=ROOT/"build/amb-mobilitydata-KMZ-first-NOT-PUBLISHABLE"
ORIG=ROOT/"sources/amb/GTFS_shape_validator_recheck"
OUT=ROOT/"build/amb-KMZ-first-vs-GH-MobilityData-QA"

def read_json(p):
    return json.loads(p.read_text(encoding="utf-8"))
def read_csv(p):
    with p.open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
def save(p,rows,columns=None):
    if not rows:return
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns or list(rows[0]),extrasaction="ignore")
        w.writeheader();w.writerows(rows)
def groups(report):
    return {n["code"]:n for n in report["notices"]}
def notice_details(n):
    if n is None:return []
    return n.get("sampleNotices",[])
def counts(report):
    c=Counter()
    for n in report["notices"]:
        c[n["severity"]]+=int(n["totalNotices"])
    return c
def issue_uid(x):
    return str(x.get("tripId","")).removeprefix("QA_")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base",type=Path,default=BASE)
    p.add_argument("--hybrid",type=Path,default=HYBRID)
    p.add_argument("--out",type=Path,default=OUT)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    a=read_json(args.base/"validator/report.json")
    b=read_json(args.hybrid/"validator/report.json")
    bs=read_json(args.base/"build_summary.json")
    hs=read_json(args.hybrid/"build_summary.json")
    info=read_json(ROOT/"build/amb-kmz-first-GH-fallback-research/summary.json")
    sels=read_csv(ROOT/"build/amb-kmz-first-GH-fallback-research/shape_source_by_pattern.csv")
    source={r["trip_pattern_id"]:r for r in sels}
    for key in ("GTFS_agencies","GTFS_routes","GTFS_stops","GTFS_demo_trips",
                "GTFS_demo_stop_times","GTFS_shapes"):
        if bs[key]!=hs[key]:
            raise ValueError("Comparison population differs on "+key)
    aa=groups(a); bb=groups(b)
    sa=counts(a); sb=counts(b)
    bycode=[]
    for key in sorted(set(aa)|set(bb)):
        x=int(aa.get(key,{}).get("totalNotices",0))
        y=int(bb.get(key,{}).get("totalNotices",0))
        bycode.append({
            "notice_code":key,
            "severity":(bb.get(key) or aa[key])["severity"],
            "GH_baseline":x,
            "KMZ_first_plus_GH_fallback":y,
            "change_KMZ_minus_GH":y-x,
        })
    save(args.out/"MobilityData_notice_comparison_by_code.csv",bycode)
    codes=("stop_too_far_from_shape","stops_match_shape_out_of_order")
    issue_rows=[]
    bytrip=defaultdict(Counter)
    for code in codes:
        for prefix,group in (("GH",aa.get(code)),("KMZ",bb.get(code))):
            for x in notice_details(group):
                uid=issue_uid(x)
                bytrip[uid][f"{prefix}_{code}"]+=1
                stop=str(x.get("stopId",""))
                issue_rows.append({
                    "validator":prefix,
                    "trip_pattern_id":uid,
                    "company":source.get(uid,{}).get("company",""),
                    "route_label":source.get(uid,{}).get("official_route_label",""),
                    "shape_source_KMZ_first":source.get(uid,{}).get("shape_source_selected",""),
                    "issue_code":code,
                    "stop_id":stop,
                    "stop_name":x.get("stopName",""),
                    "distance_m":x.get("geoDistanceToShape",""),
                    "stop_csv_row":x.get("stopTimeCsvRowNumber",""),
                    "stop_id_1":x.get("stopId1",""),
                    "stop_id_2":x.get("stopId2",""),
                    "operator_route_legally_verified":"no",
                })
    save(args.out/"MobilityData_stop_geometry_issues_both_feeds.csv",issue_rows)
    route_rows=[]
    for uid in sorted(source):
        x=bytrip[uid]
        route_rows.append({
            "trip_pattern_id":uid,
            "company":source[uid]["company"],
            "route_label":source[uid]["official_route_label"],
            "shape_origin_hybrid":source[uid]["shape_source_selected"],
            "GH_stop_too_far_warnings":x["GH_stop_too_far_from_shape"],
            "hybrid_stop_too_far_warnings":x["KMZ_stop_too_far_from_shape"],
            "GH_stop_order_warnings":x["GH_stops_match_shape_out_of_order"],
            "hybrid_stop_order_warnings":x["KMZ_stops_match_shape_out_of_order"],
            "delta_stop_too_far":x["KMZ_stop_too_far_from_shape"]-x["GH_stop_too_far_from_shape"],
            "delta_stop_order":x["KMZ_stops_match_shape_out_of_order"]-x["GH_stops_match_shape_out_of_order"],
            "GH_fallback_2026_service_verified":"no",
        })
    route_rows.sort(key=lambda x:(-x["delta_stop_order"],x["delta_stop_too_far"],x["trip_pattern_id"]))
    save(args.out/"MobilityData_geometry_validation_per_pattern.csv",route_rows)
    priority=read_csv(ORIG/"67_remaining_stop_vs_shape_source_evidence.csv")
    worst=[x for x in priority if float(x["validator_distance_to_final_GH_shape_m"])>250]
    oldissues={(issue_uid(x),x.get("stopId")) for x in notice_details(aa.get("stop_too_far_from_shape"))}
    newissues={(issue_uid(x),x.get("stopId")) for x in notice_details(bb.get("stop_too_far_from_shape"))}
    seven=[]
    for x in worst:
        key=(x["trip_pattern_id"],x["physical_SIU_stop_id"])
        seven.append({
            "trip_pattern_id":key[0],
            "route_label":x["route_label"],
            "physical_SIU_stop_id":key[1],
            "stop_name":x["physical_stop_name"],
            "GH_distance_from_prior_source_review_m":x["validator_distance_to_final_GH_shape_m"],
            "distance_to_official_AMB_KMZ_m":x["nearest_source_KMZ_distance_m"],
            "GH_current_validator_stop_far_warning":"yes" if key in oldissues else "no",
            "KMZ_first_validator_stop_far_warning":"yes" if key in newissues else "no",
            "source_shape_selected":source[key[0]]["shape_source_selected"],
        })
    if len(seven)!=7:raise ValueError("Seven biggest stop issues source review changed")
    save(args.out/"seven_P1_stop_warnings_KMZ_vs_GH.csv",seven)
    summary={
        "comparison":"Official AMB 2026 KMZ where usable, otherwise existing GH bus route versus reviewed GH baseline",
        "both_same_gtfs_trip_and_stop_population":True,
        "synthetic_gtfs_not_for_publication":True,
        "official_KMZ_source_route_patterns":info["official_2026_KMZ_patterns"],
        "GH_bus_fallback_source_patterns":info["GraphHopper_bus_fallback_patterns"],
        "routes_in_both_feeds":bs["GTFS_routes"],
        "synthetic_trips_in_both_feeds":bs["GTFS_demo_trips"],
        "stop_visits_in_both_feeds":bs["GTFS_demo_stop_times"],
        "GH_source_errors":sa["ERROR"],
        "KMZ_first_errors":sb["ERROR"],
        "GH_source_warnings":sa["WARNING"],
        "KMZ_first_warnings":sb["WARNING"],
        "GH_stop_too_far_from_shape":int(aa.get("stop_too_far_from_shape",{}).get("totalNotices",0)),
        "KMZ_first_stop_too_far_from_shape":int(bb.get("stop_too_far_from_shape",{}).get("totalNotices",0)),
        "GH_stops_match_shape_out_of_order":int(aa.get("stops_match_shape_out_of_order",{}).get("totalNotices",0)),
        "KMZ_first_stops_match_shape_out_of_order":int(bb.get("stops_match_shape_out_of_order",{}).get("totalNotices",0)),
        "KMZ_first_seven_biggest_original_stops_offshape":sum(x["KMZ_first_validator_stop_far_warning"]=="yes" for x in seven),
        "KMZ_first_source_KMZ_geo_line_must_not_be_assumed_road_routable":True,
        "automatic_road_candidate_promoted_to_published_gtfs":False,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    md=[
        "# Barranquilla: officiële 2026 KMZ-first vs GraphHopper-busweg in GTFS",
        "",
        "De GTFS-gegevens behalve shapes.txt zijn identiek; kalender, trips en tijden zijn nog steeds synthetisch.",
        "KMZ wordt alleen gebruikt als er een bruikbare AMB-KMZ 2026-figuur is; GraphHopper-buswegen blijven",
        "fallback voor onbruikbare of ontbrekende route-KMZ, en moeten op de echte route worden gevalideerd.",
        "",
        "## Gelijke testpopulatie","",
        "- Routes: **"+str(summary["routes_in_both_feeds"])+"**",
        "- Voorbeeldritten: **"+str(summary["synthetic_trips_in_both_feeds"])+"**",
        "- Haltebezoeken: **"+str(summary["stop_visits_in_both_feeds"])+"**",
        "- KMZ-bronpatronen: **"+str(summary["official_KMZ_source_route_patterns"])+"**",
        "- GraphHopper-fallbackbronpatronen: **"+str(summary["GH_bus_fallback_source_patterns"])+"**",
        "",
        "## MobilityData 8.0.1 — feitelijke resultaten","",
        "| Code | Alleen GraphHopper | KMZ eerst / GH fallback | Verschil |",
        "|---|---:|---:|---:|",
        "| ERROR | "+str(sa["ERROR"])+" | "+str(sb["ERROR"])+" | "+str(sb["ERROR"]-sa["ERROR"])+" |",
        "| alle WARNING | "+str(sa["WARNING"])+" | "+str(sb["WARNING"])+" | "+str(sb["WARNING"]-sa["WARNING"])+" |",
        "| stop_too_far_from_shape | "+str(summary["GH_stop_too_far_from_shape"])+" | "+
             str(summary["KMZ_first_stop_too_far_from_shape"])+" | "+
             str(summary["KMZ_first_stop_too_far_from_shape"]-summary["GH_stop_too_far_from_shape"])+" |",
        "| stops_match_shape_out_of_order | "+str(summary["GH_stops_match_shape_out_of_order"])+" | "+
             str(summary["KMZ_first_stops_match_shape_out_of_order"])+" | "+
             str(summary["KMZ_first_stops_match_shape_out_of_order"]-summary["GH_stops_match_shape_out_of_order"])+" |",
        "",
        "## Beoordeling","",
        "- Kleinere halte-afstand betekent NIET automatisch betere rijrichting, echt lijntracé of dienstregeling.",
        "- Bij een herhaalde passage op dezelfde straat kunnen loopvormige KMZ's validator-volgordewaarschuwingen geven.",
        "- PT2 zonder bestaande route-ID blijft uit beide testfeeds, precies als voorheen.",
        "- Geen SIU-haltes verplaatst of verwijderd, geen ritgrenzen bepaald, geen productie-GTFS aangepast.",
        "",
    ]
    if sb["ERROR"]==0 and (
        summary["KMZ_first_stop_too_far_from_shape"]<
        summary["GH_stop_too_far_from_shape"]):
        md.append("**Afstandsconclusie:** KMZ-first vermindert de geometrische halteafstandfouten in deze test.")
    elif summary["KMZ_first_stop_too_far_from_shape"]>=summary["GH_stop_too_far_from_shape"]:
        md.append("**Afstandsconclusie:** KMZ-first levert hier niet minder halteafstandwaarschuwingen op.")
    if summary["KMZ_first_stops_match_shape_out_of_order"]>summary["GH_stops_match_shape_out_of_order"]:
        md.append("**Volgordevoorbehoud:** KMZ-first produceert meer volgordewaarschuwingen en is zonder nadere correctie niet direct geschikt voor de definitieve shape.")
    (args.out/"summary.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
