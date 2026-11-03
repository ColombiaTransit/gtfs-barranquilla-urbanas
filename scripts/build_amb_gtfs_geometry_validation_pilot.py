#!/usr/bin/env python3
"""Build a STRICTLY NON-PUBLICATION GTFS Schedule QA ZIP for Barranquilla.

Sources: existing 97 AMB routes + agencies, v3 cleaned SIU stop visit order,
and concatenated (and explicitly QA-flagged) GraphHopper bus road candidates.

No real trip boundaries or schedules are claimed. One representative DEMO trip
per eligible provisional source shape is created solely to validate GTFS
structure. Synthetic weekday calendar and deterministic demo times are clearly
marked. Missing route_id mappings are excluded, never synthesized.

Never writes gtfs/*. No network calls. Run MobilityData independently on zip.
"""
from __future__ import annotations
import csv
import json
import math
import zipfile
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/amb-gtfs-mobilitydata-PILOT-NOT-PUBLISHABLE"
GTFS=ROOT/"gtfs"
STAGING=ROOT/"sources/amb/provisional_trip_stop_order_v3_clean"
PATTERN_PATH=ROOT/"sources/amb/missing_siu_trip_stop_patterns/trip_patterns_MISSING_SIU_NO_TIMES.csv"
ROAD=ROOT/"sources/amb/GH_combined_bus_road_geometry"
STOP_PATH=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
FEED_DIR=OUT/"gtfs_demo"
GEOD=Geod(ellps="WGS84")
DEMO_SERVICE="AMB_DEMO_WEEKDAYS_NOT_REAL"
DEMO_START=date(2026,11,9)
DEMO_END=date(2026,12,11)
DEMO_SPEED_M_S=5.0
DEMO_DWELL_SEC=20

