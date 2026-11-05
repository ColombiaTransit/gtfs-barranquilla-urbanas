#!/usr/bin/env python3
"""Check current corrected AMBQ KMZ coverage against existing GTFS routes.

Does not treat old 70-pattern GTFS demo as complete. Does not publish shapes.
"""
import csv,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def norm(s):return re.sub("[^A-Z0-9]","",str(s or "").upper())
def main():
    base=ROOT/"sources/amb/kmz"
    manifest=read(base/"manifest.csv")
    routes=read(ROOT/"gtfs/routes.txt")
    out=ROOT/"build/amb-current-kmz-shape-coverage";out.mkdir(parents=True,exist_ok=True)
    bylabel={}
    for x in manifest:
        if x.get("status")!="geometry_imported":continue
        key=(norm(x.get("company")),norm(x.get("route_label")))
        bylabel.setdefault(key,[]).append(x)
    results=[]
    for r in routes:
        agency=r["agency_id"].removeprefix("AMB_")
        key=(norm(agency),norm(r["route_short_name"]))
        matches=bylabel.get(key,[])
        state="KMZ_SOURCE_AVAILABLE" if len(matches)==1 else "KMZ_SOURCE_AMBIGUOUS" if matches else "NO_EXACT_KMZ_MATCH_REVIEW"
        results.append({"route_id":r["route_id"],"agency_id":r["agency_id"],
            "route_short_name":r["route_short_name"],"status":state,
            "matching_kmz_records":len(matches),
            "kmz_url":matches[0].get("final_url","") if len(matches)==1 else "",
            "linestring_count":matches[0].get("linestring_count","") if len(matches)==1 else "",
            "source_sha256":matches[0].get("sha256","") if len(matches)==1 else "",
            "geojson_path":matches[0].get("geojson_path","") if len(matches)==1 else "",
            "gtfs_shape_validated":"no"})
    with (out/"route_kmz_coverage.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    counts=Counter(x["status"] for x in results)
    overrides=["PT2-4102","A16-4161 B","B13-B-4189","C18-4141"]
    override_status={}
    for code in overrides:
        matched=[m for m in manifest if m.get("route_label")==code]
        source_ok=len(matched)==1 and matched[0].get("status")=="geometry_imported"
        route_status=next((x["status"] for x in results if x["route_short_name"]==code),"NOT_IN_ROUTES")
        override_status[code]={"source_status":"KMZ_IMPORTED" if source_ok else "KMZ_MISSING_OR_AMBIGUOUS","gtfs_route_status":route_status}
    summary={"gtfs_routes":len(routes),"source_coverage":dict(counts),
             "corrected_override_routes":override_status,
             "note":"Source availability is not equivalent to GTFS shape_id, direction, stop order or publication approval.",
             "gtfs_written":False}
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"
")
    (out/"summary.md").write_text("# Actuele AMBQ-KMZ dekking voor GTFS routes

"+json.dumps(summary,indent=2)+"
")
    print(json.dumps(summary,indent=2))
    if any(v["source_status"]!="KMZ_IMPORTED" for v in override_status.values()):
        raise SystemExit("Corrected source override absent or ambiguous in current GTFS coverage; inspect CSV")
if __name__=="__main__":main()
