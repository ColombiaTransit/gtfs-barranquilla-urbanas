#!/usr/bin/env python3
"""Publish one provisional geographic candidate per real SIU itinerary.

No legal route identity, operator entitlement or GTFS stop_times is confirmed.
"""
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sources/amb/kmz_stop_research/siu_crosswalk"
def load(name):
    with (BASE/name).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
scores=load("all_siu_kmz_spatial_scores_NOT_CONFIRMED.csv")
audits={r["siu_itinerary_uuid"]:r for r in load("siu_kmz_loop_aware_audit_DIAGNOSTIC.csv") if r["candidate_spatial_rank"]=="1"}
exceptions={r["siu_name"]:r for r in load("two_route_exception_summary_DIAGNOSTIC.csv")}
path_reviews={r["siu_uuid"]:r for r in load("four_disputed_routes_path_review_NOT_LEGAL.csv")}
result=[]
for s in scores:
    if s["candidate_spatial_rank"]!="1":continue
    a=audits[s["siu_itinerary_uuid"]]
    coverage=float(s["share_of_SIU_stops_within_50m_pct"])
    backwards=float(a["backward_pct"] or 100)
    collision=s["official_source_KMZ_URL_collision"]=="yes"
    if s["siu_name"] in exceptions:status="needs_geometry_review"
    elif collision:status="source_url_collision_review"
    elif coverage>=95 and backwards<=2:status="strong_geographic_candidate"
    elif coverage>=90 and backwards<=15:status="plausible_geographic_candidate"
    else:status="needs_geographic_review"
    note=""
    if s["siu_name"]=="LAS PALMAS":note="15 backward jumps; 1 implausible leap; 8 stops outside 50m"
    elif s["siu_name"]=="VILLA CAROLINA ZOOLOGICO":note="8 stops outside 50m at route beginning/end"
    elif s["siu_itinerary_uuid"] in path_reviews:note="four-route detailed path review completed"
    result.append({
      "siu_itinerary_uuid":s["siu_itinerary_uuid"],"siu_name":s["siu_name"],
      "siu_companies":s["siu_companies"],"siu_stop_count":s["siu_stop_count"],
      "prior_gis_code":s["prior_GIS_base_code_candidate"],
      "provisional_kmz_route":s["kmz_route_label"],
      "kmz_company":s["kmz_company"],"kmz_base_code":s["kmz_base_route_code"],
      "kmz_variant":s["kmz_variant"],
      "coverage_50m_pct":s["share_of_SIU_stops_within_50m_pct"],
      "loop_aware_backward_pct":a["backward_pct"],
      "loop_aware_orientation":a["orientation"],
      "source_url_collision":s["official_source_KMZ_URL_collision"],
      "geographic_status":status,"exception_note":note,
      "legal_route_confirmed":"no","gtfs_stop_times_approved":"no",
      "mapping_status":"PROVISIONAL_NOT_LEGAL","kmz_source_url":s["kmz_source_url"]
    })
if len(result)!=33 or len({r["siu_itinerary_uuid"] for r in result})!=33:
    raise SystemExit("Expected exactly 33 unique SIU itineraries")
out=BASE/"provisional_siu_kmz_mapping_33_NOT_LEGAL.csv"
with out.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
print(f"Published {len(result)} provisional mappings: {out}")
for row in result:print(row["siu_name"],"=>",row["provisional_kmz_route"],row["geographic_status"])
