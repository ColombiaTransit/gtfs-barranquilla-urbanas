#!/usr/bin/env python3
"""AMB GTFS v2: source-first, non-synthetic schedule/Flex builder and RT contract.

Never guesses trip starts, terminals, service calendars, trip patterns or SIU mappings.
Inputs are explicit reviewed CSVs; the legacy synthetic pilot is not an input.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,zipfile
from datetime import date, timedelta
import holidays
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"sources/amb/gtfs_v2"
TABLES={
 "agency":["agency_id","agency_name","agency_url","agency_timezone"],
 "routes":["route_id","agency_id","route_short_name","route_type"],
 "stops":["stop_id","stop_name","stop_lat","stop_lon"],
 "trips":["route_id","service_id","trip_id"],
 "stop_times":["trip_id","arrival_time","departure_time","stop_id","stop_sequence"],
 "calendar":["service_id","monday","tuesday","wednesday","thursday","friday","saturday","sunday","start_date","end_date"],
 "calendar_dates":["service_id","date","exception_type"],
 "frequencies":["trip_id","start_time","end_time","headway_secs","exact_times"],
 "shapes":["shape_id","shape_pt_lat","shape_pt_lon","shape_pt_sequence"],
 "locations.geojson":[],
 "booking_rules":["booking_rule_id"],
 "location_groups":["location_group_id","location_group_name"],
 "location_group_stops":["location_group_id","stop_id"],
 "attributions":["organization_name","is_operator"],
 "feed_info":["feed_publisher_name","feed_publisher_url","feed_lang","feed_version"]
}
def read(path):
 if not path.is_file():return []
 with path.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def write(path,rows,fields):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)

def generate_holiday_exceptions(calendar, mapping, existing):
 """Apply reviewed Colombian holiday -> Sunday/holiday service mappings only."""
 by_id={r["service_id"]:r for r in calendar}
 result={(r["service_id"],r["date"]):r for r in existing}
 for rule in mapping:
  if rule.get("review_status")!="approved":continue
  regular=rule.get("regular_service_id","")
  holiday=rule.get("holiday_service_id","")
  if regular not in by_id or holiday not in by_id:
   raise ValueError("Holiday mapping references unknown service_id")
  src=by_id[regular];dst=by_id[holiday]
  start=max(date.fromisoformat(src["start_date"][:4]+"-"+src["start_date"][4:6]+"-"+src["start_date"][6:]),date.fromisoformat(dst["start_date"][:4]+"-"+dst["start_date"][4:6]+"-"+dst["start_date"][6:]))
  end=min(date.fromisoformat(src["end_date"][:4]+"-"+src["end_date"][4:6]+"-"+src["end_date"][6:]),date.fromisoformat(dst["end_date"][:4]+"-"+dst["end_date"][4:6]+"-"+dst["end_date"][6:]))
  if start>end:continue
  days=holidays.country_holidays("CO",years=range(start.year,end.year+1))
  for day in sorted(days):
   if not start<=day<=end:continue
   key=day.strftime("%Y%m%d")
   weekday=("monday","tuesday","wednesday","thursday","friday","saturday","sunday")[day.weekday()]
   if src[weekday]=="1":result.setdefault((regular,key),{"service_id":regular,"date":key,"exception_type":"2"})
   if dst[weekday]!="1":result.setdefault((holiday,key),{"service_id":holiday,"date":key,"exception_type":"1"})
 return sorted(result.values(),key=lambda r:(r["date"],r["service_id"]))

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--registry",type=Path,default=REG);ap.add_argument("--out",type=Path,default=ROOT/"build/gtfs-v2");ap.add_argument("--publish",action="store_true");args=ap.parse_args()
 out=args.out;out.mkdir(parents=True,exist_ok=True);registry=args.registry
 routes=read(ROOT/"gtfs/routes.txt");agencies=read(ROOT/"gtfs/agency.txt")
 kmz=read(ROOT/"sources/amb/kmz/manifest.csv")
 pattern=read(registry/"trip_pattern_registry.csv")
 shape_crosswalk=read(registry/"shape_source_crosswalk.csv")
 service=read(registry/"service_templates.csv")
 visits=read(registry/"pattern_stop_visits.csv")
 stop_crosswalk=read(registry/"siu_stop_crosswalk.csv")
 rt_crosswalk=read(registry/"siu_realtime_crosswalk.csv")
 flex_scope=read(registry/"flex_scope.csv")
 checks=[];held=[];shapes=[];contract=[]
 def hold(kind,key,reason):held.append({"kind":kind,"id":key,"reason":reason})
 sources={(x.get("company","").upper(),x.get("route_label","").upper()):x for x in kmz if x.get("status")=="geometry_imported"}
 route_ids={x["route_id"] for x in routes}
 # Geometry from current manifest, never historical GH fallback.
 for x in shape_crosswalk:
  rid=x.get("route_id","");sid=x.get("shape_id","");state=x.get("review_status","")
  if rid not in route_ids or not sid or state!="approved":
   hold("shape",rid or sid,"route_missing_or_shape_not_approved");continue
  if x.get("geometry_review")=="DEFERRED_GEOMETRY_REVIEW":
   hold("shape",sid,"deferred_geometry_review");continue
  source=sources.get((x.get("company","").upper(),x.get("route_label","").upper()))
  if not source:hold("shape",sid,"current_official_KMZ_missing");continue
  geo=ROOT/"sources/amb/kmz"/source["geojson_path"]
  if not geo.is_file():hold("shape",sid,"KMZ_GeoJSON_not_materialized");continue
  data=json.loads(geo.read_text(encoding="utf-8"))
  features=[f for f in data.get("features",[]) if f.get("geometry",{}).get("type")=="LineString"]
  if len(features)!=1:
   hold("shape",sid,"multipart_requires_explicit_order_and_direction");continue
  coords=features[0]["geometry"]["coordinates"]
  if x.get("direction")=="reverse":coords=list(reversed(coords))
  elif x.get("direction")!="forward":hold("shape",sid,"direction_not_reviewed");continue
  if len(coords)<2:hold("shape",sid,"invalid_linestring");continue
  for i,p in enumerate(coords,1):shapes.append({"shape_id":sid,"shape_pt_lat":p[1],"shape_pt_lon":p[0],"shape_pt_sequence":i})
 shape_ids={x["shape_id"] for x in shapes}
 patterns={x.get("pattern_id"):x for x in pattern if x.get("review_status")=="approved" and x.get("pattern_id")}
 stopids={x["gtfs_stop_id"] for x in stop_crosswalk if x.get("review_status")=="approved" and x.get("gtfs_stop_id")}
 stop_rows=read(registry/"stops.csv")
 stops={x["stop_id"] for x in stop_rows}
 if stopids-stops:hold("stops","crosswalk","approved_stop_id_not_in_stops_csv")
 for x in flex_scope:
  if x.get("continuous_pickup")=="0" or x.get("continuous_drop_off")=="0":
   if x.get("review_status")!="approved":hold("flex",x.get("route_id",""),"continuous_boarding_scope_unapproved")
 # Apply reviewed continuous-boarding scope without treating fixed-route service as demand-responsive Flex.
 scope_by_route={x.get("route_id"):x for x in flex_scope if x.get("review_status")=="approved"}
 for route in routes:
  scope=scope_by_route.get(route["route_id"])
  if scope:
   for field in ("continuous_pickup","continuous_drop_off"):
    if scope.get(field) in ("0","1","2","3"):route[field]=scope[field]
 # Strictly no trips until explicitly reviewed, with real or explicitly modelled timing templates.
 triprows=[];stoprows=[];freqrows=[]
 for t in service:
  pid=t.get("pattern_id","");p=patterns.get(pid);trip=t.get("trip_id","")
  if not p or not trip or t.get("review_status")!="approved":
   hold("service",trip or pid,"template_or_pattern_not_approved");continue
  if p.get("shape_id") not in shape_ids or p.get("route_id") not in route_ids:
   hold("service",trip,"shape_or_route_unavailable");continue
  v=sorted((z for z in visits if z.get("pattern_id")==pid),key=lambda z:int(z.get("stop_sequence") or 0))
  if len(v)<2 or any(z.get("gtfs_stop_id") not in stops or not z.get("arrival_time") or not z.get("departure_time") for z in v):
   hold("service",trip,"stop_sequence_or_template_times_missing");continue
  if t.get("timing_provenance") not in ("verified","explicit_model"):
   hold("service",trip,"timing_provenance_missing");continue
  if not all(t.get(k) for k in ("service_id","start_time","end_time","headway_secs")):
   hold("service",trip,"frequency_window_missing");continue
  try:
   if int(t["headway_secs"])<=0 or t["start_time"]>=t["end_time"]:raise ValueError()
  except ValueError:hold("service",trip,"invalid_frequency");continue
  triprows.append({"trip_id":trip,"route_id":p["route_id"],"service_id":t["service_id"],"shape_id":p["shape_id"],"direction_id":p.get("direction_id","")})
  for z in v:stoprows.append({"trip_id":trip,"stop_id":z["gtfs_stop_id"],"stop_sequence":z["stop_sequence"],"arrival_time":z["arrival_time"],"departure_time":z["departure_time"]})
  freqrows.append({"trip_id":trip,"start_time":t["start_time"],"end_time":t["end_time"],"headway_secs":t["headway_secs"],"exact_times":"0"})
  contract.append({"pattern_id":pid,"trip_id":trip,"route_id":p["route_id"],"service_id":t["service_id"],"direction_id":p.get("direction_id",""),"shape_id":p["shape_id"],"siu_itinerary_uuid":p.get("siu_itinerary_uuid",""),"stop_sequence_signature":hashlib.sha256("|".join(z["gtfs_stop_id"]+":"+z["stop_sequence"] for z in v).encode()).hexdigest()[:20],"match_status":"STATIC_ONLY","feed_version":""})

 # Consolidate available official sources into route-level QA, without granting shape/trip approval.
 import re
 def norm(v):return re.sub(r"[^A-Z0-9]","",str(v or "").upper())
 kmz_index=defaultdict(list)
 for item in kmz:
  if item.get("status")=="geometry_imported":
   kmz_index[(norm(item.get("company")),norm(item.get("route_label")))].append(item)
 headways=defaultdict(list)
 for item in read(ROOT/"sources/amb/gtfs_staging/route_headway_candidates.csv"):
  headways[item.get("gtfs_route_id","")].append(item)
 source_coverage=[]
 for route in routes:
  rid=route["route_id"]
  company=route.get("agency_id","").removeprefix("AMB_")
  matches=kmz_index.get((norm(company),norm(route.get("route_short_name"))),[])
  h=headways.get(rid,[])
  status="exact_source_match" if len(matches)==1 else "ambiguous_source_match" if len(matches)>1 else "mapping_review_required"
  if rid in ("AMB_COOLITORAL_A4_4109","AMB_LOLAYA_D8_4165"):status="deferred_geometry_review"
  candidate=matches[0] if len(matches)==1 else {}
  frequency=h[0] if len(h)==1 else {}
  source_coverage.append({
   "route_id":rid,"agency_id":route.get("agency_id",""),"route_short_name":route.get("route_short_name",""),
   "kmz_match_status":status,"kmz_match_count":len(matches),
   "kmz_company":candidate.get("company",""),"kmz_route_label":candidate.get("route_label",""),
   "kmz_geojson_path":candidate.get("geojson_path",""),"kmz_sha256":candidate.get("sha256",""),
   "kmz_linestring_count":candidate.get("linestring_count",""),
   "headway_match_count":len(h),"peak_headway_secs":frequency.get("peak_headway_secs",""),
   "offpeak_headway_secs":frequency.get("offpeak_headway_secs",""),
   "headway_source_type":frequency.get("source_type",""),
   "headway_source_file":frequency.get("source_file",""),
   "first_dispatch_model":frequency.get("first_dispatch_model",""),
   "last_dispatch_model":frequency.get("last_dispatch_model",""),
   "headway_staging_status":frequency.get("period_staging_status",""),
   "headway_blockers":frequency.get("blockers",""),
   "shape_approved":"yes" if any(z.get("route_id")==rid and z.get("review_status")=="approved" for z in shape_crosswalk) else "no",
   "trip_approved":"yes" if any(z.get("route_id")==rid and z.get("review_status")=="approved" for z in pattern) else "no",
   "publication_status":"research_only"
  })
 write(out/"source_coverage.csv",source_coverage,list(source_coverage[0]))

 # Research-only geometry: exact KMZ matches, single LineString only, preserving source order.
 # A/B direction and multipart sequencing remain unapproved until reviewed.
 geometry_candidates=[];pattern_candidates=[]
 for row in source_coverage:
  if row["kmz_match_status"]!="exact_source_match":continue
  source=ROOT/"sources/amb/kmz"/row["kmz_geojson_path"]
  if not source.is_file():continue
  obj=json.loads(source.read_text(encoding="utf-8"))
  lines=[]
  for feature in obj.get("features",[]):
   geom=feature.get("geometry") or {}
   if geom.get("type")=="LineString":lines.append(geom.get("coordinates") or [])
   elif geom.get("type")=="MultiLineString":lines.extend(geom.get("coordinates") or [])
  if len(lines)!=1 or len(lines[0])<2:continue
  sid="KMZ_CAND_"+hashlib.sha256((row["route_id"]+":"+row["kmz_sha256"]).encode()).hexdigest()[:16]
  for i,point in enumerate(lines[0],1):
   if len(point)>=2:geometry_candidates.append({"shape_id":sid,"route_id":row["route_id"],"shape_pt_lat":point[1],"shape_pt_lon":point[0],"shape_pt_sequence":i,"review_status":"candidate_unverified_direction","source_sha256":row["kmz_sha256"]})
 # SIU stop sequences are provisional. Retain itinerary identity, repeated visits, and provenance.
 siu_orders=read(ROOT/"sources/siu/gtfs_staging/candidate_route_stop_orders_NO_TIMES.csv")
 siu_reviews={x.get("siu_itinerary_uuid"):x for x in read(ROOT/"sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv")}
 valid_route_ids={x["route_id"] for x in routes}
 for visit in siu_orders:
  review=siu_reviews.get(visit.get("siu_itinerary_uuid"),{})
  rid=review.get("suggested_gtfs_route_id","")
  if rid not in valid_route_ids:continue
  pattern_candidates.append({"route_id":rid,"siu_itinerary_uuid":visit.get("siu_itinerary_uuid",""),
   "stop_sequence":visit.get("stop_sequence",""),"siu_stop_id":visit.get("stop_id",""),
   "stop_name":visit.get("stop_name",""),"route_match_status":review.get("route_match_status",""),
   "mapping_confirmed":review.get("final_gtfs_route_mapping_confirmed","no"),
   "review_status":"candidate_not_approved"})
 write(out/"kmz_shapes_research.csv",geometry_candidates,["shape_id","route_id","shape_pt_lat","shape_pt_lon","shape_pt_sequence","review_status","source_sha256"])
 write(out/"siu_pattern_stop_visits_research.csv",pattern_candidates,["route_id","siu_itinerary_uuid","stop_sequence","siu_stop_id","stop_name","route_match_status","mapping_confirmed","review_status"])

 feed_version=hashlib.sha256(json.dumps({"routes":routes,"patterns":pattern,"services":service,"stops":stop_rows},sort_keys=True).encode()).hexdigest()[:16]
 for x in contract:x["feed_version"]=feed_version
 write(out/"gtfs_rt_static_contract.csv",contract,["pattern_id","trip_id","route_id","service_id","direction_id","shape_id","siu_itinerary_uuid","stop_sequence_signature","match_status","feed_version"])
 write(out/"held.csv",held,["kind","id","reason"])
 write(out/"shapes_candidate.csv",shapes,TABLES["shapes"])
 summary={"kmz_imported":len(sources),"source_exact_matches":sum(x["kmz_match_status"]=="exact_source_match" for x in source_coverage),"source_mapping_reviews":sum(x["kmz_match_status"]=="mapping_review_required" for x in source_coverage),"source_deferred":sum(x["kmz_match_status"]=="deferred_geometry_review" for x in source_coverage),"headway_source_matches":sum(x["headway_match_count"]==1 for x in source_coverage),"gtfs_routes":len(routes),"research_shape_points":len(geometry_candidates),"research_shape_ids":len({x["shape_id"] for x in geometry_candidates}),"research_siu_stop_visits":len(pattern_candidates),"candidate_shapes":len(shape_ids),"approved_trip_templates":len(triprows),"held":dict(Counter(x["reason"] for x in held)),"flex_scope_records":len(flex_scope),"siu_rt_crosswalk_records":len(rt_crosswalk),"feed_version":feed_version,"published":False}
 # Flex optional tables are copied only from reviewed, explicit source files; no fabricated polygons.
 for table in ("booking_rules","location_groups","location_group_stops"):
  rows=read(registry/(table+".txt"))
  if rows:write(out/(table+".txt"),rows,list(rows[0]))
 geo=registry/"locations.geojson"
 if geo.exists():
  obj=json.loads(geo.read_text(encoding="utf-8"))
  if obj.get("type")!="FeatureCollection":raise ValueError("Invalid Flex locations GeoJSON")
  (out/"locations.geojson").write_text(json.dumps(obj,ensure_ascii=False))
 (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 if args.publish:
  # Publication must never succeed with missing reviewed calendar, stops, or incomplete source coverage.
  calendar=read(registry/"calendar.txt")
  holiday_map=read(registry/"holiday_service_map.csv")
  calendar_dates=generate_holiday_exceptions(calendar,holiday_map,read(registry/"calendar_dates.txt"))
  if any(x.get("continuous_pickup")=="2" or x.get("continuous_drop_off")=="2" for x in routes) and not (registry/"booking_rules.txt").is_file():
   raise SystemExit("Flex booking rule required for on-demand scope")
  if held or not triprows or not calendar or not stop_rows or not shapes or len(patterns)!=len(triprows):
   raise SystemExit("Publication gate blocked; inspect held.csv and required calendar/stops/shape coverage")
  folder=out/"publish";folder.mkdir(exist_ok=True)
  files={"agency.txt":agencies,"routes.txt":routes,"stops.txt":stop_rows,"trips.txt":triprows,"stop_times.txt":stoprows,"frequencies.txt":freqrows,"calendar.txt":calendar,"shapes.txt":shapes}
  if calendar_dates:files["calendar_dates.txt"]=calendar_dates
  for name,rows in files.items():write(folder/name,rows,list(dict.fromkeys(list(rows[0])+[k for row in rows for k in row])))
  for optional in ("booking_rules.txt","location_groups.txt","location_group_stops.txt","locations.geojson"):
   source=out/optional
   if source.is_file(): (folder/optional).write_bytes(source.read_bytes())
  with zipfile.ZipFile(out/"gtfs.zip","w",zipfile.ZIP_DEFLATED) as z:
   for name in files:z.write(folder/name,name)
   for optional in ("booking_rules.txt","location_groups.txt","location_group_stops.txt","locations.geojson"):
    if (folder/optional).is_file():z.write(folder/optional,optional)
  summary["published"]=True;(out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
