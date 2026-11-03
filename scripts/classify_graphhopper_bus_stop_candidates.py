#!/usr/bin/env python3
"""Reproducible non-publishing classification of 125 GH bus stop candidates.

Uses *KMZ-constrained* GraphHopper bus route detour, not the shortest
point-to-point route (which can skip the official bus line). Classification is
research only; no service, curbside, route variant, or stop_times is approved.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GH = ROOT / "sources/amb/graphhopper_bus_direction_review"
INPUT = ROOT / "sources/amb/gap_direction_staging"
ROUTES = ROOT / "sources/amb/missing_siu_trip_stop_patterns"
OUT = ROOT / "build/amb-GH-bus-stop-classification"

def load(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def save(path, rows, columns=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns or list(rows[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def val(x):
    try:
        return float(x) if str(x).strip() else None
    except (ValueError, TypeError):
        return None

def gap_key(x):
    return x["trip_pattern_id"], str(x["gap_index"])

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw=load(GH/"bus_candidate_access_and_oneway_review.csv")
    source=load(INPUT/"existing_SIU_OSM_direction_candidates_for_GraphHopper.csv")
    gaps=load(INPUT/"gap_review_with_existing_OSM_snapshot.csv")
    gh_gaps=load(GH/"bus_route_gap_direction_checks.csv")
    route_qa=load(ROUTES/"route_variant_mapping_readiness_60.csv")
    existing=load(ROUTES/"candidate_stop_order_per_trip_NO_TIMES.csv")
    sr={(s["trip_pattern_id"],s["gap_index"],s["candidate_source_id"]):s for s in source}
    g={gap_key(x):x for x in gaps}
    gg={gap_key(x):x for x in gh_gaps}
    qa={(x["company"],x["official_route_label"]):x for x in route_qa}
    already=defaultdict(set)
    for s in existing:
        already[s["trip_pattern_id"]].add(s["stop_id"])
    expected={(r["trip_pattern_id"],r["gap_index"],r["candidate_id"]) for r in raw}
    if len(raw)!=125 or len(sr)!=125 or len(g)!=73 or len(gg)!=73 or len(expected)!=125:
        raise ValueError("Expected 125 unique stop candidates and 73 gaps")
    if expected!=set(sr):
        raise ValueError("GH and original SIU/OSM candidates do not match")

    result=[]
    for r in raw:
        identity=(r["trip_pattern_id"],r["gap_index"],r["candidate_id"])
        s=sr[identity]
        gap=g[gap_key(r)]
        gh=gg[gap_key(r)]
        q=qa[(r["company"],r["route_label"])]
        if r["GraphHopper_profile"]!="bus":
            raise ValueError("Expected bus routing for all classifications")
        if r["candidate_kind"]!=s["candidate_kind"]:
            raise ValueError("Source mismatch for "+str(identity))
        delta=val(r["additional_distance_KMZ_constrained_via_m"])
        ratio=val(r["ratio_KMZ_constrained_via"])
        fraction=val(r["GH_constrained_via_fraction_within_KMZ_50m"])
        snap=val(r["GH_snapped_candidate_offset_m"])
        distance=val(r["distance_to_KMZ_m"])
        position=val(s["global_shape_position_m"])
        start=val(gap["baseline_start_global_chainage_m"])
        end=val(gap["baseline_end_global_chainage_m"])
        routed=(r["bus_KMZ_constrained_via_candidate_status"]=="ok"
                and r["bus_via_candidate_status"]=="ok"
                and gh["GH_constrained_bus_status"]=="ok"
                and all(x is not None for x in (delta,ratio,fraction,snap,distance)))
        between=(position is not None and start is not None and end is not None
                 and start-15<=position<=end+15)
        stopid=s["physical_SIU_stop_id_if_known"]
        if stopid and not stopid.startswith("SIU_"):
            raise ValueError("Unexpected physical stop id")

        flags=[]
        reasons=[]
        if s["original_KMZ_direction_assessment"]=="direction_conflict":
            flags.append("previous_name_direction_conflict_keep_for_review")
        if gh["possible_oneway_or_routing_asymmetry"]=="yes":
            flags.append("graphhopper_AB_BA_bus_route_asymmetry")
        if fraction is not None and fraction<.70:
            flags.append("GH_bus_via_geometry_distant_from_KMZ_corridor")
        if snap is not None and snap>15:
            flags.append("GH_snapped_stop_more_than_15m_away")
        if not between:
            flags.append("candidate_not_between_gap_anchor_stops")
        if not stopid:
            flags.append("OSM_only_no_confirmed_physical_SIU_stop_id")
        if "ARCGIS" in q["geometry_sources"]:
            flags.append("historical_arcgis_fallback")
        if "official_AB_label_length_discrepancy" in q["qa_flags"]:
            flags.append("official_AB_label_conflict")
        if "source_geometry_mismatch_or_collision" in q["qa_flags"]:
            flags.append("source_KMZ_or_ArcGIS_collision")
        source_uncertain=any(x in flags for x in (
            "historical_arcgis_fallback","official_AB_label_conflict",
            "source_KMZ_or_ArcGIS_collision"))
        good=(routed and between and snap<=15 and distance<=35 and
              fraction>=.70 and -50<=delta<=300 and ratio<=1.12)
        direction_problem=(routed and between and (
            (delta>=500 and ratio>=1.18) or
            (delta>=1200 and ratio>=1.13) or
            (fraction<.55 and delta>=300)
        ))
        if not routed or not between:
            status="onzeker"
            reasons.append("incomplete_GH_route_or_candidate_order")
        elif direction_problem:
            status="mogelijk_richtingsconflict"
            reasons.append("GH_bus_route_needs_large_KMZ_constrained_detour")
        elif good and stopid and not source_uncertain:
            status="toevoegkandidaat"
            reasons.append("GH_bus_low_detour_KMZ_aligned_existing_SIU_stop")
            if "previous_name_direction_conflict_keep_for_review" in flags:
                reasons.append("GH_route_reopens_previously_rejected_name_direction")
        else:
            status="onzeker"
            if not stopid:reasons.append("OSM_only_no_existing_canonical_stop")
            if source_uncertain:reasons.append("official_route_variant_or_geometry_needs_verification")
            if routed and delta is not None and not source_uncertain:
                reasons.append("borderline_detour_or_corridor_alignment")
        if status=="toevoegkandidaat":
            nextstep="review_insert_existing_SIU_stop_between_anchors"
        elif status=="mogelijk_richtingsconflict":
            nextstep="review_oneway_bus_route_and_official_KMZ_before_exclusion"
        else:
            nextstep="review_evidence_and_keep_candidate_unmodified"
        if not stopid:
            nextstep="resolve_existing_physical_stop_or_OSM_platform_identity_first"
        result.append({
            "company":r["company"],"route_label":r["route_label"],
            "trip_pattern_id":r["trip_pattern_id"],"gap_index":r["gap_index"],
            "candidate_source_id":r["candidate_id"],
            "candidate_kind":s["candidate_kind"],
            "physical_SIU_stop_id_if_known":stopid,
            "stop_name":s["stop_name"],"stop_lon":s["longitude"],"stop_lat":s["latitude"],
            "candidate_class":status,"recommended_review_action":nextstep,
            "classification_reasons":";".join(reasons),
            "warnings":";".join(flags),
            "KMZ_name_direction_original":r["original_KMZ_direction_assessment"],
            "already_existing_in_trip_elsewhere":"yes" if stopid and stopid in already[r["trip_pattern_id"]] else "no_or_unknown",
            "insert_after_existing_stop_id":gap["baseline_from_existing_stop_id"],
            "insert_before_existing_stop_id":gap["baseline_to_existing_stop_id"],
            "candidate_chainage_m":s["global_shape_position_m"],
            "gap_chainage_start_m":gap["baseline_start_global_chainage_m"],
            "gap_chainage_end_m":gap["baseline_end_global_chainage_m"],
            "candidate_position_is_between_anchors":"yes" if between else "no",
            "GH_bus_KMZ_constrained_extra_distance_m":r["additional_distance_KMZ_constrained_via_m"],
            "GH_bus_KMZ_constrained_detour_ratio":r["ratio_KMZ_constrained_via"],
            "GH_bus_route_share_near_KMZ_50m":r["GH_constrained_via_fraction_within_KMZ_50m"],
            "GH_bus_candidate_snap_m":r["GH_snapped_candidate_offset_m"],
            "candidate_distance_to_KMZ_m":r["distance_to_KMZ_m"],
            "GH_possible_AB_BA_asymmetry":gh["possible_oneway_or_routing_asymmetry"],
            "route_stop_service_confirmed":"no",
            "right_side_boarding_verified":"no",
            "automatic_stop_sequence_edit":"no",
            "GTFS_publication_approved":"no"
        })
    result.sort(key=lambda r:(r["company"],r["route_label"],r["trip_pattern_id"],
                             int(r["gap_index"]),float(r["candidate_chainage_m"]),
                             r["candidate_source_id"]))
    by_gap=defaultdict(list)
    by_route=defaultdict(list)
    for r in result:
        by_gap[(r["trip_pattern_id"],r["gap_index"])].append(r)
        by_route[(r["company"],r["route_label"])].append(r)
    order=[]
    for (trip,gap),group in sorted(by_gap.items()):
        for i,r in enumerate(group,1):
            order.append({
                "trip_pattern_id":trip,"gap_index":gap,
                "geometric_rank_within_gap":i,
                "from_stop_id":r["insert_after_existing_stop_id"],
                "candidate_stop_id_if_existing":r["physical_SIU_stop_id_if_known"],
                "candidate_source_id":r["candidate_source_id"],
                "to_stop_id":r["insert_before_existing_stop_id"],
                "candidate_class":r["candidate_class"],
                "projected_shape_distance_m":r["candidate_chainage_m"],
                "automatic_trip_order_change":"no"
            })
    route_summaries=[]
    for (co,label),group in sorted(by_route.items()):
        counts=Counter(r["candidate_class"] for r in group)
        route_summaries.append({
            "company":co,"route_label":label,"candidate_links":len(group),
            "toevoegkandidaat":counts["toevoegkandidaat"],
            "mogelijk_richtingsconflict":counts["mogelijk_richtingsconflict"],
            "onzeker":counts["onzeker"],
            "previous_name_direction_conflicts_reopened":sum(
                r["candidate_class"]=="toevoegkandidaat"
                and r["KMZ_name_direction_original"]=="direction_conflict" for r in group),
            "route_stop_service_confirmed":"no",
            "stop_sequences_modified":"no"
        })
    counts=Counter(r["candidate_class"] for r in result)
    previous=Counter(r["candidate_class"] for r in result
                     if r["KMZ_name_direction_original"]=="direction_conflict")
    kind=defaultdict(Counter)
    for r in result:kind[r["candidate_kind"]][r["candidate_class"]]+=1
    summary={
        "GH_candidate_links_classified":len(result),
        "GH_gap_count_in_source":len(gaps),
        "classification_counts":dict(counts),
        "previous_name_direction_conflicts":sum(previous.values()),
        "old_name_direction_conflicts_now_addition_candidate":previous["toevoegkandidaat"],
        "old_name_direction_conflicts_now_possible_conflict":previous["mogelijk_richtingsconflict"],
        "old_name_direction_conflicts_still_uncertain":previous["onzeker"],
        "candidate_kind_counts":{k:dict(v) for k,v in kind.items()},
        "route_variants_with_classified_candidates":len(route_summaries),
        "add_max_extra_distance_m":300,"add_max_detour_ratio":1.12,
        "add_min_GH_KMZ_corridor_fraction":0.70,"add_max_GH_snap_m":15,
        "possible_conflict_min_detour_m":500,"possible_conflict_min_ratio":1.18,
        "OSM_only_without_SIU_id_is_add_candidate":False,
        "old_ArcGIS_or_AB_conflicts_are_add_candidate":False,
        "oneway_or_platform_boarding_verified":False,
        "graphhopper_new_requests":0,"osm_new_requests":0,
        "physical_GTFS_stops_created":0,"stop_sequences_modified":False,
        "real_stop_boarding_confirmed":False
    }
    save(OUT/"GH_bus_stop_candidate_decisions_125.csv",result)
    save(OUT/"proposed_insertion_order_NO_TIMES_REVIEW_ONLY.csv",order)
    save(OUT/"GH_bus_stop_classification_by_route.csv",route_summaries)
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report=["# GraphHopper bus: 125 kandidaat-haltes beoordeeld zonder GTFS te wijzigen","",
            "De uitkomsten zijn hypotheses gebaseerd op bestaande GraphHopper bus-analyses en de officiële KMZ-routecorridor.",
            "Een lage omweg bevestigt geen formele haltebediening of instapzijde. Een grote omweg bewijst niet op zichzelf een eenrichtingsweg.",
            "",
            "## Aantallen", ""]
    for k,v in counts.items():report.append("- "+k+": **"+str(v)+"**")
    report += ["",
               "Van de oorspronkelijk als KMZ-naamrichtingsconflict gemarkeerde "+
                 str(sum(previous.values()))+" SIU-kandidaten zijn "+
                 str(previous["toevoegkandidaat"])+" opnieuw toevoegkandidaat dankzij de busrouteanalyse.",
               "",
               "## Regels", "",
               "- Toevoegkandidaat: bestaande SIU fysieke stop-ID; GraphHopper bus A→halte→B langs KMZ-waypoints met maximaal 300m extra, maximaal 1,12x, minimaal 70% binnen 50m van KMZ, weg-snap maximaal 15m en halte maximaal 35m van KMZ. Geen onzekere officiële bron.",
               "- Mogelijk richtingsconflict: via de kandidaat wordt de busroute substantieel langer (minimaal 500m en factor 1,18; of minimaal 1200m en factor 1,13) of er is grote corridor-afwijking. Andere wegbeperkingen blijven mogelijk.",
               "- Onzeker: grensgeval, oudere ArcGIS-geometrie, twijfelachtig officieel A/B-label, OSM-only zonder fysieke SIU-ID of onvoldoende netwerk-/corridorbewijs.",
               "- Bij een vermoedelijk tegengestelde SIU-naamrichting kunnen goede busroute-resultaten die voorlopige afwijzing heropenen.",
               "- Geen curbside-test uitgevoerd; busroute langs haltepunt is geen bewezen instap aan de juiste kant van de weg.",
               "",
               "## Stagingbestanden","",
               "- GH_bus_stop_candidate_decisions_125.csv: volledige classificatie, afstand, omweg en benodigde verificatie.",
               "- proposed_insertion_order_NO_TIMES_REVIEW_ONLY.csv: voorlopige geografische haltepositie tussen bestaande stop-ID's, nooit automatisch GTFS stop_sequence.",
               "- GH_bus_stop_classification_by_route.csv: prioriteiten per route.",
               "",
               "Geen nieuwe GraphHopper-aanvragen, geen Overpass-aanvragen, geen wijziging in trips.txt, stop_times.txt of stops.txt.",
               ""]
    (OUT/"summary.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
if __name__=="__main__":
    main()
