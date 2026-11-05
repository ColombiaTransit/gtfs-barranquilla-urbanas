#!/usr/bin/env python3
"""Read-only topology investigation for COOLITORAL A4-4109 and LOLAYA D8-4165."""
import csv, json, math
from collections import Counter, defaultdict
from pathlib import Path
import compare_ambq_arcgis_geometry as base

TARGETS={("COOLITORAL","A4-4109"),("LOLAYA","D8-4165")}
OUT=base.OUT

def components(lines,tolerance):
    # Endpoint-only graph; no artificial road connections.
    parent=list(range(len(lines)))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    def join(a,b):
        a,b=root(a),root(b)
        if a!=b:parent[b]=a
    ends=[(line[0],line[-1]) for line in lines]
    for i in range(len(lines)):
        for j in range(i):
            if min(base.distance(a,b) for a in ends[i] for b in ends[j])<=tolerance:
                join(i,j)
    groups=defaultdict(list)
    for i in range(len(lines)):groups[root(i)].append(i)
    return sorted(groups.values(),key=len,reverse=True)

def min_gap(group1,group2,lines):
    return min(base.distance(a,b) for i in group1 for j in group2 for a in (lines[i][0],lines[i][-1]) for b in (lines[j][0],lines[j][-1]))

def inspect(lines):
    if not lines:return {"segments":0,"status":"NO_LINES"}
    result={"segments":len(lines),"points":sum(map(len,lines)),
            "closed_segments_100m":sum(base.distance(l[0],l[-1])<=100 for l in lines),
            "endpoint_components":{}}
    for tol in (10,30,100):
        groups=components(lines,tol)
        result["endpoint_components"][str(tol)+"m"]={"count":len(groups),"largest_segment_counts":[len(g) for g in groups[:10]]}
    groups=components(lines,100)
    if len(groups)>1:
        result["nearest_component_endpoint_gap_m"]=round(min(min_gap(groups[0],g,lines) for g in groups[1:]),1)
    # Count proximity of endpoints to ANY interior vertex of other segments.
    # This catches fragmented, unordered KMZ LineStrings without inventing roads.
    vertices=[(j,p) for j,line in enumerate(lines) for p in base.sample(line,250)]
    near=0
    for i,line in enumerate(lines):
        for endpoint in (line[0],line[-1]):
            if any(j!=i and base.distance(endpoint,p)<=30 for j,p in vertices):
                near+=1
    result["endpoints_near_other_segment_vertex_30m"]=near
    result["endpoints_total"]=2*len(lines)
    return result

def main():
    rows=base.csvrows(base.ROOT/"sources/amb/kmz_stop_gaps/kmz_siu_route_stop_coverage.csv")
    matches=base.csvrows(base.ROOT/"sources/amb/arcgis_shape_staging/route_shape_matches.csv")
    reports=[]
    for row in rows:
        key=(row["company"],row["kmz_base_route_code"])
        if key not in TARGETS:continue
        report={"operator":key[0],"route":key[1],"ambq_url":row["source_kmz_url"]}
        try:
            lines=base.kmz_lines(row["source_kmz_url"])
            report["ambq"]=inspect(lines)
        except Exception as exc:
            report["ambq"]={"segments":0,"status":"FETCH_OR_PARSE_FAILED","error_type":type(exc).__name__,"error":str(exc)[:250]}
        # ArcGIS geometry retrieved by the same unique object-id mapping as the comparison.
        candidates=[m for m in matches if base.clean(m["route_short_name"])==base.clean(key[1]) and m["arcgis_feature_count"]=="1"]
        ids={m["matching_objectids"] for m in candidates}
        if len(ids)==1:
            oid=next(iter(ids))
            try:
                payload=json.loads(base.request(base.LAYER+"/query",{"where":"OBJECTID="+str(int(oid)),"outFields":"OBJECTID","returnGeometry":"true","outSR":"4326","f":"geojson"}))
            except Exception as exc:
                report["arcgis"]={"status":"FETCH_OR_PARSE_FAILED","error_type":type(exc).__name__,"error":str(exc)}
                payload={}
            features=payload.get("features",[])
            if len(features)==1:
                geom=features[0]["geometry"]
                coords=geom.get("coordinates",[])
                parts=[coords] if geom.get("type")=="LineString" else coords if geom.get("type")=="MultiLineString" else []
                gis=[[(p[1],p[0]) for p in part] for part in parts if len(part)>1]
                report["arcgis_objectid"]=oid
                report["arcgis"]=inspect(gis)
        reports.append(report)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"two_route_topology.json").write_text(json.dumps(reports,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["### Detailed topology: A4-4109 and D8-4165","","Read-only. Endpoint connectivity is not proof of road continuity; no routing or GTFS changes.",""]
    for r in reports:
        lines+=["#### "+r["operator"]+" "+r["route"],""]
        for source in ("ambq","arcgis"):
            if source not in r:continue
            v=r[source]
            if v.get("status")=="FETCH_OR_PARSE_FAILED":
                lines.append(f"- {source.upper()}: source unavailable or invalid ({v['error_type']}: {v['error']}); topology not assessed")
                continue
            lines.append(f"- {source.upper()}: {v['segments']} segments, {v['points']} vertices; components at 10/30/100 m: "+"/".join(str(v["endpoint_components"][str(t)+"m"]["count"]) for t in (10,30,100))+f"; endpoints near other line vertices (30m): {v['endpoints_near_other_segment_vertex_30m']}/{v['endpoints_total']}")
            if "nearest_component_endpoint_gap_m" in v:lines.append(f"  - Nearest gap from largest component: {v['nearest_component_endpoint_gap_m']} m")
        lines.append("")
    (OUT/"two_route_topology.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))
if __name__=="__main__":main()
