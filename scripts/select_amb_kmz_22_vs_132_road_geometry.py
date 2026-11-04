#!/usr/bin/env python3
"""Select best-supported AMB KMZ road geometry, comparing validated 22 vs 132.

Inputs:
* existing research-only 22-section MobilityData-guarded KMZ/GH candidate;
* 132-section locally corridor-constrained GH vertex research candidate;
* official KMZ-first original and independent reviewed GH road geometry;
* ACTUAL MobilityData 8.0.1 validation reports for both, same GTFS stop_times.

Decision rules:
1) Both sources must keep identical 352 source KMZ/GH section identities.
2) Never replace the official KMZ/GH fallback with an ungrounded new road.
3) New 132 candidate may win an individual 22-vs-132 section if it follows
   the official KMZ within 35 metres, has no excessive length, and improves
   road detail (long-chord reduction) or proximity to independent GH road.
4) If all-132 MobilityData adds warnings on a route relative to the guarded
   22, reject 132 proposals for that route. No stop IDs/sequence changes.
5) The assembled candidate MUST then pass full MobilityData non-regression
   in the workflow. That final gate can revert it to 22.
No new GraphHopper requests. No production GTFS writes.
"""
from __future__ import annotations
import argparse,csv,json,math,shutil
from collections import Counter,defaultdict
from pathlib import Path
from shapely.geometry import LineString
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
OFFICIAL=ROOT/"build/amb-kmz-first-GH-fallback-research"
GUARDED=ROOT/"sources/amb/KMZ_GH_road_refinement_QA"
CORRIDOR=ROOT/"build/amb-KMZ-refined-GH-corridor-NOT-PUBLISHABLE"
GH=ROOT/"sources/amb/GTFS_7_largest_shape_offset_review"
VALID22=ROOT/"build/amb-KMZ-comparison-22-NOT-PUBLISHABLE/validator/report.json"
VALID132=ROOT/"build/amb-KMZ-comparison-132-NOT-PUBLISHABLE/validator/report.json"
OUT=ROOT/"build/amb-KMZ-22-vs-132-selection-NOT-PUBLISHABLE"
PROJECT=Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True)

def readjson(path):
    return json.loads(path.read_text(encoding="utf-8"))
def fk(f):
    p=f["properties"];return (p["trip_pattern_id"],int(p["section"]))
def items(folder):
    path=folder/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson"
    data=readjson(path)
    feats=data["features"]
    d={fk(f):f for f in feats}
    if len(d)!=352 or len(feats)!=352:
        raise ValueError("Expected 352 unique audited AMB route sections "+str(folder))
    return d,feats
def line(f):
    return LineString([PROJECT.transform(float(p[0]),float(p[1])) for p in f["geometry"]["coordinates"]])
def writecsv(path,rows):
    if not rows:return
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=list(rows[0]),extrasaction="ignore")
        writer.writeheader();writer.writerows(rows)
def distances(source,other,step=35,max_samples=600):
    n=max(3,min(max_samples,math.ceil(source.length/step)))
    values=sorted(source.interpolate(source.length*i/n).distance(other) for i in range(n+1))
    return {"mean":sum(values)/len(values),"p95":values[int((len(values)-1)*.95)],
            "maximum":values[-1]}
def metrics(feat,kmz,road):
    geom=line(feat)
    p=line(kmz)
    g=line(road)
    dkmz=distances(geom,p)
    dgh=distances(geom,g)
    jumps=[math.dist(a,b) for a,b in zip(geom.coords,tuple(geom.coords)[1:])]
    return {
        "points":len(geom.coords),
        "long_chords":sum(x>400 for x in jumps),
        "max_chord":max(jumps,default=0),
        "length":geom.length,
        "ratio":geom.length/max(p.length,1.),
        "kmz_mean":dkmz["mean"],"kmz_p95":dkmz["p95"],
        "kmz_max":dkmz["maximum"],
        "gh_mean":dgh["mean"],"gh_p95":dgh["p95"],
    }
def severity_counts(report):
    c=Counter()
    for g in report["notices"]:
        c[g["severity"]]+=int(g["totalNotices"])
    return c
