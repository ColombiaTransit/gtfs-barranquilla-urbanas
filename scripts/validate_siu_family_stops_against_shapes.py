#!/usr/bin/env python3
"""Research-only SIU stop-to-road-shape alignment for shared SIU route families.
GH shapes are a *proxy* for AMB KMZ; no legal route match or stop is auto-approved.
"""
import csv,json,math,argparse
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
def read(p):
 with (ROOT/p).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def coords(row):
 for lat,lon in (("stop_lat","stop_lon"),("lat","lon"),("latitude","longitude")):
  try:
   a=float(row[lat]);b=float(row[lon])
   if 9<a<12 and -76<b<-73:return (b,a)
  except (KeyError,ValueError,TypeError):pass
 return None
def dist(p,a,b):
 # local equirectangular approximation, metres; segment projection
 kx=109600;ky=111195
 px,py=p[0]*kx,p[1]*ky;ax,ay=a[0]*kx,a[1]*ky;bx,by=b[0]*kx,b[1]*ky
 dx=bx-ax;dy=by-ay
 t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
 return math.hypot(px-ax-t*dx,py-ay-t*dy)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",default="build/siu-family-shape-validation");args=ap.parse_args()
 out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 its=read(ROOT/"sources/siu/public_extract/siu_itineraries.csv")
 review={x["siu_itinerary_uuid"]:x for x in read(ROOT/"sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv")}
 stops=read(ROOT/"sources/siu/gtfs_staging/candidate_stops.csv")
 stopmap={x["stop_id"]:coords(x) for x in stops}
 visits=defaultdict(list)
 for x in read(ROOT/"sources/siu/gtfs_staging/candidate_route_stop_orders_NO_TIMES.csv"):visits[x["siu_itinerary_uuid"]].append(x)
 families=defaultdict(list)
 for x in its:families[x["siu_base_route_uuid"]].append(x)
 target=[x for v in families.values() if len(v)>1 for x in v if x.get("likely_test_itinerary")!="true"]
 patterns=read(ROOT/"sources/amb/missing_siu_trip_stop_patterns/trip_patterns_MISSING_SIU_NO_TIMES.csv")
 bycode=defaultdict(list)
 for p in patterns:bycode[p["official_route_label"].replace(" ","").upper()].append(p)
 source=ROOT/"sources/amb/GH_combined_bus_road_geometry/GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson"
 geo=json.loads(source.read_text(encoding="utf-8"))
 sections=defaultdict(list)
 for feat in geo["features"]:
  pr=feat["properties"]
  if feat["geometry"]["type"]=="LineString":sections[pr["trip_pattern_id"]].append((int(pr["section"]),feat["geometry"]["coordinates"]))
 results=[];stop_results=[]
 for x in target:
  uid=x["siu_itinerary_uuid"];rv=review.get(uid,{})
  codes=[rv.get("candidate_amb_route_code","")]
  for field in ("second_gis_name",):
   s=rv.get(field,"").split(" ")[0];codes.append(s)
  candidate=[]
  for code in codes:
   for p in bycode.get(code.replace(" ","").upper(),[]):
    if p["trip_pattern_id"] not in [z["trip_pattern_id"] for z in candidate]:candidate.append(p)
  v=sorted(visits[uid],key=lambda z:int(z["stop_sequence"]))
  for p in candidate:
   shape=[]
   for _,points in sorted(sections.get(p["trip_pattern_id"],[])):shape.extend(points)
   segments=list(zip(shape,shape[1:]))
   distances=[]
   for s in v:
    pos=stopmap.get(s["stop_id"])
    d=min((dist(pos,a,b) for a,b in segments),default=None) if pos else None
    if d is not None:distances.append(d)
    stop_results.append({"siu_itinerary_uuid":uid,"siu_name":x["siu_display_name"],"candidate_pattern_id":p["trip_pattern_id"],"candidate_official_route_label":p["official_route_label"],"stop_sequence":s["stop_sequence"],"stop_id":s["stop_id"],"stop_name":s["stop_name"],"distance_to_GH_proxy_m":round(d,1) if d is not None else "","within_50m":"yes" if d is not None and d<=50 else "no" if d is not None else "unknown","evidence":"GH road shape proxy; NOT direct official KMZ validation"})
   distances.sort()
   results.append({"siu_itinerary_uuid":uid,"siu_base_route_uuid":x["siu_base_route_uuid"],"siu_name":x["siu_display_name"],"siu_companies":x["siu_company_names"],"candidate_pattern_id":p["trip_pattern_id"],"candidate_official_route_label":p["official_route_label"],"candidate_company":p["company"],"siu_visits_in_staging":len(v),"visits_with_coordinates":len(distances),"shape_points":len(shape),"stop_coverage_50m_pct":round(100*sum(d<=50 for d in distances)/len(distances),1) if distances else "","stop_coverage_100m_pct":round(100*sum(d<=100 for d in distances)/len(distances),1) if distances else "","median_distance_m":round(distances[len(distances)//2],1) if distances else "","p90_distance_m":round(distances[min(len(distances)-1,int(len(distances)*.9))],1) if distances else "","status":"research_candidate_only_not_official_kmz","notes":"GH proxy; SIU stop visits may include both directions; no automatic GTFS confirmation"})
 def write(name,rows,fields):
  with (out/name).open("w",encoding="utf-8",newline="") as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 write("family_shape_candidate_scores.csv",results,["siu_itinerary_uuid","siu_base_route_uuid","siu_name","siu_companies","candidate_pattern_id","candidate_official_route_label","candidate_company","siu_visits_in_staging","visits_with_coordinates","shape_points","stop_coverage_50m_pct","stop_coverage_100m_pct","median_distance_m","p90_distance_m","status","notes"])
 write("siu_stop_to_shape_distances.csv",stop_results,["siu_itinerary_uuid","siu_name","candidate_pattern_id","candidate_official_route_label","stop_sequence","stop_id","stop_name","distance_to_GH_proxy_m","within_50m","evidence"])
 summary={"multi_itinerary_families":sum(len(v)>1 for v in families.values()),"non_test_itineraries_in_multi_families":len(target),"candidate_pattern_comparisons":len(results),"itineraries_with_geometry_candidate":len(set(x["siu_itinerary_uuid"] for x in results)),"unmatched_itineraries":[{"uuid":x["siu_itinerary_uuid"],"name":x["siu_display_name"]} for x in target if x["siu_itinerary_uuid"] not in {z["siu_itinerary_uuid"] for z in results}],"warning":"Only GH proxy geometry is compared. No official KMZ comparison, GTFS publication, or final route assignment."}
 (out/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps(summary,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
