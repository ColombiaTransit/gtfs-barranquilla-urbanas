#!/usr/bin/env python3
"""Harvest Barranquilla ArcGIS public bus route polyline candidates.

Layer last advertised edit: December 2023. Preserve source geometry and
only suggest exact route-code matches; no fabricated GTFS shapes or stops.
"""
import csv
import json
import re
import sys
from pathlib import Path

import requests

ROOT=Path(__file__).resolve().parents[1]
LAYER="https://services3.arcgis.com/oGYAc07w6wsvgUYr/ArcGIS/rest/services/Movilidad_Transito_WFL1/FeatureServer/6"
def clean(v):
    return re.sub(r"[^A-Z0-9]", "", str(v or "").upper())
def read_csv(path):
    with path.open("r",newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
def save_csv(path,rows,headers):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=headers,extrasaction="ignore");w.writeheader();w.writerows(rows)
def main(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    http=requests.Session()
    http.headers.update({"User-Agent":"ColombiaTransit GTFS research 1.0"})
    routes=read_csv(ROOT/"gtfs/routes.txt")
    response=http.get(LAYER,params={"f":"json"},timeout=60)
    response.raise_for_status()
    metadata=response.json()
    if "error" in metadata:raise RuntimeError(str(metadata["error"]))
    fields=[x.get("name") for x in metadata.get("fields",[])]
    (out/"layer_metadata.json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    step=min(int(metadata.get("maxRecordCount") or 1000),1000)
    all_features=[];seen=set();offset=0;pages=0
    while pages<25:
        q={"where":"1=1","outFields":"OBJECTID,Name,FolderPath,Snippet",
           "returnGeometry":"true","outSR":"4326","f":"geojson",
           "resultOffset":offset,"resultRecordCount":step}
        res=http.get(LAYER+"/query",params=q,timeout=120)
        res.raise_for_status()
        payload=res.json()
        if "error" in payload:raise RuntimeError(str(payload["error"]))
        features=payload.get("features",[])
        if not isinstance(features,list):raise RuntimeError("Unexpected GeoJSON response shape")
        new=[]
        for f in features:
            if f.get("geometry",{}).get("type") not in ("LineString","MultiLineString"):
                continue
            props=f.get("properties") or {}
            ident=str(props.get("OBJECTID") or f.get("id") or "")
            if ident and ident in seen:continue
            if ident:seen.add(ident)
            new.append(f)
        all_features.extend(new)
        pages+=1
        print(json.dumps({"page":pages,"offset":offset,"received":len(features),"unique_so_far":len(all_features)}),flush=True)
        if len(features)<step:break
        offset+=step
    if pages>=25:raise RuntimeError("Pagination limit reached; don't claim full extraction")
    if not all_features:raise RuntimeError("No public transport polylines returned")
    (out/"arcgis_routes_original.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":all_features},
                   ensure_ascii=False)+"\n",encoding="utf-8")
    matched=[];unmatched=[];ambiguous=[]
    for gtfs in routes:
        route=gtfs["route_short_name"]
        code=re.sub(r"[\s-][AB]$","",route,flags=re.I)
        base=clean(code)
        if not base:
            continue
        possible=[]
        for feature in all_features:
            props=feature.get("properties") or {}
            display=" ".join(str(props.get(k) or "") for k in ("Name","FolderPath","Snippet"))
            # Conservative: the full alphanumeric code must occur in a
            # separated piece. We don't infer codes from route descriptions.
            candidates=[clean(t) for t in re.split(r"[\s/()|,;]+",display)]
            if base in candidates:
                possible.append(feature)
        rec={"gtfs_route_id":gtfs["route_id"],"route_short_name":route,
             "agency_id":gtfs["agency_id"],"arcgis_feature_count":len(possible),
             "matching_objectids":";".join(str((x.get("properties") or {}).get("OBJECTID","")) for x in possible),
             "geometry_status":"exact_code_candidate_review_required" if len(possible)==1 else
                 "ambiguous_multiple_shape_candidates" if possible else "no_exact_code_match",
             "source_last_edit":"2023-12-27","source_url":LAYER}
        matched.append(rec)
        if len(possible)!=1:ambiguous.append(rec)
    route_tokens={clean(re.sub(r"[\s-][AB]$","",r["route_short_name"],flags=re.I)) for r in routes}
    for f in all_features:
        props=f.get("properties") or {}
        oid=str(props.get("OBJECTID",""))
        display=" ".join(str(props.get(k) or "") for k in ("Name","FolderPath","Snippet"))
        candidates=[clean(t) for t in re.split(r"[\s/()|,;]+",display)]
        matches=sorted(set(candidates)&route_tokens)
        unmatched.append({"OBJECTID":oid,"Name":props.get("Name",""),
            "FolderPath":props.get("FolderPath",""),"route_code_tokens":";".join(matches),
            "geometry_type":f.get("geometry",{}).get("type","")})
    save_csv(out/"route_shape_matches.csv",matched,
        ["gtfs_route_id","route_short_name","agency_id","arcgis_feature_count",
         "matching_objectids","geometry_status","source_last_edit","source_url"])
    save_csv(out/"arcgis_feature_inventory.csv",unmatched,
        ["OBJECTID","Name","FolderPath","route_code_tokens","geometry_type"])
    status={
        "arcgis_layer":LAYER,
        "layer_name":metadata.get("name"),
        "last_known_data_edit_utc":metadata.get("editingInfo",{}).get("lastEditDate"),
        "source_features":len(all_features),
        "gtfs_routes_checked":len(routes),
        "unique_code_matches":sum(x["arcgis_feature_count"]==1 for x in matched),
        "ambiguous_multi_matches":sum(x["arcgis_feature_count"]>1 for x in matched),
        "no_code_match":sum(x["arcgis_feature_count"]==0 for x in matched),
        "review_note":"Historic 2023 geometry is not approved as current GTFS; check against latest AMB route decisions and stops."}
    (out/"summary.json").write_text(json.dumps(status,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"summary.md").write_text("# AMB ArcGIS route geometry research\n\n"+
        "\n".join(f"- {k}: {v}" for k,v in status.items())+
        "\n\nExact name matches are candidates only. No GTFS shapes.txt created.\n",encoding="utf-8")
    print(json.dumps(status,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "build/amb-arcgis-shapes")
