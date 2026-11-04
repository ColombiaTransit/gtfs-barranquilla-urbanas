#!/usr/bin/env python3
"""Derive reviewable GraphHopper via-point candidates from uploaded OSM snapshot.

Only consecutive named-street junctions are used; missing junctions are flagged,
not invented. Output is a planning manifest, NOT a validated GTFS shape.
"""
import argparse,csv,json,math,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def norm(s):
 return "".join(c for c in unicodedata.normalize("NFKD",s.casefold()) if not unicodedata.combining(c)).strip()
def xy(p):
 return (p[0]*109160,p[1]*111195)
def dist(a,b):return math.dist(xy(a),xy(b))
def nearest(p,a,b):
 x,y=xy(p);ax,ay=xy(a);bx,by=xy(b);dx=bx-ax;dy=by-ay
 t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy or 1)))
 return math.hypot(x-ax-t*dx,y-ay-t*dy),[a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--overpass",type=Path,required=True)
 ap.add_argument("--max-junction-distance-m",type=float,default=35)
 ap.add_argument("--output",type=Path,default=ROOT/"sources/amb/kmz/coolitoral_256_graphhopper_waypoints.json")
 args=ap.parse_args()
 elements=json.loads(args.overpass.read_text())["elements"]
 ways={}
 for e in elements:
  if e.get("type")!="way" or len(e.get("geometry",[]))<2:continue
  name=norm(e.get("tags",{}).get("name",""))
  if name:
   ways.setdefault(name,[]).append([[p["lon"],p["lat"]] for p in e["geometry"]])
 rows=list(csv.DictReader((ROOT/"sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv").open()))
 result={"source":str(args.overpass),"junction_tolerance_m":args.max_junction_distance_m,"routes":{}}
 for row in rows:
  code=row["route_code"]+"-"+row["itinerary"]
  streets=[x.strip() for x in row["main_street_sequence"].split(">")]
  junctions=[]
  for a,b in zip(streets,streets[1:]):
   left=ways.get(norm(a),[]);right=ways.get(norm(b),[])
   best=(float("inf"),None,None)
   for line in left:
    for other in right:
     # Vertex to opposite segment, in both directions. Candidate midpoint only.
     for p in line:
      for u,v in zip(other,other[1:]):
       d,q=nearest(p,u,v)
       if d<best[0]:best=(d,p,q)
     for p in other:
      for u,v in zip(line,line[1:]):
       d,q=nearest(p,u,v)
       if d<best[0]:best=(d,p,q)
   distance,p,q=best
   ok=distance<=args.max_junction_distance_m
   junctions.append({"from":a,"to":b,"status":"candidate" if ok else "missing_or_distant",
                     "distance_m":round(distance,1) if math.isfinite(distance) else None,
                     "point_lon_lat":[round((p[0]+q[0])/2,7),round((p[1]+q[1])/2,7)] if ok else None,
                     "ways_a":len(left),"ways_b":len(right)})
  result["routes"][code]={"junctions":junctions,"complete":all(j["status"]=="candidate" for j in junctions),
                           "warning":"Junction candidates require route-order and one-way review before GraphHopper routing."}
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 for code,route in result["routes"].items():
  print(code, "candidate junctions:",sum(j["status"]=="candidate" for j in route["junctions"]),"/",len(route["junctions"]))
if __name__=="__main__":main()
