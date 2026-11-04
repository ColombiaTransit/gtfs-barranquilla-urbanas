#!/usr/bin/env python3
"""Audit all SIU names/base-route families against provisional AMB candidates."""
import csv,re,json,unicodedata,argparse
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
def read(path):
 with (ROOT/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def norm(v):
 v=unicodedata.normalize("NFKD",v or "");v="".join(c for c in v if not unicodedata.combining(c))
 return " ".join(re.findall(r"[A-Z0-9]+",v.upper()))
def main():
 p=argparse.ArgumentParser();p.add_argument("--out",default="build/siu-gtfs-name-audit");a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 its=read("sources/siu/public_extract/siu_itineraries.csv")
 reviews=read("sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv")
 orders=read("sources/siu/gtfs_staging/candidate_route_stop_orders_NO_TIMES.csv")
 routes=read("gtfs/routes.txt");valid={r["route_id"] for r in routes}
 byreview={r["siu_itinerary_uuid"]:r for r in reviews};bybase=defaultdict(list);byorders=defaultdict(list)
 for x in its:bybase[x["siu_base_route_uuid"]].append(x)
 for x in orders:byorders[x["siu_itinerary_uuid"]].append(x)
 result=[]
 for x in its:
  uid=x["siu_itinerary_uuid"];rv=byreview.get(uid,{})
  family=bybase[x["siu_base_route_uuid"]]
  candidate=set(filter(None,[rv.get("suggested_gtfs_route_id","")]))
  candidate.update(filter(None,(v.strip() for v in rv.get("same_company_gtfs_ids","").split(";"))))
  candidate.update(v["route_id"] for v in byorders[uid] if v.get("route_id"))
  family_candidates=set()
  for y in family:
   z=byreview.get(y["siu_itinerary_uuid"],{})
   family_candidates.update(filter(None,(v.strip() for v in z.get("same_company_gtfs_ids","").split(";"))))
   if z.get("suggested_gtfs_route_id"):family_candidates.add(z["suggested_gtfs_route_id"])
  family_names=sorted({y["siu_display_name"] for y in family})
  name_norm=norm(x["siu_display_name"])
  name_family_match=any(norm(y["siu_display_name"])!=name_norm and (name_norm in norm(y["siu_display_name"]) or norm(y["siu_display_name"]) in name_norm) for y in family)
  rows=byorders[uid];rows.sort(key=lambda z:int(z["stop_sequence"]) if z["stop_sequence"].isdigit() else 999999)
  flags=[]
  if x["likely_test_itinerary"].lower()=="true":flags.append("test_exclude")
  if len(family)>1:flags.append("shared_base_route_uuid")
  if name_family_match:flags.append("related_name_in_base_family")
  if len(candidate)>1:flags.append("multiple_direct_candidates")
  if not candidate:flags.append("no_direct_gtfs_candidate")
  if not rows:flags.append("no_staged_stop_sequence")
  if ";" in x["siu_company_names"]:flags.append("multi_operator")
  if rv.get("route_match_status"):flags.append(rv["route_match_status"])
  result.append({"siu_itinerary_uuid":uid,"siu_base_route_uuid":x["siu_base_route_uuid"],"siu_name":x["siu_display_name"],"normalized_name":name_norm,"siu_companies":x["siu_company_names"],"test_itinerary":x["likely_test_itinerary"],"base_family_size":len(family),"base_family_names":";".join(family_names),"name_related_within_family":"yes" if name_family_match else "no","direct_gtfs_candidates":";".join(sorted(candidate)),"family_gtfs_candidates":";".join(sorted(family_candidates)),"unknown_candidate_ids":";".join(sorted((candidate|family_candidates)-valid)),"gis_top_route":rv.get("candidate_amb_route_code",""),"gis_top_coverage_pct":rv.get("top_gis_coverage_pct",""),"gis_second_route":rv.get("second_gis_name",""),"gis_second_coverage_pct":rv.get("second_gis_coverage_pct",""),"staged_stop_visits":len(rows),"first_staged_stop":rows[0]["stop_name"] if rows else "","last_staged_stop":rows[-1]["stop_name"] if rows else "","source_first_stop":x.get("first_stop_name",""),"source_last_stop":x.get("last_stop_name",""),"flags":";".join(flags),"mapping_confirmed":"no"})
 fields=list(result[0])
 with (out/"all_36_siu_name_base_route_audit.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(result)
 families=[v for v in bybase.values() if len(v)>1]
 focus=[x for x in result if "SOLEDAD CALLE 84" in x["siu_name"].upper()]
 summary={"total_itineraries":len(result),"base_route_families":len(bybase),"families_with_multiple_itineraries":len(families),"test_itineraries":sum(x["test_itinerary"]=="true" for x in result),"siu_soledad_calle_84":focus,"warning":"Name/base UUID links are family evidence only. GIS percentages are historical candidates; no full shape comparison or confirmed GTFS mapping."}
 (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:v for k,v in summary.items() if k!="siu_soledad_calle_84"},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
