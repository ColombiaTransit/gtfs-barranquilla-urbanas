#!/usr/bin/env python3
"""Produce a focused ten-route geometry investigation from the comparison CSV."""
import csv,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/"build/gtfs-source-consolidation"
source=folder/"ambq_arcgis_geometry_comparison.csv"
with source.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
unresolved=[r for r in rows if r["decision"]=="GEOMETRY_UNRESOLVED"]
def asint(v):
    try:return int(v)
    except (ValueError,TypeError):return -1
def asfloat(v):
    try:return float(v)
    except (ValueError,TypeError):return 0.
for r in unresolved:
    if r["source_url_collision"]=="True": diagnosis="AMBQ_URL_COLLISION"
    elif asint(r["ambq_sections"])==0:diagnosis="AMBQ_EMPTY_OR_UNAVAILABLE"
    elif asint(r["ambq_unjoined_sections"])>0:diagnosis="AMBQ_DISCONNECTED"
    else:diagnosis="AMBQ_OTHER_SOURCE_CONFLICT"
    if not r["arcgis_objectid"] or asint(r["arcgis_sections"])==0:gis="NO_ARCGIS_GEOMETRY"
    elif asint(r["arcgis_unjoined_sections"])>0:gis="ARCGIS_DISCONNECTED"
    elif asfloat(r["ambq_near_arcgis_fraction"])>=.90 and asfloat(r["arcgis_near_ambq_fraction"])>=.90:gis="ARCGIS_GEOMETRICALLY_SIMILAR_REVIEW"
    else:gis="ARCGIS_OVERLAP_INSUFFICIENT"
    r["ambq_diagnosis"]=diagnosis;r["arcgis_diagnosis"]=gis
    r["next_action"]="REVIEW_SOURCE_IDENTITY" if diagnosis=="AMBQ_URL_COLLISION" else ("REVIEW_SEGMENT_CONNECTIVITY" if diagnosis=="AMBQ_DISCONNECTED" else "REVIEW_GEOMETRY_EVIDENCE")
    r["source_selection_final"]="NOT_APPROVED"
path=folder/"ambq_arcgis_unresolved_detailed.csv"
if unresolved:
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(unresolved[0]));w.writeheader();w.writerows(unresolved)
summary={"unresolved":len(unresolved),"ambq_diagnoses":dict(Counter(x["ambq_diagnosis"] for x in unresolved)),"arcgis_diagnoses":dict(Counter(x["arcgis_diagnosis"] for x in unresolved))}
(folder/"ambq_arcgis_unresolved_detailed.json").write_text(json.dumps({"summary":summary,"routes":unresolved},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary,indent=2))
print("### Ten unresolved AMBQ–ArcGIS routes")
print("| Operator | Route | Variant | AMBQ diagnosis | ArcGIS diagnosis | AMBQ sections / unjoined | ArcGIS sections / unjoined | Overlap AMBQ→GIS / GIS→AMBQ |")
print("|---|---|---|---|---|---|---|---|")
for x in unresolved:
    print("| "+ " | ".join([x["operator"],x["route_code"],x["variant"] or "—",x["ambq_diagnosis"],x["arcgis_diagnosis"],x["ambq_sections"]+"/"+x["ambq_unjoined_sections"],x["arcgis_sections"]+"/"+x["arcgis_unjoined_sections"],x["ambq_near_arcgis_fraction"]+"/"+x["arcgis_near_ambq_fraction"]])+" |")
