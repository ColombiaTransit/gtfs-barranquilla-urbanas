#!/usr/bin/env python3
"""Export GeoJSON overlay and standalone Leaflet review map; no private endpoints."""
import csv,json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"sources/amb/kmz/graphhopper_candidates"
def main():
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument("--overpass",type=Path,required=True)
 a=p.parse_args()
 rows=list(csv.DictReader((ROOT/"sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv").open()))
 roads=json.loads(a.overpass.read_text())["elements"]
 features=[]
 for row in rows:
  code=row["route_code"]+"-"+row["itinerary"]
  file=OUT/(code+".geojson")
  if not file.exists():continue
  shape=json.loads(file.read_text())["features"][0]["geometry"]
  features.append({"type":"Feature","properties":{"layer":"graphhopper","route":code},"geometry":shape})
  names=[s.strip() for s in row["main_street_sequence"].split(">")]
  for i,name in enumerate(names,1):
   for way in roads:
    if way.get("tags",{}).get("name","").casefold()!=name.casefold():continue
    coords=[[p["lon"],p["lat"]] for p in way.get("geometry",[])]
    if len(coords)>1:
     features.append({"type":"Feature","properties":{"layer":"corridor","route":code,"street":name,"stage":i},"geometry":{"type":"LineString","coordinates":coords}})
 OUT.mkdir(parents=True,exist_ok=True)
 geo={"type":"FeatureCollection","features":features}
 (OUT/"coolitoral_256_visual_review.geojson").write_text(json.dumps(geo,ensure_ascii=False)+"\n")
 # Embed only public OSM geometry and route codes; never any endpoint/credentials.
 payload=json.dumps(geo,ensure_ascii=False).replace("<","\\u003c")
 page='''<!doctype html><html lang="nl"><meta charset="utf-8"><title>COOLITORAL routecontrole</title>
 <meta name="viewport" content="width=device-width, initial-scale=1">
 <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
 <style>body{margin:0;font:14px sans-serif}#map{height:88vh}header{padding:12px}select{padding:6px}
 .legend{background:white;padding:8px;line-height:1.8}</style>
 <header><b>COOLITORAL — voorlopige lussen en officiële corridors</b>
 <select id="route"></select> <span>Blauw: GraphHopper · Oranje: straten uit resolutie (alle OSM-segmenten met die naam)</span></header>
 <div id="map"></div><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>
 const data=__DATA__;
 const map=L.map('map').setView([10.98,-74.8],12);
 L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors'}).addTo(map);
 const select=document.getElementById('route');
 const routes=[...new Set(data.features.map(f=>f.properties.route))];
 for(const r of routes){const o=document.createElement('option');o.textContent=r;o.value=r;select.appendChild(o)}
 let overlay;
 function draw(){
  if(overlay)map.removeLayer(overlay);
  const filtered={type:'FeatureCollection',features:data.features.filter(f=>f.properties.route===select.value)};
  overlay=L.geoJSON(filtered,{style:f=>({color:f.properties.layer==='graphhopper'?'#1459db':'#e47a16',weight:f.properties.layer==='graphhopper'?5:2,opacity:f.properties.layer==='graphhopper'?0.95:0.35}),
   onEachFeature:(f,l)=>l.bindPopup(f.properties.layer==='graphhopper'?'GraphHopper: '+f.properties.route:'Corridor '+f.properties.stage+': '+f.properties.street)}).addTo(map);
  if(overlay.getBounds().isValid())map.fitBounds(overlay.getBounds(),{padding:[20,20]});
 }
 select.addEventListener('change',draw);draw();
 </script></html>'''
 (OUT/"coolitoral_256_visual_review.html").write_text(page.replace("__DATA__",payload))
 print("Exported visual review map and GeoJSON:",len(features),"features")
if __name__=="__main__":main()
