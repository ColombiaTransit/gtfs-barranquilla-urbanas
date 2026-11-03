#!/usr/bin/env python3
"""Candidate-match SIU itinerary stop coordinates to historical AMB GIS lines.

All matches are GEOGRAPHIC CANDIDATES, not legal route matches or GTFS
stop_times. A stop being near a line does not prove vehicle service; old GIS
routes can differ from 2025/2026 resolutions.
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform

ROOT=Path(__file__).resolve().parents[1]
SIU=ROOT/"sources/siu/public_extract"
GIS=Path("build/amb-arcgis-shapes/arcgis_routes_original.geojson")
OUT=Path("build/siu-to-amb-gis")


def load(path):
    with path.open(newline="",encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write(path,items):
    with path.open("w",newline="",encoding="utf-8") as handle:
        w=csv.DictWriter(handle,fieldnames=list(items[0]))
        w.writeheader();w.writerows(items)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    itineraries=load(SIU/"siu_itineraries.csv")
    stops=load(SIU/"siu_route_stop_sequences.csv")
    features=json.loads(GIS.read_text(encoding="utf-8"))["features"]
    transformer=Transformer.from_crs(4326,32618,always_xy=True).transform
    lines=[];codes=[]
    for f in features:
        if f.get("geometry",{}).get("type") in ("LineString","MultiLineString"):
            lines.append(transform(transformer,shape(f["geometry"])))
            codes.append(str((f.get("properties") or {}).get("Name") or ""))

    grouped=defaultdict(list)
    for row in stops:
        if row["likely_test_itinerary"]!="true":
            grouped[row["siu_itinerary_uuid"]].append(row)

    results=[]
    for rt in itineraries:
        if rt["likely_test_itinerary"]=="true":continue
        rs=grouped[rt["siu_itinerary_uuid"]]
        if not rs:continue
        idx=np.linspace(0,len(rs)-1,num=min(60,len(rs)),dtype=int)
        points=[transform(transformer,Point(float(rs[i]["stop_lon"]),float(rs[i]["stop_lat"]))) for i in idx]
        scored=[]
        for code,line in zip(codes,lines):
            distances=np.array([line.distance(point) for point in points])
            scored.append({
                "gis_line_name":code,
                "sampled_within_50m":int(np.sum(distances<=50)),
                "sampled_within_100m":int(np.sum(distances<=100)),
                "sampled_stop_count":len(points),
                "median_distance_m":round(float(np.median(distances)),1),
                "p90_distance_m":round(float(np.quantile(distances,.9)),1),
            })
        scored.sort(key=lambda r:(-r["sampled_within_50m"],-r["sampled_within_100m"],r["median_distance_m"]))
        first=scored[0];second=scored[1]
        strength=first["sampled_within_50m"]/len(points)
        difference=(first["sampled_within_50m"]-second["sampled_within_50m"])/len(points)
        status=("strong_geographic_candidate" if strength>=.8 and difference>=.15
                and first["median_distance_m"]<=20 else
                "ambiguous_overlapping_routes" if difference<.10 else
                "partial_old_geometry_match")
        result={
            "siu_itinerary_uuid":rt["siu_itinerary_uuid"],
            "siu_route_uuid":rt["siu_base_route_uuid"],
            "siu_name":rt["siu_display_name"],
            "siu_companies":rt["siu_company_names"],
            "siu_stop_count":len(rs),
            "sampled_stop_count":len(points),
            "top_candidate_gis_route":first["gis_line_name"],
            "top_within_50m":first["sampled_within_50m"],
            "top_coverage_50m_pct":round(100*strength,1),
            "top_median_distance_m":first["median_distance_m"],
            "top_p90_distance_m":first["p90_distance_m"],
            "second_candidate_gis_route":second["gis_line_name"],
            "second_coverage_50m_pct":round(100*second["sampled_within_50m"]/len(points),1),
            "third_candidate_gis_route":scored[2]["gis_line_name"],
            "third_coverage_50m_pct":round(100*scored[2]["sampled_within_50m"]/len(points),1),
            "confidence_geography_only":status,
            "authoritative_gtfs_route_id":"",
            "route_code_confirmed":"no",
            "source_year_gis":"2019-2023",
            "source_year_siu":"2026",
        }
        results.append(result)
    results.sort(key=lambda r:r["siu_name"])
    write(OUT/"siu_to_amb_routecode_candidates.csv",results)
    summary={
        "siu_production_itineraries":len(results),
        "gis_reference_route_features":len(lines),
        "source_siu_route_stop_rows":len(stops),
        "geographic_strong_candidates":sum(r["confidence_geography_only"]=="strong_geographic_candidate" for r in results),
        "geographic_ambiguous_overlap":sum(r["confidence_geography_only"]=="ambiguous_overlapping_routes" for r in results),
        "geographic_partial_match":sum(r["confidence_geography_only"]=="partial_old_geometry_match" for r in results),
        "n_confirmed_legal_gtfs_route_matches":0,
        "warning":"Do not use the nearest 2019/2023 line to assign a 2026 legal route automatically; repeated corridors and A/B variants may share geometry."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"summary.md").write_text("# SIU-to-AMB geographical crosswalk candidates\n\n"+
        "\n".join(f"- {k}: {v}" for k,v in summary.items())+
        "\n\nReview against latest route resolutions before assigning GTFS route_id.\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
