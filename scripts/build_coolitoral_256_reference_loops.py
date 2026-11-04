#!/usr/bin/env python3
"""Build review-only GraphHopper loops from ordered OSM witnesses and AMB KMZ anchors.

A witness is only evidence of street-name order. GraphHopper may route between
its selected nodes differently; no automatic legal/stop-order certification.
"""
import argparse,json,math,os,urllib.request,urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
KMZ={"PT4":"sources/amb/kmz/geojson/COOLITORAL/PT4-4104_351a345396.geojson",
     "PT5":"sources/amb/kmz/geojson/COOLITORAL/PT5-4105_2fa953e451.geojson"}
OFFICIAL={"PT4-4104-A":34500,"PT4-4104-B":34500,"PT5-4105-A":35500,"PT5-4105-B":35300}
def distance(a,b):
 lat=math.radians((a[1]+b[1])/2)
 return math.hypot((a[0]-b[0])*111195*math.cos(lat),(a[1]-b[1])*111195)
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--overpass",type=Path,required=True)
 p.add_argument("--witness",type=Path,required=True)
 p.add_argument("--output-dir",type=Path,default=ROOT/"sources/amb/kmz/graphhopper_candidates")
 p.add_argument("--profile",default=os.getenv("GRAPHHOPPER_PROFILE","bus"))
 p.add_argument("--max-anchor-distance-m",type=float,default=300)
 p.add_argument("--max-waypoints",type=int,default=100)
 p.add_argument("--route",default="all",choices=["all",*OFFICIAL])
 a=p.parse_args()
 nodes={}
 for w in json.loads(a.overpass.read_text())["elements"]:
  for nid,pt in zip(w.get("nodes",[]),w.get("geometry",[])):
   nodes[nid]=[pt["lon"],pt["lat"]]
 witnesses=json.loads(a.witness.read_text())["routes"]
 url=os.getenv("GRAPHHOPPER_URL","").rstrip("/")
 if url and not url.endswith("/route"):url+="/route"
 summary={}
 for code in ([a.route] if a.route!="all" else OFFICIAL):
  w=witnesses[code]
  if w["status"]!="ordered_witness":
   summary[code]={"status":"skipped_no_ordered_witness"};continue
  kmz=json.loads((ROOT/KMZ[code[:3]]).read_text())
  line=next(f["geometry"]["coordinates"] for f in kmz["features"] if f["geometry"]["type"]=="LineString")
  anchor=line[0][:2]
  path=[nodes[n] for n in w["node_ids"] if n in nodes]
  if len(path)<2:
   summary[code]={"status":"missing_witness_nodes"};continue
  # Keep ordered witness intact: evenly spaced samples preserve order.
  step=max(1,math.ceil((len(path)-1)/(a.max_waypoints-3)))
  sampled=path[::step]
  if sampled[-1]!=path[-1]:sampled.append(path[-1])
  pts=[anchor,*sampled,anchor]
  nearest=min(distance(anchor,p) for p in path)
  item={"status":"review_only","anchor_lon_lat":anchor,
        "anchor_to_witness_min_distance_m":round(nearest,1),
        "waypoint_count":len(pts),"witness_length_m":w["distance_m"],
        "official_length_m":OFFICIAL[code],
        "kmz_reference":KMZ[code[:3]],"kmz_legal_variant_verified":False,
        "warnings":["KMZ anchor is a reference, not verified route terminal",
                    "GraphHopper path may deviate from OSM witness and official street order",
                    "SIU stop order and turn restrictions have not been independently validated"]}
  if nearest>a.max_anchor_distance_m:
   item["status"]="anchor_too_far";summary[code]=item;continue
  if not url:
   item["status"]="awaiting_graphhopper_secret";summary[code]=item;continue
  headers={"Content-Type":"application/json","Accept":"application/json",
           "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
  client_id=os.getenv("CF_ACCESS_CLIENT_ID","")
  client_secret=os.getenv("CF_ACCESS_CLIENT_SECRET","")
  if client_id and client_secret:
   headers["CF-Access-Client-Id"]=client_id
   headers["CF-Access-Client-Secret"]=client_secret
  req=urllib.request.Request(url,data=json.dumps({"profile":a.profile,"points":pts,"points_encoded":False,"instructions":False,"calc_points":True}).encode(),headers=headers,method="POST")
  try:
   with urllib.request.urlopen(req,timeout=180) as resp:res=json.load(resp)
   route=res["paths"][0];coords=route["points"]["coordinates"]
   if len(coords)<3:raise ValueError("Insufficient geometry")
   item.update({"status":"provisional_shape","distance_m":round(route["distance"],1),
                "distance_difference_pct":round((route["distance"]/OFFICIAL[code]-1)*100,1)})
   output={"type":"FeatureCollection","metadata":{"route":code,**item,
           "gtfs_ready":False,"legal_route_verified":False,"siu_stop_order_verified":False},
           "features":[{"type":"Feature","properties":{"route":code,"status":"PROVISIONAL"},
                        "geometry":{"type":"LineString","coordinates":coords}}]}
   a.output_dir.mkdir(parents=True,exist_ok=True)
   (a.output_dir/(code+".geojson")).write_text(json.dumps(output,ensure_ascii=False)+"\n")
  except (urllib.error.URLError,ValueError,KeyError,IndexError) as exc:
   # Never print HTTP errors: error strings can contain private endpoint URLs.
   item["status"]="graphhopper_request_failed"
   item["error_type"]=type(exc).__name__
   if isinstance(exc,urllib.error.HTTPError):
    item["http_status"]=exc.code
    # Only expose allowlisted diagnostic headers, never body, URLs or tokens.
    item["cloudflare_ray_present"]=bool(exc.headers.get("CF-Ray"))
    item["cloudflare_mitigated"]=exc.headers.get("cf-mitigated","").lower()=="challenge"
    item["response_content_type"]=exc.headers.get_content_type()
    item["access_credentials_configured"]=bool(client_id and client_secret)
    # Never log response body or exception text: may contain private endpoints.
   elif isinstance(exc,urllib.error.URLError):
    item["network_error_category"]=type(exc.reason).__name__
   elif isinstance(exc,(KeyError,IndexError)):
    item["response_structure_error"]=True
  summary[code]=item
  print(code,item["status"],"http_status",item.get("http_status","n/a"),"error_type",item.get("error_type","n/a"),"cloudflare_ray_present",item.get("cloudflare_ray_present","n/a"),"cloudflare_mitigated",item.get("cloudflare_mitigated","n/a"),"response_content_type",item.get("response_content_type","n/a"),"access_credentials_configured",item.get("access_credentials_configured","n/a"),"distance_m",item.get("distance_m","n/a"),flush=True)
 a.output_dir.mkdir(parents=True,exist_ok=True)
 (a.output_dir/"coolitoral_256_loop_report.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
 for code,item in summary.items():print(code,item["status"],"delta_pct",item.get("distance_difference_pct","n/a"))
if __name__=="__main__":main()
