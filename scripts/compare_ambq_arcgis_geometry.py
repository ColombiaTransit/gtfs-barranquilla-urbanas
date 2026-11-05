#!/usr/bin/env python3
"""Read-only AMBQ-first shape audit. Never writes GTFS files."""
import ast, csv, io, json, math, re, urllib.parse, urllib.request, zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/gtfs-source-consolidation"
LAYER="https://services3.arcgis.com/oGYAc07w6wsvgUYr/ArcGIS/rest/services/Movilidad_Transito_WFL1/FeatureServer/6"
JOIN_M=100
def csvrows(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def request(url,params=None):
    if params:url+="?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":"ColombiaTransit-Geometry-QA/1.0"})
    with urllib.request.urlopen(req,timeout=35) as f:return f.read(16000000)
def kmz_lines(url):
    raw=request(url)
    if zipfile.is_zipfile(io.BytesIO(raw)):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            names=[n for n in z.namelist() if n.lower().endswith(".kml")]
            if not names:return []
            raw=z.read(names[0])
    root=ET.fromstring(raw);lines=[]
    for e in root.iter():
        if e.tag.split("}")[-1]!="LineString":continue
        for c in e.iter():
            if c.tag.split("}")[-1]!="coordinates" or not c.text:continue
            line=[]
            for token in c.text.split():
                parts=token.split(",")
                if len(parts)<2:continue
                try:
                    lon,lat=float(parts[0]),float(parts[1])
                    if -75.5<lon<-74.3 and 10.3<lat<11.5:line.append((lat,lon))
                except ValueError:pass
            if len(line)>1:lines.append(line)
    return lines
def distance(a,b):
    p1,p2=math.radians(a[0]),math.radians(b[0])
    dp=p2-p1;dl=math.radians(b[1]-a[1])
    return 12742017.6*math.asin(min(1,math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2)))
def chain(lines):
    """Greedy endpoint-only connection; never bridges an unobserved road."""
    if not lines:return ([],0,0)
    remaining=[list(x) for x in lines];ordered=remaining.pop(0);gaps=[]
    while remaining:
        candidates=[]
        for i,line in enumerate(remaining):
            candidates.extend([(distance(ordered[-1],line[0]),i,False,False),
                               (distance(ordered[-1],line[-1]),i,False,True),
                               (distance(ordered[0],line[-1]),i,True,False),
                               (distance(ordered[0],line[0]),i,True,True)])
        gap,i,prepend,reverse=min(candidates)
        if gap>JOIN_M:break
        part=remaining.pop(i)
        if reverse:part.reverse()
        if prepend:ordered=part+ordered
        else:ordered+=part
        gaps.append(gap)
    return ordered,len(remaining),max(gaps,default=0)
def sample(line,n=150):
    if not line:return []
    if len(line)<=n:return line
    return [line[round(i*(len(line)-1)/(n-1))] for i in range(n)]
def proximity(a,b,limit=100):
    if not a or not b:return 0
    aa=sample(a);bb=sample(b)
    return round(sum(min(distance(p,q) for q in bb)<=limit for p in aa)/len(aa),3)
