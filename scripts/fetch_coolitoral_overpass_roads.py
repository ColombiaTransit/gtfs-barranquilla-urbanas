#!/usr/bin/env python3
"""Fetch complete road geometries from the organization's Overpass endpoint.

Uses POST form data, never puts the Overpass query in the URL. Cloudflare Access
service-token headers are optional and read from GitHub Actions secrets.
"""
import argparse,json,os,time,urllib.parse,urllib.request
from pathlib import Path

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--output",type=Path,required=True)
 p.add_argument("--bbox",default="10.88,-74.91,11.07,-74.73")
 a=p.parse_args()
 url=os.environ.get("API_OVERPASS","").strip()
 if not url:raise SystemExit("API_OVERPASS organization variable is not configured")
 if not url.rstrip("/").endswith("/interpreter"):
  url=url.rstrip("/")+"/interpreter"
 south,west,north,east=map(float,a.bbox.split(","))
 if not (south<north and west<east):raise SystemExit("Invalid bbox")
 # Four tiles limit server load, with tiny overlaps for boundary-crossing ways.
 midlat=(south+north)/2;midlon=(west+east)/2;overlap=0.001
 tiles=[(south,west,midlat+overlap,midlon+overlap),
        (south,midlon-overlap,midlat+overlap,east),
        (midlat-overlap,west,north,midlon+overlap),
        (midlat-overlap,midlon-overlap,north,east)]
 headers={"User-Agent":"ColombiaTransit-GTFS-Barranquilla/1.0 (GitHub Actions)","Accept":"application/json","Content-Type":"application/x-www-form-urlencoded"}
 if os.getenv("CF_ACCESS_CLIENT_ID") and os.getenv("CF_ACCESS_CLIENT_SECRET"):
  headers["CF-Access-Client-Id"]=os.environ["CF_ACCESS_CLIENT_ID"]
  headers["CF-Access-Client-Secret"]=os.environ["CF_ACCESS_CLIENT_SECRET"]
 allways={}
 for i,(s,w,n,e) in enumerate(tiles,1):
  q=f'[out:json][timeout:180];way["highway"]({s:.6f},{w:.6f},{n:.6f},{e:.6f});out body geom;'
  request=urllib.request.Request(url,data=urllib.parse.urlencode({"data":q}).encode(),headers=headers,method="POST")
  try:
   with urllib.request.urlopen(request,timeout=220) as response:
    payload=json.load(response)
  except Exception as exc:
   raise SystemExit(f"Overpass tile {i}/4 failed ({type(exc).__name__}); check API_OVERPASS and Cloudflare headers") from exc
  if "remark" in payload:raise SystemExit(f"Overpass tile {i}/4 returned a remark: {payload['remark']}")
  ways=[x for x in payload.get("elements",[]) if x.get("type")=="way" and len(x.get("geometry",[]))>1]
  for way in ways:allways[way["id"]]=way
  print(f"tile {i}/4: {len(ways)} ways; {len(allways)} unique total",flush=True)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps({"version":0.6,"generator":"ColombiaTransit own Overpass","elements":list(allways.values())},ensure_ascii=False)+"\n")
 print(f"Saved {len(allways)} unique ways to {a.output}")
if __name__=="__main__":main()
