#!/usr/bin/env python3
"""Create a standalone map of the original AMB KMZ-derived GeoJSON lines."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sources={"PT4-4104":"PT4-4104_351a345396.geojson","PT5-4105":"PT5-4105_2fa953e451.geojson"}
features=[]
for route,file in sources.items():
 data=json.loads((root/"sources/amb/kmz/geojson/COOLITORAL"/file).read_text())
 for f in data["features"]:
  if f["geometry"]["type"] in ("LineString","MultiLineString"):
   features.append({"type":"Feature","properties":{"route":route},"geometry":f["geometry"]})
out=root/"sources/amb/kmz/graphhopper_candidates"
out.mkdir(parents=True,exist_ok=True)
geo={"type":"FeatureCollection","features":features}
(out/"coolitoral_256_kmz_visual_review.geojson").write_text(json.dumps(geo))
html='''<!doctype html><html lang="nl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>COOLITORAL AMB KMZ</title><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>body{margin:0;font:14px sans-serif}header{padding:12px}#map{height:85vh}</style>
<header><b>COOLITORAL — originele AMB KMZ-lussen</b>
<select id="route"><option>PT4-4104</option><option>PT5-4105</option><option value="all">Beide</option></select>
<p>Paars: KMZ-lijn · Groen: begin · Rood: einde. Niet bevestigd als officiële A/B-variant.</p></header>
<div id="map"></div><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>
const data=__DATA__,map=L.map('map').setView([10.98,-74.8],12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap'}).addTo(map);
let layer;const select=document.getElementById('route');
function draw(){if(layer)map.removeLayer(layer);layer=L.layerGroup().addTo(map);let bounds=L.latLngBounds([]);
for(const f of data.features.filter(f=>select.value==='all'||f.properties.route===select.value)){
const lines=f.geometry.type==='LineString'?[f.geometry.coordinates]:f.geometry.coordinates;
for(const line of lines){if(!line.length)continue;const pts=line.map(p=>[p[1],p[0]]);
L.polyline(pts,{color:f.properties.route==='PT4-4104'?'#6846c4':'#c044a3',weight:5}).addTo(layer);
L.circleMarker(pts[0],{radius:7,color:'green'}).addTo(layer).bindPopup('Begin '+f.properties.route);
L.circleMarker(pts[pts.length-1],{radius:7,color:'red'}).addTo(layer).bindPopup('Einde '+f.properties.route);
bounds.extend(L.latLngBounds(pts));}}
if(bounds.isValid())map.fitBounds(bounds,{padding:[20,20]});}
select.addEventListener('change',draw);draw();
</script></html>'''
(out/"coolitoral_256_kmz_visual_review.html").write_text(html.replace("__DATA__",json.dumps(geo).replace("<","\\u003c")))
print("Exported original AMB KMZ visual map")