def byroute(report):
    """Per-code source route warnings. Do not claim sampled notices complete."""
    result=defaultdict(Counter)
    unowned=Counter()
    for g in report["notices"]:
        if g["severity"]!="WARNING":continue
        code=g["code"]
        if code in ("mixed_case_recommended_field","missing_recommended_file",
                    "trip_coverage_not_active_for_next7_days"):
            continue # Unchanged GTFS files; not geometry evidence.
        samples=g.get("sampleNotices",[])
        if len(samples)!=int(g["totalNotices"]):
            raise ValueError("MobilityData sampled warnings; selection cannot be attributed: "+code)
        for item in samples:
            trip=item.get("tripId","")
            shape=item.get("shapeId","")
            uid=(trip.removeprefix("QA_") if trip.startswith("QA_") else
                 shape.removeprefix("GH_QA_") if shape.startswith("GH_QA_") else "")
            if uid:
                result[uid][code]+=1
            else:
                unowned[code]+=1
    return result,unowned
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=OUT)
    p.add_argument("--corridor-limit-m",type=float,default=35.)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    official,ordered=items(OFFICIAL)
    safe,_=items(GUARDED)
    wide,_=items(CORRIDOR)
    gh,_=items(GH)
    if set(official)!=set(safe) or set(safe)!=set(wide) or set(wide)!=set(gh):
        raise ValueError("Mismatch in route shapes: cannot compare")
    r22=readjson(VALID22);r132=readjson(VALID132)
    c22=severity_counts(r22);c132=severity_counts(r132)
    if c22["ERROR"]!=0 or c132["ERROR"]!=0:
        raise ValueError("One input is not technically valid GTFS")
    b22,unknown22=byroute(r22)
    b132,unknown132=byroute(r132)
    increased_global={code for code,count in unknown132.items()
                      if count>unknown22[code]}
    if increased_global:
        raise ValueError("New unattributable validator warning(s): "+str(increased_global))
    review=[]
    proposals={}
    route_guard_rejected=set()
    considered=Counter()
    geometry_byroute=defaultdict(list)
    for k in sorted(official):
        uid,sec=k
        kmz=official[k]
        f22=safe[k]
        f132=wide[k]
        source=kmz["properties"]["shape_source_actual"]
        m0=metrics(kmz,kmz,gh[k])
        m22=metrics(f22,kmz,gh[k])
        m132=metrics(f132,kmz,gh[k])
        changed22=f22["geometry"]["coordinates"]!=kmz["geometry"]["coordinates"]
        changed132=f132["geometry"]["coordinates"]!=kmz["geometry"]["coordinates"]
        considered["original_2026_KMZ_sections" if source=="official_AMB_KMZ_2026" else
                   "GH_fallback_sections"]+=1
        if changed22:considered["22_GH_refinements"]+=1
        if changed132:considered["132_GH_refinements"]+=1
        reason="same_as_22_or_GH_fallback"
        # Guard the OFFICIAL KMZ corridor and historic provenance.
        # Average GH nearest-road distance is not a proof of operation.
        improvement=(m132["long_chords"]<m22["long_chords"] or
                     m132["gh_mean"]+2<m22["gh_mean"] or
                     m132["gh_p95"]+5<m22["gh_p95"])
        allowed=bool(
            source=="official_AMB_KMZ_2026" and changed132 and
            m132["kmz_max"]<=args.corridor_limit_m+1 and
            m132["ratio"]<=1.35 and m132["ratio"]>=.96 and
            m132["points"]>=m0["points"] and improvement
        )
        if source!="official_AMB_KMZ_2026":
            reason="no_usable_official_KMZ_keep_GH_fallback"
        elif not changed132:
            reason="no_132_section_change"
        elif not allowed:
            reason="132_lacks_grounded_road_gain_or_source_corridor_limit"
        else:
            # This guard is applied to the *entire route pattern* based on
            # actual full-132 MobilityData, before the final mixed validator.
            worse=[code for code in b132[uid] if b132[uid][code]>b22[uid][code]]
            if worse:
                reason="132_route_would_add_validator_"+",".join(sorted(worse))
                route_guard_rejected.add(uid)
            else:
                reason="132_geometric_candidate_and_per_route_validator_no_increase"
                proposals[k]=f132
        row={
            "trip_pattern_id":uid,"section_number":sec,
            "official_source":source,
            "changed_in_22_version":"yes" if changed22 else "no",
            "changed_in_132_version":"yes" if changed132 else "no",
            "KMZ_original_vertices":m0["points"],
            "22_vertices":m22["points"],"132_vertices":m132["points"],
            "KMZ_original_over400m_chords":m0["long_chords"],
            "22_over400m_chords":m22["long_chords"],
            "132_over400m_chords":m132["long_chords"],
            "22_max_chord_m":round(m22["max_chord"],1),
            "132_max_chord_m":round(m132["max_chord"],1),
            "22_mean_to_independent_GH_road_m":round(m22["gh_mean"],2),
            "132_mean_to_independent_GH_road_m":round(m132["gh_mean"],2),
            "22_p95_to_independent_GH_road_m":round(m22["gh_p95"],2),
            "132_p95_to_independent_GH_road_m":round(m132["gh_p95"],2),
            "22_max_distance_to_official_KMZ_m":round(m22["kmz_max"],1),
            "132_max_distance_to_official_KMZ_m":round(m132["kmz_max"],1),
            "22_length_ratio_vs_KMZ":round(m22["ratio"],3),
            "132_length_ratio_vs_KMZ":round(m132["ratio"],3),
            "geometrically_preselected_132":"yes" if k in proposals else "no",
            "decision_reason":reason,
            "actual_operator_route_legally_confirmed":"no",
        }
        review.append(row)
        geometry_byroute[uid].append(row)
    selected={k:proposals.get(k,safe[k]) for k in sorted(safe)}
    # The previous 22-only result is the safe default. Final validation
    # must still be performed on the assembled union.
    feats=[selected[fk(f)] for f in ordered]
    (args.out/"GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson").write_text(
        json.dumps({"type":"FeatureCollection","features":feats},
                   ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    shutil.copy2(OFFICIAL/"GH_full_route_bus_segment_alignment.csv",
                 args.out/"GH_full_route_bus_segment_alignment.csv")
    for row in review:
        k=(row["trip_pattern_id"],row["section_number"])
        row["preliminary_selection"]="132_corridor" if k in proposals else (
            "22_guarded" if safe[k]["geometry"]["coordinates"]!=official[k]["geometry"]["coordinates"]
            else "official_KMZ_or_GH_fallback")
    writecsv(args.out/"per_section_22_vs_132_road_fidelity.csv",review)
    route_summaries=[]
    for uid,rows in sorted(geometry_byroute.items()):
        route_summaries.append({
            "trip_pattern_id":uid,
            "official_KMZ_sections":sum(x["official_source"]=="official_AMB_KMZ_2026" for x in rows),
            "22_changed_sections":sum(x["changed_in_22_version"]=="yes" for x in rows),
            "132_changed_sections":sum(x["changed_in_132_version"]=="yes" for x in rows),
            "proposed_132_sections":sum(x["geometrically_preselected_132"]=="yes" for x in rows),
            "source_KMZ_long_chords_over400":sum(x["KMZ_original_over400m_chords"] for x in rows),
            "22_remaining_chords_over400":sum(x["22_over400m_chords"] for x in rows),
            "132_remaining_chords_over400":sum(x["132_over400m_chords"] for x in rows),
            "132_validator_route_additional_warning":("yes" if uid in route_guard_rejected else "no"),
            "operator_route_confirmed":"no",
        })
    writecsv(args.out/"per_route_22_vs_132_quality.csv",route_summaries)
    summary={
        "comparison_scope_sections":len(selected),
        "official_KMZ_sections":considered["original_2026_KMZ_sections"],
        "GH_fallback_sections":considered["GH_fallback_sections"],
        "22_changed_sections_vs_official":considered["22_GH_refinements"],
        "132_changed_sections_vs_official":considered["132_GH_refinements"],
        "132_candidate_sections_selected_by_geometry_and_route_validator":len(proposals),
        "additional_vs_22_sections_in_candidate":sum(
            selected[k]["geometry"]["coordinates"]!=safe[k]["geometry"]["coordinates"]
            for k in safe),
        "candidate_patterns_with_132_selection":len({k[0] for k in proposals}),
        "patterns_denied_132_due_to_new_route_warnings":len(route_guard_rejected),
        "22_baseline_total_errors":c22["ERROR"],
        "132_standalone_total_errors":c132["ERROR"],
        "22_baseline_total_warnings":c22["WARNING"],
        "132_standalone_total_warnings":c132["WARNING"],
        "original_KMZ_sparse_chords_400m":sum(r["KMZ_original_over400m_chords"] for r in review),
        "remaining_22_sparse_chords_400m":sum(r["22_over400m_chords"] for r in review),
        "remaining_132_sparse_chords_400m":sum(r["132_over400m_chords"] for r in review),
        "proposed_selection_only_not_production":True,
        "full_assembled_candidate_needs_independent_validator":True,
        "actual_bus_operator_route_confirmed":False,
        "unchanged_SIU_stop_ids_stop_order_trips":True,
    }
    (args.out/"selection_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
