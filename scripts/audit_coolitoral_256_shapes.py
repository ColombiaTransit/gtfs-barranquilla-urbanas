#!/usr/bin/env python3
"""Audit provisional GraphHopper shapes against legal street order; never certify GTFS."""
import csv,json,math,unicodedata
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def norm(s):
 return "".join(c for c in unicodedata.normalize("NFKD",s.casefold()) if not unicodedata.combining(c)).strip()
def meters(a,b):
 lat=math.radians((a[1]+b[1])/2)
 return math.hypot((a[0]-b[0])*111195*math.cos(lat),(a[1]-b[1])*111195)
def main():
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument("--overpass",type=Path,required=True)
 p.add_argument("--shapes",type=Path,default=ROOT/"sources/amb/kmz/graphhopper_candidates")
 a=p.parse_args()
 rows=list(csv.DictReader((ROOT/"sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv").open()))
 wanted={norm(n.strip()) for row in rows for n in row["main_street_sequence"].split(">")}
 grid=defaultdict(list)
 # A small spatial grid keeps nearest-road matching tractable on full Overpass extracts.
 for way in json.loads(a.overpass.read_text())["elements"]:
  name=norm(way.get("tags",{}).get("name",""))
  if name not in wanted:continue
  for pt in way.get("geometry",[]):
   xy=(pt["lon"],pt["lat"]);key=(round(xy[0]*1000),round(xy[1]*1000))
   grid[key].append((name,xy))
 result={}
 for row in rows:
  code=row["route_code"]+"-"+row["itinerary"]
  f=a.shapes/(code+".geojson")
  if not f.exists():
   result[code]={"status":"no_shape"};continue
  doc=json.loads(f.read_text())
  line=doc["features"][0]["geometry"]["coordinates"]
  # Sample every <=100m of existing vertices; only observations within 80m count.
  sample=[line[0]]
  for pt in line[1:]:
   if meters(sample[-1],pt)>=50:sample.append(pt)
  if sample[-1]!=line[-1]:sample.append(line[-1])
  observations=[]
  for i,pt in enumerate(sample):
   key=(round(pt[0]*1000),round(pt[1]*1000))
   near={}
   for x in range(key[0]-2,key[0]+3):
    for y in range(key[1]-2,key[1]+3):
     for name,xy in grid.get((x,y),()):
      d=meters(pt,xy)
      if d<near.get(name,float("inf")):near[name]=d
   observations.append({name for name,d in near.items() if d<=80})
  names=[norm(x.strip()) for x in row["main_street_sequence"].split(">")]
  # Greedy ordered matching: diagnostic only, not proof of traversal.
  stage=0;indices=[]
  for i,seen in enumerate(observations):
   if stage<len(names) and names[stage] in seen:
    indices.append(i);stage+=1
  missing=[row["main_street_sequence"].split(">")[j].strip() for j in range(stage,len(names))]
  coverage={name:sum(name in seen for seen in observations) for name in dict.fromkeys(names)}
  result[code]={"status":"review_only","sample_count":len(sample),"ordered_stages_observed":stage,
                "total_stages":len(names),"first_unobserved_stage":missing[0] if missing else None,
                "unobserved_remaining_stages":missing,
                "street_sample_counts":coverage,
                "warning":"80m proximity to named OSM road nodes is a heuristic, not street traversal, legal route or stop-order validation"}
  print(code,"ordered_stages",stage,"/",len(names),"first_unobserved",missing[0] if missing else "none",flush=True)
 out=a.shapes/"coolitoral_256_street_audit.json"
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
