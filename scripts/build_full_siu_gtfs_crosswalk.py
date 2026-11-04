#!/usr/bin/env python3
"""Complete SIU itinerary inventory and candidate GTFS crosswalk; never auto-confirm."""
import csv,json,argparse
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):
 with (ROOT/p).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",default="build/siu-gtfs-crosswalk");args=ap.parse_args()
 out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 itineraries=load("sources/siu/public_extract/siu_itineraries.csv")
 reviews=load("sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv")
 stop_orders=load("sources/siu/gtfs_staging/candidate_route_stop_orders_NO_TIMES.csv")
 routes=load("gtfs/routes.txt")
 known={x["route_id"] for x in routes};by_review=defaultdict(list);by_stops=defaultdict(list)
 for x in reviews:by_review[x["siu_itinerary_uuid"]].append(x)
 for x in stop_orders:by_stops[x["siu_itinerary_uuid"]].append(x)
 rows=[];seen=set()
 for x in itineraries:
  uid=x["siu_itinerary_uuid"]
  if uid in seen:raise ValueError("Duplicate SIU itinerary UUID: "+uid)
  seen.add(uid);rr=by_review[uid];ss=by_stops[uid]
  candidate=set();methods=[]
  for z in rr:
   for field in ("suggested_gtfs_route_id","same_company_gtfs_ids"):
    candidate.update(t.strip() for t in z.get(field,"").split(";") if t.strip())
  candidate.update(t["route_id"] for t in ss if t.get("route_id"))
  candidate=sorted(candidate)
  unknown=sorted(set(candidate)-known)
  if rr:methods.append("gis_crosswalk")
  if ss:methods.append("staged_stop_order")
  confirmed=[z["suggested_gtfs_route_id"] for z in rr if z.get("final_gtfs_route_mapping_confirmed","").lower()=="yes" and z.get("suggested_gtfs_route_id") in known]
  flags=[]
  if not rr:flags.append("missing_in_33_row_gis_review")
  if not candidate:flags.append("no_gtfs_candidate")
  if unknown:flags.append("candidate_route_id_not_in_gtfs_routes")
  if len(candidate)>1:flags.append("multiple_candidate_routes")
  if not confirmed:flags.append("no_final_mapping_confirmation")
  if x.get("likely_test_itinerary","").lower()=="true":flags.append("test_itinerary_review")
  if ";" in x.get("siu_company_names",""):flags.append("shared_operators_review")
  if not ss:flags.append("no_staged_stop_order")
  rows.append({"siu_itinerary_uuid":uid,"siu_base_route_uuid":x["siu_base_route_uuid"],"siu_display_name":x["siu_display_name"],"siu_company_names":x["siu_company_names"],"siu_active":x.get("siu_active",""),"likely_test_itinerary":x.get("likely_test_itinerary",""),"siu_stop_count":x.get("stop_count",""),"gis_review_status":"present" if rr else "missing","gis_route_match_status":";".join(sorted(set(z.get("route_match_status","") for z in rr))),"candidate_gtfs_route_ids":";".join(candidate),"candidate_count":len(candidate),"unknown_gtfs_route_ids":";".join(unknown),"staged_stop_order_rows":len(ss),"evidence_methods":";".join(methods),"final_gtfs_route_id":confirmed[0] if len(set(confirmed))==1 else "","mapping_confirmed":"yes" if len(set(confirmed))==1 else "no","review_flags":";".join(flags),"source_siu_snapshot_utc":x.get("source_snapshot_utc",""),"source_siu":"sources/siu/public_extract/siu_itineraries.csv","source_gis":"sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv","source_stops":"sources/siu/gtfs_staging/candidate_route_stop_orders_NO_TIMES.csv"})
 missing_review=sorted(set(by_review)-seen);missing_stops=sorted(set(by_stops)-seen)
 fields=list(rows[0]);dest=out/"siu_to_gtfs_full_crosswalk.csv"
 with dest.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 summary={"siu_itineraries":len(rows),"gis_review_rows":len(reviews),"itineraries_with_candidates":sum(bool(z["candidate_count"]) for z in rows),"itineraries_without_candidates":sum(not z["candidate_count"] for z in rows),"itineraries_with_multiple_candidates":sum(z["candidate_count"]>1 for z in rows),"confirmed_mappings":sum(z["mapping_confirmed"]=="yes" for z in rows),"siu_missing_from_review":sum(z["gis_review_status"]=="missing" for z in rows),"review_uuids_missing_from_latest_siu":missing_review,"staged_stop_uuids_missing_from_latest_siu":missing_stops,"note":"All candidates provisional; no mapping approved automatically."}
 (out/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 (out/"summary.md").write_text("# Complete SIU → GTFS candidate crosswalk\n\n"+"\n".join(f"- {k}: {v}" for k,v in summary.items())+"\n\nNo candidate is auto-confirmed.\n",encoding="utf-8")
 print(json.dumps(summary,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
