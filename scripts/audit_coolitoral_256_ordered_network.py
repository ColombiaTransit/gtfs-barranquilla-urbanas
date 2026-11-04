#!/usr/bin/env python3
"""Find directed OSM path witnesses visiting legal street names in order.

This is an ordered connectivity proof only, NOT a full route shape. Starts at
any node on the first named street and stops on the last named street.
Uses all driveable named/unnamed roads and directed edges. Does not enforce
OSM turn restriction relations, route endpoints, stop order or full loop.
"""
import argparse,csv,heapq,json,math,unicodedata
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def norm(s):
 return "".join(c for c in unicodedata.normalize("NFKD",s.casefold()) if not unicodedata.combining(c)).strip()
def meters(a,b):
 lat=math.radians((a[1]+b[1])/2)
 return math.hypot((a[0]-b[0])*111195*math.cos(lat),(a[1]-b[1])*111195)
def directions(t):
 h=t.get("highway","")
 if h in {"footway","pedestrian","steps","path","cycleway","bridleway","construction","proposed","corridor","platform"}:return ()
 if any(t.get(k) in {"no","private"} for k in ("access","motor_vehicle","motorcar","bus","psv")):return ()
 ow=t.get("oneway","").lower()
 if t.get("junction")=="roundabout" and not ow:ow="yes"
 if ow in {"yes","true","1"}:return (1,)
 if ow=="-1":return (-1,)
 return (1,-1)
def solve(graph,street_nodes,names,max_states):
 start=street_nodes.get(norm(names[0]),set())
 if not start:return {"status":"first_street_missing"}
 missing=[s for s in names if not street_nodes.get(norm(s))]
 if missing:return {"status":"named_street_missing","missing":missing}
 q=[];dist={};parent={};counter=0
 for n in start:
  key=(n,0);dist[key]=0;heapq.heappush(q,(0,n,0))
 seen=0;best_progress=0
 while q and seen<max_states:
  d,u,k=heapq.heappop(q);key=(u,k)
  if d!=dist[key]:continue
  seen+=1;best_progress=max(best_progress,k)
  if k==len(names)-1:
   chain=[];cur=key
   while cur in parent:
    prev,way_id=parent[cur];chain.append((cur[0],way_id));cur=prev
   chain.append((cur[0],None));chain.reverse()
   return {"status":"ordered_witness","distance_m":round(d,1),"visited_states":seen,
           "node_count":len(chain),"way_ids":list(dict.fromkeys(wid for _,wid in chain if wid is not None)),
           "node_ids":[node for node,_ in chain],
           "warning":"Partial street-order witness, not full legal route or GTFS shape"}
  for v,w,wid,street in graph.get(u,()):
   nk=k
   # Require actually traversing an edge of the next named street.
   if street==norm(names[k+1]):nk=k+1
   nd=d+w;new=(v,nk)
   if nd<dist.get(new,float("inf")):
    dist[new]=nd;parent[new]=(key,wid);heapq.heappush(q,(nd,v,nk))
 return {"status":"no_ordered_witness","max_stage_reached":best_progress,
         "last_reached_street":names[best_progress],"visited_states":seen,
         "limit_hit":seen>=max_states}
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--overpass",type=Path,required=True)
 ap.add_argument("--output",type=Path,default=ROOT/"sources/amb/kmz/coolitoral_256_ordered_network.json")
 ap.add_argument("--max-states",type=int,default=1500000)
 a=ap.parse_args()
 graph=defaultdict(list);street_nodes=defaultdict(set);missing_nodes=0;edges=0
 for way in json.loads(a.overpass.read_text())["elements"]:
  if way.get("type")!="way":continue
  nodes=way.get("nodes",[]);geo=way.get("geometry",[])
  if len(nodes)<2 or len(nodes)!=len(geo):missing_nodes+=1;continue
  tags=way.get("tags",{});dirs=directions(tags)
  if not dirs:continue
  name=norm(tags.get("name",""))
  if name:street_nodes[name].update(nodes)
  for i in range(len(nodes)-1):
   u,v=nodes[i:i+2];p=geo[i];q=geo[i+1]
   w=meters([p["lon"],p["lat"]],[q["lon"],q["lat"]])
   if 1 in dirs:graph[u].append((v,w,way["id"],name));edges+=1
   if -1 in dirs:graph[v].append((u,w,way["id"],name));edges+=1
 rows=list(csv.DictReader((ROOT/"sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv").open()))
 result={"warning":"Directed ordered-street witnesses only. Not a full route, does not enforce OSM turn restrictions or validate stops/loop.","directed_edges":edges,"ways_missing_node_ids":missing_nodes,"routes":{}}
 for row in rows:
  code=row["route_code"]+"-"+row["itinerary"]
  names=[s.strip() for s in row["main_street_sequence"].split(">")]
  found=solve(graph,street_nodes,names,a.max_states)
  result["routes"][code]=found
  print(code,found["status"],"distance_m=",found.get("distance_m"),"stage=",found.get("last_reached_street"),flush=True)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
