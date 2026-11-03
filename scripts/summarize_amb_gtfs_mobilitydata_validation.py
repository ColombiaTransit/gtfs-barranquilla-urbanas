#!/usr/bin/env python3
"""Summarize MobilityData GTFS 8.0.1 JSON notices for research pilot.

Do not conflate test-fixture validator success with confirmed operator service.
Keep top notice codes and full report in GitHub artifact, compact totals in repo.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/amb-gtfs-mobilitydata-PILOT-NOT-PUBLISHABLE"

def main():
    build=json.loads((OUT/"build_summary.json").read_text(encoding="utf-8"))
    path=OUT/"validator"/"report.json"
    if not path.is_file():
        raise SystemExit("MobilityData report.json not created; validator failed to complete")
    raw=json.loads(path.read_text(encoding="utf-8"))
    groups=raw.get("notices")
    if not isinstance(groups,list):
        raise SystemExit("MobilityData report lacks notices list; validation is NOT verified")
    classified=[]
    total=Counter()
    for n in groups:
        severity=str(n.get("severity","UNKNOWN")).upper()
        count=int(n.get("totalNotices",len(n.get("notices",[]) or [])))
        code=str(n.get("code","unknown"))
        total[severity]+=count
        classified.append({"code":code,"severity":severity,"count":count})
    classified.sort(key=lambda x:({"ERROR":0,"WARNING":1,"INFO":2}.get(x["severity"],3),-x["count"],x["code"]))
    for name in ("system_errors.json",):
        err=OUT/"validator"/name
        if not err.exists():raise SystemExit("Validator system_errors.json is missing")
        if err.stat().st_size>0:
            payload=err.read_text(encoding="utf-8").strip()
            if payload not in ("[]","{}","null",""):
                raise SystemExit("Validator reports unexpected system errors: see artifact")
    with (OUT/"notice_counts.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["code","severity","count"])
        w.writeheader()
        w.writerows(classified)
    with (OUT/"validation_summary.json").open("w",encoding="utf-8") as f:
        summary={
            "validator_version_pinned":"8.0.1",
            "validation_engine":"MobilityData canonical GTFS Schedule validator",
            "synthetic_demo_feed_only":True,
            "full_json_and_html_in_artifact_only":True,
            "notice_group_count":len(classified),
            "notices_by_severity":dict(total),
            "error_count":total["ERROR"],
            "warning_count":total["WARNING"],
            "info_count":total["INFO"],
            "zero_validation_errors":total["ERROR"]==0,
            "feed_publishable":False,
            "source_operators_service_and_schedules_confirmed":False,
            "top_20_notice_codes":classified[:20],
            "build_counts":{k:v for k,v in build.items() if k.startswith("GTFS_")},
        }
        json.dump(summary,f,ensure_ascii=False,indent=2)
        f.write("\n")
    report=[
        "# MobilityData GTFS validator — proefbuild Barranquilla",
        "",
        "**Dit rapport hoort bij een demonstratiefeed met fictieve trips, kalender en tijden. Niet publiceren.**",
        "",
        "## Feedaantallen","",
    ]
    for k,v in build.items():
        if k.startswith("GTFS_"):report.append("- "+k+": **"+str(v)+"**")
    report+=["","## Validator 8.0.1","",
             "- ERROR notices: **"+str(total["ERROR"])+"**",
             "- WARNING notices: **"+str(total["WARNING"])+"**",
             "- INFO notices: **"+str(total["INFO"])+"**",
             "",
             "## Meest voorkomende codes","",
             "| Severity | Code | Aantal |",
             "|---|---|---:|"]
    for x in classified[:25]:
        report.append("| "+x["severity"]+" | "+x["code"]+" | "+str(x["count"])+" |")
    report+=["",
        "## Beperkingen","",
        "- De proef-ZIP, volledige report.html en report.json staan in het workflow-artifact.",
        "- Een nulscore op validator-ERROR betekent **niet** dat deze routes worden bediend, dat brontrips correct gesplitst zijn of dat de dienstregeling klopt.",
        "- Voor ingebruikname moeten officiële tripgrenzen, frequenties, haltebediening, de 21 geometrische afwijkingen en resterende haltevolgordesignalen worden opgelost.",
        "- Geen productiefeed /gtfs gewijzigd.",
        ""]
    (OUT/"validation_summary.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps({"notices_by_severity":dict(total),"top_codes":classified[:15]},indent=2))
if __name__=="__main__":
    main()
