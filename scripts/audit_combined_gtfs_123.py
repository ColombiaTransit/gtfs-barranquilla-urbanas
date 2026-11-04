#!/usr/bin/env python3
"""Research-only route/geometry/stop/frequency coverage report; never publishes GTFS."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def load(path):
 with (R/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def main():
 out=R/"build/combined-gtfs-123";out.mkdir(parents=True,exist_ok=True)
 routes=load("gtfs/routes.txt")
 gis={r["gtfs_route_id"]:r for r in load("sources/amb/arcgis_shape_staging/route_shape_matches.csv")}
 freq={r["gtfs_route_id"]:r for r in load("sources/amb/gtfs_staging/route_headway_candidates.csv")}
 stops=load("sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv")
 aliases=load("sources/amb/legal_validity_ocr_review/coochofal_242_route_code_aliases.csv")
 legal=load("sources/amb/legal_validity_ocr_review/verified_462_242_route_headways_2026-11-04.csv")
 rows=[]
 for r in routes:
  rid=r["route_id"];code=r["route_short_name"].split(" ")[0]
  s=[x for x in stops if x.get("suggested_gtfs_route_id")==rid]
  rows.append(dict(route_id=rid,route_code=code,arcgis_indexed=bool(gis.get(rid)),
    geometry_review=gis.get(rid,{}).get("geometry_status","missing"),
    siu_proposed=len(s),siu_confirmed=sum(x.get("final_gtfs_route_mapping_confirmed","").lower()=="yes" for x in s),
    frequency_staged=bool(freq.get(rid,{}).get("peak_headway_secs")),
    legal_462_242_found=any(x["route_code"]==code and x["agency"] in r["agency_id"] for x in legal),
    needs_variant_review=True))
 with (out/"route_join_audit.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 errors=[]
 for a in aliases:
  src,dst=a["source_route_code"],a["canonical_route_code"]
  if src!=dst and any(r["route_short_name"]==src for r in routes):errors.append("Legacy alias still a route: "+src)
  if src==dst and not any(r["route_short_name"]==dst for r in routes):errors.append("Canonical route missing: "+dst)
 summary=dict(total_routes=len(rows),arcgis_indexed=sum(r["arcgis_indexed"] for r in rows),
  siu_proposed_routes=sum(r["siu_proposed"]>0 for r in rows),frequency_staged=sum(r["frequency_staged"] for r in rows),
  errors=errors,notice="Research only: stale staging and unverified geometry/operational dates cannot authorize publication")
 (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
 (out/"summary.md").write_text("# Combined work packages 1/2/3\n\n"+json.dumps(summary,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(summary,indent=2))
 if errors:raise SystemExit(1)
if __name__=="__main__":main()
