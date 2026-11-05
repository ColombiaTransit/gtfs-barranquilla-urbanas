#!/usr/bin/env python3
"""Read-only geometry worklist for non-deferred AMB routes; no network or GTFS writes."""
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"sources/amb/KMZ_first_GH_fallback_validation/source_shape_source_by_pattern.csv"
OUT=ROOT/"build/other-route-geometry-review"
DEFERRED={("COOLITORAL","A4-4109"),("LOLAYA","D8-4165")}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with SOURCE.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
    grouped=defaultdict(list)
    for row in rows:
        grouped[(row["company"],row["official_route_label"].split(" ")[0])].append(row)
    output=[]
    for (company,code),parts in sorted(grouped.items()):
        deferred=(company,code) in DEFERRED
        sources=sorted({x["shape_source_selected"] for x in parts})
        warnings=sorted({x["historical_fallback_warning"] for x in parts if x["historical_fallback_warning"]})
        if deferred:status="DEFERRED_GEOMETRY_REVIEW"
        elif any(x["genuine_2026_KMZ_used"]!="yes" for x in parts):status="REVIEW_GH_FALLBACK"
        elif warnings:status="REVIEW_SOURCE_WARNING"
        else:status="KMZ_CANDIDATE_NEEDS_DIRECTION_CHECK"
        output.append(dict(company=company,route_code=code,patterns=len(parts),
            source_types=";".join(sources),source_warnings=";".join(warnings),
            status=status,verified_for_publication="no"))
    with (OUT/"other_routes_geometry_worklist.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
    counts=Counter(x["status"] for x in output)
    summary={"source_patterns":len(rows),"distinct_route_keys":len(output),
        "deferred_routes":[x["route_code"] for x in output if x["status"]=="DEFERRED_GEOMETRY_REVIEW"],
        "other_route_keys":sum(x["status"]!="DEFERRED_GEOMETRY_REVIEW" for x in output),
        "status_counts":dict(counts),"gtfs_modified":False,
        "limitation":"Only routes represented in existing 70 source patterns; not a 97-route comprehensive geometry certification"}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    with (OUT/"summary.md").open("w",encoding="utf-8") as f:
        f.write("# Overige AMB-geometrieën — onderzoekswerklijst\n\n")
        f.write("Geen GTFS-publicatiegoedkeuring. A4-4109 en D8-4165 blijven uitgesteld.\n\n")
        f.write(f"Bronpatronen: {len(rows)}; routecodegroepen: {len(output)}; overige groepen: {summary['other_route_keys']}.\n\n")
        for k,n in sorted(counts.items()):f.write(f"- {k}: {n}\n")
        f.write("\nControleer per groep bronidentiteit, KMZ-aansluitingen midden op lijnen, rijrichting, wegverloop en SIU-stopvolgorde. De 97 routes buiten de bestaande bronpatronen vereisen een afzonderlijke volledigheidscontrole.\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
