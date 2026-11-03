#!/usr/bin/env python3
"""Create a reproducible review queue for the 60 AMB route variants without SIU links."""
import csv
import json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"sources/amb/kmz_stop_gaps"
OUT=ROOT/"build/amb-stops-priority-queue"

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def write(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader();w.writerows(rows)

def main():
    raw=read(SRC/"uncovered_route_stop_search_summary.csv")
    if len(raw)!=60:
        raise ValueError("Expected 60 uncovered KMZ records: got "+str(len(raw)))
    out=[]
    for r in raw:
        co=r["company"]
        osm=int(r["osm_near_30m"])
        siu=int(r["siu_near_30m"])
        coll=r.get("source_url_collision")=="yes"
        if co=="SOBUSA":
            tier="P1_SOBUSA_AB_and_base_routes"
            next_step="manual_check_KMZ_AB_branch_and_boarding_evidence"
        elif coll:
            tier="P2_fix_official_KMZ_link_conflict"
            next_step="find_correct_official_route_geometry_before_candidate_stop_approval"
        elif osm>0:
            tier="P2_review_nearby_OSM_platforms_and_SIU_cross_route_stops"
            next_step="verify_source_platform_network_operator_and_route_boarding"
        else:
            tier="P3_seek_extra_TPC_stops_and_cross_route_evidence"
            next_step="insufficient_OSM_stop_evidence;research_official_field_or_public_stop_sources"
        out.append({
            "review_tier":tier,"company":co,"kmz_route_label":r["kmz_route_label"],
            "base_route_code":r["kmz_base_route_code"],"variant":r["kmz_variant"],
            "other_SIU_line_stop_locations_within_30m":siu,
            "unconfirmed_OSM_platforms_within_30m":osm,
            "candidate_points_within_50m":int(r["nearby_points_50m"]),
            "official_KMZ_URL_collision":"yes" if coll else "no",
            "review_work":next_step,
            "stop_list_proven_by_SIU_for_this_route":"no",
            "stop_service_proven_by_other_location_proximity":"no",
            "GTFS_pattern_approved":"no",
            "manual_validation_status":"unreviewed",
            "evidence_route_url":r["source_kmz_url"]
        })
    order={"P1":0,"P2":1,"P3":2}
    out.sort(key=lambda r:(order[r["review_tier"].split("_")[0]],r["company"],r["base_route_code"],r["variant"]))
    for i,r in enumerate(out,1):r["queue_number"]=i
    fields=["queue_number"]+list(out[0].keys())
    fields=list(dict.fromkeys(fields))
    write(OUT/"siu_missing_60_kmz_route_variant_workqueue.csv",out,fields)
    counts=Counter(x["review_tier"] for x in out)
    summary={"total_missing_kmz_route_variant_records":len(out),
             "distinct_official_base_route_code_and_operator":len({(r["company"],r["base_route_code"]) for r in out}),
             "sOBUSA_variant_records":sum(r["company"]=="SOBUSA" for r in out),
             "priority_counts":dict(counts),
             "source":"KMZ-SIU gap audit and proximity candidate reports",
             "approval_status":"All research only; no claimed boarding stops"}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# Werkvoorraad: AMB KMZ-varianten zonder eigen SIU-haltevolgorde","",
           "**De 60 vermeldingen zijn geen 60 unieke route_id's.** A/B blijven als aparte patronen onder dezelfde basisroute.",
           "Er zijn geen officiële SOBUSA-haltes uit geografische nabijheid afgeleid.","",
           "## Prioriteiten", ""]
    for k,n in counts.items():lines.append("- "+k+": "+str(n)+" varianten")
    lines+=["","## Nieuwe controlebronnen en opvolging","",
            "1. SOBUSA C12/C16/B18: vergelijk de afzonderlijke A/B-geometrieën met de originele vergunningen; controleer waar de trajecten werkelijk uiteenlopen.",
            "2. Bestaande SIU-stops langs dezelfde straat zijn hooguit kandidaat-instaplocaties voor andere lijnen, nooit automatisch een SOBUSA-halte.",
            "3. Controleer OSM-platformen op netwerk/transitoperator en bewijs van instap langs de route; huidige Overpass-export bevat **0 bevestigde traditionele TPC-haltes**.",
            "4. Markeer de vier foutieve gedeelde KMZ-URL's en valideer de correcte geometrie eerst.",
            "5. Pas na bewijs van daadwerkelijke haltebediening en richting/volgorde mag een variant naar GTFS stop_times.txt.",
            "",
            "De 20 bestaande SIU-haltevolgorde-kandidaten blijven behouden; de afzonderlijke ambiguïteitsreview voor 13 SIU-itineraries gebruikt de KMZ-corridors als tweede bron.",
            ""]
    (OUT/"summary.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
