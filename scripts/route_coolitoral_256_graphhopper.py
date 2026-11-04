#!/usr/bin/env python3
"""Generate provisional A/B shapes via GraphHopper from reviewed via-points.

Requires a GraphHopper API key and explicit --approved flag. Never promotes
unreviewed candidate junctions to production GTFS shapes.
"""
import argparse,json,os,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--manifest",type=Path,required=True)
 ap.add_argument("--route",required=True,choices=["PT4-4104-A","PT4-4104-B","PT5-4105-A","PT5-4105-B"])
 ap.add_argument("--approved",action="store_true",help="Confirm junctions have been manually reviewed")
 ap.add_argument("--output-dir",type=Path,default=ROOT/"sources/amb/kmz/graphhopper_candidates")
 args=ap.parse_args()
 if not args.approved:raise SystemExit("Refusing to route unreviewed OSM junctions; supply --approved only after review.")
 key=os.getenv("GRAPHHOPPER_API_KEY")
 if not key:raise SystemExit("GRAPHHOPPER_API_KEY is required")
 manifest=json.loads(args.manifest.read_text())
 item=manifest["routes"][args.route]
 if not item["complete"]:raise SystemExit("Missing junctions: route cannot be reconstructed safely")
 points=[j["point_lon_lat"] for j in item["junctions"]]
 # Junctions are intermediate points; close circular route at first point.
 if len(points)<3:raise SystemExit("Insufficient waypoints")
 points.append(points[0])
 payload={"profile":"car","points":points,"points_encoded":False,"instructions":False,"calc_points":True}
 url="https://graphhopper.com/api/1/route?"+urllib.parse.urlencode({"key":key})
 req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST")
 with urllib.request.urlopen(req,timeout=90) as resp:res=json.load(resp)
 path=res["paths"][0]
 coords=path["points"]["coordinates"]
 if len(coords)<3:raise SystemExit("GraphHopper returned no usable geometry")
 output={"type":"FeatureCollection","metadata":{"route":args.route,"source":"GraphHopper","status":"PROVISIONAL_REQUIRES_VALIDATION","distance_m":path["distance"],"legal_variant_verified":False,"waypoints":points},"features":[{"type":"Feature","properties":{"route":args.route},"geometry":{"type":"LineString","coordinates":coords}}]}
 args.output_dir.mkdir(parents=True,exist_ok=True)
 dest=args.output_dir/(args.route+".geojson")
 dest.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
 print(f"Generated {dest} ({path['distance']/1000:.2f} km); NOT promoted to GTFS")
if __name__=="__main__":main()
