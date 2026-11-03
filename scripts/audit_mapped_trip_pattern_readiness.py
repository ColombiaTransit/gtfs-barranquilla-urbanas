#!/usr/bin/env python3
"""Quality gate and route-level register for KMZ/ArcGIS-matched physical SIU stop patterns.

Reads only staged research results. A KMZ LineString component is not necessarily
a GTFS trip. Flag fragmented geometries and large stop gaps; emit GraphHopper
waypoint inputs with no travel times, keyed by existing SIU physical stop_id.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"build/amb-missing-route-stop-trip-patterns"
SIU=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
ROUTES=ROOT/"gtfs/routes.txt"

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as fh:
        return list(csv.DictReader(fh))

def write(path,rows,cols):
    with path.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=cols,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def main():
    patterns=read(BASE/"trip_patterns_MISSING_SIU_NO_TIMES.csv")
    visits=read(BASE/"candidate_stop_order_per_trip_NO_TIMES.csv")
    candidates=read(SIU)
    original_routes=read(ROUTES)
    physical={r["stop_id"]:r for r in candidates}
    if len(physical)!=len(candidates):
        raise ValueError("Duplicate physical stop ID in SIU catalog")
    gtfs_ids={x["route_id"] for x in original_routes}
    by_route=defaultdict(list)
    by_pattern=defaultdict(list)
    for pat in patterns:
        by_route[(pat["company"],pat["official_route_label"])].append(pat)
    for visit in visits:
        by_pattern[visit["trip_pattern_id"]].append(visit)

    routes=[]
    waypoints=[]
    counted=set()
    for (company,label),components in sorted(by_route.items()):
        flags=set()
        ncomp=len(components)
        base=components[0]["route_id_proposed_base"]
        record_source={r["source_geometry"] for r in components}
        total_stops=sum(len(by_pattern.get(r["trip_pattern_id"],[])) for r in components)
        viable=sum(len(by_pattern.get(r["trip_pattern_id"],[]))>=5 for r in components)
        max_gap=0
        for comp in components:
            qa_stops=by_pattern.get(comp["trip_pattern_id"],[])
            if qa_stops:
                positions=[float(r["shape_dist_traveled_candidate_m"]) for r in qa_stops]
                max_gap=max(max_gap,max((b-a for a,b in zip(positions,positions[1:])),default=0))
        if ncomp>1:
            flags.add("disconnected_shape_fragments_not_separate_legal_trips")
        if ncomp>=10:
            flags.add("extremely_fragmented_shape_requires_reconstruction")
        if not viable:
            flags.add("no_component_has_5_or_more_stop_candidates")
        if max_gap>=2000:
            flags.add("long_corridor_gap_over_2km")
        if any(r["geometry_warning"] for r in components):
            flags.add("source_geometry_mismatch_or_collision")
        if any(s.startswith("ARCGIS") for s in record_source):
            flags.add("older_arcgis_fallback")
        if company=="SOBUSA" and label.startswith("B18-4175"):
            flags.add("official_AB_label_length_discrepancy")
        if base not in gtfs_ids:
            flags.add("proposed_base_route_id_not_yet_in_existing_gtfs_routes")
        if any((r["trip_pattern_id"],r["route_id_proposed_base"]) not in counted for r in components):
            pass
        routes.append({
            "company":company,"official_route_label":label,
            "base_route_id_candidate":base,
            "KMZ_ArcGIS_geometry_components":ncomp,
            "components_with_5plus_existing_SIU_stops":viable,
            "provisional_stop_visits_all_components":total_stops,
            "distinct_physical_SIU_stops_all_components":len({
                r["stop_id"] for comp in components for r in by_pattern.get(comp["trip_pattern_id"],[])
            }),
            "largest_gap_between_selected_stops_m":round(max_gap,1),
            "geometry_sources":";".join(sorted(record_source)),
            "base_route_id_exists_in_current_gtfs_routes":"yes" if base in gtfs_ids else "no",
            "review_priority":"fragmented_geometry" if ncomp>1 else
                "large_gap" if max_gap>=2000 else "single_line_candidate",
            "qa_flags":";".join(sorted(flags)),
            "SIU_route_to_stop_link_directly_available":"no",
            "route_stop_assignment_authoritatively_confirmed":"no",
            "GTFS_trip_segment_confirmed":"no",
            "arrival_and_departure_times_assigned":"no",
            "GraphHopper_routing_status":"not_run",
        })
    for pat in patterns:
        ordered=by_pattern.get(pat["trip_pattern_id"],[])
        if len(ordered)<5:
            continue
        seq=[int(r["stop_sequence"]) for r in ordered]
        if seq!=list(range(1,len(ordered)+1)):
            raise ValueError("Invalid stop_sequence: "+pat["trip_pattern_id"])
        if not all(x["stop_id"] in physical for x in ordered):
            raise ValueError("Route-specific invented stop ID in "+pat["trip_pattern_id"])
        for v in ordered:
            stop=physical[v["stop_id"]]
            waypoints.append({
                "trip_pattern_id":pat["trip_pattern_id"],
                "route_id_candidate":pat["route_id_proposed_base"],
                "route_label":pat["official_route_label"],
                "company":pat["company"],
                "geometry_component":pat["geometry_component"],
                "stop_sequence":v["stop_sequence"],
                "physical_stop_id":v["stop_id"],
                "stop_lat":stop["stop_lat"],"stop_lon":stop["stop_lon"],
                "route_shape_distance_m":v["shape_dist_traveled_candidate_m"],
                "match_distance_m":v["distance_from_route_m"],
                "direction_alignment":v["source_vs_shape_direction"],
                "stop_id_reused_from_SIU":"yes",
                "GraphHopper_duration_seconds":"",
                "arrival_time":"","departure_time":"",
                "manual_pattern_review_status":"unreviewed",
            })
    if len(routes)!=60:
        raise ValueError(f"Expected 60 route variants, found {len(routes)}")
    if len(waypoints)!=len(visits):
        raise ValueError("Research mapping lost stop visits or includes invalid trip patterns")
    write(BASE/"route_variant_mapping_readiness_60.csv",routes,list(routes[0]))
    write(BASE/"graphhopper_waypoint_staging_NO_TIMES.csv",waypoints,list(waypoints[0]))
    summary={
        "route_variants_with_geometry":len(routes),
        "single_component_route_variants":sum(r["KMZ_ArcGIS_geometry_components"]==1 for r in routes),
        "multiple_component_route_variants":sum(r["KMZ_ArcGIS_geometry_components"]>1 for r in routes),
        "extremely_fragmented_route_variants_10plus_parts":sum(r["KMZ_ArcGIS_geometry_components"]>=10 for r in routes),
        "route_variants_with_5plus_stop_candidates_in_a_component":sum(r["components_with_5plus_existing_SIU_stops"]>0 for r in routes),
        "route_variants_with_gaps_over_2km":sum(r["largest_gap_between_selected_stops_m"]>=2000 for r in routes),
        "ordered_stop_visits_prepared_for_future_GraphHopper":len(waypoints),
        "source_SIU_physical_stop_ids_reused":len({r["physical_stop_id"] for r in waypoints}),
        "new_physical_stop_ids_created":0,
        "GTFS_stop_times_published":False,
        "stop_service_verified":False,
    }
    (BASE/"route_readiness_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Routevarianten versus lijnstukken: QA vóór echte GTFS-trips","",
      "Een losse KML/ArcGIS LineString is niet automatisch één operationele busrit. "
      "De bestaande geprojecteerde haltevolgorde is een **kandidaat**; fysieke halte-ID's blijven over routes heen gedeeld.",
      ""]
    for k,v in summary.items():
        if type(v) is int:lines.append("- "+k+": **"+str(v)+"**")
    for item in routes:
        if item["KMZ_ArcGIS_geometry_components"]>=10:
            lines+=["",
              f"**Geometriefragmenten: {item['company']} {item['official_route_label']} heeft "
              f"{item['KMZ_ArcGIS_geometry_components']} losse lijnstukken.** "
              "Die zijn niet gevalideerd als afzonderlijke trips. "
              "Stitching of verificatie van de brongemetrie is nodig."]
    lines+=["",
      "De waypoint-staging bevat lege tijden voor latere GraphHopper-berekening. "
      "Zonder gevalideerde haltebediening en richting is dit geen publiceerbare stop_times-indeling.",
      "",
      "### Bestanden","",
      "- route_variant_mapping_readiness_60.csv: alle routes, bronnen, afwijkingen, selectie- en geometriecontroles",
      "- graphhopper_waypoint_staging_NO_TIMES.csv: geordende bestaande SIU-stops inclusief coördinaten en lege tijden",
      ""]
    (BASE/"route_readiness_summary.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
