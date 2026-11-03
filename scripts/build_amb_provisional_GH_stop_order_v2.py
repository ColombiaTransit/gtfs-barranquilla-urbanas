#!/usr/bin/env python3
"""Build a NEW non-publishable trip stop-order draft with GH addition candidates.

Read-only sources:
- existing AMB KMZ/ArcGIS stop-order staging (9,000 observations)
- existing GH bus stop classification (65 suggested insertions of 125 assessed)
- SIU canonical physical stop catalog and existing route pattern manifest

Never edits previous source staging or gtfs/*. All 65 addition candidates remain
research-only; travel times and real route-specific boarding aren't inferred.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources/amb/missing_siu_trip_stop_patterns"
GH = ROOT / "sources/amb/graphhopper_stop_classification"
SIU = ROOT / "sources/siu/gtfs_staging/candidate_stops.csv"
OUT = ROOT / "build/amb-provisional-trip-stop-order-v2"

BASE_HEADERS = [
    "trip_pattern_id","route_id_proposed_base","company","official_route_label",
    "variant","stop_sequence","stop_id","stop_name",
    "shape_dist_traveled_candidate_m","distance_from_route_m",
    "source_vs_shape_direction","candidate_quality","arrival_time",
    "departure_time","actual_route_stops_verified","source_stop_id_reused",
    "geographic_pattern_only"
]
MORE_HEADERS = [
    "source_row_kind","original_stop_sequence","GH_candidate_source_id",
    "GH_source_gap_index","GH_classification","GH_KMZ_constrained_extra_distance_m",
    "GH_KMZ_constrained_detour_ratio","same_stop_id_elsewhere_in_trip",
    "near_existing_same_stop_passage_warning",
    "nearby_candidate_visit_warning","candidate_service_verified",
    "concept_only_not_validated_GTFS"
]

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as handle:
        return list(csv.DictReader(handle))

def save(path,items,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:
        w=csv.DictWriter(handle,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(items)

def metric(x):
    return float(x)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    base=read(SOURCE/"candidate_stop_order_per_trip_NO_TIMES.csv")
    gh=read(GH/"GH_bus_stop_candidate_decisions_125.csv")
    physical=read(SIU)
    routes=read(SOURCE/"trip_patterns_MISSING_SIU_NO_TIMES.csv")
    if len(base)!=9000 or len(gh)!=125:
        raise ValueError(f"Source changed: baseline={len(base)}, GH={len(gh)}; review before staging")
    physical_ids={r["stop_id"] for r in physical}
    if len(physical_ids)!=len(physical):raise ValueError("Nonunique canonical SIU stop IDs")
    bypattern=defaultdict(list)
    bybasepattern=defaultdict(list)
    for row in base:
        if row["stop_id"] not in physical_ids:raise ValueError("Unknown SIU stop in base: "+row["stop_id"])
        if row["arrival_time"] or row["departure_time"]:
            raise ValueError("Unexpected real passage times in original research rows")
        bybasepattern[row["trip_pattern_id"]].append(row)
    for route in routes:
        if route["trip_pattern_id"] in bypattern:
            raise ValueError("Duplicate route pattern manifest")
        bypattern[route["trip_pattern_id"]]=route
    for uid,items in bybasepattern.items():
        if uid not in bypattern:
            raise ValueError("Missing trip pattern manifest: "+uid)
        items.sort(key=lambda r:int(r["stop_sequence"]))
        seq=[int(r["stop_sequence"]) for r in items]
        if seq!=list(range(1,len(items)+1)):
            raise ValueError("Original stop order not contiguous: "+uid)
        if any(metric(a["shape_dist_traveled_candidate_m"])>
               metric(b["shape_dist_traveled_candidate_m"])+0.2 for a,b in zip(items,items[1:])):
            raise ValueError("Original chainage not monotonic: "+uid)

    additions=[r for r in gh if r["candidate_class"]=="toevoegkandidaat"]
    if len(additions)!=65:
        raise ValueError(f"Expected 65 GraphHopper addition candidates, got {len(additions)}")
    if any(r["candidate_kind"]!="existing_physical_SIU_stop" for r in additions):
        raise ValueError("An OSM-only candidate may not create an undocumented stop_id")
    adds=defaultdict(list)
    ids=set()
    for r in additions:
        pattern=r["trip_pattern_id"]
        if pattern not in bybasepattern:
            raise ValueError("Addition has no original stop pattern "+pattern)
        sid=r["physical_SIU_stop_id_if_known"]
        if sid not in physical_ids:
            raise ValueError("New physical stop_id forbidden: "+sid)
        if r["candidate_position_is_between_anchors"]!="yes":
            raise ValueError("Addition candidate not between reported anchor stops")
        trip=bypattern[pattern]
        if r["company"]!=trip["company"] or r["route_label"]!=trip["official_route_label"]:
            raise ValueError("Addition route does not match source route manifest")
        key=(pattern,r["gap_index"],r["candidate_source_id"])
        if key in ids:raise ValueError("Duplicate insertion identity")
        ids.add(key)
        gap=int(r["gap_index"])
        orig=bybasepattern[pattern]
        if not (1<=gap<len(orig)):
            raise ValueError("Gap index outside source trip "+pattern)
        before,after=orig[gap-1],orig[gap]
        if before["stop_id"]!=r["insert_after_existing_stop_id"] or after["stop_id"]!=r["insert_before_existing_stop_id"]:
            raise ValueError("Anchor stop_id mismatch: "+str(key))
        position=metric(r["candidate_chainage_m"])
        left,right=metric(before["shape_dist_traveled_candidate_m"]),metric(after["shape_dist_traveled_candidate_m"])
        if position<left-2 or position>right+2:
            raise ValueError("Addition candidate outside original source chainage")
        if r["route_stop_service_confirmed"]!="no" or r["automatic_stop_sequence_edit"]!="no":
            raise ValueError("Input GraphHopper review confirmation fields changed unexpectedly")
        adds[(pattern,gap)].append(r)

    final=[]
    changes=[]
    QA=[]
    warnings=[]
    affected=Counter()
    accepted_source_keys=set()
    for tripid,orig in sorted(bybasepattern.items()):
        identity=bypattern[tripid]
        original_visits_by_id=defaultdict(list)
        for o in orig:
            original_visits_by_id[o["stop_id"]].append(metric(o["shape_dist_traveled_candidate_m"]))
        records=[]
        for n,o in enumerate(orig,1):
            item=dict(o)
            item.update({
                "source_row_kind":"existing_GIS_KMZ_SIU_physical_stop",
                "original_stop_sequence":o["stop_sequence"],
                "GH_candidate_source_id":"",
                "GH_classification":"",
                "GH_KMZ_constrained_extra_distance_m":"",
                "GH_KMZ_constrained_detour_ratio":"",
                "same_stop_id_elsewhere_in_trip":"",
                "near_existing_same_stop_passage_warning":"",
                "nearby_candidate_visit_warning":"",
                "candidate_service_verified":"no",
                "concept_only_not_validated_GTFS":"yes",
            })
            records.append(item)
            proposed=sorted(adds.get((tripid,n),[]),
                            key=lambda x:(metric(x["candidate_chainage_m"]),x["physical_SIU_stop_id_if_known"]))
            seen_added_ids=set()
            for candidate in proposed:
                sid=candidate["physical_SIU_stop_id_if_known"]
                chainage=metric(candidate["candidate_chainage_m"])
                if sid in seen_added_ids:
                    raise ValueError("Same physical stop repeated within one gap: "+tripid)
                seen_added_ids.add(sid)
                previous=original_visits_by_id.get(sid,[])
                same_near=any(abs(z-chainage)<30 for z in previous)
                if same_near:
                    # Safety: do not insert a second stop visit for the exact same
                    # nearby passage. Existing 65 are retained in review audit.
                    raise ValueError("Candidate duplicates the same physical stop at the same route passage: "+sid)
                if candidate["candidate_source_id"]!=sid:
                    raise ValueError("SIU candidate source and stop identity disagree")
                cid=(tripid,candidate["gap_index"],candidate["candidate_source_id"])
                accepted_source_keys.add(cid)
                added={
                    "trip_pattern_id":tripid,
                    "route_id_proposed_base":identity["route_id_proposed_base"],
                    "company":identity["company"],
                    "official_route_label":identity["official_route_label"],
                    "variant":identity["variant"],
                    "stop_sequence":"",
                    "stop_id":sid,
                    "stop_name":candidate["stop_name"],
                    "shape_dist_traveled_candidate_m":candidate["candidate_chainage_m"],
                    "distance_from_route_m":candidate["candidate_distance_to_KMZ_m"],
                    "source_vs_shape_direction":candidate["KMZ_name_direction_original"],
                    "candidate_quality":"GH_bus_low_detour_review_candidate",
                    "arrival_time":"","departure_time":"",
                    "actual_route_stops_verified":"no",
                    "source_stop_id_reused":"yes",
                    "geographic_pattern_only":"yes",
                    "source_row_kind":"NEW_GH_bus_addition_candidate_RESEARCH_ONLY",
                    "original_stop_sequence":"",
                    "GH_candidate_source_id":sid,
                    "GH_source_gap_index":str(n),
                    "GH_classification":"toevoegkandidaat",
                    "GH_KMZ_constrained_extra_distance_m":candidate["GH_bus_KMZ_constrained_extra_distance_m"],
                    "GH_KMZ_constrained_detour_ratio":candidate["GH_bus_KMZ_constrained_detour_ratio"],
                    "same_stop_id_elsewhere_in_trip":"yes" if previous else "no",
                    "near_existing_same_stop_passage_warning":"no",
                    "nearby_candidate_visit_warning":"",
                    "candidate_service_verified":"no",
                    "concept_only_not_validated_GTFS":"yes",
                }
                records.append(added)
                affected[tripid]+=1
                changes.append({
                    "trip_pattern_id":tripid,
                    "company":identity["company"],"official_route_label":identity["official_route_label"],
                    "source_gap_index":n,
                    "existing_stop_before":o["stop_id"],
                    "existing_stop_after":orig[n]["stop_id"],
                    "inserted_same_physical_SIU_stop_id":sid,
                    "inserted_stop_name":candidate["stop_name"],
                    "previous_occurrence_of_same_stop_elsewhere_in_trip":"yes" if previous else "no",
                    "source_KMZ_direction_name":candidate["KMZ_name_direction_original"],
                    "GH_route_delta_m":candidate["GH_bus_KMZ_constrained_extra_distance_m"],
                    "GH_route_delta_ratio":candidate["GH_bus_KMZ_constrained_detour_ratio"],
                    "original_shape_position_m":candidate["candidate_chainage_m"],
                    "new_concept_stop_sequence":"",
                    "public_GTFS_modified":"no",
                    "actual_operator_stop_service_verified":"no"
                })
        if len(records)!=len(orig)+affected[tripid]:
            raise ValueError("Lost or duplicated original visits in "+tripid)
        for i,item in enumerate(records,1):
            item["stop_sequence"]=i
        if any(metric(a["shape_dist_traveled_candidate_m"])>
               metric(b["shape_dist_traveled_candidate_m"])+2
               for a,b in zip(records,records[1:])):
            raise ValueError("Model stop order not monotone in "+tripid)
        # Detect close candidate-to-candidate and candidate-to-old visits without
        # discarding legitimate same-direction route visits. These need review.
        close_pairs=0
        for x,y in zip(records,records[1:]):
            close=metric(y["shape_dist_traveled_candidate_m"])-metric(x["shape_dist_traveled_candidate_m"])
            if close<115 and (x["source_row_kind"].startswith("NEW_") or
                              y["source_row_kind"].startswith("NEW_")):
                close_pairs+=1
                if x["source_row_kind"].startswith("NEW_"):
                    x["nearby_candidate_visit_warning"]="adjacent_gap_under_115m"
                if y["source_row_kind"].startswith("NEW_"):
                    y["nearby_candidate_visit_warning"]="adjacent_gap_under_115m"
                warnings.append({
                    "trip_pattern_id":tripid,
                    "earlier_sequence":x["stop_sequence"],
                    "later_sequence":y["stop_sequence"],
                    "earlier_stop_id":x["stop_id"],
                    "later_stop_id":y["stop_id"],
                    "route_distance_between_m":round(close,1),
                    "possible_duplicate_platform":"review",
                    "auto_removed":"no",
                })
        original_replayed=[x["stop_id"] for x in records if x["source_row_kind"]=="existing_GIS_KMZ_SIU_physical_stop"]
        if original_replayed != [x["stop_id"] for x in orig]:
            raise ValueError("Original stop visit order was modified: "+tripid)
        new_positions={(x["GH_source_gap_index"],x["GH_candidate_source_id"]):x["stop_sequence"] for x in records
                       if x["source_row_kind"].startswith("NEW_")}
        for change in changes:
            if change["trip_pattern_id"]==tripid:
                change["new_concept_stop_sequence"]=new_positions[(str(change["source_gap_index"]),change["inserted_same_physical_SIU_stop_id"])]
        final.extend(records)
        QA.append({
            "trip_pattern_id":tripid,
            "company":identity["company"],
            "official_route_label":identity["official_route_label"],
            "base_route_id_proposed":identity["route_id_proposed_base"],
            "source_geometry":identity["source_geometry"],
            "original_stop_visits":len(orig),
            "new_GH_addition_candidate_visits":affected[tripid],
            "new_concept_stop_visits":len(records),
            "adjacent_pairs_under_115m_involving_new_candidate":close_pairs,
            "source_original_stop_order_preserved":"yes",
            "source_canonical_stop_ids_reused":"yes",
            "arrival_and_departure_times_present":"no",
            "official_bus_stop_service_verified":"no",
            "operational_trip_direction_and_AB_verified":"no",
            "GTFS_publication_approved":"no"
        })
    if accepted_source_keys!=ids or sum(affected.values())!=65:
        raise ValueError("Did not stage exactly all 65 GraphHopper addition candidates")
    if len(final)!=9065:
        raise ValueError(f"Wrong concept output size: {len(final)}, expected 9065")
    if len({(r["trip_pattern_id"],r["stop_sequence"]) for r in final})!=len(final):
        raise ValueError("Duplicate trip_id/stop_sequence in candidate concept")
    if any(x["stop_id"] not in physical_ids for x in final):
        raise ValueError("Generated a non-source stop_id")
    if any(x["arrival_time"] or x["departure_time"] for x in final):
        raise ValueError("Timetables should be calculated later")
    if any("yes"==x["actual_route_stops_verified"] for x in final):
        raise ValueError("Unverified route-stop service falsely marked confirmed")

    save(OUT/"candidate_trip_stop_sequences_v2_NO_TIMES_NOT_GTFS.csv",
         final, BASE_HEADERS+MORE_HEADERS)
    save(OUT/"new_GH_addition_candidates_65_with_concept_position.csv",
         changes,list(changes[0]))
    save(OUT/"trip_pattern_new_stop_counts_QA.csv",QA,list(QA[0]))
    save(OUT/"close_adjacent_stop_visits_REVIEW_ONLY.csv",warnings,
         list(warnings[0]) if warnings else
         ["trip_pattern_id","earlier_sequence","later_sequence","earlier_stop_id",
          "later_stop_id","route_distance_between_m","possible_duplicate_platform","auto_removed"])

    unique_add_ids=len({x["inserted_same_physical_SIU_stop_id"] for x in changes})
    byroute=Counter((x["company"],x["official_route_label"]) for x in changes)
    summary={
        "existing_route_stop_visits_preserved":len(base),
        "new_GH_addition_candidate_visits":len(changes),
        "concept_route_stop_visits_total":len(final),
        "unique_existing_SIU_physical_stop_ids_newly_referenced":unique_add_ids,
        "affected_trip_patterns":len(affected),
        "affected_route_variants":len(byroute),
        "trip_patterns_with_existing_sequence":len(QA),
        "new_candidates_that_already_occur_elsewhere_in_same_trip":sum(
            x["previous_occurrence_of_same_stop_elsewhere_in_trip"]=="yes" for x in changes),
        "adjacent_pairs_with_new_candidate_under_115m_to_review":len(warnings),
        "all_original_stop_visit_orders_preserved":True,
        "all_original_physical_stop_ids_preserved":True,
        "new_physical_stop_ids_created":0,
        "trip_timing_calculation_performed":False,
        "source_KMZ_GH_route_stop_service_verified":False,
        "production_GTFS_stops_trips_or_stop_times_changed":False,
        "classification_source":"sources/amb/graphhopper_stop_classification/GH_bus_stop_candidate_decisions_125.csv",
        "source_observed_counts_expected":True,
    }
    (OUT/"summary.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report=[
        "# Nieuwe conceptversie van haltevolgordes (zonder tijden) — GraphHopper 65 toevoegkandidaten",
        "",
        "**DIT IS ONDERZOEKSSTAGING; er zijn geen GTFS-bestanden aangepast.**",
        "De 9.000 bestaande route-haltebezoeken blijven behouden, in exact dezelfde relatieve volgorde.",
        "Alle 65 bestaande fysieke SIU-haltes zijn als voorlopige haltepassage tussen de "
        "twee oorspronkelijk gekoppelde haltes van hun bron-gat gezet. "
        "Een reeds elders in de route genoemde stop_id mag terugkomen bij een andere passage van een rondrit.",
        "Alle 125 GraphHopper-kandidaten blijven apart in de classificatie; alleen de 65 toevoegkandidaten "
        "komen in deze nieuwe *conceptversie* voor.",
        "",
        "## Resultaten", ""
    ]
    for key,value in summary.items():
        if isinstance(value,int):
            report.append("- "+key+": **"+str(value)+"**")
    report += [
        "",
        "## Stapsgewijze verificatie", "",
        "1. Controleer twijfelachtige korte halteafstanden (onder 115 m), dubbele stop_id-passages en bron-A/B-varianten.",
        "2. Verifieer dat de 65 kandidaat-haltes daadwerkelijk door deze buslijn worden bediend; GraphHopper bewijst alleen berijdbaarheid.",
        "3. Bevestig de werkelijke tripgrenzen en keerpunten op basis van originele AMB- en SIU-routegegevens.",
        "4. Zodra de geordende trips zijn gevalideerd, laat GraphHopper afstand en rijtijd per opeenvolgende halte berekenen.",
        "5. Publiceer alleen na brontoetsing in GTFS trips.txt en stop_times.txt; er zijn nu geen arrival/departure tijden.",
        "",
        "## Bestanden", "",
        "- candidate_trip_stop_sequences_v2_NO_TIMES_NOT_GTFS.csv — complete conceptvolgorde per routepatroon.",
        "- new_GH_addition_candidates_65_with_concept_position.csv — precies de nieuw ingevoegde 65 haltepassages.",
        "- trip_pattern_new_stop_counts_QA.csv — voortgang en checks per patroon.",
        "- close_adjacent_stop_visits_REVIEW_ONLY.csv — potentiële nabijheid/dubbele passages voor menselijke beoordeling.",
        "",
    ]
    (OUT/"summary.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
