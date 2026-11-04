#!/usr/bin/env python3
"""Overlay AMB PT4/PT5 circular KMZ shapes on OSM named roads.

Uses full line-to-line overlap, not stop-name or intersection proximity.
Requires Overpass JSON with way.geometry. Reports geometric evidence only;
does not certify legal A/B correspondence.
"""
import argparse, json, math, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHAPES={
 "PT4":"sources/amb/kmz/geojson/COOLITORAL/PT4-4104_351a345396.geojson",
 "PT5":"sources/amb/kmz/geojson/COOLITORAL/PT5-4105_2fa953e451.geojson",
}
BRANCHES={
 "PT4":["Carrera 44","Calle 10","Carrera 41B","Calle 8"],
 "PT5":["Calle 8","Carrera 41B","Calle 10","Carrera 43"],
}
STREETS=sorted(set(sum(BRANCHES.values(),[])))
def norm(s):
 import unicodedata
 return "".join(c for c in unicodedata.normalize("NFKD",s.casefold()) if not unicodedata.combining(c)).strip()
def project(pt):
 lon,lat=pt
 return (lon*111195*math.cos(math.radians(10.97)),lat*111195)
def distance_to_segment(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy or 1)))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--overpass",required=True,type=Path)
 ap.add_argument("--output",default="sources/amb/kmz/coolitoral_256_osm_overlay.json")
 ap.add_argument("--threshold-m",type=float,default=20)
 args=ap.parse_args()
 ways=json.loads(args.overpass.read_text())["elements"]
 roads={s:[] for s in STREETS}
 for way in ways:
  name=norm(way.get("tags",{}).get("name",""))
  for street in STREETS:
   if name==norm(street) and len(way.get("geometry",[]))>1:
    coords=[project((p["lon"],p["lat"])) for p in way["geometry"]]
    roads[street].extend(zip(coords,coords[1:]))
 out={"method":"midpoint_sampling_20m_line_to_named_osm_segments","threshold_m":args.threshold_m,
      "caveat":"Overlap near intersections is not evidence of a traversed branch; require continuous length and full ordered branch."}
 for route,path in SHAPES.items():
  j=json.loads((ROOT/path).read_text())
  coords=j["features"][0]["geometry"]["coordinates"]
  route_pts=[project(p) for p in coords]
  samples=[]
  for a,b in zip(route_pts,route_pts[1:]):
   length=math.dist(a,b)
   for k in range(max(1,math.ceil(length/20))):
    t=(k+.5)/max(1,math.ceil(length/20))
    samples.append(((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])),length/max(1,math.ceil(length/20))))
  stats={}
  for street in STREETS:
   matches=[]
   for p,weight in samples:
    dist=min((distance_to_segment(p,a,b) for a,b in roads[street]),default=float("inf"))
    matches.append((dist<=args.threshold_m,weight,dist))
   runs=[];current=0
   for yes,weight,_ in matches+[(False,0,0)]:
    if yes:current+=weight
    elif current:runs.append(current);current=0
   stats[street]={"osm_segments":len(roads[street]),
                  "matched_length_m":round(sum(w for yes,w,_ in matches if yes)),
                  "longest_contiguous_m":round(max(runs,default=0)),
                  "runs_over_100m":sum(x>=100 for x in runs)}
  branch=BRANCHES[route]
  # Only an evidence flag, not a classification; all four B streets must
  # have substantial continuous traversal to support a B route.
  b_supported=all(stats[s]["longest_contiguous_m"]>=100 for s in branch)
  out[route]={"kmz_length_km":round(sum(math.dist(a,b) for a,b in zip(route_pts,route_pts[1:]))/1000,3),
              "branch_streets":branch,"street_overlay":stats,
              "B_full_branch_supported":b_supported,
              "variant_status":"B_geometric_candidate_needs_order_check" if b_supported else "A_or_historic_or_incomplete_OSM_unresolved"}
 target=ROOT/args.output;target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
