#!/usr/bin/env python3
"""Map existing physical SIU stops onto AMB KMZ/ArcGIS route-shape trip patterns.

Scope: only AMB KMZ routes without an existing SIU route-stop pattern. Existing
physical SIU stop_ids are reused. Route geometry determines provisional visit
order; compass direction and nearby-stop competition reduce false assignments.
No departure/arrival times are estimated; GraphHopper can be integrated later.

All results are research staging; proximity is not proof of boarding service.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[1]
KMZ_DIR = ROOT / "sources/amb/kmz"
COVERAGE = ROOT / "sources/amb/kmz_stop_gaps/kmz_siu_route_stop_coverage.csv"
STOPS = ROOT / "sources/siu/gtfs_staging/candidate_stops.csv"
OCCURRENCES = ROOT / "sources/siu/gtfs_staging/siu_stop_occurrence_crosswalk.csv"
ARCGIS_INVENTORY = ROOT / "sources/amb/arcgis_shape_staging/arcgis_feature_inventory.csv"
DEFAULT_ARCGIS = ROOT / "build/amb-arcgis-fallback/arcgis_routes_original.geojson"
DEFAULT_OUTPUT = ROOT / "build/amb-missing-route-stop-trip-patterns"
FORWARD = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)
BACK = Transformer.from_crs("EPSG:32618", "EPSG:4326", always_xy=True)
MAX_SEARCH_M = 35
SELECT_LIMIT_M = 25
MIN_STOP_GAP_M = 115
OCCURRENCE_COLLAPSE_M = 60

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))

def write_csv(path,rows,cols):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=cols,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def norm(value):
    s=unicodedata.normalize("NFKD",str(value or "").upper())
    return re.sub("[^A-Z0-9]","", "".join(c for c in s if not unicodedata.combining(c)))

def company_norm(value):
    return norm(value).removeprefix("TRANSPORTES")

def marker_from_name(name):
    # Source SIU N-S etc indicators are informative, not definitive platform directions.
    tokens = re.findall(r"(?<![A-Z0-9])(?:NS|SN|OE|EO)(?![A-Z0-9])", name.upper())
    return tokens[-1] if tokens else ""

def heading_at(line,position):
    before=line.interpolate(max(0.0,position-25))
    after=line.interpolate(min(line.length,position+25))
    dx=after.x-before.x
    dy=after.y-before.y
    distance=math.hypot(dx,dy)
    return (dx/distance,dy/distance) if distance>=.1 else (0.0,0.0)

def direction_score(marker,dx,dy):
    # Spanish cartographic abbreviations: NS = north -> south.
    return {"NS":-dy,"SN":dy,"OE":dx,"EO":-dx}.get(marker)

def input_lines(feature_or_geojson):
    output=[]
    if feature_or_geojson.get("type") == "FeatureCollection":
        features=feature_or_geojson.get("features",[])
    elif feature_or_geojson.get("type") == "Feature":
        features=[feature_or_geojson]
    else:
        return []
    for feature in features:
        geom=feature.get("geometry") or {}
        kind=geom.get("type")
        geometries=([geom.get("coordinates",[])] if kind=="LineString" else
                    geom.get("coordinates",[]) if kind=="MultiLineString" else [])
        for part in geometries:
            if len(part)<2:continue
            try:
                coords=[FORWARD.transform(float(c[0]),float(c[1])) for c in part]
                line=LineString(coords)
                if line.length>=100:output.append(line)
            except (ValueError,TypeError,IndexError):
                continue
    return output

def load_arcgis(path):
    if not path.is_file():return {}
    content=json.loads(path.read_text(encoding="utf-8"))
    result={}
    for f in content.get("features",[]):
        ident=str((f.get("properties") or {}).get("OBJECTID") or f.get("id") or "")
        if ident:result[ident]=f
    return result

def source_selection(record,arcgis_features,inventory):
    """Prefer KMZ. If the website points a route to another route's file, use historic GIS."""
    label=record["kmz_route_label"]
    original_path=unquote(urlsplit(record["source_kmz_url"]).path)
    filename=Path(original_path).stem
    base=record["kmz_base_route_code"]
    if norm(filename).startswith(norm(base)):
        # Do not conflate a full route code with a shorter prefix (PT1 vs PT11).
        stem_code = re.sub(r"[\s-][AB]$","",filename.upper()).strip()
        accurate = norm(stem_code)==norm(base)
    else:
        accurate=False
    source_file=KMZ_DIR/record["source_geojson_path"]
    if accurate and source_file.is_file():
        line_data=json.loads(source_file.read_text(encoding="utf-8"))
        lines=input_lines(line_data)
        if lines:
            return ("AMB_KMZ_2026",lines,record["source_kmz_url"],
                    "source_url_shared_with_other_route_label" if record["source_url_collision"]=="yes" else "")
    # ArcGIS fallback for missing / mislabeled route KMZ, NOT assumed current.
    possible=[row for row in inventory if norm(row["route_code_tokens"])==norm(base)
              and company_norm(record["company"]) in company_norm(row["FolderPath"])]
    candidates=[arcgis_features[x["OBJECTID"]] for x in possible if x["OBJECTID"] in arcgis_features]
    if len(candidates)==1:
        lines=input_lines(candidates[0])
        if lines:
            return ("ARCGIS_2019_2023_FALLBACK",lines,
                    "https://services3.arcgis.com/oGYAc07w6wsvgUYr/ArcGIS/rest/services/Movilidad_Transito_WFL1/FeatureServer/6",
                    "AMB_KMZ_filename_does_not_match_route_code;older_GIS_shape_not_legally_verified")
    return ("NO_VALIDATED_SOURCE_SHAPE",[],"",
            "AMB_KMZ_label_filename_mismatch_or_missing;arcgis_fallback_unavailable")

