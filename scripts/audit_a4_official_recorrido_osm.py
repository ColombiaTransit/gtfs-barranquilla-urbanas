#!/usr/bin/env python3
"""A4-4109: match official ordered street names to AMBQ KMZ vertices using OSM.

Read-only candidate analysis. Does not infer legal turns or publish a GTFS shape.
"""
import csv
import json
import math
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"sources/amb/kmz/geojson/COOLITORAL/A4-4109_539ee1b2e3.geojson"
OUT=ROOT/"build/a4-recorrido"
# Street occurrences, NOT a unique unordered set. Explicit returns are retained.
STREETS=[
"Calle 120","Carrera 10","Avenida Circunvalar","Carrera 9G","Diagonal 138",
"Calle 134","Pinar del Río","Carrera 38","Calle 120","Carrera 37","Calle 123",
"Carrera 31","Avenida Circunvalar","Carrera 28","Avenida Circunvalar",
"Carrera 52","Calle 106","Carrera 51B","Universidad del Atlántico",
"Carrera 51B","Calle 96","Carrera 46","Calle 90","Parque Venezuela",
"Calle 90","Carrera 42B1","Calle 81","Carrera 42A","Calle 80B","Carrera 42",
"Calle 75B","Carrera 41D","Calle 74","Carrera 44","Calle 37","Carrera 43",
"Carrera 42F","Calle 75B","Carrera 42","Calle 80B","Carrera 42B",
"Calle 81","Carrera 42B1","Calle 93","Carrera 51B","Universidad del Atlántico",
"Carrera 51B","Avenida Circunvalar","Carrera 9G","Calle 120"]
def norm(s):
    s=s.upper().replace("AV.","AVENIDA").replace("CRA","CARRERA").replace("CLL","CALLE")
    return re.sub(r"[^A-Z0-9]","",s)
def meters(a,b):
    x=(a[0]-b[0])*111195*math.cos(math.radians((a[1]+b[1])/2))
    y=(a[1]-b[1])*111195
    return math.hypot(x,y)
def project(p,a,b):
    scale=math.cos(math.radians(p[1]))
    ax,ay=(a[0]-p[0])*scale,a[1]-p[1]
    bx,by=(b[0]-p[0])*scale,b[1]-p[1]
    vx,vy=bx-ax,by-ay
    t=max(0,min(1,-(ax*vx+ay*vy)/(vx*vx+vy*vy))) if vx*vx+vy*vy else 0
    return [a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])],t
def osm():
    if (OUT/"osm_roads.json").exists():
        return json.loads((OUT/"osm_roads.json").read_text())
    url=os.environ.get("API_OVERPASS","").strip()
    if not url:
        raise RuntimeError("API_OVERPASS is required; public fallback disabled")
    if not url.rstrip("/").endswith("/interpreter"):
        url=url.rstrip("/")+"/interpreter"
    q='[out:json][timeout:90];way["highway"]["name"](10.95,-74.89,11.04,-74.76);out geom;'
    headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
             "Accept":"application/json, text/javascript, */*; q=0.01",
             "Accept-Language":"nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
             "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}
    if os.getenv("CF_ACCESS_CLIENT_ID") and os.getenv("CF_ACCESS_CLIENT_SECRET"):
        headers["CF-Access-Client-Id"]=os.environ["CF_ACCESS_CLIENT_ID"]
        headers["CF-Access-Client-Secret"]=os.environ["CF_ACCESS_CLIENT_SECRET"]
    req=urllib.request.Request(url,data=urllib.parse.urlencode({"data":q}).encode(),headers=headers,method="POST")
    with urllib.request.urlopen(req,timeout=130) as resp:
        data=json.load(resp)
    if "remark" in data:
        raise RuntimeError("Private Overpass returned an error remark")
    (OUT/"osm_roads.json").write_text(json.dumps(data))
    return data
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=json.loads(SOURCE.read_text())
    lines=[f["geometry"]["coordinates"] for f in source["features"] if f["geometry"]["type"]=="LineString"]
    assert len(lines)==6 and sum(map(len,lines))==657,"Unexpected AMBQ source; stop rather than silently remap"
    try:
        roads=osm().get("elements",[])
        error=None
    except Exception as exc:
        raise SystemExit(f"Private Overpass failed ({type(exc).__name__}); check API_OVERPASS and Cloudflare credentials") from exc
    byname={}
    for road in roads:
        name=road.get("tags",{}).get("name","")
        key=norm(name)
        if key and road.get("geometry"):
            byname.setdefault(key,[]).append(road)
    rows=[]
    points=[]
    for i,name in enumerate(STREETS,1):
        ways=byname.get(norm(name),[])
        candidates=[]
        for road in ways:
            coords=[[p["lon"],p["lat"]] for p in road["geometry"]]
            for seg_idx,line in enumerate(lines,1):
                best=(float("inf"),None,None)
                for k in range(len(line)-1):
                    for a in coords[::max(1,len(coords)//25)]:
                        pt,t=project(a,line[k],line[k+1])
                        d=meters(a,pt)
                        if d<best[0]:best=(d,k+t,pt)
                if best[1] is not None:
                    candidates.append((best[0],seg_idx,best[1],best[2],road["id"]))
        candidates.sort(key=lambda x:x[0])
        best=candidates[:5]
        for rank,c in enumerate(best,1):
            rows.append({"sequence":i,"street":name,"rank":rank,"distance_m":round(c[0],1),
                         "kmz_segment":c[1],"kmz_edge_position":round(c[2],3),"osm_way_id":c[4],
                         "candidate_only":"yes"})
        if best and best[0][0]<=35:
            points.append({"type":"Feature","properties":{"sequence":i,"street":name,"kmz_segment":best[0][1],
               "distance_m":round(best[0][0],1),"review":"candidate_not_approved"},
               "geometry":{"type":"Point","coordinates":best[0][3]}})
    with (OUT/"street_segment_candidates.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["sequence","street","rank","distance_m","kmz_segment","kmz_edge_position","osm_way_id","candidate_only"])
        w.writeheader();w.writerows(rows)
    (OUT/"street_snap_candidates.geojson").write_text(json.dumps({"type":"FeatureCollection","features":points},indent=2))
    summary={"source_sha256":source["metadata"]["source_sha256"],"official_street_occurrences":len(STREETS),
             "osm_ways":len(roads),"candidate_rows":len(rows),"candidate_points_within_35m":len(points),
             "osm_error":error,"gtfs_modified":False,
             "status":"CANDIDATE_ONLY_REQUIRES_ORDER_AND_DIRECTION_REVIEW"}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    md=["# A4-4109: AMBQ-to-OSM street candidates","",
        "No ArcGIS used. These are nearest-name matches, NOT verified intersections or legal turns.",
        "Repeated streets may refer to different road portions. Do not create a GTFS shape from this output.","",
        "| # | Official street | Nearest KMZ segment | Distance (m) |",
        "|---:|---|---:|---:|"]
    for i,name in enumerate(STREETS,1):
        matches=[x for x in rows if x["sequence"]==i and x["rank"]==1]
        m=matches[0] if matches else None
        md.append(f"| {i} | {name} | {m['kmz_segment'] if m else '—'} | {m['distance_m'] if m else '—'} |")
    md.extend(["",f"OSM query error: {error or 'none'}","",
               "NEXT: verify intersection pairings and monotonic progress through the directed KMZ segments, including one-way roads and return loops."])
    (OUT/"report.md").write_text("\n".join(md)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
