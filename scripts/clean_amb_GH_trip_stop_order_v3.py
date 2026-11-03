#!/usr/bin/env python3
"""Prepare a quieter v3 research stop-order draft by excluding flagged GH visits.

User-directed research-only cleanup of v2:
- Exclude GH-added visits where the same physical stop_id already appeared
  elsewhere in the original route pattern (26 flags).
- Exclude BOTH GH-added stops of any adjacent pair <115 m along KMZ (13 pair
  flags, 26 visits; seven of these overlap the repeated-ID exclusions).

The result is 45 DISTINCT excluded visits, not "39 stops": 39 was the count
of review alerts, not unique stop IDs. Existing source SIU stops and the
original 9,000 trip visits are NEVER removed. This is not a determination
that a line cannot serve these points. The original v2 remains unchanged.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"sources/amb/provisional_trip_stop_order_v2"
OUT=ROOT/"build/amb-provisional-trip-stop-order-v3-clean"

def load(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def save(path,items,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(items)

def identity(row):
    return row["trip_pattern_id"], int(row["stop_sequence"])

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source_path=SRC/"candidate_trip_stop_sequences_v2_NO_TIMES_NOT_GTFS.csv"
    visits=load(source_path)
    original_added=load(SRC/"new_GH_addition_candidates_65_with_concept_position.csv")
    close=load(SRC/"close_adjacent_stop_visits_REVIEW_ONLY.csv")
    if len(visits)!=9065 or len(original_added)!=65 or len(close)!=13:
        raise ValueError("Source v2 has changed; audit before automatic research cleanup")

    by_key={identity(v):v for v in visits}
    if len(by_key)!=len(visits):
        raise ValueError("Duplicated trip_pattern_id + stop_sequence in v2")
    added_by_key={}
    for add in original_added:
        key=(add["trip_pattern_id"],int(add["new_concept_stop_sequence"]))
        if key in added_by_key:raise ValueError("Duplicate GH candidate recorded")
        v=by_key.get(key)
        if v is None or v["source_row_kind"]!="NEW_GH_bus_addition_candidate_RESEARCH_ONLY":
            raise ValueError("GH addition reference is not a new GH visit: "+str(key))
        if v["stop_id"]!=add["inserted_same_physical_SIU_stop_id"]:
            raise ValueError("Candidate stop ID does not match v2 row")
        added_by_key[key]=add
    if len(added_by_key)!=65:
        raise ValueError("Not all GH additions linked to v2 visits")

    repeated_keys=set()
    for key,add in added_by_key.items():
        if add["previous_occurrence_of_same_stop_elsewhere_in_trip"]=="yes":
            repeated_keys.add(key)
    if len(repeated_keys)!=26:
        raise ValueError("Expected exactly 26 repeated physical stop candidate visits")

    close_keys=set()
    for near in close:
        left=(near["trip_pattern_id"],int(near["earlier_sequence"]))
        right=(near["trip_pattern_id"],int(near["later_sequence"]))
        if left==right or left not in added_by_key or right not in added_by_key:
            raise ValueError("Close-distance flag does not reference two GH-added visits")
        if (by_key[left]["stop_id"]!=near["earlier_stop_id"]
            or by_key[right]["stop_id"]!=near["later_stop_id"]):
            raise ValueError("Close-distance visit source differs from v2")
        if float(near["route_distance_between_m"])>=115:
            raise ValueError("Distance not short enough to flag")
        close_keys.update((left,right))
    # 13 problem PAIRS reference 26 candidate visits; seven of those
    # candidates are also in the 26 repeated-ID visit set.
    overlap=repeated_keys & close_keys
    blocked=repeated_keys | close_keys
    if len(close_keys)!=26 or len(overlap)!=7 or len(blocked)!=45:
        raise ValueError(
            f"Review count drift: close={len(close_keys)}, shared={len(overlap)}, remove={len(blocked)}"
        )

    grouped=defaultdict(list)
    original_stop_sequences=defaultdict(list)
    draft_kept=defaultdict(list)
    removed=[]
    kept_additions=[]
    for v in visits:
        key=identity(v)
        trip=v["trip_pattern_id"]
        if v["arrival_time"] or v["departure_time"]:
            raise ValueError("v2 contained times unexpectedly")
        if v["source_row_kind"]=="existing_GIS_KMZ_SIU_physical_stop":
            original_stop_sequences[trip].append((int(v["original_stop_sequence"]),v["stop_id"]))
        elif key not in added_by_key:
            raise ValueError("Unexpected nonoriginal row without GH addition identity")
        if key in blocked:
            add=added_by_key[key]
            reasons=[]
            if key in repeated_keys:reasons.append("same_physical_SIU_stop_id_elsewhere_in_trip")
            if key in close_keys:reasons.append("in_GH_added_pair_less_than_115m_apart")
            removed.append({
                "trip_pattern_id":trip,
                "company":v["company"],
                "route_label":v["official_route_label"],
                "v2_stop_sequence":v["stop_sequence"],
                "removed_from_concept_v3_stop_id":v["stop_id"],
                "stop_name":v["stop_name"],
                "distance_along_KMZ_m":v["shape_dist_traveled_candidate_m"],
                "GH_bus_extra_distance_m":add["GH_route_delta_m"],
                "GH_bus_detour_ratio":add["GH_route_delta_ratio"],
                "research_removal_reasons":";".join(reasons),
                "original_9000_SIU_visits_removed":"no",
                "physical_SIU_stop_catalog_entry_deleted":"no",
                "actual_boarding_service_disproven":"no",
            })
        else:
            draft_kept[trip].append(dict(v))
            if key in added_by_key:
                add=added_by_key[key]
                kept_additions.append({
                    "trip_pattern_id":trip,
                    "company":v["company"],
                    "route_label":v["official_route_label"],
                    "v2_stop_sequence":v["stop_sequence"],
                    "candidate_SIU_stop_id":v["stop_id"],
                    "candidate_stop_name":v["stop_name"],
                    "distance_along_KMZ_m":v["shape_dist_traveled_candidate_m"],
                    "GH_bus_extra_distance_m":add["GH_route_delta_m"],
                    "GH_bus_detour_ratio":add["GH_route_delta_ratio"],
                    "v3_stop_sequence":"",
                    "still_requires_route_boarding_verification":"yes",
                })

    if len(removed)!=45 or len(kept_additions)!=20:
        raise ValueError("Did not exclude precisely 45 GH-added visits and retain 20")
    result=[]
    summary_rows=[]
    kept_position={}
    for trip,items in sorted(draft_kept.items()):
        v2_sequences=[int(v["stop_sequence"]) for v in items]
        if v2_sequences!=sorted(v2_sequences):
            raise ValueError("Source relative visit order changed")
        positions=[float(v["shape_dist_traveled_candidate_m"]) for v in items]
        if any(b+2<a for a,b in zip(positions,positions[1:])):
            raise ValueError("Geometry order reversed by cleanup")
        originals=[(int(v["original_stop_sequence"]),v["stop_id"]) for v in items
                   if v["source_row_kind"]=="existing_GIS_KMZ_SIU_physical_stop"]
        if originals != original_stop_sequences[trip]:
            raise ValueError("An original SIU stop visit was removed from "+trip)
        for seq,v in enumerate(items,1):
            if v["source_row_kind"]=="NEW_GH_bus_addition_candidate_RESEARCH_ONLY":
                kept_position[trip,int(v["stop_sequence"])]=seq
            v["v2_stop_sequence"]=v["stop_sequence"]
            v["stop_sequence"]=str(seq)
            v["v3_research_status"]="unverified_research_concept"
            v["removed_problem_candidates_applied"]="yes"
            result.append(v)
        summary_rows.append({
            "trip_pattern_id":trip,
            "original_SIU_GIS_stop_visits":len(originals),
            "GH_additions_in_v2":sum(x[0]==trip for x in added_by_key),
            "removed_noisy_GH_candidate_visits":sum(x["trip_pattern_id"]==trip for x in removed),
            "GH_additions_retained_in_v3":sum(x["trip_pattern_id"]==trip for x in kept_additions),
            "all_visits_in_v3":len(items),
            "GTFS_publication_approved":"no",
        })
    for item in kept_additions:
        item["v3_stop_sequence"]=kept_position[item["trip_pattern_id"],int(item["v2_stop_sequence"])]
    if len(result)!=9020:
        raise ValueError("Wrong v3 total: "+str(len(result)))
    if sum(r["source_row_kind"]=="existing_GIS_KMZ_SIU_physical_stop" for r in result)!=9000:
        raise ValueError("Original physical stop visit count must be 9000")
    if len({identity(r) for r in result})!=len(result):
        raise ValueError("stop_sequence collision in concept v3")
    if any(r["arrival_time"] or r["departure_time"] for r in result):
        raise ValueError("No times can be generated")
    # Original remaining sequence rank within each trip is strictly preserved.
    for trip,items in draft_kept.items():
        if [int(x["stop_sequence"]) for x in items]!=list(range(1,len(items)+1)):
            raise ValueError("Noncontiguous v3 stop_sequence in "+trip)

    extended_fields=list(visits[0])+["v2_stop_sequence","v3_research_status",
                                     "removed_problem_candidates_applied"]
    save(OUT/"candidate_trip_stop_sequences_v3_CLEAN_NO_TIMES_NOT_GTFS.csv",result,extended_fields)
    save(OUT/"excluded_GH_candidates_45_WITH_REASONS.csv",removed,list(removed[0]))
    save(OUT/"remaining_GH_candidates_20_with_v3_sequence.csv",kept_additions,list(kept_additions[0]))
    save(OUT/"route_pattern_cleaning_QA.csv",summary_rows,list(summary_rows[0]))
    counts=Counter(x["company"]+" / "+x["route_label"] for x in removed)
    stats={
        "baseline_existing_original_stop_visits_preserved":9000,
        "v2_added_GH_visits":65,
        "review_alerts_total":39,
        "review_alerts_repeated_stop_id":26,
        "review_alerts_short_adjacent_candidate_pairs":13,
        "GH_visits_in_close_pairs":26,
        "GH_visits_flagged_both_repeat_and_close":len(overlap),
        "distinct_GH_candidate_visits_excluded_from_v3":len(removed),
        "v3_GH_candidate_visits_remaining":len(kept_additions),
        "v3_all_concept_stop_visits":len(result),
        "v3_route_patterns":len(summary_rows),
        "affected_route_variants":len(counts),
        "number_of_physical_stop_records_deleted":0,
        "original_source_staging_modified":False,
        "production_gtfs_modified":False,
        "trips_or_stop_times_produced":False,
        "real_stop_service_proven_or_disproven":False,
    }
    (OUT/"summary.json").write_text(json.dumps(stats,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report=[
        "# Opgeschoonde trip-haltevolgorde v3 — 39 signalen gecontroleerd",
        "",
        "39 was het **aantal signalen**, niet het aantal unieke halte-ID's.",
        "26 meldingen betroffen een herhaald fysiek SIU-stop-ID elders in een ritpatroon; "
        "13 andere meldingen betroffen twee GH-toevoegingen binnen 115 meter van elkaar.",
        "Bij 7 van die 26 + 26 verwijzingen was er overlap. "
        "We hebben **alle bij deze 39 meldingen betrokken GH-toevoegingen** "
        "uit een nieuwe conceptversie geweerd: 45 unieke haltebezoeken.",
        "",
        "## Tellingen","",
    ]
    for k,v in stats.items():
        if type(v) is int:
            report.append("- "+k+": **"+str(v)+"**")
    report += [
        "",
        "## Bewuste bescherming","",
        "- De 9.000 oorspronkelijke KMZ-/SIU-haltebezoeken en hun onderlinge volgorde zijn integraal behouden.",
        "- De centrale fysieke SIU-haltecatalogus blijft ongewijzigd; hergebruik van stop_ID's op meerdere routes is nog steeds normaal.",
        "- Bij een echte rondrit kan dezelfde halte opnieuw worden bediend: uitsluiting hier is een **ruisreductie op verzoek** en geen bewijs dat zo'n tweede haltepassage onmogelijk is.",
        "- Ook de twee GH-kandidaten van een te kort paar zijn weggelaten om geen willekeurige winnaar te kiezen.",
        "- De oorspronkelijke v2 en de GH-classificatie blijven voor herstel beschikbaar.",
        "- Geen tijden, GraphHopper-aanvragen of publiceerbare GTFS-wijzigingen.",
        "",
        "## Bestanden","",
        "- candidate_trip_stop_sequences_v3_CLEAN_NO_TIMES_NOT_GTFS.csv — nieuwe complete conceptvolgorde van 9.020 passages.",
        "- excluded_GH_candidates_45_WITH_REASONS.csv — exact welke 45 GH-haltebezoeken niet in v3 zijn overgenomen.",
        "- remaining_GH_candidates_20_with_v3_sequence.csv — alle 20 resterende GH-toevoegingen.",
        "- route_pattern_cleaning_QA.csv — controles en aantallen per trip-patroon.",
        "",
    ]
    (OUT/"summary.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps(stats,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
