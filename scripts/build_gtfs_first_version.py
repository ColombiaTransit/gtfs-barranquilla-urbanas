#!/usr/bin/env python3
"""First-pass static GTFS from reviewed SIU patterns, AMBQ headways and private GraphHopper.
The GraphHopper server URL is injected via GRAPHHOPPER_URL (organization variable).
A failed routing call never becomes a fabricated stop time.
"""
import csv, json, os, math, hashlib, zipfile, time
from collections import defaultdict, Counter
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import requests
import holidays
from datetime import date, timedelta

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/gtfs-v2"
def read(p):
 if not p.exists():return []
 with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write(p,rows,fields):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
def seconds(v):
 a=[int(x) for x in v.split(":")];return a[0]*3600+a[1]*60+(a[2] if len(a)>2 else 0)
def clock(v):
 return f"{v//3600:02d}:{v//60%60:02d}:{v%60:02d}"
def norm(v):
 import re
 return re.sub("[^A-Z0-9]","",str(v or "").upper())
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 routes=read(ROOT/"gtfs/routes.txt");agency=read(ROOT/"gtfs/agency.txt")
 decisions=read(ROOT/"sources/siu/open_route_review/siu_amb_crosswalk_visual_decisions_2026-11-05.csv")
 if len(decisions)!=33:raise ValueError("Expected 33 reviewed SIU decisions")
 reviews=read(ROOT/"sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv")
 itineraries=read(ROOT/"sources/siu/public_extract/siu_itineraries.csv")
 names=defaultdict(set)
 for x in reviews:
  if x.get("siu_name") and x.get("siu_itinerary_uuid"):names[norm(x["siu_name"])].add(x["siu_itinerary_uuid"])
 for x in itineraries:
  name=x.get("siu_display_name") or x.get("siu_name") or x.get("name") or ""
  uid=x.get("siu_itinerary_uuid") or x.get("itinerary_uuid") or ""
  if name and uid:names[norm(name)].add(uid)
 route_by_code=defaultdict(list)
 for r in routes:route_by_code[norm(r["route_short_name"])].append(r)
 assignments={};issues=[]
 for d in decisions:
  name=d["siu_name"];base=d.get("amb_base_candidate","");variant=d.get("operational_kmz_variant","")
  if not base or "|" in base:
   issues.append((name,"explicitly_unmapped_or_ambiguous"));continue
  matches=[r for r in routes if norm(r["route_short_name"])==norm(base)+(norm(variant) if variant else "")]
  if not variant and not matches:
   matches=[r for r in routes if norm(r["route_short_name"]).startswith(norm(base)) and norm(r["route_short_name"])[len(norm(base)):] in ("A","B")]
  if len(matches)!=1:
   issues.append((name,"route_id_ambiguous_or_missing"));continue
  uuids=names.get(norm(name),set())
  if len(uuids)!=1:
   issues.append((name,"siu_uuid_missing_or_ambiguous"));continue
  uid=next(iter(uuids))
  if uid in assignments and assignments[uid]!=matches[0]["route_id"]:
   issues.append((name,"siu_uuid_conflict"));continue
  assignments[uid]=matches[0]["route_id"]
 stops=read(ROOT/"sources/siu/gtfs_staging/candidate_stops.csv")
 by_stop={s["stop_id"]:s for s in stops if s.get("stop_id")}
 occurrences=read(ROOT/"sources/siu/gtfs_staging/siu_stop_occurrence_crosswalk.csv")
 by_it=defaultdict(list)
 for x in occurrences:by_it[x.get("siu_itinerary_uuid","")].append(x)
 headways={r["gtfs_route_id"]:r for r in read(ROOT/"sources/amb/gtfs_staging/route_headway_candidates.csv")}
 url=os.environ.get("GRAPHHOPPER_URL","").rstrip("/")
 if not url:raise SystemExit("GRAPHHOPPER_URL organization variable required for SIU stop_times")
 if url.endswith("/route"):endpoint=url
 else:endpoint=url+"/route"
 session=requests.Session()
 cache_file=OUT/"graphhopper_leg_cache.json"
 try:cache=json.loads(cache_file.read_text())
 except (OSError,ValueError):cache={}
 def leg(a,b):
  key=hashlib.sha256(json.dumps([a,b],separators=(",",":")).encode()).hexdigest()
  if key in cache:return cache[key]
  payload={"profile":os.getenv("GRAPHHOPPER_PROFILE","car"),"points":[[a[1],a[0]],[b[1],b[0]]],"points_encoded":False,"instructions":False,"calc_points":False}
  for attempt in range(3):
   try:
    res=session.post(endpoint,json=payload,timeout=40)
    res.raise_for_status()
    paths=res.json().get("paths",[])
    if not paths or paths[0].get("time") is None:raise ValueError("GraphHopper returned no path/time")
    duration=max(1,math.ceil(float(paths[0]["time"])/1000))
    cache[key]=duration
    return duration
   except (requests.RequestException,ValueError,KeyError):
    if attempt<2:time.sleep(2*(attempt+1))
  return None
 generated=[];times=[];frequencies=[];used_stops=set();used_routes=set();audit=[]
 for uid,rid in sorted(assignments.items()):
  ordered=sorted(by_it.get(uid,[]),key=lambda x:int(x.get("stop_sequence") or 0))
  if len(ordered)<2:
   issues.append((uid,"fewer_than_two_siu_stops"));continue
  ids=[x.get("candidate_stop_id","") for x in ordered]
  if any(i not in by_stop for i in ids):
   issues.append((uid,"missing_siu_stop_coordinates"));continue
  h=headways.get(rid,{})
  try:
   start=seconds(h["first_dispatch_model"]);end=seconds(h["last_dispatch_model"])
   peak=int(h.get("peak_headway_secs") or 0);offpeak=int(h.get("offpeak_headway_secs") or 0)
   if not (0<=start<end<=30*3600 and (peak>0 or offpeak>0)):raise ValueError()
  except (ValueError,KeyError):
   issues.append((uid,"missing_or_invalid_dispatch_window_or_headway"));continue
  coords=[]
  try:
   for i in ids:
    s=by_stop[i];coords.append((float(s["stop_lat"]),float(s["stop_lon"])))
  except (ValueError,TypeError):
   issues.append((uid,"invalid_stop_coordinate"));continue
  elapsed=[0];failed=False
  for a,b in zip(coords,coords[1:]):
   if a==b:duration=1
   else:duration=leg(a,b)
   if duration is None:
    issues.append((uid,"graphhopper_leg_failed"));failed=True;break
   elapsed.append(elapsed[-1]+duration)
  if failed:continue
  headway=offpeak or peak
  trip="SIU_"+hashlib.sha256(uid.encode()).hexdigest()[:16]
  generated.append({"route_id":rid,"service_id":"MODEL_DAILY","trip_id":trip})
  for n,(stop_id,offset) in enumerate(zip(ids,elapsed),1):
   times.append({"trip_id":trip,"arrival_time":clock(offset),"departure_time":clock(offset),"stop_id":stop_id,"stop_sequence":n})
   used_stops.add(stop_id)
  frequencies.append({"trip_id":trip,"start_time":clock(start),"end_time":clock(end),"headway_secs":headway,"exact_times":0})
  used_routes.add(rid)
  audit.append({"siu_itinerary_uuid":uid,"route_id":rid,"stop_count":len(ids),"travel_seconds":elapsed[-1],
                "headway_secs":headway,"dispatch_window_source_year":h.get("dispatch_window_source_year",""),
                "source_file":h.get("source_file",""),"timing_provenance":"graphhopper_model"})
 cache_file.write_text(json.dumps(cache))
 write(OUT/"graphhopper_siu_timing_audit.csv",audit,["siu_itinerary_uuid","route_id","stop_count","travel_seconds","headway_secs","dispatch_window_source_year","source_file","timing_provenance"])
 write(OUT/"first_version_held.csv",[{"name":a,"reason":b} for a,b in issues],["name","reason"])
 if not generated:
  (OUT/"first_version_summary.json").write_text(json.dumps({"trips":0,"held":len(issues),"reason":"No complete routable SIU trips"},indent=2))
  raise SystemExit("No SIU trips with complete GraphHopper travel times; no empty GTFS generated")

 # Official KMZ-based continuous boarding: two real geometry endpoints are the only anchors.
 # A fixed-route service with continuous_pickup/drop_off=0 is NOT demand-responsive booking.
 manifest=read(ROOT/"sources/amb/kmz/manifest.csv")
 kmz_index=defaultdict(list)
 for m in manifest:
  if m.get("status")=="geometry_imported":
   kmz_index[(norm(m.get("company")),norm(m.get("route_label")))].append(m)
 flex_audit=[];shape_rows=[];flex_count=0
 for r in routes:
  rid=r["route_id"]
  if rid in used_routes:continue
  h=headways.get(rid,{})
  try:
   first=seconds(h["first_dispatch_model"]);last=seconds(h["last_dispatch_model"])
   headway=int(h.get("offpeak_headway_secs") or h.get("peak_headway_secs") or 0)
   if not (0<=first<last<=30*3600 and headway>0):raise ValueError()
  except (ValueError,KeyError):
   issues.append((rid,"flex_missing_frequency_or_dispatch_window"));continue
  company=r.get("agency_id","").removeprefix("AMB_")
  candidates=kmz_index.get((norm(company),norm(r.get("route_short_name"))),[])
  if len(candidates)!=1:
   issues.append((rid,"flex_missing_or_ambiguous_official_kmz"));continue
  source=candidates[0]
  try:
   geo=json.loads((ROOT/"sources/amb/kmz"/source["geojson_path"]).read_text(encoding="utf-8"))
   lines=[]
   for feature in geo.get("features",[]):
    geom=feature.get("geometry") or {}
    if geom.get("type")=="LineString":lines.append(geom["coordinates"])
    elif geom.get("type")=="MultiLineString":lines.extend(geom["coordinates"])
   if len(lines)!=1 or len(lines[0])<2:raise ValueError("multipart_or_invalid")
   coords=lines[0]
   if any(len(p)<2 for p in coords):raise ValueError("invalid_coordinates")
  except (OSError,ValueError,KeyError,TypeError):
   issues.append((rid,"flex_invalid_or_multipart_kmz"));continue
  def haversine(a,b):
   p1,p2=math.radians(a[1]),math.radians(b[1])
   dp=p2-p1;dl=math.radians(b[0]-a[0])
   x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
   return 12742000*math.asin(min(1,math.sqrt(x)))
  distance=sum(haversine(a,b) for a,b in zip(coords,coords[1:]))
  if distance<100:
   issues.append((rid,"flex_geometry_too_short"));continue
  # Transparent first-version assumption: 18 km/h urban running speed.
  travel=max(60,math.ceil(distance/5))
  sid="KMZ_"+hashlib.sha256((rid+source.get("sha256","")).encode()).hexdigest()[:16]
  for n,p in enumerate(coords,1):
   shape_rows.append({"shape_id":sid,"shape_pt_lat":p[1],"shape_pt_lon":p[0],"shape_pt_sequence":n})
  a,b="KMZ_START_"+hashlib.sha256(rid.encode()).hexdigest()[:12],"KMZ_END_"+hashlib.sha256(rid.encode()).hexdigest()[:12]
  by_stop[a]={"stop_id":a,"stop_name":r["route_short_name"]+" - inicio de geometría","stop_lat":coords[0][1],"stop_lon":coords[0][0],"location_type":0}
  by_stop[b]={"stop_id":b,"stop_name":r["route_short_name"]+" - fin de geometría","stop_lat":coords[-1][1],"stop_lon":coords[-1][0],"location_type":0}
  trip="FLEX_"+hashlib.sha256(rid.encode()).hexdigest()[:16]
  generated.append({"route_id":rid,"service_id":"MODEL_DAILY","trip_id":trip,"shape_id":sid})
  times.extend([
   {"trip_id":trip,"arrival_time":"00:00:00","departure_time":"00:00:00","stop_id":a,"stop_sequence":1,"continuous_pickup":0,"continuous_drop_off":0},
   {"trip_id":trip,"arrival_time":clock(travel),"departure_time":clock(travel),"stop_id":b,"stop_sequence":2,"continuous_pickup":0,"continuous_drop_off":0}])
  frequencies.append({"trip_id":trip,"start_time":clock(first),"end_time":clock(last),"headway_secs":headway,"exact_times":0})
  used_stops.update((a,b));used_routes.add(rid);flex_count+=1
  flex_audit.append({"route_id":rid,"source_sha256":source.get("sha256",""),"shape_id":sid,"distance_m":round(distance),
    "model_travel_seconds":travel,"model_speed_kmh":18,"frequency_source":h.get("source_file",""),"source_year":h.get("dispatch_window_source_year","")})
 write(OUT/"continuous_boarding_generated_audit.csv",flex_audit,
  ["route_id","source_sha256","shape_id","distance_m","model_travel_seconds","model_speed_kmh","frequency_source","source_year"])
 # Colombian public holidays are modelled as Sunday-equivalent service exceptions.
 # Duplicate templates preserve distinct GTFS service IDs; do not double-count a holiday.
 calendar_start=date(2026,11,5);calendar_end=date(2027,12,31)
 calendar=[
  {"service_id":"MODEL_DAILY","monday":1,"tuesday":1,"wednesday":1,"thursday":1,"friday":1,"saturday":1,"sunday":1,"start_date":"20261105","end_date":"20271231"},
  {"service_id":"MODEL_HOLIDAY","monday":0,"tuesday":0,"wednesday":0,"thursday":0,"friday":0,"saturday":0,"sunday":0,"start_date":"20261105","end_date":"20271231"}]
 calendar_dates=[]
 for day in sorted(holidays.country_holidays("CO",years=[2026,2027])):
  if calendar_start<=day<=calendar_end:
   stamp=day.strftime("%Y%m%d")
   calendar_dates.extend([
    {"service_id":"MODEL_DAILY","date":stamp,"exception_type":2},
    {"service_id":"MODEL_HOLIDAY","date":stamp,"exception_type":1}])
 holiday_trips=[];holiday_times=[];holiday_freq=[]
 for trip in generated:
  copy=dict(trip);copy["trip_id"]=trip["trip_id"]+"_HOL";copy["service_id"]="MODEL_HOLIDAY";holiday_trips.append(copy)
 for st in times:
  copy=dict(st);copy["trip_id"]+="_HOL";holiday_times.append(copy)
 for freq in frequencies:
  copy=dict(freq);copy["trip_id"]+="_HOL";holiday_freq.append(copy)
 generated+=holiday_trips;times+=holiday_times;frequencies+=holiday_freq
 write(OUT/"first_version_held.csv",[{"name":a,"reason":b} for a,b in issues],["name","reason"])

 folder=OUT/"first-version";folder.mkdir(exist_ok=True)
 tables={
  "agency.txt":(agency,["agency_id","agency_name","agency_url","agency_timezone"]),
  "routes.txt":([r for r in routes if r["route_id"] in used_routes],["route_id","agency_id","route_short_name","route_long_name","route_type"]),
  "stops.txt":([by_stop[k] for k in sorted(used_stops)],["stop_id","stop_name","stop_lat","stop_lon","location_type"]),
  "trips.txt":(generated,["route_id","service_id","trip_id","shape_id"]),
  "stop_times.txt":(times,["trip_id","arrival_time","departure_time","stop_id","stop_sequence","continuous_pickup","continuous_drop_off"]),
  "frequencies.txt":(frequencies,["trip_id","start_time","end_time","headway_secs","exact_times"]),
  "calendar.txt":(calendar,["service_id","monday","tuesday","wednesday","thursday","friday","saturday","sunday","start_date","end_date"]),
  "calendar_dates.txt":(calendar_dates,["service_id","date","exception_type"]),
  "shapes.txt":(shape_rows,["shape_id","shape_pt_lat","shape_pt_lon","shape_pt_sequence"])
 }
 for name,(rows,fields) in tables.items():write(folder/name,rows,fields)
 with zipfile.ZipFile(OUT/"gtfs-first-version.zip","w",zipfile.ZIP_DEFLATED) as z:
  for name in tables:z.write(folder/name,name)
 summary={"gtfs_zip":"gtfs-first-version.zip","status":"MODEL_NOT_VERIFIED_FOR_PUBLICATION",
  "siu_trip_templates":len(audit),"continuous_boarding_route_templates":flex_count,"holiday_exception_dates":len(calendar_dates)//2,"routes":len(used_routes),"stops":len(used_stops),"stop_times":len(times),
  "held":len(issues),"notes":"GraphHopper SIU travel times; 18 km/h geometry-based flex model; holiday schedule currently duplicates daily headways; source dispatch windows may be historical"}
 (OUT/"first_version_summary.json").write_text(json.dumps(summary,indent=2))
 print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
