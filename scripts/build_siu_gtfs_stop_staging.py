#!/usr/bin/env python3
"""Stage GTFS stop IDs and a conservative SIU-to-AMB route crosswalk.

Inputs: public SIU itineraries + route-ordered GPS stops, researched 2023 GIS
name proximity, and existing 97 AMB route IDs. All crosswalk matches are
PROVISIONAL, not a confirmation of legal route identity. This script neither
creates trips/stop_times nor publishes a production GTFS feed.

For deduplication, only identical normalized rider-facing stop names (including
the original compass/traffic direction markers) may merge, and only if every
member of the 5m cluster is within 5m of every other member. Identical GPS with
different names and opposing directions are flagged rather than collapsed.
"""
import argparse
import csv
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SIU=ROOT/"sources/siu/public_extract"
GIS=ROOT/"sources/siu/analysis/siu_to_amb_routecode_candidates.csv"
ROUTES=ROOT/"gtfs/routes.txt"
CORRECTIONS=ROOT/"sources/siu/stop_name_spelling_corrections_2026-11-03.csv"
PREVIOUS=ROOT/"sources/siu/gtfs_staging"
MAX_MERGE_METERS=5.0

def load(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def write(path, rows, fields):
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def simplify(text):
    s=unicodedata.normalize("NFKD",str(text or "").upper())
    return "".join(c for c in s if not unicodedata.combining(c))

def key(text):
    return re.sub(r"[^A-Z0-9]","",simplify(text))

def route_base(name):
    # Only strip suffixes separated by space or "-"; never strip internal B
    # of "B11-B-4192" or "C2-B-4187".
    text=simplify(name).strip()
    m=re.fullmatch(r"(.+-\d{4})(?:[\s-]([AB]))?",text)
    return m.group(1) if m else text

def gis_code(text):
    m=re.search(r"\b([A-Z]{1,4}\d+(?:-?[A-Z])?-\s*\d{4})\b",simplify(text))
    return m.group(1) if m else ""

def agency_keys(names):
    companies=[key(x) for x in str(names or "").split(";") if x.strip()]
    out=set(companies)
    if "TRANSPORTESMONTERREY" in out:out.add("MONTERREY")
    return out

def metres(a,b):
    a_lat,a_lon=a;b_lat,b_lon=b
    dy=(a_lat-b_lat)*111195.0
    dx=(a_lon-b_lon)*111195.0*math.cos(math.radians((a_lat+b_lat)/2))
    return math.hypot(dx,dy)

def build_crosswalk(itins,gis,routes):
    by_code=defaultdict(list)
    for rt in routes:
        by_code[key(route_base(rt["route_short_name"]))].append(rt)
    gis_by_uuid={r["siu_itinerary_uuid"]:r for r in gis}
    output=[];summary=Counter();route_by_siu={}
    for item in itins:
        if item["likely_test_itinerary"]=="true":
            summary["test_excluded"]+=1
            continue
        entry=gis_by_uuid.get(item["siu_itinerary_uuid"])
        if not entry:raise ValueError("Missing spatial audit for SIU itinerary "+item["siu_itinerary_uuid"])
        companies=agency_keys(item["siu_company_names"])
        ranked=[]
        for position,prefix in [(1,"top"),(2,"second"),(3,"third")]:
            route_label=entry[f"{prefix}_candidate_gis_route"]
            score=float(entry[f"{prefix}_coverage_50m_pct"] or 0)
            code=gis_code(route_label)
            candidates=by_code[key(code)] if code else []
            same_company=[r for r in candidates if key(r["agency_id"].removeprefix("AMB_")) in companies]
            ranked.append((position,route_label,code,score,candidates,same_company))
        top=ranked[0]
        second=ranked[1]
        delta=round(top[3]-second[3],1)
        multi_operator=len([x for x in str(item["siu_company_names"]).split(";") if x.strip()])!=1
        status="needs_route_resolution_review"
        if not top[4]:
            status="top_gis_code_absent_in_gtfs_routes"
        elif not top[5]:
            status="top_gis_operator_does_not_match_siu"
        elif multi_operator:
            status="shared_multi_operator_itinerary"
        elif len(top[5])!=1:
            status="variant_A_B_unresolved"
        elif top[3]<80:
            status="gis_coverage_below_80pct"
        elif delta<15:
            status="overlapping_routes_margin_below_15pct"
        else:
            status="high_confidence_provisional"
        chosen=top[5][0]["route_id"] if status=="high_confidence_provisional" else ""
        summary[status]+=1
        route_by_siu[item["siu_itinerary_uuid"]]=chosen
        output.append({
            "siu_itinerary_uuid":item["siu_itinerary_uuid"],
            "siu_base_route_uuid":item["siu_base_route_uuid"],
            "siu_name":item["siu_display_name"],
            "siu_companies":item["siu_company_names"],
            "siu_stop_count":item["stop_count"],
            "suggested_gtfs_route_id":chosen,
            "candidate_amb_route_code":top[2],
            "candidate_gis_name":top[1],
            "top_gis_coverage_pct":top[3],
            "second_gis_name":second[1],
            "second_gis_coverage_pct":second[3],
            "gis_margin_percentage_points":delta,
            "same_company_gtfs_ids":";".join(r["route_id"] for r in top[5]),
            "route_match_status":status,
            "official_amb_route_code_explicit_in_siu":"no",
            "legal_resolution_reviewed_for_crosswalk":"no",
            "final_gtfs_route_mapping_confirmed":"no",
            "source_siu_snapshot_utc":item["source_snapshot_utc"],
            "source_gis_year":"2019-2023",
            "review_next":"Compare direction and route-name with latest legally applicable AMB resolution; check A/B variants and shared operators",
        })
    return output,route_by_siu,summary

def spelling_rules(rows):
    rules={}
    for row in rows:
        if row["review_status"]!="approved_clear_typo":
            continue
        before,after=row["source_name_exact"],row["canonical_name"]
        if not before or not after or before==after:
            raise ValueError("Invalid approved spelling rule")
        if before in rules:
            raise ValueError("Duplicate spelling correction: "+before)
        # Spelling fixes may not change direction codes or the return marker.
        dirs=lambda x:re.findall(r"(?<!\w)(?:NS|SN|EO|OE|REGRESO|RETORNO|VUELTA)(?!\w)",simplify(x))
        if dirs(before)!=dirs(after):
            raise ValueError("Spelling rule modifies a direction/return marker")
        rules[before]=after
    return rules

def build_stop_candidates(stop_rows,route_by_siu,corrections):
    prod=[s for s in stop_rows if s["likely_test_itinerary"]!="true"]
    # Strictly preserve directional codes by keeping *full* normalized name.
    indexed=defaultdict(list)
    for s in prod:
        uid=s["siu_stop_uuid"]
        if not uid:raise ValueError("Missing SIU stop UUID")
        lat=float(s["stop_lat"]);lon=float(s["stop_lon"])
        if not (10.0<=lat<=11.5 and -75.5<=lon<=-74.0):
            raise ValueError("Out-of-region SIU coordinate: "+uid)
        original=s["stop_name"]
        canonical=corrections.get(original,original)
        s={**s,"_lat":lat,"_lon":lon,
           "_original_stop_name":original,"stop_name":canonical,
           "_name_was_corrected":original!=canonical}
        indexed[key(s["stop_name"])].append(s)
    cluster_list=[]
    mapping={}
    # Deterministic input sort makes stop IDs stable for the same input data.
    for name_key in sorted(indexed):
        rows=sorted(indexed[name_key],key=lambda r:(r["_lat"],r["_lon"],r["siu_stop_uuid"]))
        clusters=[]
        for row in rows:
            assigned=None
            for cl in clusters:
                # Require *every* pair of points in a cluster to be <=5m apart:
                # a chain of 4m segments cannot collapse 40m of road.
                if all(metres((row["_lat"],row["_lon"]),(x["_lat"],x["_lon"]))<=MAX_MERGE_METERS for x in cl):
                    assigned=cl;break
            if assigned is None:
                assigned=[]
                clusters.append(assigned)
            assigned.append(row)
        for cl in clusters:
            marker=min(x["siu_stop_uuid"] for x in cl)
            stop_id="SIU_"+marker
            lat=round(sum(x["_lat"] for x in cl)/len(cl),7)
            lon=round(sum(x["_lon"] for x in cl)/len(cl),7)
            chosen_name=Counter(x["stop_name"] for x in cl).most_common(1)[0][0]
            is_exact=len({(x["_lat"],x["_lon"]) for x in cl})==1
            cluster_list.append({
                "stop_id":stop_id,"stop_name":chosen_name,"stop_lat":lat,
                "stop_lon":lon,"location_type":0,
                "source_uuid_anchor":marker,
                "original_siu_names":" | ".join(sorted({x["_original_stop_name"] for x in cl})),
                "spelling_corrected_occurrences":sum(x["_name_was_corrected"] for x in cl),
                "siu_uuid_occurrences":len(cl),
                "siu_itineraries":len({x["siu_itinerary_uuid"] for x in cl}),
                "merge_rule":"same_full_normalized_name_exact_coordinate" if is_exact else "same_full_normalized_name_all_within_5m",
                "stop_id_stability":"stable_within_snapshot_anchor_uuid;retain_alias_mapping_on_update",
                "boarding_direction_status":"preserved_in_stop_name",
                "publication_license_status":"unverified",
                "source":"SIU_public_route_stop_listing",
            })
            for row in cl:
                if row["siu_stop_uuid"] in mapping:raise ValueError("duplicate SIU source stop UUID")
                mapping[row["siu_stop_uuid"]]=stop_id
    occurrence=[]
    for row in sorted(prod,key=lambda r:(r["siu_itinerary_uuid"],int(r["siu_stop_sequence"]))):
        occurrence.append({
            "siu_itinerary_uuid":row["siu_itinerary_uuid"],
            "siu_base_route_uuid":row["siu_base_route_uuid"],
            "siu_route_name":row["siu_display_name"],
            "siu_companies":row["siu_companies"],
            "stop_sequence":row["siu_stop_sequence"],
            "siu_stop_uuid":row["siu_stop_uuid"],
            "candidate_stop_id":mapping[row["siu_stop_uuid"]],
            "proposed_gtfs_route_id":route_by_siu.get(row["siu_itinerary_uuid"],""),
            "stop_name_source":row["_original_stop_name"],
            "stop_name_normalized":row["stop_name"],
            "spelling_correction_applied":str(row["_name_was_corrected"]).lower(),
            "stop_lat_source":row["stop_lat"],
            "stop_lon_source":row["stop_lon"],
            "stop_time_intervals_available":"no",
            "gtfs_trip_id_available":"no",
            "gtfs_stop_assignment_confirmed":"no",
        })
    # Identical coordinates, differing names: don't automatically merge.
    by_point=defaultdict(list)
    for stop in cluster_list:
        by_point[(stop["stop_lat"],stop["stop_lon"])].append(stop)
    conflicts=[]
    for (lat,lon),stops in sorted(by_point.items()):
        if len({key(x["stop_name"]) for x in stops})<=1:continue
        conflicts.append({
            "stop_lat":lat,"stop_lon":lon,
            "candidate_stop_ids":";".join(x["stop_id"] for x in stops),
            "distinct_stop_names":" | ".join(x["stop_name"] for x in stops),
            "manual_review_reason":"identical_centroid_but_name_or_direction_differs",
            "auto_merged":"no",
        })
    return cluster_list,occurrence,conflicts

def compute_aliases(occurrences):
    """Retain old stop IDs merged by spelling correction on future reruns."""
    oldmap={}
    oldfile=PREVIOUS/"siu_stop_occurrence_crosswalk.csv"
    if oldfile.is_file():
        oldmap={x["siu_stop_uuid"]:x["candidate_stop_id"] for x in load(oldfile)}
    aliases={}
    aliasfile=PREVIOUS/"stop_id_alias_history.csv"
    if aliasfile.is_file():
        for row in load(aliasfile):
            aliases[row["old_stop_id"]]=row["new_stop_id"]
    changes=[]
    for row in occurrences:
        old=oldmap.get(row["siu_stop_uuid"])
        new=row["candidate_stop_id"]
        if old and old!=new:
            if old in aliases and aliases[old]!=new:
                raise ValueError("Existing stop ID alias changed unexpectedly: "+old)
            aliases[old]=new
            changes.append((old,new))
    target_ids={x["candidate_stop_id"] for x in occurrences}
    for old,new in aliases.items():
        if old in target_ids:
            raise ValueError("Alias still points to a current stop ID: "+old)
        if new not in target_ids:
            raise ValueError("Alias target no longer exists: "+new)
    alias_rows=[{
        "old_stop_id":old,"new_stop_id":new,
        "reason":"verified_spelling_normalization_merged_same_named_stop_within_5m",
        "source_rule_file":"sources/siu/stop_name_spelling_corrections_2026-11-03.csv"
        } for old,new in sorted(aliases.items())]
    return alias_rows,len(set(changes))

def validate(routes,occurrence,stop_rows):
    by_it=defaultdict(list)
    for r in occurrence:by_it[r["siu_itinerary_uuid"]].append(int(r["stop_sequence"]))
    for uuid,nums in by_it.items():
        if sorted(nums)!=list(range(1,len(nums)+1)):
            raise ValueError(f"Non-contiguous sequence for {uuid}")
    ids={r["stop_id"] for r in stop_rows}
    if len(ids)!=len(stop_rows):raise ValueError("Duplicate staged stop_id")
    if any(r["candidate_stop_id"] not in ids for r in occurrence):raise ValueError("Unknown stop_id")
    if len(occurrence)!=sum(len(v) for v in by_it.values()):raise ValueError("Invalid occurrence accounting")

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    itins=load(SIU/"siu_itineraries.csv")
    route_rows=load(SIU/"siu_route_stop_sequences.csv")
    routes=load(ROUTES)
    gis=load(GIS)
    crosswalk,route_map,types=build_crosswalk(itins,gis,routes)
    rules=spelling_rules(load(CORRECTIONS))
    unrecognized=set(rules)-{r["stop_name"] for r in route_rows}
    if unrecognized:
        raise ValueError("Spelling rule source absent in original SIU export: "+str(sorted(unrecognized)))
    stops,seq,conflicts=build_stop_candidates(route_rows,route_map,rules)
    validate(crosswalk,seq,stops)
    aliases,new_alias_count=compute_aliases(seq)
    corrected=[r for r in seq if r["spelling_correction_applied"]=="true"]
    write(out/"stop_name_correction_audit.csv",[
        {"siu_stop_uuid":r["siu_stop_uuid"],"siu_itinerary_uuid":r["siu_itinerary_uuid"],
         "original_name":r["stop_name_source"],"canonical_name":r["stop_name_normalized"],
         "candidate_stop_id":r["candidate_stop_id"],
         "rule_file":"sources/siu/stop_name_spelling_corrections_2026-11-03.csv"}
        for r in corrected],
        ["siu_stop_uuid","siu_itinerary_uuid","original_name","canonical_name","candidate_stop_id","rule_file"])
    write(out/"stop_id_alias_history.csv",aliases,
        ["old_stop_id","new_stop_id","reason","source_rule_file"])
    write(out/"siu_amb_route_crosswalk_review.csv",crosswalk,list(crosswalk[0]))
    write(out/"candidate_stops.csv",stops,list(stops[0]))
    write(out/"siu_stop_occurrence_crosswalk.csv",seq,list(seq[0]))
    # These previews are GTFS-shaped but not a publishable stops.txt/feed.
    preview_stops=[
        {k:r[k] for k in ("stop_id","stop_name","stop_lat","stop_lon","location_type")}
        for r in stops
    ]
    write(out/"stops_draft_NOT_FOR_PUBLICATION.txt",preview_stops,
          ["stop_id","stop_name","stop_lat","stop_lon","location_type"])
    matched_stop_orders=[
        {"route_id":r["proposed_gtfs_route_id"],
         "siu_itinerary_uuid":r["siu_itinerary_uuid"],
         "stop_sequence":r["stop_sequence"],
         "stop_id":r["candidate_stop_id"],
         "stop_name":r["stop_name_normalized"],
         "stop_name_original_siu":r["stop_name_source"],
         "status":"provisional_route_mapping_not_stop_times",
         "trip_id":"","arrival_time":"","departure_time":""}
        for r in seq if r["proposed_gtfs_route_id"]
    ]
    write(out/"candidate_route_stop_orders_NO_TIMES.csv",matched_stop_orders,
          ["route_id","siu_itinerary_uuid","stop_sequence","stop_id","stop_name",
           "stop_name_original_siu","status","trip_id","arrival_time","departure_time"])

    write(out/"coincident_different_name_review.csv",conflicts,
          list(conflicts[0]) if conflicts else ["stop_lat","stop_lon","candidate_stop_ids","distinct_stop_names","manual_review_reason","auto_merged"])
    summary={
        "siu_regular_itineraries":len(crosswalk),
        "excluded_test_itineraries":len(itins)-len(crosswalk),
        "siu_stop_occurrences_regular":len(seq),
        "conservatively_deduplicated_candidate_stops":len(stops),
        "stop_records_merged_to_existing_candidate":len(seq)-len(stops),
        "provisionally_linked_route_stop_occurrences":len(matched_stop_orders),
        "provisionally_linked_distinct_stop_ids":len({r["stop_id"] for r in matched_stop_orders}),
        "different_name_same_rounded_coordinate_review":len(conflicts),
        "approved_spelling_rules":len(rules),
        "siu_stop_occurrences_spelling_normalized":len(corrected),
        "retained_historical_stop_id_aliases":len(aliases),
        "new_stop_id_aliases_detected_this_run":new_alias_count,
        "high_confidence_provisional_route_code_links":types["high_confidence_provisional"],
        "route_code_links_held_for_review":len(crosswalk)-types["high_confidence_provisional"],
        "route_crosswalk_statuses":dict(sorted(types.items())),
        "auto_confirmed_legal_route_matches":0,
        "production_gtfs_stops_txt_generated":False,
        "production_gtfs_stop_times_txt_generated":False,
        "merge_threshold_metres":MAX_MERGE_METERS,
        "caution":"2026 public SIU data has unverified reuse license; GIS 2019/2023 cannot alone confirm legal 2026 route code. Research staging only."
    }
    (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# SIU route-code crosswalk and conservative stop clustering","",
           f"**{len(crosswalk)} non-test SIU itineraries**, {len(seq)} ordered stop visits.",
           f"**{len(stops)} candidate physical stops** grouped only by SAME direction-preserving normalized name and all points within {MAX_MERGE_METERS}m.",
           f"**{len(conflicts)} same-coordinate/different-name cases left separate**.",
           f"**{len(rules)} reviewed spelling corrections**, {len(corrected)} SIU occurrences corrected; originals preserved.",
           f"**{len(aliases)} historical stop ID aliases** retained after merge.",
           f"**{len(matched_stop_orders)} stop visits have a provisional AMB route ID**, with no timetable fields.",
           f"**{types['high_confidence_provisional']} high-confidence geographic/operator route links**; NO legal code mappings automatically confirmed.",
           "", "Route crosswalk status:"]
    lines.extend(f"- {k}: {v}" for k,v in sorted(types.items()))
    lines+=["","No synthetic GPS, no invented arrivals/departures, no test routes, no vehicle fleet values.",
            "The final official AMB route and stop mapping remains subject to latest resolution and itinerary-variant review.",
            "A stop ID anchored to the minimum SIU UUID is stable for a fixed snapshot; preserve this mapping when updating SIU data.",
            "Do not publish the derived SIU stops until public data reuse rights are checked."]
    (out/"summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",default="build/siu-gtfs-staging")
    args=p.parse_args();run(args.out)
