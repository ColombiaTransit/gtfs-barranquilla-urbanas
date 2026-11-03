#!/usr/bin/env python3
"""Compare public SIU ordered itinerary GPS points with official AMB KMZ lines.

Produces ranked research evidence only. Different legal A/B patterns can overlap
almost completely; nearest KMZ geometry cannot prove route or variant identity.
"""
import csv
import json
import statistics
import unicodedata
import re
from collections import defaultdict,Counter
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import Point,LineString
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/amb-siu-kmz-crosswalk"
SIU=ROOT/"sources/siu"
KMZ=ROOT/"sources/amb/kmz"
PROJ=Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True)

def read(path):
    with path.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))

def write(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def normalized(t):
    t=unicodedata.normalize("NFKD",(t or "").upper())
    return re.sub("[^A-Z0-9]","", "".join(ch for ch in t if not unicodedata.combining(ch)))

def company(t):
    t=normalized(t)
    return "MONTERREY" if t in ("TRANSPORTESMONTERREY","MONTERREY") else t

def matches_company(kmz_company, siu_companies):
    return company(kmz_company) in {company(x) for x in siu_companies.split(";")}

def lines_from_geojson(source):
    geo=json.loads(source.read_text(encoding="utf-8"))
    result=[]
    for f in geo.get("features",[]):
        obj=f.get("geometry") or {}
        if obj.get("type")!="LineString":continue
        coords=obj.get("coordinates") or []
        if len(coords)<2:continue
        try:
            p=LineString([PROJ.transform(float(c[0]),float(c[1])) for c in coords])
            if p.length>0:result.append(p)
        except (ValueError,TypeError):continue
    return unary_union(result) if result else None

def percentile(sorted_values,p):
    if not sorted_values:return None
    return round(sorted_values[min(len(sorted_values)-1,int((len(sorted_values)-1)*p))],1)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    siu=read(SIU/"gtfs_staging/siu_amb_route_crosswalk_review.csv")
    provisional={x["siu_itinerary_uuid"] for x in read(SIU/"open_route_review/provisional_base_route_code_candidates.csv")}
    records=read(SIU/"public_extract/siu_route_stop_sequences.csv")
    by_itinerary=defaultdict(list)
    for r in records:
        if r.get("likely_test_itinerary")=="true":continue
        try:
            p=Point(*PROJ.transform(float(r["stop_lon"]),float(r["stop_lat"])))
            by_itinerary[r["siu_itinerary_uuid"]].append((int(r["siu_stop_sequence"]),p))
        except (ValueError,TypeError,KeyError):continue
    kmzs=read(KMZ/"manifest.csv")
    shapes={}
    for r in kmzs:
        if not r.get("geojson_path"):continue
        g=KMZ/r["geojson_path"]
        if g.exists():shapes[(r["company"],r["route_label"])]=lines_from_geojson(g)
    scores=[]
    best_rows=[]
    for row in siu:
        itinerary=row["siu_itinerary_uuid"]
        points=[p for _,p in sorted(by_itinerary[itinerary],key=lambda x:x[0])]
        if not points:continue
        status=("existing_strong_geographic_staging" if row["route_match_status"]=="high_confidence_provisional"
                else "existing_provisional_base_staging" if itinerary in provisional
                else "unresolved_or_shared_operator")
        for m in kmzs:
            if not matches_company(m["company"],row["siu_companies"]):continue
            shape=shapes.get((m["company"],m["route_label"]))
            if shape is None:continue
            ds=sorted(p.distance(shape) for p in points)
            count=len(ds)
            coverage_15=sum(x<=15 for x in ds)
            coverage_30=sum(x<=30 for x in ds)
            coverage_50=sum(x<=50 for x in ds)
            reference=normalized(row["candidate_amb_route_code"])
            same_code=bool(reference) and reference==normalized(m["base_route_id_candidate"])
            scores.append({
                "siu_itinerary_uuid":itinerary,
                "siu_name":row["siu_name"],"siu_companies":row["siu_companies"],
                "siu_stop_count":count,
                "existing_siu_status":status,
                "prior_GIS_base_code_candidate":row["candidate_amb_route_code"],
                "kmz_company":m["company"],
                "kmz_route_label":m["route_label"],
                "kmz_base_route_code":m["base_route_id_candidate"],
                "kmz_variant":m["variant"],
                "share_of_SIU_stops_within_15m_pct":round(100*coverage_15/count,1),
                "share_of_SIU_stops_within_30m_pct":round(100*coverage_30/count,1),
                "share_of_SIU_stops_within_50m_pct":round(100*coverage_50/count,1),
                "median_distance_m":round(statistics.median(ds),1),
                "p90_distance_m":percentile(ds,.9),
                "first_SIU_stop_distance_m":round(points[0].distance(shape),1),
                "last_SIU_stop_distance_m":round(points[-1].distance(shape),1),
                "same_as_old_GIS_code_candidate":"yes" if same_code else "no",
                "official_source_KMZ_URL_collision":m.get("source_url_collision",""),
                "kmz_source_url":m["kmz_url"],
                "proven_legal_route_or_AB_variant_mapping":"no",
                "legal_operator_assignment_confirmed":"no",
                "allowed_for_GTFS_stop_times":"no"
            })
    by_itinerary_scores=defaultdict(list)
    for s in scores:
        by_itinerary_scores[s["siu_itinerary_uuid"]].append(s)
    top=[]
    for row in siu:
        uid=row["siu_itinerary_uuid"]
        candidates=sorted(by_itinerary_scores.get(uid,[]),
                          key=lambda x:(-x["share_of_SIU_stops_within_30m_pct"],
                                        -x["share_of_SIU_stops_within_50m_pct"],
                                        x["median_distance_m"],
                                        x["kmz_route_label"]))
        for rank,r in enumerate(candidates,1):
            r["candidate_spatial_rank"]=rank
            if rank<=5:
                top.append(dict(r))
        if candidates:
            first=candidates[0]
            second=candidates[1] if len(candidates)>1 else None
            best_rows.append({
                "siu_itinerary_uuid":uid,"siu_name":row["siu_name"],
                "siu_companies":row["siu_companies"],
                "siu_stop_count":len(by_itinerary.get(uid,[])),
                "current_status":first["existing_siu_status"],
                "legacy_GIS_candidate":row["candidate_amb_route_code"],
                "best_KMZ_candidate":first["kmz_company"]+" / "+first["kmz_route_label"],
                "best_KMZ_coverage30_pct":first["share_of_SIU_stops_within_30m_pct"],
                "best_KMZ_coverage50_pct":first["share_of_SIU_stops_within_50m_pct"],
                "second_KMZ_candidate":second["kmz_company"]+" / "+second["kmz_route_label"] if second else "",
                "second_KMZ_coverage30_pct":second["share_of_SIU_stops_within_30m_pct"] if second else "",
                "best_second_30m_coverage_gap_pct_points":round(
                    first["share_of_SIU_stops_within_30m_pct"]-second["share_of_SIU_stops_within_30m_pct"],1) if second else "",
                "best_KMZ_same_as_old_GIS_code":"yes" if first["same_as_old_GIS_code_candidate"]=="yes" else "no",
                "requires_human_review":"yes",
                "authoritative_AB_mapping_proven":"no"
            })
    if not scores:raise SystemExit("No SIU-to-KMZ geometry scores calculated")
    write(OUT/"all_siu_kmz_spatial_scores_NOT_CONFIRMED.csv",scores,list(scores[0]))
    write(OUT/"top5_kmz_candidates_by_siu_itinerary.csv",top,list(top[0]))
    write(OUT/"siu_kmz_candidate_ranking_review.csv",best_rows,list(best_rows[0]))
    unresolved=[r for r in best_rows if r["current_status"]=="unresolved_or_shared_operator"]
    write(OUT/"thirteen_unresolved_siu_itineraries_kmz_ranking.csv",unresolved,list(best_rows[0]))
    summary={"siu_itineraries_scored":len(best_rows),
             "siu_unresolved_itineraries_scored":len(unresolved),
             "siu_strong_staging_itineraries_scored":sum(r["current_status"]=="existing_strong_geographic_staging" for r in best_rows),
             "siu_provisional_staging_itineraries_scored":sum(r["current_status"]=="existing_provisional_base_staging" for r in best_rows),
             "spatial_candidate_comparisons":len(scores),
             "legally_confirmed_AB_assignments_from_geometry_alone":0,
             "legal_route_crosswalk_overwritten":False,
             "scope":"Research only: SIU stop GPS proximity to official KMZ paths"}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# SIU → AMB KMZ: kandidaten per itinerary",
           "",
           "**Geen automatische hernummering van SIU-itinerary naar AMB-route-ID:** een hoge geografische match bewijst geen juridische A/B-variant.",
           "",f"- {len(best_rows)} SIU-itineraries beoordeeld.",
           f"- {len(unresolved)} nog onzekere SIU-itineraries krijgen een KMZ-ranking.",
           f"- {len(scores)} routegeometrie-kandidaatcombinaties doorgerekend.",
           "",
           "## Onzekere SIU-koppelingen","",
           "| SIU-itinerary | GIS-basiscode | Beste KMZ-kandidaat | Binnen 30 m | Nummer 2 | Binnen 30 m nr.2 |",
           "|---|---|---|---:|---|---:|"]
    for row in unresolved:
        lines.append("| {} | {} | {} | {}% | {} | {}{} |".format(
            row["siu_name"],row["legacy_GIS_candidate"],row["best_KMZ_candidate"],
            row["best_KMZ_coverage30_pct"],row["second_KMZ_candidate"],
            row["second_KMZ_coverage30_pct"],"%" if row["second_KMZ_coverage30_pct"]!="" else ""))
    lines+=["","## Gebruik","",
            "- Controleer eerst operatoren, originele wettelijke straatverlopen en mogelijke A/B-varianten.",
            "- PT4/PT5 en gedeelde vervoerders mogen bij overlappende geometrie niet op rang 1 worden toegewezen.",
            "- De 12 sterke en 8 voorlopige SIU-stopvolgordes worden **niet vervangen** door KMZ-kandidaten.",
            "- Output bevat geen GTFS-stop_times of shapes-publicatie.", ""]
    (OUT/"summary.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
