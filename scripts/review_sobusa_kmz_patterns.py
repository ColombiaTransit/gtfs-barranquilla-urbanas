#!/usr/bin/env python3
"""SOBUSA KMZ A/B spatial review and ordered, unconfirmed nearby boarding candidates.

Research staging only: projecting a SIU/OSM point onto a route is NOT evidence that
the route serves it, and geometric order is NOT GTFS stop_sequence.
"""
from __future__ import annotations
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree

ROOT=Path(__file__).resolve().parents[1]
KMZ=ROOT/"sources/amb/kmz"
SIU=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
OSM=ROOT/"sources/osm/analysis/possible_boarding_platforms.csv"
OUT=ROOT/"build/amb-sobusa-pattern-review"
PROJ=Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True)
BACK=Transformer.from_crs("EPSG:32618","EPSG:4326",always_xy=True)
MAX_RADIUS=35

def csvread(path):
    with path.open(encoding="utf-8-sig",newline="") as file:
        return list(csv.DictReader(file))

def csvwrite(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def load_lines(info):
    filepath=KMZ/info["geojson_path"]
    geo=json.loads(filepath.read_text(encoding="utf-8"))
    lines=[]
    for idx, feature in enumerate(geo.get("features",[]),1):
        g=feature.get("geometry") or {}
        if g.get("type")!="LineString": continue
        coords=g.get("coordinates",[])
        if len(coords)<2: continue
        line=LineString([PROJ.transform(float(x[0]),float(x[1])) for x in coords])
        if line.length>1:
            lines.append((idx,line))
    if not lines:
        raise ValueError("No valid LineString in "+str(filepath))
    return lines

def source_stops():
    rows=[]
    for row in csvread(SIU):
        try:
            rows.append({"id":row["stop_id"],"name":row["stop_name"],
                         "lat":float(row["stop_lat"]),"lon":float(row["stop_lon"]),
                         "source":"SIU_other_route_location","confirmed_sobusa":"no"})
        except (KeyError,ValueError):
            continue
    for row in csvread(OSM):
        try:
            rows.append({"id":row["osm_type"]+"/"+row["osm_id"],
                         "name":row.get("name",""),"lat":float(row["lat"]),
                         "lon":float(row["lon"]),"source":"OSM_unclassified_candidate",
                         "confirmed_sobusa":"no"})
        except (KeyError,ValueError):
            continue
    return rows

def compare_shapes(route, left, right):
    a=unary_union([line for _,line in left])
    b=unary_union([line for _,line in right])
    # Use fixed route length sample spacing so small single-street deviations
    # remain visible; never compare only endpoints or length difference.
    def scan(source,target):
        distances=[]
        deviating=[]
        for line in ([source] if source.geom_type=="LineString" else list(source.geoms)):
            if line.geom_type!="LineString":continue
            count=max(2,math.ceil(line.length/35))
            for k in range(count+1):
                p=line.interpolate(line.length*k/count)
                d=p.distance(target)
                distances.append(d)
                if d>25:
                    lon,lat=BACK.transform(p.x,p.y)
                    deviating.append((d,lon,lat))
        distances.sort()
        worst=max(deviating,default=(0,None,None))
        return {"n":len(distances),
                "over25":sum(d>25 for d in distances),
                "over50":sum(d>50 for d in distances),
                "p90":round(distances[min(len(distances)-1,int((len(distances)-1)*.9))],1),
                "max_d":round(worst[0],1) if worst[0] else round(distances[-1],1),
                "worst_lon":round(worst[1],6) if worst[1] is not None else "",
                "worst_lat":round(worst[2],6) if worst[2] is not None else ""}
    result_a=scan(a,b)
    result_b=scan(b,a)
    return {"route_code":route,"length_A_m":round(a.length,1),
            "length_B_m":round(b.length,1),
            "samples_A":result_a["n"],"samples_B":result_b["n"],
            "A_samples_more_than_25m_from_B":result_a["over25"],
            "B_samples_more_than_25m_from_A":result_b["over25"],
            "A_samples_more_than_50m_from_B":result_a["over50"],
            "B_samples_more_than_50m_from_A":result_b["over50"],
            "A_p90_distance_to_B_m":result_a["p90"],
            "B_p90_distance_to_A_m":result_b["p90"],
            "A_max_deviation_m":result_a["max_d"],
            "B_max_deviation_m":result_b["max_d"],
            "A_max_deviation_lon":result_a["worst_lon"],
            "A_max_deviation_lat":result_a["worst_lat"],
            "B_max_deviation_lon":result_b["worst_lon"],
            "B_max_deviation_lat":result_b["worst_lat"],
            "method":"densify_35m_compare_to_other_KMZ_route;spatial_difference_only",
            "legal_AB_geometry_validated":"no"}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    all_manifest=csvread(KMZ/"manifest.csv")
    sobusa=[r for r in all_manifest if r["company"]=="SOBUSA"]
    if len(sobusa)!=9: raise ValueError("Expected 9 SOBUSA KMZ route/variant files; got "+str(len(sobusa)))
    stops=source_stops()
    coords=[Point(*PROJ.transform(stop["lon"],stop["lat"])) for stop in stops]
    tree=STRtree(coords)
    review=[]
    patterns=[]
    layouts={}
    for r in sobusa:
        label=r["route_label"]
        lines=load_lines(r)
        layouts[label]=lines
        hits={}
        for idx,line in lines:
            for raw in tree.query(line.buffer(MAX_RADIUS)):
                n=int(raw)
                distance=line.distance(coords[n])
                if distance>MAX_RADIUS:continue
                old=hits.get(n)
                if old is None or distance<old["distance_m"]:
                    proj=line.project(coords[n])
                    snapped=line.interpolate(proj)
                    lon,lat=BACK.transform(snapped.x,snapped.y)
                    hits[n]={
                        "company":"SOBUSA","kmz_route_label":label,
                        "route_id_candidate":r["base_route_id_candidate"],"variant":r["variant"],
                        "source_stop_id":stops[n]["id"],
                        "source_stop_name":stops[n]["name"],"source_type":stops[n]["source"],
                        "stop_lat":stops[n]["lat"],"stop_lon":stops[n]["lon"],
                        "nearest_line_index":idx,
                        "projected_line_position_m":round(proj,1),
                        "distance_from_route_m":round(distance,2),
                        "snapped_lon_unverified":round(lon,7),
                        "snapped_lat_unverified":round(lat,7),
                        "proximity_band":"within_15m" if distance<=15 else "within_30m" if distance<=30 else "within_35m",
                        "boarding_for_SOBUSA_confirmed":"no",
                        "trip_pattern_stop_sequence_confirmed":"no",
                        "do_not_use_as_GTFS_stop_times":"yes",
                        "kmz_source_url":r["kmz_url"]
                    }
        ordered=sorted(hits.values(),key=lambda x:(x["nearest_line_index"],x["projected_line_position_m"],x["distance_from_route_m"]))
        for pos,v in enumerate(ordered,1):
            v["provisional_geometric_rank_NOT_stop_sequence"]=pos
        review.extend(ordered)
        num_siu=sum(x["source_type"].startswith("SIU") for x in ordered)
        num_osm=sum(x["source_type"].startswith("OSM") for x in ordered)
        patterns.append({
            "route":label,"route_id_candidate":r["base_route_id_candidate"],"variant":r["variant"],
            "kmz_source_url":r["kmz_url"],"source_url_collision":r.get("source_url_collision",""),
            "kmz_length_m":round(sum(line.length for _,line in lines),1),
            "kmz_lines":len(lines),"unverified_SIU_location_candidates_35m":num_siu,
            "unverified_OSM_boarding_candidates_35m":num_osm,
            "candidates_15m":sum(x["distance_from_route_m"]<=15 for x in ordered),
            "candidates_30m":sum(x["distance_from_route_m"]<=30 for x in ordered),
            "total_unverified_candidates_35m":len(ordered),
            "verified_SOBUSA_boarding_stops":0,
            "correct_stop_sequence_verified":"no",
            "source_geometry_source":"official_AMB_KMZ",
            "needs_review":"yes"
        })
    paired={}
    pairs=[]
    for pattern in patterns:
        if pattern["variant"] in ("A","B"):
            paired.setdefault(pattern["route_id_candidate"],{})[pattern["variant"]]=pattern
    for code,versions in paired.items():
        if not {"A","B"}.issubset(versions):
            raise ValueError("Expected both variants for "+code)
        shape=compare_shapes(code, layouts[versions["A"]["route"]], layouts[versions["B"]["route"]])
        a={x["source_stop_id"] for x in review if x["kmz_route_label"]==versions["A"]["route"]}
        b={x["source_stop_id"] for x in review if x["kmz_route_label"]==versions["B"]["route"]}
        shape.update({"nearby_source_points_shared_AB_35m":len(a&b),
                      "nearby_source_points_A_only_35m":len(a-b),
                      "nearby_source_points_B_only_35m":len(b-a),
                      "these_counts_do_NOT_prove_stop_service":"yes"})
        pairs.append(shape)

    fields=["company","kmz_route_label","route_id_candidate","variant","provisional_geometric_rank_NOT_stop_sequence",
            "source_stop_id","source_stop_name","source_type","stop_lat","stop_lon",
            "nearest_line_index","projected_line_position_m","distance_from_route_m",
            "snapped_lon_unverified","snapped_lat_unverified","proximity_band",
            "boarding_for_SOBUSA_confirmed","trip_pattern_stop_sequence_confirmed",
            "do_not_use_as_GTFS_stop_times","kmz_source_url"]
    csvwrite(OUT/"sobusa_all_nearby_candidates_NOT_CONFIRMED.csv",review,fields)
    csvwrite(OUT/"sobusa_variant_candidate_summary.csv",patterns,list(patterns[0]))
    csvwrite(OUT/"sobusa_AB_shape_differences.csv",pairs,list(pairs[0]))
    summary={
        "route_variant_records":len(patterns),
        "base_routes":len(set(x["route_id_candidate"] for x in patterns)),
        "variant_pairs_analyzed":len(pairs),
        "unique_nearby_candidate_route_assignments":len(review),
        "nearby_SIU_other_route_locations":sum(r["source_type"].startswith("SIU") for r in review),
        "nearby_OSM_unclassified_candidate_locations":sum(r["source_type"].startswith("OSM") for r in review),
        "SOBUSA_stops_authoritatively_confirmed":0,
        "A_B_differences_include_one_street_possibility":True,
        "gtfs_stops_or_stop_times_created":False,
        "source":"official_AMB_KMZ_plus_existing_SIU_and_OSM_locations",
        "source_status":"geographical_nearby_only"
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# SOBUSA: AMB-KMZ A/B-verschillen en halte-kandidaten","",
           "**Onderzoek, géén gevalideerde SOBUSA-stops.** SIU is voor SOBUSA niet opgenomen in de publieke 33-itinerarylijst. "
           "De geprojecteerde punten zijn afkomstig van SIU-haltes van andere lijnen of onbevestigde OSM-punten.","",
           "## Per routelabel","",
           "| AMB KMZ | Lengte KMZ (km) | Nabij SIU (35 m) | Nabij OSM (35 m) |","|---|---:|---:|---:|"]
    for row in patterns:
        lines.append("| {} | {:.1f} | {} | {} |".format(row["route"],row["kmz_length_m"]/1000,
                     row["unverified_SIU_location_candidates_35m"],row["unverified_OSM_boarding_candidates_35m"]))
    lines += ["","## A/B-routeverschillen (afstand tot de andere geometrie)","",
              "| Route | A-lengte (km) | B-lengte (km) | A-punten >25m van B | B-punten >25m van A |","|---|---:|---:|---:|---:|"]
    for row in pairs:
        lines.append("| {} | {:.1f} | {:.1f} | {} | {} |".format(row["route_code"],row["length_A_m"]/1000,
                     row["length_B_m"]/1000,row["A_samples_more_than_25m_from_B"],row["B_samples_more_than_25m_from_A"]))
    lines += ["","## Verificatie","",
              "- Projectie langs route geeft een **geometrische volgorde**, niet een valide haltevolgorde of geautoriseerde halte.",
              "- Bij lussen, terugritten en tegenliggers is LineString-projectie ambigu; herhaalde haltepassages kunnen ontbreken.",
              "- Nabij SIU-punt: bewezen locatie voor **een andere SIU-lijn**, niet voor SOBUSA.",
              "- Nabij OSM-punt: **geen bevestigde TPC-instapplaats**; expliciete Transmetro-haltes zijn gefilterd.",
              "- Bestaande officiële A/B-frequenties blijven leidend, maar zonder bevestigde haltes worden geen GTFS-ritpatronen gepubliceerd.",
              "- Eerst terminalstraten en A/B-afwijkingszones controleren tegen resolutie 466-2025 en 082-2026.", ""]
    (OUT/"summary.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