def candidate_locations(line,source_stops,stop_points,stop_tree,occ_count):
    coords=list(line.coords)
    segments=[]
    prefixes=[]
    acc=0.0
    for a,b in zip(coords,coords[1:]):
        seg=LineString((a,b))
        prefixes.append(acc)
        segments.append(seg)
        acc+=seg.length
    segment_tree=STRtree(segments)
    # First reduce to physical SIU stops near this entire line.
    nearby=stop_tree.query(line.buffer(MAX_SEARCH_M))
    raw=[]
    for sidx in nearby:
        stop_idx=int(sidx)
        physical=source_stops[stop_idx]
        p=stop_points[stop_idx]
        if p.distance(line)>MAX_SEARCH_M:continue
        marker=marker_from_name(physical["stop_name"])
        crossings=[]
        for raw_seg_index in segment_tree.query(p.buffer(MAX_SEARCH_M)):
            seg_idx=int(raw_seg_index)
            seg=segments[seg_idx]
            distance=p.distance(seg)
            if distance>MAX_SEARCH_M:continue
            position=prefixes[seg_idx]+seg.project(p)
            dx,dy=heading_at(line,position)
            score=direction_score(marker,dx,dy)
            if score is None:
                alignment="unknown_no_direction_marker"
            elif score>=.25:
                alignment="direction_consistent"
            elif score<=-.25:
                alignment="direction_conflict"
            else:
                alignment="direction_tangent_ambiguous"
            crossings.append((position,distance,score,alignment))
        if not crossings:continue
        # A route can pass the same stop again on the return leg. Collapse only
        # adjacent segment projections of the same passage, not the whole trip.
        crossings.sort(key=lambda v:v[0])
        groups=[]
        for crossing in crossings:
            if not groups or crossing[0]-groups[-1][-1][0] > OCCURRENCE_COLLAPSE_M:
                groups.append([crossing])
            else:
                groups[-1].append(crossing)
        for occurrence_index,group in enumerate(groups,1):
            preferred=min(group,key=lambda x:(
                0 if x[3]=="direction_consistent" else
                1 if x[3]=="unknown_no_direction_marker" else
                2 if x[3]=="direction_tangent_ambiguous" else 3,
                x[1],x[0]))
            pos,dist,score,alignment=preferred
            eligible=(dist<=SELECT_LIMIT_M and alignment in
                      ("direction_consistent","unknown_no_direction_marker","direction_tangent_ambiguous"))
            lon,lat=BACK.transform(*line.interpolate(pos).coords[0])
            confidence=(
                "direction_consistent_nearby" if alignment=="direction_consistent" and dist<=15 else
                "provisional_nearby" if eligible else
                "direction_conflict_or_outside_selection_limit"
            )
            raw.append({
                "physical_stop_id":physical["stop_id"],
                "physical_stop_name":physical["stop_name"],
                "stop_lat":physical["stop_lat"],
                "stop_lon":physical["stop_lon"],
                "existing_SIU_itinerary_count":occ_count.get(physical["stop_id"],0),
                "source_direction_marker":marker,
                "source_vs_shape_direction":alignment,
                "direction_alignment_score":round(score,3) if score is not None else "",
                "distance_to_route_m":round(dist,2),
                "distance_along_shape_m":round(pos,1),
                "shape_projected_lat":round(lat,7),
                "shape_projected_lon":round(lon,7),
                "occurrence_index_of_physical_stop":occurrence_index,
                "source_SIU_stop_reused":"yes",
                "selection_confidence":confidence,
                "_eligible":eligible
            })
    # Prioritize closer and direction-consistent stops. Require spacing to avoid
    # attaching five nearby stops across the street to the same route segment.
    eligible=[r for r in raw if r["_eligible"]]
    eligible.sort(key=lambda r:(
        0 if r["source_vs_shape_direction"]=="direction_consistent" else 1,
        r["distance_to_route_m"],-r["existing_SIU_itinerary_count"],
        r["distance_along_shape_m"],r["physical_stop_id"]))
    chosen=[]
    for item in eligible:
        pos=item["distance_along_shape_m"]
        if all(abs(pos-x["distance_along_shape_m"])>=MIN_STOP_GAP_M for x in chosen):
            chosen.append(item)
    chosen.sort(key=lambda v:(v["distance_along_shape_m"],v["physical_stop_id"]))
    ids={(x["physical_stop_id"],x["distance_along_shape_m"]) for x in chosen}
    for item in raw:
        key=(item["physical_stop_id"],item["distance_along_shape_m"])
        if key in ids:
            item["selected_for_model_trip"]="yes"
            item["rejection_or_review_reason"]=""
        else:
            item["selected_for_model_trip"]="no"
            item["rejection_or_review_reason"]=(
                "direction_conflict" if item["source_vs_shape_direction"]=="direction_conflict" else
                "distance_over_25m" if item["distance_to_route_m"]>SELECT_LIMIT_M else
                "nearby_competing_stop_or_duplicate_route_passage"
            )
        item.pop("_eligible",None)
    return chosen,raw

