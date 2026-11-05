#!/usr/bin/env python3
"""Extract provider-authored Google Maps Embed waypoints, not Google road geometry."""
import csv, hashlib, html, json, re, urllib.request
from pathlib import Path
from urllib.parse import unquote

URL = "https://coolitoral.com/pages/rutas.html"
OUT = Path("build/coolitoral_google")
OUT.mkdir(parents=True, exist_ok=True)
req = urllib.request.Request(URL, headers={"User-Agent": "ColombiaTransit-GTFS-research/1.0"})
with urllib.request.urlopen(req, timeout=40) as response:
    source = response.read()
(OUT / "rutas.html").write_bytes(source)
raw = html.unescape(source.decode("utf-8", errors="replace"))
routes = []
for match in re.finditer(r"case\s*['\"](\d+)['\"]\s*:(.*?)(?=\b(?:case\s*['\"]\d+['\"]|default\s*:)|\}\s*return\s+x)", raw, re.S):
    number, body = int(match.group(1)), match.group(2)
    desc = re.search(r"getElementById\(['\"]valor['\"]\)\.value\s*=\s*['\"]([^'\"]*)", body)
    embed = re.search(r"https://www\.google\.com/maps/embed\?pb=[^'\"\s<]+", body)
    if not embed:
        continue
    url = embed.group(0)
    # Only coordinates in 3m2!1dLAT!2dLON route-waypoint blocks.
    coords = [(float(a), float(b)) for a, b in re.findall(r"!3m2!1d(-?\d+(?:\.\d+)?)!2d(-?\d+(?:\.\d+)?)", unquote(url))]
    # Other Google Maps blocks use 3m2 for display viewport; 4m3/4m5 are actual route waypoints.
    coords = [(float(a), float(b)) for a, b in re.findall(r"!4m(?:3|5)!(?:[^!]*!)*?3m2!1d(-?\d+(?:\.\d+)?)!2d(-?\d+(?:\.\d+)?)", unquote(url))] or coords
    routes.append({"selection": number, "route": {1:"A1",2:"A2",3:"A3",4:"A4",5:"B1",6:"B2",7:"B3",8:"B17",9:"C19",10:"PT1",11:"PT2",12:"PT3",13:"PT4",14:"PT5"}.get(number), "description": desc.group(1) if desc else "", "embed_url": url, "waypoints": [{"lat": a, "lon": b} for a,b in coords]})
routes.sort(key=lambda x: x["selection"])
if len(routes) != 14 or any(not r["waypoints"] for r in routes):
    raise SystemExit(f"Expected 14 route maps with points; found {len(routes)}")
(OUT / "routes.json").write_text(json.dumps({"source":URL,"source_sha256":hashlib.sha256(source).hexdigest(),"routes":routes},indent=2,ensure_ascii=False))
features=[{"type":"Feature","properties":{"route":r["route"],"selection":r["selection"],"description":r["description"],"geometry_type":"ordered_waypoints_not_road_shape"},"geometry":{"type":"LineString","coordinates":[[p["lon"],p["lat"]] for p in r["waypoints"]]}} for r in routes if len(r["waypoints"])>1]
(OUT / "waypoint_connections_RESEARCH_ONLY.geojson").write_text(json.dumps({"type":"FeatureCollection","features":features},ensure_ascii=False,indent=2))
crosswalk=Path("sources/siu/open_route_review/siu_amb_crosswalk_visual_decisions_2026-11-05.csv")
rows=list(csv.DictReader(crosswalk.open())) if crosswalk.exists() else []
with (OUT/"crosswalk_reference.csv").open("w",newline="") as f:
    writer=csv.writer(f);writer.writerow(["coolitoral_route","siu_name","amb_candidate","decision_status","note"])
    for r in routes:
        matches=[row for row in rows if row.get("amb_base_candidate","").startswith(r["route"]+"-")]
        if matches:
            for row in matches:writer.writerow([r["route"],row["siu_name"],row["amb_base_candidate"],row["decision_status"],"name-based reference only; not geometry validation"])
        else:writer.writerow([r["route"],"","","","unmatched by route code"])
print(f"Extracted {len(routes)} maps; waypoint counts:",[(r["route"],len(r["waypoints"])) for r in routes])


# Preserve the source table's irregular rows, including Saturday overrides and
# PT1 subservices. No inferred headways or missing end times.
from html.parser import HTMLParser
class DispatchTableParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.in_table=False; self.depth=0; self.in_row=False; self.in_cell=False
        self.cells=[]; self.rows=[]; self.cell_text=[]; self.table_text=""
    def handle_starttag(self,tag,attrs):
        if tag=="table" and not self.in_table:
            self.in_table=True; self.depth=1
        elif tag=="table" and self.in_table: self.depth+=1
        if not self.in_table:return
        if tag=="tr":self.in_row=True;self.cells=[]
        elif tag in ("td","th") and self.in_row:self.in_cell=True;self.cell_text=[]
    def handle_data(self,data):
        if self.in_table:
            self.table_text+=data
            if self.in_cell:self.cell_text.append(data)
    def handle_endtag(self,tag):
        if not self.in_table:return
        if tag in ("td","th") and self.in_cell:
            self.cells.append(" ".join(" ".join(self.cell_text).split()));self.in_cell=False
        elif tag=="tr" and self.in_row:
            if self.cells:self.rows.append(self.cells[:])
            self.in_row=False
        elif tag=="table":
            self.depth-=1
            if self.depth==0:self.in_table=False
parser=DispatchTableParser();parser.feed(raw)
if "DESPACHOS" not in parser.table_text.upper() or len(parser.rows)<15:
    raise SystemExit("Dispatch table not found or unexpectedly short")
records=[];section=""
for index,cells in enumerate(parser.rows):
    if len(cells)==1:
        section=cells[0];continue
    if len(cells)==6 and "PRIMER DESPACHO" in cells[1].upper():continue
    def val(i):return cells[i] if i<len(cells) else ""
    records.append({"source_row":index,"section":section,"label_mon_sat":val(0),
        "first_mon_sat":val(1),"last_mon_sat":val(2),
        "label_sun_holiday":val(3),"first_sun_holiday":val(4),
        "last_sun_holiday":val(5),"raw_cells":cells,
        "interpretation":"source_table_raw; Saturday and CUÑA rows require contextual interpretation"})
(OUT/"dispatches.json").write_text(json.dumps({"source":URL,"source_sha256":hashlib.sha256(source).hexdigest(),"rows":records},ensure_ascii=False,indent=2))
with (OUT/"dispatches.csv").open("w",newline="",encoding="utf-8") as fp:
    columns=["source_row","section","label_mon_sat","first_mon_sat","last_mon_sat","label_sun_holiday","first_sun_holiday","last_sun_holiday","interpretation"]
    writer=csv.DictWriter(fp,fieldnames=columns);writer.writeheader()
    for record in records:writer.writerow({k:record[k] for k in columns})
print(f"Preserved {len(records)} dispatch rows, including special service rows")
