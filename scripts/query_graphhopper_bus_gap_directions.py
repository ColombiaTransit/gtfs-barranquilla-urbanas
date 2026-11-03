#!/usr/bin/env python3
"""GraphHopper bus routing QA for gaps in AMB KMZ/ArcGIS stop patterns.

Private endpoint only from GitHub org-level GRAPHHOPPER_URL environment variable.
No endpoint/key/hostname logged or persisted; no OSM requests; no GTFS edits.

Input: 73 existing >=2 km stop gaps and 125 existing SIU/OSM candidates.
For each pilot gap, compare permitted A->B and B->A bus routes, then A->candidate->B.
Strict right-hand curbside is tested optionally and reported separately. All
decisions are REVIEW ONLY: routing does not prove bus operator boarding service.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests
from pyproj import Transformer
from shapely.geometry import LineString, Point

ROOT=Path(__file__).resolve().parents[1]
GAP=ROOT/"sources/amb/missing_siu_trip_stop_patterns"
CAND=ROOT/"sources/amb/gap_direction_staging"
STOPS=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
DEFAULT_OUT=ROOT/"build/amb-graphhopper-bus-direction-QA"
PROJECT=Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True)
BACK=Transformer.from_crs("EPSG:32618","EPSG:4326",always_xy=True)

def read_csv(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path,rows,fields):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def endpoints(base):
    """Preserve subpath and query credentials without ever printing them."""
    if not base or not base.strip():
        raise ValueError("missing_GITHUB_ORG_GRAPHHOPPER_URL")
    parsed=urlsplit(base.strip())
    if parsed.scheme not in ("http","https") or not parsed.netloc:
        raise ValueError("invalid_GITHUB_ORG_GRAPHHOPPER_URL")
    # This env may be either the GraphHopper server root or its /route endpoint.
    path=parsed.path.rstrip("/")
    if path.endswith("/route"):
        prefix=path[:-len("/route")]
    elif path.endswith("/info"):
        prefix=path[:-len("/info")]
    else:
        prefix=path
    def build(suffix):
        return urlunsplit((parsed.scheme,parsed.netloc,prefix+suffix,parsed.query,""))
    return build("/info"),build("/route")

class Client:
    def __init__(self,base,timeout=25):
        self.info_url,self.route_url=endpoints(base)
        self.timeout=timeout
        self.session=requests.Session()
        self.session.headers.update({
            # Cloudflare-fronted self-hosted GraphHopper: use normal browser request
            # headers for both /info and /route, while retaining a single session.
            # A browser User-Agent alone cannot solve a JavaScript challenge.
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        })
        self.route_queries=0
        self.info_queries=0
    def _call(self,kind,url,payload=None):
        try:
            if kind=="GET":
                response=self.session.get(url,timeout=(8,self.timeout),allow_redirects=False)
            else:
                response=self.session.post(url,json=payload,timeout=(8,self.timeout),allow_redirects=False)
        except requests.Timeout:
            return None,"timeout"
        except requests.RequestException:
            # Never serialize exception details: requests exceptions can include the private URL.
            return None,"network_or_TLS_error"
        if response.status_code>=300:
            return None,"HTTP_"+str(response.status_code)
        try:
            data=response.json()
        except ValueError:
            return None,"non_JSON_response"
        if not isinstance(data,dict):
            return None,"malformed_JSON_response"
        return data,"ok"
    def info(self):
        self.info_queries+=1
        return self._call("GET",self.info_url)
    def route(self,points,curbside=False):
        self.route_queries+=1
        payload={"profile":"bus","points":points,"points_encoded":False,
                 "instructions":False,"calc_points":True}
        if curbside:
            # Right-side access matters in Colombian right-hand traffic.
            # Only edge-based turn-cost profiles support strict curbsides.
            payload["curbsides"]=["any","right","any"]
            payload["curbside_strictness"]="strict"
        data,status=self._call("POST",self.route_url,payload)
        if status!="ok":return None,status
        paths=data.get("paths")
        if not isinstance(paths,list) or not paths or not isinstance(paths[0],dict):
            return None,"no_paths"
        path=paths[0]
        try:
            distance=float(path["distance"])
            coords=path["points"]["coordinates"]
            if not math.isfinite(distance) or distance<=0 or len(coords)<2:
                return None,"invalid_route_geometry"
            line=LineString([PROJECT.transform(float(v[0]),float(v[1])) for v in coords])
            if line.length<=0:return None,"invalid_route_geometry"
            snapped=(path.get("snapped_waypoints") or {}).get("coordinates") or []
            return {"distance_m":round(distance,1),
                    "time_ms":int(path.get("time") or 0),
                    "geometry":line,"snapped":snapped,
                    "coordinates":[[round(float(v[0]),6),round(float(v[1]),6)] for v in coords]}, "ok"
        except (ValueError,TypeError,KeyError,IndexError):
            return None,"invalid_route_geometry"

def path_similarity(result,expected):
    # Only a heuristic comparing shortest bus routing against official KMZ corridor.
    line=result["geometry"]
    count=max(2,min(300,math.ceil(line.length/35)))
    dist=sorted(line.interpolate(line.length*i/count).distance(expected)
                for i in range(count+1))
    return {
        "p90_distance_to_KMZ_corridor_m":round(dist[int(.90*(len(dist)-1))],1),
        "max_distance_to_KMZ_corridor_m":round(dist[-1],1),
        "fraction_GH_path_within_50m_KMZ":round(sum(x<=50 for x in dist)/len(dist),3)
    }

def constrained_anchor_points(line,maximum=12):
    """Use intermediary KMZ waypoints to prevent shortest-path shortcuts across loops."""
    n=min(maximum+1,max(2,math.ceil(line.length/700)))
    positions=[line.length*i/n for i in range(1,n)]
    points=[list(BACK.transform(*line.interpolate(d).coords[0])) for d in positions]
    return positions,points

def via_anchor_points(a,b,positions,anchors,stop,along_m):
    items=list(zip(positions,anchors))+[(along_m,stop)]
    items.sort(key=lambda pair:pair[0])
    return [a]+[point for _,point in items]+[b]

def load_inputs():
    gaps=read_csv(CAND/"gap_review_with_existing_OSM_snapshot.csv")
    candidates=read_csv(CAND/"existing_SIU_OSM_direction_candidates_for_GraphHopper.csv")
    stops={x["stop_id"]:x for x in read_csv(STOPS)}
    raw=json.loads((GAP/"gap_corridors_for_review.geojson").read_text(encoding="utf-8"))
    shape={}
    for f in raw["features"]:
        p=f["properties"]
        key=(p["trip_pattern_id"],str(p["gap_index"]))
        geom=f["geometry"]
        if geom["type"]!="LineString":
            raise ValueError("Not a LineString in source gap: "+str(key))
        shape[key]=LineString([PROJECT.transform(float(x[0]),float(x[1]))
                               for x in geom["coordinates"]])
    bykey=defaultdict(list)
    for c in candidates:
        bykey[(c["trip_pattern_id"],str(c["gap_index"]))].append(c)
    assert len(gaps)==73 and len(candidates)==125 and len(shape)==73
    for g in gaps:
        key=(g["trip_pattern_id"],g["gap_index"])
        if key not in shape:raise ValueError("Missing gap shape for "+str(key))
        if g["baseline_from_existing_stop_id"] not in stops or g["baseline_to_existing_stop_id"] not in stops:
            raise ValueError("Missing SIU anchor stop for "+str(key))
    return gaps,bykey,stops,shape

def stop_coords(stop):
    return [float(stop["stop_lon"]),float(stop["stop_lat"])]

def candidate_coords(c):
    return [float(c["longitude"]),float(c["latitude"])]

def pick_gaps(gaps,bykey,max_gaps):
    # Study a mix of cases with existing SIU and OSM alternatives first.
    # Full audit with --max-gaps 73. Choose stable ordering.
    def score(g):
        cs=bykey.get((g["trip_pattern_id"],g["gap_index"]),[])
        return (0 if cs and any(c["candidate_kind"].startswith("existing_OSM") for c in cs) else
                1 if cs else 2,
                0 if g["company"]=="SOBUSA" else 1,
                -len(cs),-float(g["gap_length_m"]),g["company"],g["route_label"],int(g["gap_index"]))
    return sorted(gaps,key=score)[:max_gaps]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=DEFAULT_OUT)
    parser.add_argument("--max-gaps",type=int,default=10)
    parser.add_argument("--max-via-queries",type=int,default=30)
    parser.add_argument("--max-curbside-checks",type=int,default=0)
    parser.add_argument("--timeout",type=int,default=25)
    args=parser.parse_args()
    if not(1<=args.max_gaps<=73 and 0<=args.max_via_queries<=125 and 0<=args.max_curbside_checks<=125):
        raise ValueError("Invalid routing request limits")
    args.output.mkdir(parents=True,exist_ok=True)
    gaps,bykey,stops,geom=load_inputs()
    client=Client(os.environ.get("GRAPHHOPPER_URL",""),timeout=args.timeout)
    data,status=client.info()
    if status!="ok":
        raise SystemExit("GraphHopper /info failed ("+status+"); private server location is not printed")
    names=[x.get("name","") for x in (data.get("profiles") or []) if isinstance(x,dict)]
    if "bus" not in names:
        raise SystemExit("GraphHopper /info does not advertise the required bus profile. Available profile count: "+str(len(names)))
    chosen=pick_gaps(gaps,bykey,args.max_gaps)
    rows=[]
    diagnostics=[]
    geometry_features=[]
    curbside_calls=0
    via_calls=0
    for g in chosen:
        key=(g["trip_pattern_id"],g["gap_index"])
        a=stop_coords(stops[g["baseline_from_existing_stop_id"]])
        b=stop_coords(stops[g["baseline_to_existing_stop_id"]])
        reference=geom[key]
        ab,ab_status=client.route([a,b])
        ba,ba_status=client.route([b,a])
        base_distance=ab["distance_m"] if ab else None
        reverse_distance=ba["distance_m"] if ba else None
        off_reference=path_similarity(ab,reference) if ab else {}
        anchor_positions,anchor_points=constrained_anchor_points(reference)
        kmz_bus,kmz_bus_status=client.route([a]+anchor_points+[b])
        kmz_bus_metrics=path_similarity(kmz_bus,reference) if kmz_bus else {}
        kmz_distance=kmz_bus["distance_m"] if kmz_bus else None
        diag={
            "company":g["company"],"route_label":g["route_label"],
            "trip_pattern_id":g["trip_pattern_id"],"gap_index":g["gap_index"],
            "baseline_from_SIU_stop_id":g["baseline_from_existing_stop_id"],
            "baseline_to_SIU_stop_id":g["baseline_to_existing_stop_id"],
            "KMZ_gap_length_m":g["gap_length_m"],
            "GH_profile":"bus",
            "KMZ_interior_waypoints":len(anchor_points),
            "GH_constrained_bus_status":kmz_bus_status,
            "GH_constrained_bus_distance_m":kmz_distance if kmz_distance is not None else "",
            "GH_constrained_fraction_within_KMZ_50m":kmz_bus_metrics.get("fraction_GH_path_within_50m_KMZ",""),
            "GH_shortest_bus_distance_less_than_half_KMZ_length":"yes" if base_distance is not None
               and base_distance<float(g["gap_length_m"])*0.5 else "no_or_unknown",
            "GH_baseline_A_to_B_status":ab_status,
            "GH_reverse_B_to_A_status":ba_status,
            "GH_baseline_bus_distance_m":base_distance if base_distance is not None else "",
            "GH_reverse_bus_distance_m":reverse_distance if reverse_distance is not None else "",
            "GH_AB_vs_BA_distance_ratio":round(max(base_distance,reverse_distance)/min(base_distance,reverse_distance),3)
               if base_distance and reverse_distance else "",
            "possible_oneway_or_routing_asymmetry":"yes" if base_distance and reverse_distance
                and max(base_distance,reverse_distance)/min(base_distance,reverse_distance)>=1.20 else "no_or_unknown",
            "GH_baseline_fraction_within_KMZ_50m":off_reference.get("fraction_GH_path_within_50m_KMZ",""),
            "GH_baseline_p90_m_from_KMZ":off_reference.get("p90_distance_to_KMZ_corridor_m",""),
            "operator_stops_verified":"no",
            "bus_traffic_rules_confirmed_from_GH":"only_profile_vehicle_access_and_oneways",
            "GH_path_is_exact_official_KMZ_route":"no",
        }
        diagnostics.append(diag)
        if ab:
            geometry_features.append({
                "type":"Feature",
                "properties":{"company":g["company"],"route_label":g["route_label"],
                              "gap_index":g["gap_index"],"type":"GH_bus_shortest_A_to_B",
                              "GH_KMZ_coverage_50m":diag["GH_baseline_fraction_within_KMZ_50m"]},
                "geometry":{"type":"LineString","coordinates":ab["coordinates"]},
            })
        if kmz_bus:
            geometry_features.append({
                "type":"Feature",
                "properties":{"company":g["company"],"route_label":g["route_label"],
                              "gap_index":g["gap_index"],"type":"GH_bus_KMZ_anchor_constrained_A_to_B",
                              "GH_KMZ_coverage_50m":diag["GH_constrained_fraction_within_KMZ_50m"]},
                "geometry":{"type":"LineString","coordinates":kmz_bus["coordinates"]},
            })
        if ba:
            geometry_features.append({
                "type":"Feature",
                "properties":{"company":g["company"],"route_label":g["route_label"],
                              "gap_index":g["gap_index"],"type":"GH_bus_shortest_B_to_A"},
                "geometry":{"type":"LineString","coordinates":ba["coordinates"]},
            })
        for c in sorted(bykey.get(key,[]),key=lambda x:(float(x["global_shape_position_m"]),x["candidate_source_id"])):
            result={
                "company":g["company"],"route_label":g["route_label"],
                "trip_pattern_id":g["trip_pattern_id"],"gap_index":g["gap_index"],
                "candidate_id":c["candidate_source_id"],
                "physical_SIU_stop_id_if_known":c["physical_SIU_stop_id_if_known"],
                "candidate_kind":c["candidate_kind"],
                "original_KMZ_direction_assessment":c["original_KMZ_direction_assessment"],
                "gap_length_m":g["gap_length_m"],
                "distance_to_KMZ_m":c["distance_to_gap_shape_m"],
                "bus_route_baseline_m":base_distance if base_distance is not None else "",
                "bus_via_candidate_status":"",
                "bus_KMZ_constrained_via_candidate_status":"",
                "bus_KMZ_constrained_via_distance_m":"",
                "additional_distance_KMZ_constrained_via_m":"",
                "ratio_KMZ_constrained_via":"",
                "GH_constrained_via_fraction_within_KMZ_50m":"",
                "bus_via_candidate_distance_m":"",
                "additional_distance_via_candidate_m":"",
                "distance_ratio_via_vs_baseline":"",
                "GH_via_fraction_within_KMZ_50m":"",
                "GH_snapped_candidate_offset_m":"",
                "GH_right_curbside_status":"not_tested",
                "GraphHopper_profile":"bus",
                "direction_and_access_assessment":"pending_GH_result",
                "may_be_served_by_actual_operator":"unverified",
                "new_SIU_physical_stop_created":"no",
                "trip_stop_sequence_modified":"no",
            }
            if via_calls>=args.max_via_queries:
                result["bus_via_candidate_status"]="limit_not_queried"
                rows.append(result)
                continue
            via_calls+=1
            via,via_status=client.route([a,candidate_coords(c),b])
            result["bus_via_candidate_status"]=via_status
            relative_pos=max(0.,min(reference.length,float(c["global_shape_position_m"])-
                                      float(g["baseline_start_global_chainage_m"])))
            through_points=via_anchor_points(a,b,anchor_positions,anchor_points,
                                             candidate_coords(c),relative_pos)
            via_kmz,via_kmz_status=client.route(through_points)
            result["bus_KMZ_constrained_via_candidate_status"]=via_kmz_status
            if via_kmz:
                result["bus_KMZ_constrained_via_distance_m"]=via_kmz["distance_m"]
                result["GH_constrained_via_fraction_within_KMZ_50m"]=path_similarity(
                    via_kmz,reference)["fraction_GH_path_within_50m_KMZ"]
                if kmz_distance is not None:
                    result["additional_distance_KMZ_constrained_via_m"]=round(
                        via_kmz["distance_m"]-kmz_distance,1)
                    result["ratio_KMZ_constrained_via"]=round(via_kmz["distance_m"]/kmz_distance,3)
            if via:
                more=via["distance_m"]-base_distance if base_distance is not None else None
                ratio=via["distance_m"]/base_distance if base_distance else None
                result["bus_via_candidate_distance_m"]=via["distance_m"]
                result["additional_distance_via_candidate_m"]=round(more,1) if more is not None else ""
                result["distance_ratio_via_vs_baseline"]=round(ratio,3) if ratio is not None else ""
                result["GH_via_fraction_within_KMZ_50m"]=path_similarity(
                    via,reference)["fraction_GH_path_within_50m_KMZ"]
                snapped=via.get("snapped",[])
                if len(snapped)>=3:
                    lon,lat=snapped[1][:2]
                    target=candidate_coords(c)
                    snapped_distance=Point(*PROJECT.transform(float(lon),float(lat))).distance(
                        Point(*PROJECT.transform(*target)))
                    result["GH_snapped_candidate_offset_m"]=round(snapped_distance,1)
                if via_kmz and kmz_distance:
                    extra=via_kmz["distance_m"]-kmz_distance
                    fraction=float(result["GH_constrained_via_fraction_within_KMZ_50m"])
                    if fraction<0.5:
                        result["direction_and_access_assessment"]="constrained_bus_route_diverges_from_KMZ_review"
                    elif extra<=300 and via_kmz["distance_m"]/kmz_distance<=1.20:
                        result["direction_and_access_assessment"]="corridor_bus_via_candidate_small_detour_review"
                    else:
                        result["direction_and_access_assessment"]="corridor_bus_via_candidate_large_detour_review"
                else:
                    result["direction_and_access_assessment"]="KMZ_bus_constrained_query_failed_do_not_infer"
                if (curbside_calls<args.max_curbside_checks and
                    c["candidate_kind"]=="existing_physical_SIU_stop"):
                    curbside_calls+=1
                    side,side_status=client.route([a,candidate_coords(c),b],curbside=True)
                    result["GH_right_curbside_status"]="right_access_routable" if side else side_status
                    if side and base_distance is not None:
                        result["GH_right_curbside_distance_m"]=side["distance_m"]
                    # Curbside unsupported profiles result in HTTP400; do not
                    # claim wrong-side bus stop from unsupported routing feature.
            else:
                result["direction_and_access_assessment"]="direct_bus_via_failed_wait_for_constrained_review"
            if not via and via_kmz:
                result["direction_and_access_assessment"]="direct_bus_via_failed_but_KMZ_constrained_route_available_review"
            rows.append(result)
        # The directory includes only publicly sourced geometry+anonymous metrics,
        # not the configured private instance URL nor request credentials.
        print("gap="+g["company"]+"/"+g["route_label"]+"#"+str(g["gap_index"])+
              " baseline="+ab_status+" reverse="+ba_status+
              " candidates="+str(len(bykey.get(key,[]))),flush=True)
    write_csv(args.output/"bus_route_gap_direction_checks.csv",diagnostics,list(diagnostics[0]))
    write_csv(args.output/"bus_candidate_access_and_oneway_review.csv",rows,
              ["company","route_label","trip_pattern_id","gap_index","candidate_id",
               "physical_SIU_stop_id_if_known","candidate_kind",
               "original_KMZ_direction_assessment","gap_length_m","distance_to_KMZ_m",
               "bus_route_baseline_m","bus_via_candidate_status","bus_via_candidate_distance_m",
               "bus_KMZ_constrained_via_candidate_status","bus_KMZ_constrained_via_distance_m",
               "additional_distance_KMZ_constrained_via_m","ratio_KMZ_constrained_via",
               "GH_constrained_via_fraction_within_KMZ_50m",
               "additional_distance_via_candidate_m","distance_ratio_via_vs_baseline",
               "GH_via_fraction_within_KMZ_50m","GH_snapped_candidate_offset_m",
               "GH_right_curbside_status","GH_right_curbside_distance_m","GraphHopper_profile",
               "direction_and_access_assessment","may_be_served_by_actual_operator",
               "new_SIU_physical_stop_created","trip_stop_sequence_modified"])
    (args.output/"GraphHopper_bus_paths_for_KMZ_comparison.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":geometry_features},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    statuses=Counter(x["bus_via_candidate_status"] for x in rows)
    summary={
        "GraphHopper_connection":"responded_to_info",
        "required_profile":"bus","bus_profile_present":True,
        "version_reported":str(data.get("version",""))[:64],
        "OSM_import_date_reported":str(data.get("import_date",""))[:64],
        "private_GraphHopper_URL_exported_to_research_files":False,
        "public_GraphHopper_API_docs":"https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md",
        "input_gap_count":len(gaps),"input_candidate_links":sum(len(x) for x in bykey.values()),
        "gap_bus_routes_tested":len(chosen),"bus_baseline_success":sum(x["GH_baseline_A_to_B_status"]=="ok" for x in diagnostics),
        "bus_reverse_success":sum(x["GH_reverse_B_to_A_status"]=="ok" for x in diagnostics),
        "KMZ_anchor_constrained_bus_success":sum(x["GH_constrained_bus_status"]=="ok" for x in diagnostics),
        "direct_bus_shortcuts_under_half_KMZ_distance":sum(x["GH_shortest_bus_distance_less_than_half_KMZ_length"]=="yes" for x in diagnostics),
        "gaps_with_observed_bus_directional_asymmetry":sum(x["possible_oneway_or_routing_asymmetry"]=="yes" for x in diagnostics),
        "candidates_in_tested_gaps":len(rows),
        "bus_via_queries_attempted":via_calls,
        "bus_via_status_counts":dict(statuses),
        "curbside_queries_attempted":curbside_calls,
        "KMZ_constrained_via_candidate_success":sum(x["bus_KMZ_constrained_via_candidate_status"]=="ok" for x in rows),
        "successful_right_curbside_tests":sum(x["GH_right_curbside_status"]=="right_access_routable" for x in rows),
        "total_route_queries":client.route_queries,
        "total_info_queries":client.info_queries,
        "GTFS_stops_created":0,
        "GTFS_trip_sequences_modified":False,
        "new_OSM_queries":0,
        "route_operator_boarding_proven":False,
    }
    (args.output/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Busprofiel GraphHopper: wegrichting en bereikbaarheid voor SIU-haltegaten","",
           "**Gebruikt uitsluitend ColombiaTransit organisatievariabele GRAPHHOPPER_URL.** "
           "Geen privé-adres, token of querystring wordt door het Python-script geprint of opgeslagen. "
           "GitHub organisatievariabelen zijn geen geheimen: gebruik een Organization Secret als het adres zelf vertrouwelijk moet blijven.","",
           "De test vergelijkt de kortste busroute met een via KMZ-tussenpunten begrensde busroute om "
           "te voorkomen dat een korte weg een officieel omwegtraject overslaat. "
           "De test is uitsluitend onderzoek naar bus-toegankelijke wegtrajecten, rijrichtingsasymmetrie "
           "en de omweg bij rijden via een bestaande SIU-/OSM-haltekandidaat. "
           "Een route kan een juridisch andere corridor volgen dan de kortste GraphHopper-busroute. "
           "Curbside werkt alleen bij edge-based turn-cost routing en een ondersteund busprofiel.","",
           "## Resultaat",""]
    for k,v in summary.items():
        if k not in ("private_GraphHopper_URL_exported_to_research_files","public_GraphHopper_API_docs"):
            if isinstance(v,(int,str)):
                lines.append("- "+k+": **"+str(v)+"**")
    lines+=["","## Bestanden","",
            "- bus_route_gap_direction_checks.csv — kortste A→B/B→A en KMZ-tussenpunt-begrensde busroute, met shortcut-status",
            "- bus_candidate_access_and_oneway_review.csv — kortste en KMZ-begrensde routes via halte-kandidaat; haltebediening onbevestigd",
            "- GraphHopper_bus_paths_for_KMZ_comparison.geojson — gegenereerde busweg-geometrie voor vergelijking met officiële bronlijnen",
            "",
            "## Bronnen en vervolg","",
            "- Publieke API-referentie: https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md",
            "- De private runtime-URL staat alleen in de ColombiaTransit GitHub Actions-organisatievariabele.",
            "- Niet automatisch toevoegen of verwijderen: busroute en curbside kunnen afwijken van exacte AMB-shape; aanvullende operator-/haltevalidatie nodig.",
            "- In een vervolgactie kan dezelfde workflow voor 73 gaten en 125 kandidaten volledig worden uitgevoerd.",
            ""]
    (args.output/"summary.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