def gtfs_base_route_id(record):
    # In a future routes.txt normalization, A/B share this one base route ID.
    return "AMB_"+re.sub("[^A-Z0-9]+","_",record["company"].upper()).strip("_") + "_" + (
        re.sub("[^A-Z0-9]+","_",record["kmz_base_route_code"].upper()).strip("_"))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--arcgis-geojson",type=Path,default=DEFAULT_ARCGIS)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    coverage=read_csv(COVERAGE)
    missing=[r for r in coverage if r["siu_coverage_status"]=="no_siu_route_stop_candidate"]
    if len(missing)!=60:
        raise ValueError(f"Expected 60 missing SIU-route KMZ variant records, received {len(missing)}")
    stops=read_csv(STOPS)
    stopids={r["stop_id"] for r in stops}
    if len(stopids)!=len(stops):
        raise ValueError("Canonical SIU physical stop_id collision")
    occurrences=read_csv(OCCURRENCES)
    by_siu_stop=defaultdict(set)
    for r in occurrences:
        by_siu_stop[r["candidate_stop_id"]].add(r["siu_itinerary_uuid"])
    count={sid:len(itins) for sid,itins in by_siu_stop.items()}
    stop_points=[Point(*FORWARD.transform(float(r["stop_lon"]),float(r["stop_lat"]))) for r in stops]
    stop_tree=STRtree(stop_points)
    arcgis_features=load_arcgis(args.arcgis_geojson)
    inventory=read_csv(ARCGIS_INVENTORY)

    patterns=[]
    selected_rows=[]
    all_candidates=[]
    quality=[]
    for item in missing:
        source_name,lines,url,source_warning=source_selection(item,arcgis_features,inventory)
        for component_idx,line in enumerate(lines,1):
            picked,candidates=candidate_locations(line,stops,stop_points,stop_tree,count)
            code=gtfs_base_route_id(item)
            pattern_id="KMZSTOP_"+norm(item["company"])+"_"+norm(item["kmz_route_label"]) + "_P"+str(component_idx)
            # A physical stop may be present on several trips; never create a route-specific stop_id.
            trip_pattern_id="AMB_RECON_"+norm(item["company"])+"_"+norm(item["kmz_route_label"])+"_P"+str(component_idx)
            trip={
                "trip_pattern_id":trip_pattern_id,
                "route_id_proposed_base":code,
                "company":item["company"],
                "official_route_label":item["kmz_route_label"],
                "official_base_route_code":item["kmz_base_route_code"],
                "variant":item["kmz_variant"],
                "geometry_component":component_idx,
                "source_geometry":source_name,
                "source_geometry_url":url,
                "shape_length_m":round(line.length,1),
                "physical_SIU_stop_candidates_in_order":len(picked),
                "trip_stop_order_status":"provisional_geometry_based_not_SIU_order",
                "direction_id":"",
                "route_variant_legal_verified":"no",
                "single_continuous_vehicle_trip_proven":"no",
                "possible_outbound_and_return_combined":"yes",
                "timing_source":"GraphHopper_to_calculate_later",
                "all_stop_times_unset":"yes",
                "publication_ready":"no",
                "geometry_warning":source_warning,
                "stop_selection_model":"SIU_physical_stops_35m_search_25m_select_directional_115m_spacing",
            }
            if len(picked)>=5:
                for seq,x in enumerate(picked,1):
                    selected_rows.append({
                        "trip_pattern_id":trip_pattern_id,
                        "route_id_proposed_base":code,
                        "company":item["company"],
                        "official_route_label":item["kmz_route_label"],
                        "variant":item["kmz_variant"],
                        "stop_sequence":seq,
                        "stop_id":x["physical_stop_id"],
                        "stop_name":x["physical_stop_name"],
                        "shape_dist_traveled_candidate_m":x["distance_along_shape_m"],
                        "distance_from_route_m":x["distance_to_route_m"],
                        "source_vs_shape_direction":x["source_vs_shape_direction"],
                        "candidate_quality":x["selection_confidence"],
                        "arrival_time":"",
                        "departure_time":"",
                        "actual_route_stops_verified":"no",
                        "source_stop_id_reused":"yes",
                        "geographic_pattern_only":"yes",
                    })
            else:
                trip["trip_stop_order_status"]="insufficient_candidates_not_staged"
            patterns.append(trip)
            quality.append({
                "company":item["company"],"route_label":item["kmz_route_label"],
                "trip_pattern_id":trip_pattern_id,"geometry_component":component_idx,
                "source_geometry":source_name,"source_url":url,
                "geometry_warning":source_warning,
                "kmz_source_url_collision":item["source_url_collision"],
                "route_shape_length_km":round(line.length/1000,2),
                "all_SIU_stops_within_35m_with_occurrences":len(candidates),
                "selected_existing_SIU_stop_references":len(picked),
                "rejected_direction_conflicts":sum(r["rejection_or_review_reason"]=="direction_conflict" for r in candidates),
                "selected_stops_with_direction_marker":sum(bool(r["source_direction_marker"]) for r in picked),
                "selected_stops_with_unknown_direction":sum(r["source_vs_shape_direction"]=="unknown_no_direction_marker" for r in picked),
                "max_gap_between_selected_stops_m":round(max(
                    (b["distance_along_shape_m"]-a["distance_along_shape_m"] for a,b in zip(picked,picked[1:])),default=0),1),
                "pattern_stop_order_publishable":"no"
            })
            for x in candidates:
                all_candidates.append({
                    "trip_pattern_id":trip_pattern_id,
                    "company":item["company"],
                    "route_label":item["kmz_route_label"],
                    "source_geometry":source_name,
                    **x,
                })
        if not lines:
            quality.append({
                "company":item["company"],"route_label":item["kmz_route_label"],
                "trip_pattern_id":"","geometry_component":0,"source_geometry":source_name,
                "source_url":url,"geometry_warning":source_warning,
                "kmz_source_url_collision":item["source_url_collision"],
                "route_shape_length_km":0,
                "all_SIU_stops_within_35m_with_occurrences":0,
                "selected_existing_SIU_stop_references":0,
                "rejected_direction_conflicts":0,
                "selected_stops_with_direction_marker":0,
                "selected_stops_with_unknown_direction":0,
                "max_gap_between_selected_stops_m":0,
                "pattern_stop_order_publishable":"no"
            })
        print(json.dumps({"route":item["company"]+"/"+item["kmz_route_label"],
                          "geometry":source_name,"components":len(lines),
                          "candidates":sum(p["physical_SIU_stop_candidates_in_order"] for p in patterns
                                           if p["official_route_label"]==item["kmz_route_label"]
                                           and p["company"]==item["company"])}),flush=True)
    if not patterns:
        raise SystemExit("No route-stop patterns generated")
    # There must never be a freshly minted physical stop ID for each route.
    if any(r["stop_id"] not in stopids for r in selected_rows):
        raise ValueError("Invented route-specific stop ID detected")
    ids=[r["trip_pattern_id"] for r in patterns]
    if len(set(ids))!=len(ids):
        raise ValueError("Non-unique trip pattern IDs")
    by_trip=defaultdict(list)
    for row in selected_rows:
        by_trip[row["trip_pattern_id"]].append(row)
    for tripid,seq in by_trip.items():
        if [r["stop_sequence"] for r in seq] != list(range(1,len(seq)+1)):
            raise ValueError("Non-contiguous stop order in "+tripid)
        if any(float(b["shape_dist_traveled_candidate_m"]) < float(a["shape_dist_traveled_candidate_m"])
               for a,b in zip(seq,seq[1:])):
            raise ValueError("Non-monotone stop projection in "+tripid)
    all_base_route_codes={(r["company"],r["official_base_route_code"]) for r in patterns}
    unique_linked={r["stop_id"] for r in selected_rows}
    summary={
        "source_KMZ_route_variants_missing_SIU":len(missing),
        "route_variants_with_at_least_one_shape":len({(p["company"],p["official_route_label"]) for p in patterns}),
        "generated_provisional_trip_patterns":len(patterns),
        "trip_patterns_with_at_least_five_candidate_stops":sum(r["physical_SIU_stop_candidates_in_order"]>=5 for r in patterns),
        "distinct_company_base_routes_in_patterns":len(all_base_route_codes),
        "provisional_route_stop_visits":len(selected_rows),
        "distinct_existing_physical_SIU_stop_ids_reused":len(unique_linked),
        "total_route_stop_projection_candidates_within_35m":len(all_candidates),
        "arcgis_fallback_pattern_components":sum(p["source_geometry"].startswith("ARCGIS") for p in patterns),
        "missing_route_variants_with_no_geometry":len(missing)-len({(p["company"],p["official_route_label"]) for p in patterns}),
        "new_physical_stop_ids_created":0,
        "arrival_departure_times_generated":0,
        "graphhopper_route_duration_future_dependency":True,
        "SIU_existing_route_stop_links_preserved":True,
        "service_of_route_at_stop_confirmed_by_geometry_alone":False,
        "publication_ready":False,
        "parameters":{"max_search_m":MAX_SEARCH_M,"selected_distance_m":SELECT_LIMIT_M,
                      "minimum_stop_spacing_along_route_m":MIN_STOP_GAP_M,
                      "passage_collapse_m":OCCURRENCE_COLLAPSE_M}
    }
    write_csv(args.output/"trip_patterns_MISSING_SIU_NO_TIMES.csv",patterns,list(patterns[0]))
    write_csv(args.output/"candidate_stop_order_per_trip_NO_TIMES.csv",selected_rows,
              ["trip_pattern_id","route_id_proposed_base","company","official_route_label","variant",
               "stop_sequence","stop_id","stop_name","shape_dist_traveled_candidate_m",
               "distance_from_route_m","source_vs_shape_direction","candidate_quality",
               "arrival_time","departure_time","actual_route_stops_verified",
               "source_stop_id_reused","geographic_pattern_only"])
    write_csv(args.output/"all_projected_SIU_stop_candidates_WITH_DECISIONS.csv",all_candidates,
              list(all_candidates[0]) if all_candidates else
              ["trip_pattern_id","company","route_label","source_geometry","physical_stop_id"])
    write_csv(args.output/"route_shape_and_stop_mapping_QA.csv",quality,list(quality[0]))
    (args.output/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    reports=["# KMZ/ArcGIS → ritpatronen en bestaande SIU-haltevolgorde (nog zonder tijden)","",
        "**Onderzoeksstaging: geen GTFS stop_times.txt gepubliceerd.**",
        "Het programma verwerkt uitsluitend AMB-routevarianten zonder directe SIU-route-halte-koppeling. "
        "Bestaande SIU-route-haltevolgordes blijven ongewijzigd.","",
        "## Resultaten",""]
    for k,v in summary.items():
        if isinstance(v,int):reports.append("- "+k+": **"+str(v)+"**")
    reports+=["","## Methode","",
      "1. Officiële AMB-KMZ is voorkeursgeometrie; bij foutief KMZ-bestandslabel wordt de 2019–2023 ArcGIS-bron gemarkeerd als tijdelijke fallback.",
      "2. Vind bestaande fysieke SIU-stop-ID's binnen 35 meter van een shape. Projecteer elke halte op alle lijnpassages zodat een rondrit dezelfde fysieke halte bij terugkeer opnieuw kan bezoeken.",
      "3. Bij haltebenamingen met NS/SN/OE/EO vergelijkt het script de rijrichting van de lokale routetangent; tegenstrijdige richting wordt niet geselecteerd.",
      "4. Alleen kandidaten binnen 25 meter mogen in de modelrit worden geselecteerd. Kies per 115 meter afgelegde routeafstand één beste kandidaat om overmatige dubbele instappunten te vermijden.",
      "5. Leg de geselecteerde bestaande stop_ID's vast in oplopende shapeafstand met aaneengesloten stop_sequence. Arrival/departure blijven leeg voor latere GraphHopper-berekening.",
      "",
      "## Belangrijke beperkingen","",
      "- Een fysieke halte mag door veel routes en trips worden gedeeld. Er worden **geen route-specifieke haltes verzonnen**.",
      "- Geografische nabijheid en richting zijn een **modelaanname**, geen officiële bevestiging dat een bus stopt.",
      "- 115 meter is een selectieregel om te veel haltes te voorkomen, niet een vastgesteld halte-interval.",
      "- Soms beschrijft één KML-lijn een volledige rondrit (heen én terug). De gegenereerde pattern is dan een onderzoeksroute, niet noodzakelijk één operationele trip.",
      "- Bij verkeersassen waar heen/terug dezelfde geometrie delen, kan de richtingsclassificatie onzeker blijven.",
      "- De bron-AM B18-variantlabels kunnen omgewisseld zijn; PT2 kan een oudere ArcGIS-fallback gebruiken. Iedere bronafwijking staat in de QA.",
      "- Geen tijden of frequenties gewijzigd en geen GTFS-bestanden onder gtfs/ overschreven.",
      "",
      "## Vervolg",
      "Beoordeel per lijn de stopselectie en echte tripgrenzen. Vervolgens kan GraphHopper over de gekozen trajecten een reistijdmodel aanleveren.",
      ""]
    (args.output/"summary.md").write_text("\n".join(reports),encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
