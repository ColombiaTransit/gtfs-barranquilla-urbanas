#!/usr/bin/env python3
"""Directed OSM connectivity audit for consecutive legal COOLITORAL streets.

Finds shortest connections via unnamed ways only. OSM node IDs establish topology;
nearby coordinates are never treated as connected. This is a diagnostic, not an
approved route shape or a bus-accessibility guarantee.
"""
import argparse, csv, heapq, json, math, unicodedata
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def norm(s):
 return "".join(c for c in unicodedata.normalize("NFKD",s.casefold()) if not unicodedata.combining(c)).strip()
def meters(a,b):
 lat=math.radians((a[1]+b[1])/2)
 return math.hypot((a[0]-b[0])*111195*math.cos(lat),(a[1]-b[1])*111195)
def directed_edges(way):
 tags=way.get("tags",{})
 highway=tags.get("highway","")
 if highway in {"footway","pedestrian","steps","path","cycleway","bridleway","construction","proposed","corridor","platform"}:return ()
 if tags.get("access") in {"no","private"} or tags.get("motor_vehicle") in {"no","private"} or tags.get("motorcar") in {"no","private"}:return ()
 if tags.get("bus") in {"no","private"} or tags.get("psv") in {"no","private"}:return ()
 ow=tags.get("oneway","").lower()
 if tags.get("junction")=="roundabout" and not ow:ow="yes"
 if ow in {"yes","true","1"}:return (1,)
 if ow=="-1":return (-1,)
 return (1,-1)
def shortest(graph,sources,targets,max_m,max_visits=250000):
 queue=[];dist={};parent={}
 for node in sources:
  dist[node]=0;heapq.heappush(queue,(0,node))
 target_set=set(targets);visits=0
 while queue and visits<max_visits:
  d,u=heapq.heappop(queue)
  if d!=dist[u]:continue
  visits+=1
  if u in target_set:
   ids=[];v=u
   while v in parent:
    prev,wid=parent[v];ids.append(wid);v=prev
   return {"distance_m":round(d,1),"via_way_ids":list(reversed(ids)),"visited_nodes":visits}
  for v,w,wid in graph.get(u,()):
   nd=d+w
   if nd<=max_m and nd<dist.get(v,float("inf")):
    dist[v]=nd;parent[v]=(u,wid);heapq.heappush(queue,(nd,v))
 return None
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--overpass",type=Path,required=True)
 p.add_argument("--output",type=Path,default=ROOT/"sources/amb/kmz/coolitoral_256_directed_connectivity.json")
 p.add_argument("--max-connector-m",type=float,default=2000)
 a=p.parse_args()
 data=json.loads(a.overpass.read_text())
 graph=defaultdict(list);street_nodes=defaultdict(set);coords={};unnamed=0;missing_node_ids=0
 for way in data["elements"]:
  if way.get("type")!="way":continue
  nodes=way.get("nodes",[]);geom=way.get("geometry",[])
  if len(nodes)!=len(geom) or len(nodes)<2:
   missing_node_ids+=1;continue
  name=norm(way.get("tags",{}).get("name",""))
  directions=directed_edges(way)
  if not directions:continue
  for nid,pnt in zip(nodes,geom):coords[nid]=[pnt["lon"],pnt["lat"]]
  if name:street_nodes[name].update(nodes)
  else:unnamed+=1
  # Named streets are checkpoints, not connector shortcuts.
  if name:continue
  for i in range(len(nodes)-1):
   u,v=nodes[i:i+2];w=meters(coords[u],coords[v])
   if 1 in directions:graph[u].append((v,w,way["id"]))
   if -1 in directions:graph[v].append((u,w,way["id"]))
 rows=list(csv.DictReader((ROOT/"sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv").open()))
 routes={}
 for row in rows:
  code=row["route_code"]+"-"+row["itinerary"]
  names=[s.strip() for s in row["main_street_sequence"].split(">")]
  transitions=[]
  for src,dst in zip(names,names[1:]):
   sources=street_nodes[norm(src)];targets=street_nodes[norm(dst)]
   shared=sources&targets
   if shared:status="shared_osm_node";connection={"distance_m":0,"via_way_ids":[]}
   elif not sources or not targets:status="street_missing";connection=None
   else:
    connection=shortest(graph,sources,targets,a.max_connector_m)
    status="unnamed_directed_connector" if connection else "no_directed_unnamed_connector"
   transitions.append({"from":src,"to":dst,"status":status,
                       "source_nodes":len(sources),"target_nodes":len(targets),
                       "connection":connection})
  routes[code]={"transitions":transitions,"all_transitions_connected":all(t["connection"] is not None for t in transitions),
                "ordered_route_verified":False}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 result={"source":str(a.overpass),"max_connector_m":a.max_connector_m,
         "unnamed_road_ways":unnamed,"ways_missing_osm_node_ids":missing_node_ids,
         "routes":routes,
         "limitations":["Each transition is evaluated independently; this does not prove that all transitions can be traversed in legal order.","Named intermediary streets are excluded from connector paths.","OSM one-way, access and motor-vehicle restrictions are considered; turn restrictions, bus-specific conditional restrictions and graph route order are not fully verified.","Shared OSM nodes are topology evidence, not necessarily legal turns or bus access."]}
 a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 for code,route in routes.items():
  print(code,":",sum(t["connection"] is not None for t in route["transitions"]),"/",len(route["transitions"]),"directed connections")
  for t in route["transitions"]:
   if t["status"] not in {"shared_osm_node","unnamed_directed_connector"}:print("  UNRESOLVED",t["from"],">",t["to"],t["status"])
 print("Ways lacking OSM node IDs:",missing_node_ids)
if __name__=="__main__":main()
