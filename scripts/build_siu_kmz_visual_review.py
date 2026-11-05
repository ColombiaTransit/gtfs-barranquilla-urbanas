#!/usr/bin/env python3
"""Generate 11 offline-data Leaflet/OSM review pages for unresolved SIU→KMZ mappings.

Only OpenStreetMap basemap tiles and Leaflet assets need internet in browser.
No SIU API access; reads checked-in source and fresh matching output.
"""
import csv, json, re, html, argparse
from pathlib import Path
from collections import defaultdict

UNRESOLVED = [
    "MAKRO", "MIRAMAR ALAMEDA DEL RIO", "VIA 40 MURILLO",
    "RIOMAR AMARILLA", "ROJA RIOMAR", "SOLEDAD 2000 CORREDOR UNIVERSITARIO",
    "JUAN MINA", "SOLEDAD CALLE 84 VILLA CAROLINA", "VILLA SAN PABLO",
    "LAS GAVIOTAS CALLE 76", "SOLEDAD CALLE 84",
]
COLORS = ["#e63946","#4361ee","#2a9d8f","#9b5de5","#ff9f1c"]
def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,default=Path("."))
    ap.add_argument("--out",type=Path,default=Path("build/siu_kmz_visual_review"))
    a=ap.parse_args(); root=a.repo.resolve(); out=(root/a.out).resolve(); out.mkdir(parents=True,exist_ok=True)
    stops=defaultdict(list)
    for row in read(root/"sources/siu/public_extract/siu_route_stop_sequences.csv"):
        if row.get("likely_test_itinerary","").lower()=="true":continue
        stops[row.get("siu_display_name") or row.get("siu_name")].append(row)
    ranks=defaultdict(list)
    for row in read(root/"build/siu_kmz_all_matches/ranked_candidates.csv"):
        ranks[row["siu_itinerary_uuid"]].append(row)
    manifest=read(root/"sources/amb/kmz/manifest.csv")
    bypath={m["geojson_path"]:m for m in manifest}
    index=[]
    for name in UNRESOLVED:
        group=sorted(stops.get(name,[]),key=lambda x:int(x["siu_stop_sequence"]))
        if not group: raise SystemExit("Missing SIU itinerary: "+name)
        uid=group[0]["siu_itinerary_uuid"]
        group=[s for s in group if s["siu_itinerary_uuid"]==uid]
        candidates=sorted(ranks.get(uid,[]),key=lambda x:(int(x["rank"]),-float(x["coverage_50_pct"]),-float(x["sequence_coverage_pct"]),int(x["backward_gt20m"])+int(x["implausible_forward"]),float(x["median_distance_m"]),x["kmz_route_label"]))
        if not candidates: raise SystemExit("Missing ranked KMZ candidates for "+name)
        # Preserve close alternatives and at least top 3. No route assignments inferred here.
        candidates=[c for c in candidates if int(c["rank"])<=3 or float(c["coverage_50_pct"])>=float(candidates[0]["coverage_50_pct"])-10][:5]
        shapes=[]
        for c in candidates:
            path=root/"sources/amb/kmz"/c["kmz_geojson_path"]
            if not path.is_file(): raise SystemExit("Missing KMZ GeoJSON "+str(path))
            shapes.append({"label":c["kmz_route_label"],"company":c["kmz_company"],
                           "coverage":c["coverage_50_pct"],"sequence_coverage":c["sequence_coverage_pct"],
                           "orientation":c["orientation"],"rank":c["rank"],
                           "source":bypath.get(c["kmz_geojson_path"],{}).get("kmz_url",""),
                           "geojson":json.loads(path.read_text(encoding="utf-8"))})
        features=[]
        for s in group:
            try: lat=float(s["stop_lat"]);lon=float(s["stop_lon"])
            except (ValueError,TypeError):continue
            features.append({"lat":lat,"lon":lon,"seq":int(s["siu_stop_sequence"]),
                             "name":s.get("stop_name",""),"uuid":s.get("siu_stop_uuid","")})
        payload=json.dumps({"name":name,"uid":uid,"stops":features,"shapes":shapes},ensure_ascii=False).replace("<","\\u003c")
        page=PAGE.replace("__TITLE__",html.escape(name)).replace("__PAYLOAD__",payload)
        filename=slug(name)+".html"
        (out/filename).write_text(page,encoding="utf-8")
        index.append({"name":name,"file":filename,"stops":len(features),
                      "best":candidates[0]["kmz_route_label"],"coverage":candidates[0]["coverage_50_pct"],
                      "alternatives":len(shapes)})
    links="\\n".join(f'<tr><td><a href="{html.escape(x["file"])}">{html.escape(x["name"])}</a></td><td>{x["stops"]}</td><td>{html.escape(x["best"])}</td><td>{x["coverage"]}%</td><td>{x["alternatives"]}</td></tr>' for x in index)
    (out/"index.html").write_text('<!doctype html><html lang="nl"><meta charset="utf-8"><title>11 SIU–KMZ kaarten</title><style>body{font:16px system-ui;max-width:1050px;margin:3em auto;padding:1em}td,th{padding:.6em;border-bottom:1px solid #ddd;text-align:left}table{border-collapse:collapse}a{color:#1261aa}</style><h1>11 onzekere SIU → AMB/KMZ koppelingen</h1><p>Open een kaart om kandidaat-KMZ-lijnen en alle genummerde SIU-haltepassages te vergelijken. Kandidaten zijn niet goedgekeurd. Basemap vereist internet.</p><table><tr><th>SIU</th><th>Haltes</th><th>Beste KMZ</th><th>Dekking binnen 50 m</th><th>Getoonde kandidaten</th></tr>'+links+'</table></html>',encoding="utf-8")
    (out/"manifest.json").write_text(json.dumps(index,indent=2,ensure_ascii=False)+"\\n",encoding="utf-8")
    print(json.dumps({"pages":len(index),"output":str(out),"names":[x["name"] for x in index]},ensure_ascii=False,indent=2))

