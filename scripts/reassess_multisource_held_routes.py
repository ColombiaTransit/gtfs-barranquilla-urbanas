#!/usr/bin/env python3
"""Reassess held research routes from existing evidence; no OCR or network."""
import csv,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/multisource-route-reassessment"
LEGAL={"route_variant_scope_and_legal_effect_unverified","legal_effective_period_and_operational_activation_unverified"}
def read(path):
 with (ROOT/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def norm(s):return re.sub("[^A-Z0-9]","",(s or "").upper())
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 held=read("sources/amb/gtfs_staging/unresolved_route_issues.csv")
 routes={r["route_id"]:r for r in read("gtfs/routes.txt")}
 gis={r["gtfs_route_id"]:r for r in read("sources/amb/arcgis_shape_staging/route_shape_matches.csv")}
 siu=read("sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv")
 kmz=read("sources/amb/KMZ_first_GH_fallback_validation/source_shape_source_by_pattern.csv")
 headways={r["gtfs_route_id"]:r for r in read("sources/amb/gtfs_staging/route_headway_candidates.csv")}
 legal=read("sources/amb/legal_validity_ocr_review/verified_462_242_route_headways_2026-11-04.csv")
 periods=read("sources/amb/legal_validity_ocr_review/route_variant_legal_periods.csv")
 rows=[]
 for h in held:
  rid=h["gtfs_route_id"];r=routes[rid];agency=r["agency_id"].removeprefix("AMB_");code=h["base_route_code"]
  variant=r["route_short_name"].removeprefix(code).strip(" -")
  km=[x for x in kmz if x["company"]==agency and norm(x["official_route_label"])==norm(code) and x["genuine_2026_KMZ_used"]=="yes"]
  si=[x for x in siu if x.get("suggested_gtfs_route_id")==rid and x.get("final_gtfs_route_mapping_confirmed","").lower()=="yes"]
  # A tentative SIU candidate is never counted as confirmed evidence.
  pdf=any(x["agency"]==agency and norm(x["route_code"])==norm(code) for x in legal) or any(x["agency"]==agency and norm(x["route"])==norm(code) for x in periods)
  arc=bool(gis.get(rid))
  recent=bool(km or si or pdf)
  families=sum((bool(km),bool(si),pdf,arc))
  old=[x for x in h["blockers"].split(";") if x]
  remaining=[x for x in old if x not in LEGAL]
  legal_waived=[x for x in old if x in LEGAL] if families>=2 and recent else []
  if not legal_waived:remaining=old[:]
  status="research_staging_eligible" if not remaining else "held_for_other_review"
  rows.append(dict(gtfs_route_id=rid,route_code=r["route_short_name"],kmz_2026=bool(km),siu_confirmed=bool(si),
    arcgis_indexed=arc,verified_pdf_headway=pdf,evidence_families=families,
    source_recency_gate=recent,legal_blockers_waived=";".join(legal_waived),
    remaining_blockers=";".join(remaining),decision=status,
    caution="Base route evidence does not establish A/B geometry or observed timetable"))
 with (OUT/"route_reassessment.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary={"held_input":len(rows),"legal_waiver_routes":sum(bool(r["legal_blockers_waived"]) for r in rows),
  "eligible_after_waiver":sum(r["decision"]=="research_staging_eligible" for r in rows),
  "still_held":sum(r["decision"]!="research_staging_eligible" for r in rows),
  "notes":"Conservative evidence audit. SIU proposals not confirmed are excluded. ArcGIS is historical; KMZ is official 2026. No publication authorization."}
 (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
 (OUT/"summary.md").write_text("# Reassessment of 52 held routes\n\n"+json.dumps(summary,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
