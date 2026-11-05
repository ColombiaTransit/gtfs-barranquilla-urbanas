#!/usr/bin/env python3
"""Deep research and *guarded* alternative GH bus shapes for the seven >250m stops.

The actual 7 validator warnings have SIU stops <=7.2m from 2026 official AMB
KMZ but >250m from the latest GH bus road. Earlier 240m rerouting corrected
their positions but added out-of-order notices. Here we check two DIFFERENT
source waypoint densities per affected segment, one at a time, with the actual
MobilityData 8.0.1 validator on the entire 67-shape demo GTFS.

Keep only candidates that:
- follow the source KMZ road corridor and don't worsen other stops in segment;
- reduce the route's real MobilityData far-from-shape notices;
- demonstrably remove >=1 of the SEVEN targeted stop notices;
- add NO new route stop-order notices or specification ERROR;
- leave the canonical SIU catalog, source stop_sequence, GTFS production alone.

When a road candidate fails these checks, retain the previous shape and issue
a precise source-vs-GH route QA note rather than drawing a fake shortcut.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import LineString, Point
from shapely.ops import substring

from audit_amb_full_route_graphhopper_bus_geometry import (
    ROOT, PATTERNS, TO_METERS, TO_WGS, load_geometries, coverage
)
from query_graphhopper_bus_gap_directions import Client
from retry_amb_mobilitydata_stop_shape_warnings import reroute_section, as_line
from guard_amb_gh_shape_fixes_against_validator_order import occurrences, grouped

ROOTDIR=ROOT
BASE=ROOT/"sources/amb/GTFS_shape_validator_recheck"
GH_SECTIONS=ROOT/"sources/amb/GH_combined_bus_road_geometry/GH_full_route_bus_segment_alignment.csv"
SIU=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"
SEVEN=BASE/"67_remaining_stop_vs_shape_source_evidence.csv"
OUT=ROOT/"build/amb-seven-P1-GH-shape-investigation"
PILOT_GENERATOR=ROOT/"archive/research_2026/scripts/build_amb_gtfs_geometry_validation_pilot.py"

def read_csv(path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def save(path,items):
    if not items:return
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]),extrasaction="ignore")
        w.writeheader()
        w.writerows(items)

def ident(f):
    p=f["properties"]
    return p["trip_pattern_id"],int(p["section"])

def road_geom(mapping,uid):
    rows=sorted((k,f) for k,f in mapping.items() if k[0]==uid)
    pts=[]
    for _,f in rows:
        pts.extend(as_line(f).coords)
    return LineString(pts)

def validator_trial(mapping,uid,jar,folder):
    work=folder/"roads"
    work.mkdir()
    collection={"type":"FeatureCollection","features":list(mapping.values())}
    (work/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").write_text(
        json.dumps(collection,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    shutil.copy2(GH_SECTIONS,work/"GH_full_route_bus_segment_alignment.csv")
    output=folder/"pilot"
    generated=subprocess.run(
        [sys.executable,str(PILOT_GENERATOR),"--road-dir",str(work),"--out",str(output)],
        cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=75
    )
    if generated.returncode!=0:
        raise RuntimeError("GTFS fixture could not be generated: "+generated.stderr[-350:])
    reportdir=output/"validator"
    v=subprocess.run(
        ["java","-Xmx3g","-jar",str(jar),"-i",
         str(output/"barranquilla_geometry_ONLY_TEST_NOT_FOR_PUBLICATION.zip"),
         "-o",str(reportdir),"-c","co","-t","2"],
        cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=95
    )
    if v.returncode!=0 or not (reportdir/"report.json").is_file():
        raise RuntimeError("Actual MobilityData validator did not return a JSON report")
    rep=json.loads((reportdir/"report.json").read_text(encoding="utf-8"))
    errors=sum(int(g["totalNotices"]) for g in rep["notices"] if g["severity"]=="ERROR")
    # Exact stop id checks, not merely a change in total warning count.
    far_ids={(x["tripId"].removeprefix("QA_"),x["stopId"]) for x in
             occurrences(rep,"stop_too_far_from_shape")}
    return {
        "errors":errors,
        "far_count_by_route":grouped(rep,"stop_too_far_from_shape"),
        "order_count_by_route":grouped(rep,"stops_match_shape_out_of_order"),
        "far_ids":far_ids,
        "report":rep,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--jar",type=Path,required=True)
    p.add_argument("--out",type=Path,default=OUT)
    p.add_argument("--max-trials",type=int,default=14)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    evidence=read_csv(SEVEN)
    flagged=[e for e in evidence if float(e["validator_distance_to_final_GH_shape_m"])>250]
    flagged.sort(key=lambda e:-float(e["validator_distance_to_final_GH_shape_m"]))
    if len(flagged)!=7 or len({e["physical_SIU_stop_id"] for e in flagged})!=7:
        raise ValueError("Expected precisely seven distinct SIU physical stop IDs >250m")
    if any(float(e["nearest_source_KMZ_distance_m"])>15
           or e["source_geometry"]!="AMB_KMZ_2026" for e in flagged):
        raise ValueError("These seven do not all closely follow 2026 official KMZ source")
    original_records=read_csv(GH_SECTIONS)
    segments={(r["trip_pattern_id"],int(r["segment_number"])):r for r in original_records}
    manifest={r["trip_pattern_id"]:r for r in read_csv(PATTERNS)}
    shape_sources,_=load_geometries(manifest)
    siu={s["stop_id"]:s for s in read_csv(SIU)}
    raw=json.loads((BASE/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").read_text(encoding="utf-8"))
    accepted={ident(f):f for f in raw["features"]}
    if len(accepted)!=352 or set(accepted)!=set(segments):
        raise ValueError("Expected 352 GH source road sections")
    # Most recent real validator report was the ORDER-GUARDED full pilot.
    # Instead of relying on inaccessible action artifacts, rebuild and validate
    # exact current baseline once here.
    with tempfile.TemporaryDirectory(prefix="baseline-seven-",dir=args.out) as d:
        base_validation=validator_trial(accepted,"",args.jar,Path(d))
    if base_validation["errors"]!=0:
        raise ValueError("Current GH seven-stop baseline already has GTFS errors")
    current_far=Counter(base_validation["far_count_by_route"])
    current_order=Counter(base_validation["order_count_by_route"])
    current_far_ids=set(base_validation["far_ids"])
    selected_ids={(e["trip_pattern_id"],e["physical_SIU_stop_id"]) for e in flagged}
    if not selected_ids.issubset(base_validation["far_ids"]):
        raise ValueError("Seven source P1 flags no longer present in actual validator baseline")
    orig_far={k:current_far[k] for k in {e["trip_pattern_id"] for e in flagged}}
    orig_order={k:current_order[k] for k in orig_far}
    grouped_rows=defaultdict(list)
    stops_by_route=defaultdict(list)
    for s in flagged:
        uid=s["trip_pattern_id"]
        position=float(s["original_shape_chainage_candidates_m"].split(";")[0])
        seg_candidates=[int(k[1]) for k,r in segments.items()
                        if k[0]==uid and
                        float(r["KMZ_segment_start_m"])-.1<=position<=float(r["KMZ_segment_end_m"])+.1]
        if len(seg_candidates)!=1:
            raise ValueError("Ambiguous source KMZ section for "+uid+"/"+s["physical_SIU_stop_id"])
        key=(uid,seg_candidates[0])
        grouped_rows[key].append(s)
        stops_by_route[uid].append(s)
    if len(grouped_rows)!=6:
        raise ValueError("Seven source warnings should map to six GH road sections")
    # Include all existing candidate source stop visits; one source stop placed
    # 350m off the road can be a symptom of an GH shortcut affecting other stops.
    visits=read_csv(ROOT/"sources/amb/provisional_trip_stop_order_v3_clean/candidate_trip_stop_sequences_v3_CLEAN_NO_TIMES_NOT_GTFS.csv")
    bysection=defaultdict(list)
    for v in visits:
        uid=v["trip_pattern_id"]
        chain=float(v["shape_dist_traveled_candidate_m"])
        matches=[(k,r) for k,r in segments.items() if k[0]==uid and
                 float(r["KMZ_segment_start_m"])-.1<=chain<=float(r["KMZ_segment_end_m"])+.1]
        if matches:
            k=sorted(matches,key=lambda x:x[0][1])[0][0]
            bysection[k].append(v)
    case_records=[]
    checks=[]
    road_features=[]
    selected_repaired=set()
    trials=0
    client=Client(os.environ.get("GRAPHHOPPER_URL",""),timeout=30)
    info,status=client.info()
    if status!="ok" or "bus" not in [
        x.get("name") for x in info.get("profiles",[]) if isinstance(x,dict)]:
        raise RuntimeError("Private ColombiaTransit GraphHopper bus profile unavailable")
    # Prioritize the clusters with two affected SIU stops.
    targets=sorted(grouped_rows,key=lambda k:(-len(grouped_rows[k]),k))
    for key in targets:
        uid,segno=key
        seg=segments[key]
        m=manifest[uid]
        source_id=(m["company"],m["official_route_label"],m["geometry_component"])
        source=shape_sources[source_id]
        piece=substring(source,float(seg["KMZ_segment_start_m"]),
                       float(seg["KMZ_segment_end_m"]))
        original_road=as_line(accepted[key])
        vis=bysection[key]
        local_points=[
            Point(*TO_METERS.transform(float(siu[v["stop_id"]]["stop_lon"]),
                                       float(siu[v["stop_id"]]["stop_lat"]))) for v in vis]
        oldoffsets=[pt.distance(original_road) for pt in local_points]
        for e in grouped_rows[key]:
            case_records.append({
                "company":e["company"],"route_label":e["route_label"],
                "trip_pattern_id":uid,"GH_section_number":segno,
                "physical_SIU_stop_id":e["physical_SIU_stop_id"],
                "stop_name":e["physical_stop_name"],
                "longitude":e["longitude"],"latitude":e["latitude"],
                "original_validator_GH_distance_m":e["validator_distance_to_final_GH_shape_m"],
                "official_KMZ_distance_m":e["nearest_source_KMZ_distance_m"],
                "original_KMZ_chainage_m":e["original_shape_chainage_candidates_m"],
                "original_stop_sequence":e["original_concept_stop_sequences"],
                "case_diagnosis":"GH_bus_road_shortcut_or_road_graph_vs_official_KMZ_conflict",
                "SIU_point_error_proven":"no",
                "legal_2026_operator_stop_service_proven":"no",
                "current_research_status":"pending_exact_MobilityData_probe",
            })
        for spacing,sub_km in [(375,1.9),(550,2.2)]:
            if trials>=args.max_trials:break
            proposed,route_status,sub_count=reroute_section(client,piece,
                            subsection_km=sub_km,spacing_m=spacing)
            if proposed is None:
                checks.append({
                    "trip_pattern_id":uid,"GH_section_number":segno,
                    "target_count":len(grouped_rows[key]),
                    "GH_spacing_m":spacing,"GH_subsegment_km":sub_km,
                    "GH_route_status":route_status,"GH_queries_in_section":sub_count,
                    "KMZ_bidirectional_coverage_min":"","GH_road_distance_ratio":"",
                    "source_stops_far_over_100_before":sum(x>100 for x in oldoffsets),
                    "source_stops_far_over_100_after":"",
                    "newly_broken_100m_source_stops":"",
                    "relevant_7_stops_resolved_by_real_validator":"",
                    "MobilityData_errors":"","MobilityData_distance_warnings_for_route":"",
                    "MobilityData_order_warnings_for_route":"",
                    "candidate_accepted":"no","decision":"GraphHopper_route_unavailable"
                })
                continue
            newoffsets=[pt.distance(proposed) for pt in local_points]
            bad=sum(a<=100 and b>100 for a,b in zip(oldoffsets,newoffsets))
            before_count=sum(a>100 for a in oldoffsets)
            after_count=sum(b>100 for b in newoffsets)
            cover=coverage(piece,proposed)
            similarity=min(cover["source_near_road"],cover["road_near_source"])
            ratio=proposed.length/piece.length
            ends=max(Point(piece.coords[0]).distance(proposed),
                     Point(piece.coords[-1]).distance(proposed))
            # Never force waypoints directly to unconfirmed curbside SIU stops.
            geo_plausible=(bad==0 and after_count<before_count and
                           similarity>=.68 and .65<=ratio<=1.9 and ends<=60)
            real=None
            decision="no_local_geometry_improvement"
            if geo_plausible:
                trials+=1
                updated={
                    "type":"Feature",
                    "properties":{**accepted[key]["properties"],
                        "road_candidate_source":"P1_seven_MobilityData_cautious_KMZ_waypoints",
                        "real_2026_bus_operator_service_verified":False,
                        "research_not_published":True},
                    "geometry":{"type":"LineString",
                                "coordinates":[[round(lon,7),round(lat,7)] for lon,lat
                                    in (TO_WGS.transform(*xy) for xy in proposed.coords)]},
                }
                before=accepted[key]
                accepted[key]=updated
                with tempfile.TemporaryDirectory(prefix="sevenGH-probe-",dir=args.out) as d:
                    try:
                        real=validator_trial(accepted,uid,args.jar,Path(d))
                    except (RuntimeError, subprocess.TimeoutExpired) as err:
                        real=None
                # guard whole source route, all 7 targeted SIU visits, and
                # every source route's order notes against new regressions.
                resolved=set(selected_ids) & base_validation["far_ids"]-(
                    real["far_ids"] if real else set())
                original_target_for_route=sum(1 for x in grouped_rows[key]
                         if (uid,x["physical_SIU_stop_id"]) in base_validation["far_ids"])
                resolved_here=sum((uid,x["physical_SIU_stop_id"]) in resolved
                              for x in grouped_rows[key])
                candidate_ok=bool(
                    real is not None and real["errors"]==0 and
                    real["far_count_by_route"][uid]<current_far[uid] and
                    real["order_count_by_route"][uid]<=orig_order[uid] and
                    resolved_here>=1 and
                    # Never trade one resolved SIU stop for a NEW offroute
                    # warning at another stop (especially at route loops).
                    real["far_ids"].issubset(current_far_ids) and
                    all(real["order_count_by_route"][x]<=current_order[x]
                        for x in real["order_count_by_route"])
                )
                if candidate_ok:
                    current_far[uid]=real["far_count_by_route"][uid]
                    current_order[uid]=real["order_count_by_route"][uid]
                    current_far_ids=set(real["far_ids"])
                    selected_repaired.add(key)
                    decision="accepted_by_real_validator_no_order_regression"
                    road_features.append(updated)
                else:
                    accepted[key]=before
                    decision="rejected_real_validator_distance_or_order"
                result_resolved=resolved_here
            else:
                candidate_ok=False
                result_resolved=0
                decision="not_compatible_with_other_SIU_stops_or_KMZ"
            checks.append({
                "trip_pattern_id":uid,"GH_section_number":segno,
                "target_count":len(grouped_rows[key]),
                "GH_spacing_m":spacing,"GH_subsegment_km":sub_km,
                "GH_route_status":route_status,"GH_queries_in_section":sub_count,
                "KMZ_bidirectional_coverage_min":round(similarity,3),
                "GH_road_distance_ratio":round(ratio,3),
                "source_stops_far_over_100_before":before_count,
                "source_stops_far_over_100_after":after_count,
                "newly_broken_100m_source_stops":bad,
                "relevant_7_stops_resolved_by_real_validator":result_resolved,
                "MobilityData_errors":real["errors"] if real else "",
                "MobilityData_distance_warnings_for_route":real["far_count_by_route"][uid] if real else "",
                "MobilityData_order_warnings_for_route":real["order_count_by_route"][uid] if real else "",
                "candidate_accepted":"yes" if candidate_ok else "no",
                "new_offroute_stop_IDs_created_during_validator_trial":(
                    len(real["far_ids"]-current_far_ids) if real and not candidate_ok else 0),
                "decision":decision,
            })
            print("7-P1 "+uid+"#"+str(segno)+
                  " spacing="+str(spacing)+"m accepted="+str(candidate_ok)+
                  " original far="+str(orig_far[uid])+
                  " source_mismatch="+str(round(similarity,3))+
                  " validator="+(str(real["far_count_by_route"][uid])+"/"+str(real["order_count_by_route"][uid])
                                 if real else "not_evaluated"),flush=True)
            if candidate_ok:break

    with tempfile.TemporaryDirectory(prefix="final-seven-",dir=args.out) as d:
        final_validation=validator_trial(accepted,"",args.jar,Path(d))
    if (final_validation["errors"]!=0 or
        any(final_validation["order_count_by_route"][x]>base_validation["order_count_by_route"][x]
            for x in set(base_validation["order_count_by_route"])|set(final_validation["order_count_by_route"])) or
        not final_validation["far_ids"].issubset(base_validation["far_ids"]) or
        sum(final_validation["far_count_by_route"].values())>
        sum(base_validation["far_count_by_route"].values())):
        raise ValueError("Seven stop research candidates introduce new offroute or order warnings")
    remaining=set(selected_ids)&final_validation["far_ids"]
    for c in case_records:
        is_remaining=(c["trip_pattern_id"],c["physical_SIU_stop_id"]) in remaining
        c["current_research_status"]=(
            "distance_warning_resolved_in_test_only" if not is_remaining else
            "GH_bus_vs_source_KMZ_discrepancy_remains_unverified"
        )
    save(args.out/"seven_priority_stops_source_road_comparison.csv",case_records)
    # Include validator-specific fields from later trials even when the
    # first tested road candidate never became routable.
    if checks:
        cols=list(dict.fromkeys(k for r in checks for k in r))
        with (args.out/"seven_GH_alternative_candidates_MobilityData_decisions.csv").open(
                "w",newline="",encoding="utf-8") as h:
            w=csv.DictWriter(h,fieldnames=cols,extrasaction="ignore")
            w.writeheader()
            w.writerows(checks)
    collection={"type":"FeatureCollection","features":list(accepted.values())}
    (args.out/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").write_text(
        json.dumps(collection,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    shutil.copy2(GH_SECTIONS,args.out/"GH_full_route_bus_segment_alignment.csv")
    points=[]
    for c in case_records:
        points.append({"type":"Feature","properties":{k:v for k,v in c.items() if k not in ("longitude","latitude")},
                       "geometry":{"type":"Point","coordinates":[float(c["longitude"]),float(c["latitude"])]}})
    (args.out/"seven_250m_offsets_GPS_SOURCE_REVIEW.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":points},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    summary={
        "original_high_priority_stop_offsets_over_250m":7,
        "source_route_patterns_with_high_priority_offsets":len(orig_far),
        "GH_road_sections_implicated":len(grouped_rows),
        "GH_bus_routing_alternative_profiles":2,
        "GH_bus_route_queries":client.route_queries,
        "full_MobilityData_validation_trials":trials+2,
        "GH_alternative_route_sections_accepted_under_full_validator":len(selected_repaired),
        "MobilityData_baseline_off_shape_warnings":sum(base_validation["far_count_by_route"].values()),
        "MobilityData_final_off_shape_warnings":sum(final_validation["far_count_by_route"].values()),
        "MobilityData_baseline_out_of_order_warnings":sum(base_validation["order_count_by_route"].values()),
        "MobilityData_final_out_of_order_warnings":sum(final_validation["order_count_by_route"].values()),
        "new_MobilityData_far_offroute_stop_IDs_created":len(
            final_validation["far_ids"]-base_validation["far_ids"]),
        "seven_original_stops_resolved_from_GTFS_test_warnings":7-len(remaining),
        "seven_stops_remaining_unresolved":len(remaining),
        "each_seven_SIU_stop_within_15m_of_AMB_official_KMZ":True,
        "canonical_SIU_stop_ids_or_coordinates_modified":False,
        "GTFS_production_files_modified":False,
        "GTFS_demo_still_nonpublishing":True,
        "real_operator_boarding_stop_service_verified":False,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    md=["# Zeven grootste SIU-/GH-shape-afwijkingen: bron- en validatoronderzoek",
        "",
        "De zeven haltes liggen binnen 15 meter van officiële AMB KMZ 2026.",
        "Er is geen bewijs voor een onjuiste SIU-stoplocatie; afwijking ligt",
        "tussen bronroute en GraphHopper bus-wegroute. Nieuwe GH-alternatieven",
        "worden alleen aanvaard na echte MobilityData-validatorcontrole",
        "zonder verhoging van het aantal volgorde-/afstandsfouten.",
        "",
        "## Resultaten",""]
    for k,v in summary.items():
        if type(v) is int:
            md.append("- "+k+": **"+str(v)+"**")
    md+=["",
        "## Individuele bevindingen",
        "",
        "| Route | SIU-halte | GH-afwijking vóór | KMZ-afstand | Validator na |",
        "|---|---|---:|---:|---|"]
    for c in case_records:
        md.append("| "+c["company"]+" "+c["route_label"]+" | "+
                  c["stop_name"].replace("|","/")+" | "+
                  str(c["original_validator_GH_distance_m"])+"m | "+
                  str(c["official_KMZ_distance_m"])+"m | "+
                  c["current_research_status"]+" |")
    md+=["",
        "## Grenzen","",
        "Als een waypoint-kandidaat een nieuw stops_match_shape_out_of_order-signaal",
        "oplevert, wordt de kandidaat-shape **niet** overgenomen, zelfs als",
        "alle fysieke halteafstanden verbeteren.",
        "Geen herordening, geen SIU GPS-verplaatsing, geen nieuwe vaste",
        "dienstregeling, geen automatische productie-GTFS-publicatie.",
        ""]
    (args.out/"summary.md").write_text("\n".join(md),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