def read(path):
    with path.open("r",newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def fmt_sec(t):
    return f"{t//3600:02d}:{(t//60)%60:02d}:{t%60:02d}"

def distance_m(a,b):
    lon1,lat1=a[:2]
    lon2,lat2=b[:2]
    return abs(GEOD.inv(lon1,lat1,lon2,lat2)[2])

def build_shapes(road_features):
    bypattern=defaultdict(dict)
    for f in road_features:
        prop=f["properties"]
        uid=prop["trip_pattern_id"]
        n=int(prop["section"])
        if n in bypattern[uid]:raise ValueError("Duplicate GH shape section")
        coords=f["geometry"]["coordinates"]
        if f["geometry"]["type"]!="LineString" or len(coords)<2:
            raise ValueError("Expected GH LineString")
        bypattern[uid][n]=coords
    accum={}
    stats={}
    for uid,sections in bypattern.items():
        expected=list(range(1,max(sections)+1))
        if sorted(sections)!=expected:
            raise ValueError("Missing GH section number for "+uid)
        points=[]
        spans={}
        connectors=[]
        previous=None
        running=0.
        for number in expected:
            coords=sections[number]
            length=0.
            section_start=running
            for j,raw in enumerate(coords):
                pos=(float(raw[0]),float(raw[1]))
                if not (-76<pos[0]<-73 and 9<pos[1]<12):
                    raise ValueError("Road shape coordinate outside Barranquilla project limits")
                if previous is not None:
                    step=distance_m(previous,pos)
                    if j==0:
                        connectors.append(step)
                    if step<0.15:
                        continue
                    running+=step
                    length+=step
                points.append((pos[0],pos[1],running))
                previous=pos
            if running<=section_start+0.15:
                raise ValueError("No measurable distance in section for "+uid)
            spans[number]=(section_start,running)
        if len(points)<2:raise ValueError("Shape has too few points")
        accum[uid]={"points":points,"spans":spans,"distance_m":running}
        stats[uid]={
            "GH_shape_total_distance_m":round(running,1),
            "GH_sequential_section_count":len(expected),
            "GH_section_connector_max_gap_m":round(max(connectors,default=0),1),
            "GH_section_connectors_above_100m":sum(x>100 for x in connectors),
            "GH_road_geometry_point_count":len(points),
        }
    return accum,stats

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    FEED_DIR.mkdir(parents=True,exist_ok=True)
    routes=read(GTFS/"routes.txt")
    agencies=read(GTFS/"agency.txt")
    patterns=read(PATTERN_PATH)
    stops=read(STOP_PATH)
    visits=read(STAGING/"candidate_trip_stop_sequences_v3_CLEAN_NO_TIMES_NOT_GTFS.csv")
    qa=read(ROAD/"GH_full_route_bus_segment_alignment.csv")
    roads=json.loads((ROAD/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").read_text(encoding="utf-8"))
    if len(routes)!=97 or len(visits)!=9020 or len(roads["features"])!=352:
        raise ValueError("Source feed scope changed; review before creating a new validation pilot")
    stopid={s["stop_id"]:s for s in stops}
    agency_by_id={a["agency_id"]:a for a in agencies}
    route_by_pair=defaultdict(list)
    for r in routes:
        route_by_pair[(r["agency_id"],r["route_short_name"])].append(r)
    shapes,shape_stats=build_shapes(roads["features"])
    pattern_by_id={p["trip_pattern_id"]:p for p in patterns}
    bytrip=defaultdict(list)
    for v in visits:
        bytrip[v["trip_pattern_id"]].append(v)
        if v["stop_id"] not in stopid:
            raise ValueError("Candidate visit refers to a missing SIU physical stop_id")
    grouped_sections=defaultdict(list)
    for row in qa:
        grouped_sections[row["trip_pattern_id"]].append(row)
    lookup=[]
    eligible=[]
    missing_routes=[]
    for uid,part in sorted(bytrip.items()):
        p=pattern_by_id.get(uid)
        if not p or uid not in shapes:
            raise ValueError("Source manifest or GH road for trip pattern missing: "+uid)
        agency_id="AMB_"+p["company"].replace("-","_").replace(" ","_")
        selected=route_by_pair.get((agency_id,p["official_route_label"]),[])
        if len(selected)!=1:
            reason="missing_route_in_existing_gtfs_routes" if not selected else "ambiguous_existing_route_id"
            missing_routes.append({"trip_pattern_id":uid,
                                   "company":p["company"],"route_label":p["official_route_label"],
                                   "route_id_proposed_base":p["route_id_proposed_base"],
                                   "status":reason,
                                   "synthetic_route_id_created":"no"})
            lookup.append({"trip_pattern_id":uid,"route_short_name":p["official_route_label"],
                           "company":p["company"],"route_id":"","mapping_status":reason,
                           "source_route_id_proposed":p["route_id_proposed_base"]})
            continue
        route=selected[0]
        if route["agency_id"] not in agency_by_id:
            raise ValueError("Route references missing agency")
        lookup.append({"trip_pattern_id":uid,"route_short_name":p["official_route_label"],
                       "company":p["company"],"route_id":route["route_id"],
                       "mapping_status":"exact_agency_and_route_short_name",
                       "source_route_id_proposed":p["route_id_proposed_base"]})
        part.sort(key=lambda x:int(x["stop_sequence"]))
        if [int(x["stop_sequence"]) for x in part]!=list(range(1,len(part)+1)):
            raise ValueError("Non-contiguous existing v3 stop order")
        eligible.append((uid,p,route,part))
    if len(bytrip)!=70 or len(eligible)+len(missing_routes)!=70:
        raise ValueError("Unexpected routing coverage in GTFS pilot")
    if len(missing_routes)!=3:
        raise ValueError("Route crosswalk exclusions differ from expected source PT2 patterns")

    route_ids={r["route_id"] for uid,p,r,v in eligible}
    used_routes=[r for r in routes if r["route_id"] in route_ids]
    used_agencies=[a for a in agencies if a["agency_id"] in {r["agency_id"] for r in used_routes}]
    used_stop_ids={v["stop_id"] for uid,p,r,part in eligible for v in part}
    used_stops=[{
        "stop_id":s["stop_id"],
        "stop_name":s["stop_name"] or ("SIU "+s["stop_id"][:12]),
        "stop_lat":f"{float(s['stop_lat']):.7f}",
        "stop_lon":f"{float(s['stop_lon']):.7f}",
        "location_type":"0",
    } for s in stops if s["stop_id"] in used_stop_ids]

    lines=[]
    trips=[]
    times=[]
    mapping=[]
    issues=[]
    included_count=0
    for uid,p,route,part in eligible:
        geo=shapes[uid]
        shape_id="GH_QA_"+uid
        for seq,(lon,lat,d) in enumerate(geo["points"],1):
            lines.append({
                "shape_id":shape_id,"shape_pt_lat":f"{lat:.7f}",
                "shape_pt_lon":f"{lon:.7f}","shape_pt_sequence":str(seq),
                "shape_dist_traveled":f"{d/1000:.3f}"
            })
        trip_id="QA_"+uid
        trips.append({
            "route_id":route["route_id"],"service_id":DEMO_SERVICE,
            "trip_id":trip_id,"shape_id":shape_id,
        })
        sregions=sorted(grouped_sections[uid],key=lambda x:int(x["segment_number"]))
        if len(sregions)!=len(geo["spans"]):
            raise ValueError("Source KMZ region / GH road region mismatch")
        ranges={int(x["segment_number"]):(float(x["KMZ_segment_start_m"]),float(x["KMZ_segment_end_m"])) for x in sregions}
        start_time=7*3600
        previous_dist=None
        previous_time=None
        prev_rounded=-1.
        for i,visit in enumerate(part,1):
            src_dist=float(visit["shape_dist_traveled_candidate_m"])
            seg=next((k for k,(a,b) in sorted(ranges.items()) if src_dist<=b+0.01),max(ranges))
            kmz_start,kmz_end=ranges[seg]
            road_start,road_end=geo["spans"][seg]
            frac=max(0.,min(1.,(src_dist-kmz_start)/max(kmz_end-kmz_start,1.)))
            projected=road_start+frac*(road_end-road_start)
            # Ensure 3-decimal km rounding is non-decreasing, without
            # manufacturing extra distances beyond the GH road shape.
            rounded=max(prev_rounded,round(projected/1000,3))
            rounded=min(rounded,round(geo["distance_m"]/1000,3))
            if previous_dist is None:
                tm=start_time
            else:
                delta=max(0.,projected-previous_dist)
                # Time is demonstrably fictional, strictly QA-only: generic
                # 18km/h + 20s stop activity. NO real service schedule claim.
                tm=previous_time+max(30,math.ceil(delta/DEMO_SPEED_M_S)+DEMO_DWELL_SEC)
            times.append({
                "trip_id":trip_id,"arrival_time":fmt_sec(tm),
                "departure_time":fmt_sec(tm),"stop_id":visit["stop_id"],
                "stop_sequence":str(i),
            })
            previous_time=tm
            previous_dist=projected
            prev_rounded=rounded
        included_count+=len(part)
        bad_sections=[q for q in sregions if q["road_geometry_candidate_status"]!="candidate_consistent_with_KMZ"]
        if bad_sections:
            issues.append({"trip_pattern_id":uid,"route_id":route["route_id"],
                           "issue":"GH_road_not_aligned_with_source_KMZ",
                           "count":len(bad_sections)})
        if shape_stats[uid]["GH_section_connector_max_gap_m"]>100:
            issues.append({"trip_pattern_id":uid,"route_id":route["route_id"],
                           "issue":"GH_road_sections_have_long_connectors",
                           "count":shape_stats[uid]["GH_section_connectors_above_100m"]})
        mapping.append({
            "trip_pattern_id":uid,"route_id":route["route_id"],
            "trip_id":trip_id,"shape_id":shape_id,
            "source_geometry":p["source_geometry"],
            "source_variant":p["official_route_label"],
            "stop_visit_count":len(part),
            **shape_stats[uid],
            "GTFS_demo_times_only":"yes",
            "source_route_legally_confirmed":"no",
            "source_stop_service_confirmed":"no",
        })

    if included_count!=len(times) or len(times)!=sum(len(part) for uid,p,r,part in eligible):
        raise ValueError("Missing stop_times records")
    if not trips or not lines or not used_stops:
        raise ValueError("Empty feed prevented")
    if any(x["stop_id"] not in used_stop_ids for x in times):
        raise ValueError("Invalid stop-times foreign key")
    if {t["route_id"] for t in trips}!={r["route_id"] for r in used_routes}:
        raise ValueError("Unused or unresolved route was included")
    if {t["shape_id"] for t in trips}!={m["shape_id"] for m in mapping}:
        raise ValueError("Missing shape for a QA trip")
    for f in FEED_DIR.glob("*.txt"):
        f.unlink()
    write(FEED_DIR/"agency.txt",used_agencies,
          ["agency_id","agency_name","agency_url","agency_timezone","agency_lang"])
    write(FEED_DIR/"routes.txt",used_routes,
          ["route_id","agency_id","route_short_name","route_long_name","route_type"])
    write(FEED_DIR/"stops.txt",used_stops,
          ["stop_id","stop_name","stop_lat","stop_lon","location_type"])
    write(FEED_DIR/"trips.txt",trips,
          ["route_id","service_id","trip_id","shape_id"])
    write(FEED_DIR/"stop_times.txt",times,
          ["trip_id","arrival_time","departure_time","stop_id","stop_sequence"])
    write(FEED_DIR/"shapes.txt",lines,
          ["shape_id","shape_pt_lat","shape_pt_lon","shape_pt_sequence","shape_dist_traveled"])
    write(FEED_DIR/"calendar.txt",[{
        "service_id":DEMO_SERVICE,
        "monday":"1","tuesday":"1","wednesday":"1","thursday":"1","friday":"1",
        "saturday":"0","sunday":"0",
        "start_date":DEMO_START.strftime("%Y%m%d"),
        "end_date":DEMO_END.strftime("%Y%m%d"),
    }],["service_id","monday","tuesday","wednesday","thursday","friday",
        "saturday","sunday","start_date","end_date"])
    # Monday-Friday QA service is only a validation fixture, not an AMB timetable.
    path=OUT/"barranquilla_geometry_ONLY_TEST_NOT_FOR_PUBLICATION.zip"
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for file in sorted(FEED_DIR.glob("*.txt")):
            z.write(file,arcname=file.name)
    write(OUT/"pattern_to_real_gtfs_route_crosswalk.csv",
          lookup,list(lookup[0]))
    write(OUT/"excluded_patterns_missing_real_route_id.csv",
          missing_routes,list(missing_routes[0]))
    write(OUT/"trial_trip_and_shape_provenance.csv",mapping,list(mapping[0]))
    if issues:write(OUT/"road_and_shape_gaps_unverified.csv",issues,list(issues[0]))
    summary={
        "purpose":"GTFS geometry/schema validation fixture only; NEVER publish",
        "existing_amb_routes_total":len(routes),
        "source_route_patterns_with_stop_sequences":len(bytrip),
        "demonstration_patterns_included":len(eligible),
        "patterns_excluded_without_real_route_id":len(missing_routes),
        "A_B_variant_route_ids_fixed_using_existing_routes_txt":sum(
            bool(x["route_id"]) and x["route_id"]!=x["source_route_id_proposed"] for x in lookup),
        "GTFS_agencies":len(used_agencies),
        "GTFS_routes":len(used_routes),
        "GTFS_stops":len(used_stops),
        "GTFS_demo_trips":len(trips),
        "GTFS_demo_stop_times":len(times),
        "GTFS_shapes":len(mapping),
        "GTFS_shape_points":len(lines),
        "GH_road_segments_total_available":352,
        "GH_road_aligned_segments_total_available":331,
        "GH_unresolved_segment_count_total_available":21,
        "source_GTFS_visit_count":len(visits),
        "excluded_visitor_count_due_to_missing_route_id":len(visits)-included_count,
        "synthetic_calendar":DEMO_SERVICE,
        "synthetic_calendar_start":str(DEMO_START),
        "synthetic_calendar_end":str(DEMO_END),
        "synthetic_trip_start_local":"07:00:00",
        "synthetic_cruise_speed_km_h":DEMO_SPEED_M_S*3.6,
        "synthetic_minimum_leg_seconds":30,
        "synthetic_dwell_seconds":DEMO_DWELL_SEC,
        "actual_trip_directions_or_terminals_proven":False,
        "actual_stop_service_proven":False,
        "real_arrival_and_departure_times":False,
        "production_gtfs_changed":False,
        "zip_name":path.name,
    }
    (OUT/"build_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    doc=["# Barranquilla GTFS proefbuild — uitsluitend schema/shape-validatie",
         "",
         "**WAARSCHUWING: FICTIONELE RITTEN EN TIJDEN, NIET PUBLICEREN.**",
         "Elke opgenomen voorlopige KMZ/ArcGIS component heeft één kunstmatige",
         "QA-rit van 07:00, een voorbeeldkalender op werkdagen 9 november–11 december",
         "2026 en een theoretisch reistijdmodel (18 km/h + stop-pauze).",
         "Dit is NIET de AMB-dienstregeling. Richting, begin/eindpunten en stopbediening",
         "zijn NIET uit juridische exploitatiegegevens bevestigd.",
         "",
         "## Aantallen",""]
    for k,v in summary.items():
        if type(v) in (int,float):
            doc.append("- "+k+": **"+str(v)+"**")
    doc+=["",
          "## Technische methode","",
          "- shapes.txt: wegenvolgende GH-buswegsegementen in KMZ-volgorde; 21 bronafwijkingen blijven gemarkeerd.",
          "- stop_times.shape_dist_traveled bewust weggelaten: de huidige relatieve KMZ-/GraphHopper-projectie is niet precies genoeg voor een correcte per-halte wegafstand. shapes.txt bevat wel echte GH-wegafstanden.",
          "- Werkelijke route_id: exacte combinatie agency_id en route_short_name uit bestaande gtfs/routes.txt; geen nieuwe fictieve routes.",
          "- COOLITORAL PT2 niet opgenomen omdat de bestaande gtfs/routes.txt geen overeenkomende officiële route_id heeft.",
          "- Onbevestigde SIU-haltebediening en bron-A/B-routeprovenance blijven QA-risico.",
          "- De GTFS ZIP is uitsluitend een GitHub Actions artifact, niet een publicatiefeed.",
          "",
          "## Validator","",
          "MobilityData GTFS Schedule validator CLI 8.0.1 (https://github.com/MobilityData/gtfs-validator).",
          "De HTML/JSON-validatorrapporten worden bij de proefbuild als artifacts opgeslagen.",
          ""]
    (OUT/"README_NOT_FOR_PUBLICATION.md").write_text("\n".join(doc),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
