#!/usr/bin/env python3
"""Insert 65 GraphHopper bus-route candidates into a NEW no-time trip concept.

Retain all 9,000 existing stop visits, physical SIU stop_ids, original order
and existing route geometry component IDs. Only re-number concept sequences.
Stop-service and direction remain unconfirmed; do not modify live GTFS.
"""
import csv
import json
from collections import defaultdict, Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sources/amb/missing_siu_trip_stop_patterns"
CLASS=ROOT/"sources/amb/graphhopper_stop_classification"
OUT=ROOT/"build/amb-expanded-GH-stop-concept"
SIU=ROOT/"sources/siu/gtfs_staging/candidate_stops.csv"

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def write(path,rows,columns):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def m(value):
    return float(value)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    initial=read(BASE/"candidate_stop_order_per_trip_NO_TIMES.csv")
    patterns=read(BASE/"trip_patterns_MISSING_SIU_NO_TIMES.csv")
    decisions=read(CLASS/"GH_bus_stop_candidate_decisions_125.csv")
    catalog=read(SIU)
    catalog_by_id={s["stop_id"]:s for s in catalog}
    if len(catalog_by_id)!=len(catalog):
        raise ValueError("Duplicate physical SIU stop IDs")
    if len(initial)!=9000 or len(decisions)!=125:
        raise ValueError("The input baseline has changed; review before proceeding")
    candidates=[x for x in decisions if x["candidate_class"]=="toevoegkandidaat"]
    if len(candidates)!=65:
        raise ValueError("Exactly 65 classified add candidates were expected")
    pattern_ids={p["trip_pattern_id"] for p in patterns}
    by_trip=defaultdict(list)
    for row in initial:
        tid=row["trip_pattern_id"]
        if tid not in pattern_ids:
            raise ValueError("Unrecognized trip pattern "+tid)
        if row["stop_id"] not in catalog_by_id:
            raise ValueError("Unknown baseline SIU stop "+row["stop_id"])
        by_trip[tid].append(row)
    for tid,rows in by_trip.items():
        rows.sort(key=lambda x:int(x["stop_sequence"]))
        if [int(x["stop_sequence"]) for x in rows]!=list(range(1,len(rows)+1)):
            raise ValueError("Non-contiguous source sequence "+tid)
        positions=[m(x["shape_dist_traveled_candidate_m"]) for x in rows]
        if any(a>b for a,b in zip(positions,positions[1:])):
            raise ValueError("Original route geometry order is invalid: "+tid)
    if len(by_trip)!=sum(int(p["physical_SIU_stop_candidates_in_order"])>=5 for p in patterns):
        raise ValueError("Unexpected source patterns or missing candidate visits")
    inserts=defaultdict(list)
    unique_keys=set()
    for r in candidates:
        tid=r["trip_pattern_id"]
        idx=int(r["gap_index"])
        baseline=by_trip.get(tid,[])
        if idx<1 or idx>=len(baseline):
            raise ValueError("Candidate has no corresponding stop gap "+tid)
        a,b=baseline[idx-1],baseline[idx]
        pos=m(r["candidate_chainage_m"])
        lo=m(a["shape_dist_traveled_candidate_m"])
        hi=m(b["shape_dist_traveled_candidate_m"])
        if not lo<pos<hi:
            raise ValueError("Candidate is not between exact route stop anchors "+tid)
        if a["stop_id"]!=r["insert_after_existing_stop_id"] or b["stop_id"]!=r["insert_before_existing_stop_id"]:
            raise ValueError("Stop anchor IDs have changed for "+tid)
        if abs(lo-m(r["gap_chainage_start_m"]))>1 or abs(hi-m(r["gap_chainage_end_m"]))>1:
            raise ValueError("The source KMZ chainage has changed for "+tid)
        sid=r["physical_SIU_stop_id_if_known"]
        if sid not in catalog_by_id or r["candidate_kind"]!="existing_physical_SIU_stop":
            raise ValueError("Attempted to invent an SIU stop or insert an OSM-only point")
        if r["candidate_position_is_between_anchors"]!="yes":
            raise ValueError("Candidate ordering not reviewed")
        key=(tid,idx,r["candidate_source_id"])
        if key in unique_keys:
            raise ValueError("Duplicate source candidate within same stop gap")
        unique_keys.add(key)
        inserts[tid,idx].append(r)
    if sum(len(x) for x in inserts.values())!=65:
        raise ValueError("Candidate count changed before merge")

    fields=[
        "trip_pattern_id","route_id_candidate","company","route_label",
        "variant","stop_sequence","stop_id","stop_name","stop_lat","stop_lon",
        "KMZ_shape_distance_m","original_stop_sequence",
        "source_status","GH_candidate_source_id","GH_original_direction_assessment",
        "GH_KMZ_constrained_extra_distance_m","GH_KMZ_constrained_detour_ratio",
        "insert_after_baseline_stop_id","insert_before_baseline_stop_id",
        "arrival_time","departure_time","actual_route_stop_service_confirmed",
        "trip_direction_confirmed","GTFS_publishable"
    ]
    expanded=[]
    audit=[]
    close=[]
    affected=set()
    for tid,baseline in by_trip.items():
        draft=[]
        for i,b in enumerate(baseline,1):
            sid=b["stop_id"]
            p=catalog_by_id[sid]
            common={
                "trip_pattern_id":tid,"route_id_candidate":b["route_id_proposed_base"],
                "company":b["company"],"route_label":b["official_route_label"],
                "variant":b["variant"],
                "arrival_time":"","departure_time":"",
                "actual_route_stop_service_confirmed":"no",
                "trip_direction_confirmed":"no","GTFS_publishable":"no"
            }
            draft.append({
                **common,"stop_id":sid,"stop_name":p["stop_name"],
                "stop_lat":p["stop_lat"],"stop_lon":p["stop_lon"],
                "KMZ_shape_distance_m":b["shape_dist_traveled_candidate_m"],
                "original_stop_sequence":i,
                "source_status":"original_KMZ_SIU_geographic_stop_candidate",
                "GH_candidate_source_id":"","GH_original_direction_assessment":"",
                "GH_KMZ_constrained_extra_distance_m":"",
                "GH_KMZ_constrained_detour_ratio":"",
                "insert_after_baseline_stop_id":"",
                "insert_before_baseline_stop_id":""
            })
            for c in sorted(inserts.get((tid,i),[]),
                            key=lambda x:(m(x["candidate_chainage_m"]),x["candidate_source_id"])):
                sid=c["physical_SIU_stop_id_if_known"]
                physical=catalog_by_id[sid]
                draft.append({
                    **common,"stop_id":sid,"stop_name":physical["stop_name"],
                    "stop_lat":physical["stop_lat"],"stop_lon":physical["stop_lon"],
                    "KMZ_shape_distance_m":c["candidate_chainage_m"],
                    "original_stop_sequence":"",
                    "source_status":"GH_bus_toevoegkandidaat_REVIEW_ONLY",
                    "GH_candidate_source_id":c["candidate_source_id"],
                    "GH_original_direction_assessment":c["KMZ_name_direction_original"],
                    "GH_KMZ_constrained_extra_distance_m":c["GH_bus_KMZ_constrained_extra_distance_m"],
                    "GH_KMZ_constrained_detour_ratio":c["GH_bus_KMZ_constrained_detour_ratio"],
                    "insert_after_baseline_stop_id":c["insert_after_existing_stop_id"],
                    "insert_before_baseline_stop_id":c["insert_before_existing_stop_id"]
                })
                affected.add(tid)
                audit.append({
                    "trip_pattern_id":tid,"company":b["company"],
                    "route_label":b["official_route_label"],
                    "gap_index_original":i,"GH_candidate_source_id":c["candidate_source_id"],
                    "reused_physical_SIU_stop_id":sid,
                    "existing_anchor_stop_before":b["stop_id"],
                    "existing_anchor_stop_after":baseline[i]["stop_id"],
                    "KMZ_shape_distance_m":c["candidate_chainage_m"],
                    "new_concept_stop_sequence":"",
                    "GH_original_name_direction":c["KMZ_name_direction_original"],
                    "GH_extra_distance_m":c["GH_bus_KMZ_constrained_extra_distance_m"],
                    "GH_detour_ratio":c["GH_bus_KMZ_constrained_detour_ratio"],
                    "manual_route_stop_validation":"pending",
                    "published_GTFS_updated":"no"
                })
        for idx,row in enumerate(draft,1):
            row["stop_sequence"]=idx
        old=[(int(r["original_stop_sequence"]),r["stop_id"]) for r in draft
             if r["original_stop_sequence"]!=""]
        expected=[(int(r["stop_sequence"]),r["stop_id"]) for r in baseline]
        if old!=expected:
            raise ValueError("Original SIU source stop visits have changed for "+tid)
        shape_positions=[m(r["KMZ_shape_distance_m"]) for r in draft]
        if any(b<a for a,b in zip(shape_positions,shape_positions[1:])):
            raise ValueError("New concept stop order not monotone: "+tid)
        for prev,now in zip(draft,draft[1:]):
            delta=m(now["KMZ_shape_distance_m"])-m(prev["KMZ_shape_distance_m"])
            if delta<60 and ("GH_bus_toevoegkandidaat" in prev["source_status"]
                             or "GH_bus_toevoegkandidaat" in now["source_status"]):
                close.append({
                    "trip_pattern_id":tid,"stop_id_A":prev["stop_id"],
                    "stop_id_B":now["stop_id"],
                    "concept_sequence_A":prev["stop_sequence"],
                    "concept_sequence_B":now["stop_sequence"],
                    "KMZ_distance_between_visits_m":round(delta,1),
                    "same_physical_SIU_stop_id":"yes" if prev["stop_id"]==now["stop_id"] else "no",
                    "rejected_automatically":"no",
                    "needs_manual_review":"yes"
                })
        expanded.extend(draft)
    # Candidate order: a source ID can occur multiple times along loop,
    # so each insert is uniquely identified by trip + original gap number.
    inserted_idx={}
    for r in expanded:
        if r["source_status"]!="GH_bus_toevoegkandidaat_REVIEW_ONLY":
            continue
        inserted_idx.setdefault((r["trip_pattern_id"],r["GH_candidate_source_id"]),[]).append(r)
    for a in audit:
        hits=[r for r in inserted_idx.get((a["trip_pattern_id"],a["GH_candidate_source_id"]),[])
              if (m(r["KMZ_shape_distance_m"])==m(a["KMZ_shape_distance_m"])
                  and r["insert_after_baseline_stop_id"]==a["existing_anchor_stop_before"]
                  and r["insert_before_baseline_stop_id"]==a["existing_anchor_stop_after"])]
        if len(hits)!=1:raise ValueError("Ambiguous concept stop insert audit identity")
        a["new_concept_stop_sequence"]=hits[0]["stop_sequence"]
    if len(audit)!=65 or len(expanded)!=9065:
        raise ValueError("Expected exact 65 new visits and 9,065 total concept visits")
    by_concept=defaultdict(list)
    for r in expanded:by_concept[r["trip_pattern_id"]].append(r)
    for tid,rows in by_concept.items():
        if [int(r["stop_sequence"]) for r in rows]!=list(range(1,len(rows)+1)):
            raise ValueError("Non-contiguous concept trip sequence")
        if any(r["arrival_time"] or r["departure_time"] for r in rows):
            raise ValueError("Times must remain empty")
    original_gaps=sum(m(b["shape_dist_traveled_candidate_m"])-m(a["shape_dist_traveled_candidate_m"])>2000
                      for items in by_trip.values() for a,b in zip(items,items[1:]))
    remaining=[]
    for tid,items in by_concept.items():
        for a,b in zip(items,items[1:]):
            gap=m(b["KMZ_shape_distance_m"])-m(a["KMZ_shape_distance_m"])
            if gap>2000:
                remaining.append({
                    "company":a["company"],"route_label":a["route_label"],
                    "trip_pattern_id":tid,
                    "from_concept_stop_sequence":a["stop_sequence"],
                    "to_concept_stop_sequence":b["stop_sequence"],
                    "from_stop_id":a["stop_id"],"to_stop_id":b["stop_id"],
                    "KMZ_distance_between_selected_stops_m":round(gap,1),
                    "actual_nonstop_road_segment_verified":"no"
                })
    perroute=defaultdict(Counter)
    for p in patterns:
        perroute[(p["company"],p["official_route_label"])]["component_count"]+=1
    for x in expanded:
        item=perroute[(x["company"],x["route_label"])]
        item["rows_total"]+=1
        item["rows_added"]+=x["source_status"]=="GH_bus_toevoegkandidaat_REVIEW_ONLY"
    route_rows=[{
        "company":co,"route_label":label,
        "KMZ_ArcGIS_pattern_components":v["component_count"],
        "concept_total_stop_visits":v["rows_total"],
        "GH_stop_candidates_inserted":v["rows_added"],
        "operator_stop_service_verified":"no",
        "published_gtfs_changed":"no"
    } for (co,label),v in sorted(perroute.items())]

    concise=[{
        "trip_id":r["trip_pattern_id"],"stop_sequence":r["stop_sequence"],
        "stop_id":r["stop_id"],"arrival_time":"","departure_time":"",
        "source_status":r["source_status"],"GTFS_publishable":"no"
    } for r in expanded]
    write(OUT/"concept_trip_stop_order_ALL_NO_TIMES.csv",expanded,fields)
    write(OUT/"concept_stop_times_RESEARCH_NO_TIMES.csv",concise,list(concise[0]))
    write(OUT/"GH_65_insertions_with_new_sequences.csv",audit,list(audit[0]))
    write(OUT/"route_variant_coverage.csv",route_rows,list(route_rows[0]))
    write(OUT/"remaining_gaps_over_2km_CONCEPT.csv",remaining,[
        "company","route_label","trip_pattern_id",
        "from_concept_stop_sequence","to_concept_stop_sequence",
        "from_stop_id","to_stop_id","KMZ_distance_between_selected_stops_m",
        "actual_nonstop_road_segment_verified"])
    write(OUT/"close_stop_pairs_after_insertion_REVIEW.csv",close,[
        "trip_pattern_id","stop_id_A","stop_id_B","concept_sequence_A",
        "concept_sequence_B","KMZ_distance_between_visits_m",
        "same_physical_SIU_stop_id","rejected_automatically","needs_manual_review"])
    summary={
        "original_existing_stop_visits":len(initial),
        "GH_add_candidates_inserted_in_concept":len(audit),
        "concept_stop_visits":len(expanded),
        "existing_trip_pattern_components":len(by_concept),
        "route_variants_in_concept":len(route_rows),
        "trip_pattern_components_with_additions":len(affected),
        "route_variants_with_additions":sum(r["GH_stop_candidates_inserted"]>0 for r in route_rows),
        "unique_existing_physical_SIU_stop_ids_reused":len({r["stop_id"] for r in expanded}),
        "original_gaps_over_2km":original_gaps,
        "remaining_concept_gaps_over_2km":len(remaining),
        "close_pairs_under_60m_around_new_candidates":len(close),
        "existing_stop_visits_deleted_or_reordered":False,
        "new_physical_stops_created":0,
        "travel_times_generated":0,
        "published_GTFS_files_modified":False,
        "all_added_stops_require_operator_boarding_validation":True,
        "trip_direction_and_legal_variant_verified":False
    }
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    doc=[
        "# Concepthaltevolgordes uitgebreid met 65 bestaande SIU-haltes", "",
        "Onderzoeksstaging; niet publiceren als GTFS. De nieuwe stop_sequence is "
        "per bestaand geometrisch trip-patroon hernummerd na het invoegen van "
        "65 GraphHopper-toevoegkandidaten precies tussen hun bestaande SIU-ankers.",
        "Alle oorspronkelijke haltebezoeken blijven in dezelfde volgorde.",
        "Een halte mag op meerdere trips of meerdere passages van een rondrit voorkomen.", "",
        "## Aantallen", ""]
    for key,v in summary.items():
        if type(v) is int:doc.append("- "+key+": **"+str(v)+"**")
    doc += [
        "", "## Onderzoek en beperkingen", "",
        "- Alle nieuwe rijen zijn bestaande fysieke SIU-stop_ID's, niet haltes per route.",
        "- De GH-status bewijst geen daadwerkelijke stopbediening of officiële rijrichting.",
        "- De geordende rijen verwijzen naar KMZ/ArcGIS-componenten; één component is niet altijd één echte trip.",
        "- Bij twee haltepunten binnen 60 meter langs het traject blijft de mogelijke doublure behouden maar gemarkeerd.",
        "- Arrival en departure blijven leeg, voor GraphHopper-rijtijdverwerking op een later moment.",
        "- Geen source-bestanden of productiebestanden onder gtfs/ aangepast.", "",
        "## Bestanden", "",
        "- concept_trip_stop_order_ALL_NO_TIMES.csv: alle 9.065 haltepassages inclusief metadata.",
        "- concept_stop_times_RESEARCH_NO_TIMES.csv: GTFS-achtig concept, nadrukkelijk zonder tijden.",
        "- GH_65_insertions_with_new_sequences.csv: exacte nieuwe positie en twee omliggende oorspronkelijke stop-ID's.",
        "- route_variant_coverage.csv: resultaten per officiële routevariant.",
        "- remaining_gaps_over_2km_CONCEPT.csv: resterende geografische gaten.",
        "- close_stop_pairs_after_insertion_REVIEW.csv: korte onderlinge afstanden die aparte controle vragen.", ""
    ]
    (OUT/"summary.md").write_text("\n".join(doc),encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
if __name__=="__main__":
    main()
