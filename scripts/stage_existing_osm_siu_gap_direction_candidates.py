#!/usr/bin/env python3
"""Reuse the EXISTING OSM export + SIU stop catalog in unresolved AMB route gaps.

NO Overpass or any network call. Does not change GTFS or existing mapping.
Preserves opposite-direction SIU candidates for future GraphHopper oneway/curbside
road access checks. A matched OSM point reuses the SIU physical stop_id.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree

ROOT=Path(__file__).resolve().parents[1]
GAP=ROOT/"sources/amb/missing_siu_trip_stop_patterns"
OSM=ROOT/"sources/osm/analysis/possible_boarding_platforms.csv"
SIU=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
OUT=ROOT/"build/amb-gap-direction-candidate-staging"
METRIC=Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True)
MAX_OSM_DISTANCE_M=75
SAME_PHYSICAL_STOP_M=12

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def write(path,items,fields):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(items)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    gapgeo=json.loads((GAP/"gap_corridors_for_review.geojson").read_text(encoding="utf-8"))
    gaps=read(GAP/"stop_gaps_over_2km_review.csv")
    if len(gapgeo["features"])!=len(gaps) or len(gaps)!=73:
        raise ValueError("The 73 gap geometries and CSV gap records must match")
    source_siu=json.loads((GAP/"SIU_stop_alternatives_inside_gaps_REVIEW_ONLY.geojson").read_text(encoding="utf-8"))
    physical=read(SIU)
    physical_by_id={r["stop_id"]:r for r in physical}
    siu_geom=[Point(*METRIC.transform(float(r["stop_lon"]),float(r["stop_lat"]))) for r in physical]
    siu_index=STRtree(siu_geom)
    osm=read(OSM)
    # Store all pre-existing SIU candidates as-is: GraphHopper gets to check
    # 'direction_conflict' rather than having these candidates permanently lost.
    candidates=[]
    for feature in source_siu["features"]:
        p=feature["properties"]
        sid=p["existing_physical_SIU_stop_id"]
        if sid not in physical_by_id:raise ValueError("Unknown SIU stop ID: "+sid)
        lon,lat=feature["geometry"]["coordinates"]
        candidates.append({
            "company":p["company"],"route_label":p["route_label"],
            "trip_pattern_id":p["trip_pattern_id"],"gap_index":p["gap_index"],
            "gap_length_m":p["gap_m"],"candidate_kind":"existing_physical_SIU_stop",
            "candidate_source_id":sid,"physical_SIU_stop_id_if_known":sid,
            "stop_name":p.get("stop_name",""),"longitude":lon,"latitude":lat,
            "distance_to_gap_shape_m":p["distance_to_route_m"],
            "global_shape_position_m":p["projection_along_shape_m"],
            "original_KMZ_direction_assessment":p["local_direction_assessment"],
            "previous_decision":p["reason_for_review"],
            "near_tagged_transmetro_50m":"unknown_SIU",
            "GraphHopper_vehicle_access_check":"pending",
            "GraphHopper_oneway_direction_check":"pending",
            "GraphHopper_curbsides_check":"pending",
            "added_to_existing_route_pattern":"no",
            "actual_bus_route_stop_verified":"no",
        })
    siu_count=len(candidates)
    osm_links=0
    osm_new=0
    gap_map={}
    for feature,record in zip(gapgeo["features"],gaps):
        p=feature["properties"]
        assert p["trip_pattern_id"]==record["trip_pattern_id"]
        assert str(p["gap_index"])==record["gap_index"]
        key=(p["trip_pattern_id"],str(p["gap_index"]))
        gap_map[key]=record

    gaps_metric=[LineString([METRIC.transform(lon,lat)
                             for lon,lat in feature["geometry"]["coordinates"]])
                 for feature in gapgeo["features"]]
    idx=STRtree(gaps_metric)
    existing_keys={(str(r["trip_pattern_id"]),str(r["gap_index"]),r["candidate_source_id"])
                   for r in candidates}
    for item in osm:
        p=Point(*METRIC.transform(float(item["lon"]),float(item["lat"])))
        hits=idx.query(p.buffer(MAX_OSM_DISTANCE_M))
        if not len(hits):continue
        nearest_id=""
        maybe_same=siu_index.query(p.buffer(SAME_PHYSICAL_STOP_M))
        if len(maybe_same):
            near=min((int(x) for x in maybe_same),key=lambda x:p.distance(siu_geom[x]))
            nearest_id=physical[near]["stop_id"]
        for rawid in hits:
            i=int(rawid)
            line=gaps_metric[i]
            distance=p.distance(line)
            if distance>MAX_OSM_DISTANCE_M:continue
            g=gaps[i]
            identity=item["osm_type"]+"/"+item["osm_id"]
            if (g["trip_pattern_id"],g["gap_index"],identity) in existing_keys:
                continue
            osm_links+=1
            if not nearest_id:osm_new+=1
            candidates.append({
                "company":g["company"],"route_label":g["route_label"],
                "trip_pattern_id":g["trip_pattern_id"],"gap_index":g["gap_index"],
                "gap_length_m":g["gap_m"],"candidate_kind":"existing_OSM_boarding_candidate_unverified",
                "candidate_source_id":identity,
                "physical_SIU_stop_id_if_known":nearest_id,
                "stop_name":item["name"],
                "longitude":item["lon"],"latitude":item["lat"],
                "distance_to_gap_shape_m":round(distance,1),
                "global_shape_position_m":round(
                    float(g["distance_along_shape_start_m"])+line.project(p),1),
                "original_KMZ_direction_assessment":"unknown_needs_road_network",
                "previous_decision":"not_added_from_original_OSM_snapshot",
                "near_tagged_transmetro_50m":item.get("near_tagged_transmetro_50m",""),
                "GraphHopper_vehicle_access_check":"pending",
                "GraphHopper_oneway_direction_check":"pending",
                "GraphHopper_curbsides_check":"pending",
                "added_to_existing_route_pattern":"no",
                "actual_bus_route_stop_verified":"no",
            })
    candidate_counts=Counter((x["trip_pattern_id"],str(x["gap_index"])) for x in candidates)
    breakdown=Counter(x["candidate_kind"] for x in candidates)
    gap_review=[]
    for g in gaps:
        key=(g["trip_pattern_id"],str(g["gap_index"]))
        hits=[x for x in candidates if (x["trip_pattern_id"],str(x["gap_index"]))==key]
        source_kinds=Counter(x["candidate_kind"] for x in hits)
        gap_review.append({
            "company":g["company"],"route_label":g["route_label"],
            "trip_pattern_id":g["trip_pattern_id"],"gap_index":g["gap_index"],
            "gap_length_m":g["gap_m"],"gap_review_class":g["gap_review_class"],
            "source_SIU_alternatives":source_kinds.get("existing_physical_SIU_stop",0),
            "source_OSM_boarding_candidates":source_kinds.get("existing_OSM_boarding_candidate_unverified",0),
            "all_candidates_in_future_GraphHopper_pool":len(hits),
            "baseline_from_existing_stop_id":g["from_stop_id"],
            "baseline_to_existing_stop_id":g["to_stop_id"],
            "baseline_start_global_chainage_m":g["distance_along_shape_start_m"],
            "baseline_end_global_chainage_m":g["distance_along_shape_end_m"],
            "requires_GraphHopper_road_network_validation":"yes",
            "stop_sequence_automatically_modified":"no",
        })
    candidates.sort(key=lambda r:(r["company"],r["route_label"],r["trip_pattern_id"],
                                  int(r["gap_index"]),float(r["global_shape_position_m"]),r["candidate_source_id"]))
    write(OUT/"existing_SIU_OSM_direction_candidates_for_GraphHopper.csv",
          candidates,list(candidates[0]))
    write(OUT/"gap_review_with_existing_OSM_snapshot.csv",gap_review,list(gap_review[0]))
    data={
        "type":"FeatureCollection",
        "features":[{"type":"Feature",
                     "properties":{k:v for k,v in r.items() if k not in ("longitude","latitude")},
                     "geometry":{"type":"Point","coordinates":[float(r["longitude"]),float(r["latitude"])]}}
                    for r in candidates],
    }
    (OUT/"existing_source_direction_candidates.geojson").write_text(
        json.dumps(data,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    summary={
        "overpass_queries_made":0,
        "input_OSM_snapshot":"sources/osm/overpass_barranquilla_bus_stops_2026-11-03.json",
        "input_OSM_boarding_candidate_count":len(osm),
        "long_shape_stop_gaps_considered":len(gaps),
        "gaps_without_original_SIU_candidates":sum(g["gap_review_class"]=="no_source_SIU_stop_on_this_corridor" for g in gaps),
        "all_original_SIU_direction_alternatives_preserved":siu_count,
        "original_OSM_source_to_route_gap_candidate_links":osm_links,
        "OSM_links_without_nearby_existing_physical_SIU_stop_id":osm_new,
        "gaps_with_at_least_one_candidate":sum(bool(candidate_counts.get((g["trip_pattern_id"],str(g["gap_index"]))))
                                               for g in gaps),
        "total_future_GraphHopper_direction_review_candidates":len(candidates),
        "original_SIU_candidates_with_earlier_opposite_direction_assessment":
            sum(x["original_KMZ_direction_assessment"]=="direction_conflict" for x in candidates),
        "new_GTFS_stop_ids_created":0,
        "trip_stop_sequences_changed":False,
        "GraphHopper_called":False,
    }
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Onderzoek bestaande SIU- en OSM-data voor latere GraphHopper-richtingstoets","",
           "**Geen nieuwe Overpass-queries. Geen GTFS-wijzigingen.**",
           "",
           "We hergebruiken de reeds ontvangen OSM-export en alle in de GIS/KMZ-analyse afgewezen SIU-haltes. "
           "Dezelfde fysieke SIU-stop-ID's worden hergebruikt; een OSM-punt dicht bij een SIU-halte "
           "krijgt hooguit een voorlopige verwijzing naar die bestaande ID, geen nieuwe halte.",
           "",
           "De rijrichting uit een haltebenaming of een KMZ-lijntangent is geen controle van eenrichtingswegen. "
           "Juist de eerder als tegenovergesteld gemarkeerde stops worden voor GraphHopper bewaard.",
           "",
           "## Resultaten",""]
    for k,v in summary.items():
        if type(v)==int:lines.append("- "+k+": **"+str(v)+"**")
    lines+=["","## Vervolg","",
             "1. Laat GraphHopper later voor de geplande route in beide richtingen de feitelijke toegestane rijbaan en bochten bepalen.",
             "2. Vergelijk elke haltekandidaat met motorvoertuig-routing langs de shape en de toegankelijke straatkant.",
             "3. Voeg pas na die toets en aanvullende route-/haltebedieningsvalidatie wijzigingen aan de trip-haltevolgorde toe.",
             "4. Houd OSM-ODbL-attributie en SIU-bronvermelding gescheiden.",
             ""]
    (OUT/"summary.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
