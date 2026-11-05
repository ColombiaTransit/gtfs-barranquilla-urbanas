#!/usr/bin/env python3
"""Prioritize existing rejected KMZ sparse-edge candidates; read-only, no new inventory."""
import csv,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"sources/amb/KMZ_GH_road_refinement_QA"
OUT=ROOT/"build/kmz-remaining-geometry-qa"
DEFERRED={("COOLITORAL","A4-4109"),("LOLAYA","D8-4165")}
def read(name):
    with (SRC/name).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    guard={(x["trip_pattern_id"],x["section_number"]):x for x in read("KMZ_sparse_road_refinement_validator_guard.csv")}
    candidates=[]
    for x in read("KMZ_sparse_edges_GH_bus_decisions.csv"):
        if x["local_candidate_accepted"].lower()!="yes":continue
        g=guard.get((x["trip_pattern_id"],x["section_number"]))
        if not g or g["validator_guard_choice"]!="reverted_to_official_KMZ":continue
        deferred=(x["company"],x["route_label"].split(" ")[0]) in DEFERRED
        x=dict(x)
        x["validator_rollback_reason"]=g["validator_guard_reason"]
        x["review_status"]="DEFERRED" if deferred else "INDIVIDUAL_VALIDATOR_RECHECK_NEEDED"
        x["priority"]="P1" if float(x["original_KMZ_chord_m"])>=1000 or int(x["SIU_visits_newly_over_100m"])>0 else "P2"
        candidates.append(x)
    candidates.sort(key=lambda x:(x["review_status"]=="DEFERRED",x["priority"]!="P1",-float(x["original_KMZ_chord_m"])))
    with (OUT/"rejected_local_KMZ_edges_review.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(candidates[0]) if candidates else [] )
        if candidates:w.writeheader();w.writerows(candidates)
    summary={"locally_accepted_edges_in_rolled_back_sections":len(candidates),
             "non_deferred_edges":sum(x["review_status"]!="DEFERRED" for x in candidates),
             "deferred_edges":sum(x["review_status"]=="DEFERRED" for x in candidates),
             "non_deferred_P1":sum(x["priority"]=="P1" and x["review_status"]!="DEFERRED" for x in candidates),
             "route_counts":dict(Counter(x["company"]+" "+x["route_label"] for x in candidates if x["review_status"]!="DEFERRED")),
             "production_gtfs_modified":False,
             "warning":"These are local GH candidates rejected by a whole-pattern validator guard; not individually validated, not approved."}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    with (OUT/"summary.md").open("w",encoding="utf-8") as f:
        f.write("# Resterende KMZ-geometrie: individuele hercontrole\n\n")
        f.write("Gebaseerd op bestaande 2026 AMBQ-KMZ/GH-resultaten; geen nieuwe inventarisatie of bronoverrides.\n\n")
        for k in ("locally_accepted_edges_in_rolled_back_sections","non_deferred_edges","deferred_edges","non_deferred_P1"):
            f.write(f"- {k}: **{summary[k]}**\n")
        f.write("\nDe 114 teruggedraaide **secties** zijn niet hetzelfde als het aantal kandidaat-**verbindingen**. Deze lijst bevat alleen lokaal geaccepteerde verbindingen in teruggedraaide secties.\n")
        f.write("\nVervolg: per afzonderlijke KMZ-verbinding shapes.txt-only proefbuild, MobilityData-notices vergelijken met baseline, alleen regressievrije wijzigingen behouden. A4/D8 niet heropenen.\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