def clean(v):return re.sub("[^A-Z0-9]","",str(v or "").upper())
def verified_overrides():
    """Read the existing harvester's literal override registry; avoid a second list."""
    tree=ast.parse((ROOT/"scripts/harvest_amb_kmz_routes.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="DIRECT_ROUTE_OVERRIDES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("Missing DIRECT_ROUTE_OVERRIDES in KMZ harvester")

def effective_url(row,overrides):
    label=row["kmz_base_route_code"]+(" "+row["kmz_variant"].strip() if row["kmz_variant"].strip() else "")
    filename=overrides.get((row["company"],label))
    if filename:
        return "https://www.ambq.gov.co/ruta-de-buses/"+urllib.parse.quote(row["company"],safe="")+"/"+urllib.parse.quote(filename,safe="._-"),True
    return row["source_kmz_url"],False

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    routes=csvrows(ROOT/"sources/amb/kmz_stop_gaps/kmz_siu_route_stop_coverage.csv")
    matches=csvrows(ROOT/"sources/amb/arcgis_shape_staging/route_shape_matches.csv")
    bycode={}
    for m in matches:
        base=re.sub(r"([ -][AB])$","",m["route_short_name"],flags=re.I)
        bycode.setdefault(clean(base),[]).append(m)
    cache={};gis_cache={};output=[];overrides=verified_overrides()
    effective_urls=[effective_url(row,overrides)[0] for row in routes]
    counts=Counter(effective_urls)
    for row in routes:
        url,overridden=effective_url(row,overrides);code=row["kmz_base_route_code"];variant=row["kmz_variant"].strip()
        errors=[]
        if url not in cache:
            try:cache[url]=kmz_lines(url)
            except Exception as e:cache[url]=[];errors.append("ambq_fetch_or_parse_failed:"+type(e).__name__)
        lines=cache[url];merged,unjoined,_=chain(lines)
        amb_ok=bool(lines) and unjoined==0
        candidates=[m for m in bycode.get(clean(code),[]) if m["arcgis_feature_count"]=="1"]
        if variant:
            specific=[m for m in candidates if m["pattern_variant"].upper()==variant.upper()]
            candidates=specific or candidates
        oids={m["matching_objectids"] for m in candidates}
        oid=next(iter(oids)) if len(oids)==1 else ""
        gis=[];gis_unjoined=-1
        if oid:
            if oid not in gis_cache:
                try:
                    payload=json.loads(request(LAYER+"/query",{"where":"OBJECTID="+str(int(oid)),"outFields":"OBJECTID,Name","returnGeometry":"true","outSR":"4326","f":"geojson"}))
                    feature=payload.get("features",[])
                    geom=feature[0]["geometry"] if len(feature)==1 else {}
                    coords=geom.get("coordinates",[])
                    parts=[coords] if geom.get("type")=="LineString" else coords if geom.get("type")=="MultiLineString" else []
                    gis_cache[oid]=[[(p[1],p[0]) for p in part if len(p)>=2] for part in parts if len(part)>1]
                except Exception:gis_cache[oid]=[]
            gis=gis_cache[oid]
        gis_merged,gis_unjoined,_=chain(gis)
        forward=proximity(merged,gis_merged);reverse=proximity(gis_merged,merged)
        collision=counts[url]>1
        # ArcGIS may corroborate an AMBQ shape, but never auto-approve a historic variant.
        if collision:decision="GEOMETRY_UNRESOLVED";reason="ambq_source_url_collision"
        elif amb_ok:decision="AMBQ_OK" if len(lines)==1 else "AMBQ_RECONSTRUCTED";reason="ambq_segments_connected"
        elif gis and gis_unjoined==0 and merged and forward>=0.90 and reverse>=0.90 and not variant:
            decision="ARCGIS_FALLBACK_CANDIDATE";reason="bidirectional_100m_overlap_at_least_90pct"
        else:decision="GEOMETRY_UNRESOLVED";reason="insufficient_continuity_or_corroboration"
        output.append({"operator":row["company"],"route_code":code,"variant":variant,"ambq_url":url,
            "original_page_url":row["source_kmz_url"],"verified_direct_override":overridden,
            "ambq_sections":len(lines),"ambq_unjoined_sections":unjoined,"ambq_connected":amb_ok,
            "arcgis_objectid":oid,"arcgis_sections":len(gis),"arcgis_unjoined_sections":gis_unjoined,
            "ambq_near_arcgis_fraction":forward,"arcgis_near_ambq_fraction":reverse,
            "source_url_collision":collision,"decision":decision,"reason":reason,
            "gtfs_shapes_modified":"no","arcgis_historic_unverified":"yes"})
    path=OUT/"ambq_arcgis_geometry_comparison.csv"
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
    summary={"routes":len(output),"decisions":dict(Counter(x["decision"] for x in output)),
             "policy":"AMBQ preferred; ArcGIS only a candidate with two-way >=90% proximity within 100m; GraphHopper excluded",
             "limitations":"Endpoint greedy chaining can miss branching/loops; historic ArcGIS cannot independently confirm current variants; no GTFS changes."}
    (OUT/"ambq_arcgis_geometry_comparison_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