PAGE=r'''<!doctype html>
<html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ — SIU/KMZ</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>html,body{margin:0;height:100%;font:14px system-ui}#map{height:100vh;width:100%}
.panel{position:absolute;z-index:1000;top:12px;left:55px;background:white;padding:12px;border-radius:8px;max-width:360px;max-height:85vh;overflow:auto;box-shadow:0 2px 12px #5555}
.panel label{display:block;margin:7px 0}.panel h2{margin:0 0 5px;font-size:18px}.panel small{color:#444}
.seq-label{font:11px system-ui;color:#222;text-shadow:1px 1px white,-1px -1px white;white-space:nowrap}
</style></head><body><div id="map"></div><section class="panel"><a href="index.html">← Overzicht</a><h2>__TITLE__</h2><div id="stats"></div><label><input type="checkbox" id="labels"> Toon alle haltevolgnummers</label><label><input type="checkbox" id="stops" checked> Toon SIU-haltes</label><div id="layers"></div><small>KMZ-lijnen zijn kandidaten, geen bevestigde mapping. Haltevolgorde = originele SIU-volgorde. Klik op haltes voor nummer/naam. OSM-tegels vereisen internet.</small></section>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>const DATA=__PAYLOAD__;
const map=L.map('map',{preferCanvas:true}).setView([10.98,-74.8],12);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; OpenStreetMap contributors',maxZoom:19}).addTo(map);
const stopLayer=L.layerGroup().addTo(map), labelLayer=L.layerGroup(), bounds=L.latLngBounds([]);
DATA.stops.forEach(s=>{const ll=[s.lat,s.lon];bounds.extend(ll);
L.circleMarker(ll,{radius:3.5,color:'#111',weight:1,fillColor:'#fff',fillOpacity:1}).bindPopup('<b>Halte '+s.seq+'</b><p>'+esc(s.name)+'</p><small>'+esc(s.uuid)+'</small>').addTo(stopLayer);
L.marker(ll,{icon:L.divIcon({className:'seq-label',html:String(s.seq),iconSize:[24,14],iconAnchor:[-5,7]})}).addTo(labelLayer);
});
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
document.getElementById('stats').textContent=DATA.stops.length+' SIU-haltepassages · '+DATA.shapes.length+' KMZ-kandidaten';
DATA.shapes.forEach((s,i)=>{const color=['#e63946','#4361ee','#2a9d8f','#9b5de5','#ff9f1c'][i];
const layer=L.geoJSON(s.geojson,{style:{color,weight:i===0?5:3,opacity:i===0?.9:.65,dashArray:i===0?null:'8,5'},onEachFeature:(f,l)=>l.bindPopup(esc(s.company+' / '+s.label)+' — '+s.coverage+'% binnen 50 m')});
if(i===0)layer.addTo(map);
const input=document.createElement('input');input.type='checkbox';input.checked=i===0;
input.addEventListener('change',()=>input.checked?layer.addTo(map):map.removeLayer(layer));
const label=document.createElement('label');label.append(input,document.createTextNode(' '+s.label+' ('+s.company+') · '+s.coverage+'% · '+s.orientation));label.style.color=color;
document.getElementById('layers').append(label);
if(i===0)layer.eachLayer(l=>{if(l.getBounds)bounds.extend(l.getBounds())});
});
if(bounds.isValid())map.fitBounds(bounds.pad(.08));
document.getElementById('labels').addEventListener('change',e=>e.target.checked?labelLayer.addTo(map):map.removeLayer(labelLayer));
document.getElementById('stops').addEventListener('change',e=>e.target.checked?stopLayer.addTo(map):map.removeLayer(stopLayer));
</script></body></html>'''
if __name__=="__main__":main()
