#!/usr/bin/env python3
"""Audit the four unresolved COOLITORAL street transitions against all OSM ways.

Uses nearest-pair coordinates from the legal waypoint manifest and lists nearby
OSM ways; does not infer turn legality or claim network connectivity.
"""
import argparse,json,math,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def xy(p):return (p[0]*109160,p[1]*111195)
def distance(a,b):return math.dist(xy(a),xy(b))
def nearest_to_poly(p,coords):
 x,y=xy(p);best=float("inf")
 for a,b in zip(coords,coords[1:]):
  ax,ay=xy(a);bx,by=xy(b);dx=bx-ax;dy=by-ay
  t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy or 1)))
  best=min(best,math.hypot(x-ax-t*dx,y-ay-t*dy))
 return best
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--overpass",type=Path,required=True)
 ap.add_argument("--manifest",type=Path,required=True)
 ap.add_argument("--radius-m",type=float,default=150)
 ap.add_argument("--output",type=Path,default=ROOT/"sources/amb/kmz/coolitoral_256_gap_audit.json")
 args=ap.parse_args()
 ways=[w for w in json.loads(args.overpass.read_text())["elements"] if w.get("type")=="way" and len(w.get("geometry",[]))>1]
 manifest=json.loads(args.manifest.read_text())
 out={"warning":"Named-road OSM export is incomplete for graph routing; this audit is proximity only.","gaps":[]}
 for gap in manifest["unresolved_unique_pairs"]:
  pair=gap.get("nearest_pair_lon_lat")
  if not pair:
   out["gaps"].append({**gap,"nearby_ways":[]});continue
  center=[(pair[0][0]+pair[1][0])/2,(pair[0][1]+pair[1][1])/2]
  nearby=[]
  for w in ways:
   coords=[[p["lon"],p["lat"]] for p in w["geometry"]]
   d=nearest_to_poly(center,coords)
   if d<=args.radius_m:
    nearby.append({"id":w["id"],"name":w.get("tags",{}).get("name"),"highway":w.get("tags",{}).get("highway"),"oneway":w.get("tags",{}).get("oneway"),"distance_m":round(d,1)})
  nearby.sort(key=lambda x:x["distance_m"])
  out["gaps"].append({**gap,"center_lon_lat":center,"nearby_ways":nearby[:35],"nearby_total":len(nearby),
                      "needs_full_highway_extract":True})
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 for g in out["gaps"]:
  print(f"{g['from']} -> {g['to']}: {g.get('distance_m')}m; {g.get('nearby_total',0)} nearby named OSM ways")
  print("  names:",", ".join(dict.fromkeys(str(w["name"]) for w in g["nearby_ways"] if w["name"]))[:300])
if __name__=="__main__":main()
