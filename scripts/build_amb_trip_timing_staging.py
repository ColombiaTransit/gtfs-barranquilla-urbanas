#!/usr/bin/env python3
"""Build non-publishable GTFS-shaped frequency trip templates and estimated stop_times.

Reuse the SAME physical SIU stop_id across all itineraries. The SIU-derived order
is source-observed. Per-stop arrival/departure times are ONLY a changeable
engineering model, not an observed bus schedule. Never write to gtfs/.
"""
import csv
import json
import math
from collections import defaultdict, Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SIU=ROOT/"sources/siu"
AMB=ROOT/"sources/amb"
OUT=ROOT/"build/gtfs-trip-timing-staging"

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def write(path, rows, headers):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=headers,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def seconds_fmt(x):
    x=int(x)
    return f"{x//3600:02d}:{(x//60)%60:02d}:{x%60:02d}"

def haversine_m(a,b):
    lat1,lon1=a;lat2,lon2=b
    x=math.radians(lat2-lat1)
    y=math.radians(lon2-lon1)
    h=math.sin(x/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(y/2)**2
    return 12742000*math.asin(min(1,math.sqrt(h)))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    orders=read(SIU/"open_route_review/combined_20_route_stop_candidates_NO_TIMES.csv")
    physical=read(SIU/"gtfs_staging/candidate_stops.csv")
    registry=read(ROOT/"gtfs/routes.txt")
    headways=read(AMB/"gtfs_staging/route_headway_candidates.csv")
    periods=read(AMB/"gtfs_staging/weekday_period_staging.csv")
    assumptions=read(AMB/"gtfs_timing_model_assumptions.csv")
    if len(assumptions)!=1:raise ValueError("Exactly one active timing model is supported")
    params=assumptions[0]
    speed=float(params["avg_moving_speed_kmh"])
    factor=float(params["distance_factor_for_between_stop_straight_lines"])
    dwell=int(params["dwell_seconds_per_stop"])
    minimum=int(params["minimum_stop_to_stop_seconds"])
    warning_gap=int(params["unusual_straight_line_gap_m"])
    if not (8<=speed<=45 and 1<=factor<=3 and 0<=dwell<=90 and minimum>=1):
        raise ValueError("Invalid travel-time model bounds")
    by_stop={x["stop_id"]:x for x in physical}
    if len(by_stop)!=len(physical):raise ValueError("Canonical SIU physical stop IDs not unique")
    known_routes={x["route_id"]:x for x in registry}
    by_headway={x["gtfs_route_id"]:x for x in headways}
    by_period=defaultdict(list)
    for x in periods:by_period[x["gtfs_route_id"]].append(x)
    grouped=defaultdict(list)
    for row in orders:
        grouped[row["siu_itinerary_uuid"]].append(row)
    if len(grouped)!=20:
        raise ValueError(f"Expected 20 source SIU itinerary candidates, found {len(grouped)}")
    if len(orders)!=3981:
        raise ValueError(f"Expected 3981 ordered SIU stop visits, got {len(orders)}")

    trips=[]
    stop_times=[]
    route_stopQA=[]
    timed_anchors=[]
    frequency=[]
    shared_usage=defaultdict(set)
    model_id=params["timing_model_id"]
    for uuid,stops in sorted(grouped.items()):
        stops.sort(key=lambda r:int(r["siu_stop_sequence"]))
        route_ids={x["gtfs_route_id_candidate"] for x in stops}
        if len(route_ids)!=1:raise ValueError(f"Inconsistent route candidate within SIU itinerary {uuid}")
        route_id=next(iter(route_ids))
        if route_id not in known_routes:raise ValueError("Unknown GTFS route candidate "+route_id)
        seqs=[int(x["siu_stop_sequence"]) for x in stops]
        if seqs!=list(range(1,len(stops)+1)):
            raise ValueError("SIU itinerary has nonconsecutive stop sequence "+uuid)
        trip_id="AMB_MODEL_SIU_"+uuid.replace("-","")
        tier=stops[0]["confidence_tier"]
        trip={
            "route_id":route_id, "service_id":"AMB_MON_FRI_MODEL",
            "trip_id":trip_id,"trip_headsign":"","direction_id":"","block_id":"",
            "shape_id":""
        }
        trips.append(trip)
        last_coords=None
        previous_departs=0
        elapsed=0
        total_straight=0.0
        unusual=0
        zero_distance=0
        for index,r in enumerate(stops):
            stop_id=r["candidate_stop_id"]
            if stop_id not in by_stop:
                raise ValueError("Unknown physical SIU stop ID "+stop_id)
            physical_stop=by_stop[stop_id]
            coordinates=(float(physical_stop["stop_lat"]),float(physical_stop["stop_lon"]))
            if index==0:
                arrival=departure=0
            else:
                straight=haversine_m(last_coords,coordinates)
                total_straight+=straight
                if straight>warning_gap:unusual+=1
                if straight<2:zero_distance+=1
                travel=math.ceil(straight*factor/(speed/3.6))
                leg_seconds=max(minimum,travel+dwell)
                arrival=previous_departs+leg_seconds
                departure=arrival  # stop dwell modeled as part of the preceding inter-stop leg
                elapsed=departure
            last_coords=coordinates
            previous_departs=departure
            shared_usage[stop_id].add(trip_id)
            stop_times.append({
                "trip_id":trip_id,
                "arrival_time":seconds_fmt(arrival),
                "departure_time":seconds_fmt(departure),
                "stop_id":stop_id,
                "stop_sequence":int(r["siu_stop_sequence"]),
                "timepoint":"1" if index in (0,len(stops)-1) else "0"
            })
            timed_anchors.append({
                "trip_id":trip_id,"source_siu_itinerary_uuid":uuid,
                "route_id_candidate":route_id,
                "stop_sequence":int(r["siu_stop_sequence"]),
                "stop_id":stop_id,"siu_stop_name":physical_stop["stop_name"],
                "arrival_time_model":seconds_fmt(arrival),
                "departure_time_model":seconds_fmt(departure),
                "source_order_verified_by_SIU":"yes",
                "route_to_legal_code_final_verified":"no",
                "timing_model_id":model_id,
                "stop_passage_time_observed":"no",
                "actual_trip_duration_observed":"no",
                "estimated_seconds_since_first_stop":departure,
                "legal_GTFS_publication_approved":"no"
            })
        freq_record=by_headway.get(route_id)
        status=freq_record["period_staging_status"] if freq_record else "no_headway_record"
        periods_available=by_period.get(route_id,[])
        is_ready=status=="ready_to_stage" and bool(periods_available)
        if is_ready:
            for p in periods_available:
                if p["gtfs_route_id"]!=route_id:raise ValueError("Frequency source changed unexpectedly")
                interval=int(p["headway_secs"])
                if interval<=0:raise ValueError("Invalid headway")
                if p["period_start_boundary_local"]>=p["period_end_boundary_local"]:
                    raise ValueError("Invalid frequency service period "+p["period"])
                frequency.append({
                    "trip_id":trip_id,
                    "start_time":p["period_start_boundary_local"],
                    "end_time":p["period_end_boundary_local"],
                    "headway_secs":interval,
                    "exact_times":"0"
                })
        route_stopQA.append({
            "trip_id":trip_id,"route_id_candidate":route_id,
            "siu_itinerary_uuid":uuid,"siu_confidence_tier":tier,
            "SIU_source_stop_visits":len(stops),
            "first_stop_id":stops[0]["candidate_stop_id"],
            "last_stop_id":stops[-1]["candidate_stop_id"],
            "total_straight_between_stop_km":round(total_straight/1000,2),
            "time_model_duration_minutes":round(elapsed/60,1),
            "time_model_duration_HHMMSS":seconds_fmt(elapsed),
            "straight_line_gaps_over_threshold":unusual,
            "near_identical_consecutive_stop_points":zero_distance,
            "model_stops_per_trip":len(stops),
            "first_and_last_anchored_by_real_times":"no",
            "SIU_sequence_observed":"yes",
            "GTFS_route_code_final_confirmed":"no",
            "model_frequency_periods":len(periods_available) if is_ready else 0,
            "frequency_staging_status":status,
            "frequency_blockers":freq_record["blockers"] if freq_record else "headway_row_missing",
            "model_quality_flags":(";".join(
              (["large_geographic_gap"] if unusual else [])+
              (["model_duration_over_5h"] if elapsed>18000 else [])+
              (["no_frequency_periods"] if not is_ready else [])
            )),
            "timing_model_id":model_id,
            "publishable":"no"
        })
    if len(stop_times)!=len(orders):
        raise ValueError("Stop-times model lost observed SIU stop visits")
    assert len(trips)==20
    assert all(t["trip_id"] in {x["trip_id"] for x in trips} for t in stop_times)
    write(OUT/"trips_MODEL_ONLY_NOT_FOR_PUBLICATION.txt",trips,list(trips[0]))
    write(OUT/"stop_times_MODEL_ONLY_NOT_FOR_PUBLICATION.txt",stop_times,list(stop_times[0]))
    write(OUT/"frequencies_MODEL_ONLY_NOT_FOR_PUBLICATION.txt",frequency,
          ["trip_id","start_time","end_time","headway_secs","exact_times"])
    write(OUT/"trip_timing_quality_review.csv",route_stopQA,list(route_stopQA[0]))
    write(OUT/"stop_time_anchor_model_audit.csv",timed_anchors,list(timed_anchors[0]))
    stop_usage=[{
        "physical_SIU_stop_id":sid,
        "existing_candidate_stop_name":by_stop[sid]["stop_name"],
        "model_trip_template_references":len(trips_here),
        "model_trip_ids":";".join(sorted(trips_here)),
        "stop_times_reference_uses_single_physical_stop":"yes",
        "source_physical_stop_from_SIU":"yes",
    } for sid,trips_here in sorted(shared_usage.items())]
    write(OUT/"shared_physical_stop_usage_by_SIU_trip.csv",stop_usage,list(stop_usage[0]))
    status_counter=Counter(x["frequency_staging_status"] for x in route_stopQA)
    summary={
       "SIU_trip_patterns_reused":len(trips),
       "SIU_ordered_stop_visits_in_model":len(stop_times),
       "distinct_physical_SIU_stops_referenced":len(stop_usage),
       "trip_templates_with_official_headway_and_provisional_2020_service_window":
           sum(x["model_frequency_periods"]>0 for x in route_stopQA),
       "frequency_model_period_rows":len(frequency),
       "frequency_trip_template_staging_statuses":dict(status_counter),
       "trip_patterns_with_large_source_stop_coordinate_gaps":
           sum(x["straight_line_gaps_over_threshold"]>0 for x in route_stopQA),
       "maximum_model_trip_duration_minutes":max(x["time_model_duration_minutes"] for x in route_stopQA),
       "timing_model_id":model_id,
       "timing_parameters":params,
       "real_runtimes_or_passage_times_observed":0,
       "trip_start_00_00_is_a_frequency_reference_not_actual_dispatch":True,
       "GTFS_routes_or_stops_modified":False,
       "GTFS_publication_approved":False
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=[
      "# SIU haltevolgorde -> GTFS trip templates + model-stop_times",
      "",
      "**Staging only: geen echte busrit- of passagevertrektijden.** De 20 routekoppelingen blijven voorlopig. "
      "De 3.981 stop_sequence-waarden komen uit SIU, en ALLE verwijzingen behouden de bestaande fysieke SIU stop_id.",
      "",
      "De trips worden als frequentie-gebaseerde sjablonen beschouwd: begin 00:00:00 in het stop_times-model is "
      "**een relatieve tijdreferentie**, geen echte eerste vertrek uit Barranquilla. "
      "De werkdagfrequenties volgen de officiële intervalresoluties waar al beschikbaar; "
      "begin/eind gebruikt het afgesproken provisorische **2020-vertrekvenster-model**.",
      "Per halte de reistijd van het vorige punt naar het volgende wordt ruw geschat via "
      "SIU-punt-tot-puntafstand, model-snelheid, wegafstandsfactor en halte-vertraging.",
      "Deze aannames zijn bewerkbaar in sources/amb/gtfs_timing_model_assumptions.csv.",
      "",
      "## Resultaten",
      "",
      f"- {len(trips)} trip-sjablonen; {len(stop_times)} geordende haltebezoeken met **uitsluitend modeltijden**.",
      f"- {len(stop_usage)} reeds bestaande fysieke SIU stop_id's hergebruikt (geen haltes per route aangemaakt).",
      f"- {sum(x['model_frequency_periods']>0 for x in route_stopQA)} trip-sjablonen beschikken over een officiële headway + voorlopig dispatchvenster; {len(frequency)} periode-records.",
      f"- {sum(x['straight_line_gaps_over_threshold']>0 for x in route_stopQA)} trip-sjablonen met grote stop-tot-stopafstand die handmatige review vergen.",
      f"- Grootste berekende modelritduur: {max(x['time_model_duration_minutes'] for x in route_stopQA)} minuten.",
      "",
      "## Volgende validatie vóór echte GTFS stop_times",
      "",
      "1. Leg echte of brononderbouwde begin-/eindritduur per route en richting vast om de modellen te ijken.",
      "2. Bevestig SIU -> juridische AMB routecode, vooral gedeelde operators en wettelijke A/B-varianten.",
      "3. Controleer dat elk stop_sequence werkelijk bij de gekozen trip-richting hoort, ook bij lussen en dubbele haltepassages.",
      "4. Vervang of kalibreer per-trip rijtijd door een route-/periode-specifiek model; pas daarna kalender en shapes valideren.",
      "5. Evalueer de verspreidings-/licentievoorwaarden van de SIU-data vóór GTFS-publicatie.",
      "",
      "Geen enkel bestand is naar gtfs/stop_times.txt of gtfs/trips.txt geschreven.",
      ""
    ]
    (OUT/"summary.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
