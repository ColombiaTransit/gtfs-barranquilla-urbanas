#!/usr/bin/env python3
"""Read-only GTFS static / SIU TripUpdates readiness audit; never invent trip matches."""
import argparse,csv,io,json,zipfile
from collections import Counter,defaultdict
from pathlib import Path

def load(z,name):
    try:
        with z.open(name) as f:return list(csv.DictReader(io.TextIOWrapper(f,encoding="utf-8-sig",newline="")))
    except KeyError:return None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gtfs",required=True,help="Path to built static GTFS zip")
    p.add_argument("--siu",default="sources/siu/public_extract/siu_itineraries.csv")
    p.add_argument("--output",default="build/gtfs-tripupdates-readiness")
    a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.gtfs) as z:
        routes=load(z,"routes.txt");trips=load(z,"trips.txt");stops=load(z,"stops.txt")
        times=load(z,"stop_times.txt");freq=load(z,"frequencies.txt") or []
        calendar=load(z,"calendar.txt") or [];exceptions=load(z,"calendar_dates.txt") or []
    errors=[];warnings=[]
    for name,rows in [("routes.txt",routes),("trips.txt",trips),("stops.txt",stops),("stop_times.txt",times)]:
        if rows is None:errors.append("Missing "+name)
    if errors:
        (out/"report.json").write_text(json.dumps({"errors":errors},indent=2)+"\n")
        raise SystemExit("; ".join(errors))
    route_ids={x.get("route_id","") for x in routes};trip_ids={x.get("trip_id","") for x in trips}
    stop_ids={x.get("stop_id","") for x in stops};services={x.get("service_id","") for x in calendar+exceptions}
    for name,ids in [("route_id",route_ids),("trip_id",trip_ids),("stop_id",stop_ids)]:
        if "" in ids:errors.append("Blank "+name)
    for name,rows,key in [("routes",routes,"route_id"),("trips",trips,"trip_id"),("stops",stops,"stop_id")]:
        dup=[v for v,n in Counter(x.get(key,"") for x in rows).items() if n>1]
        if dup:errors.append(f"Duplicate {name} {key}: {len(dup)}")
    for t in trips:
        if t.get("route_id") not in route_ids:errors.append("Trip references missing route_id")
        if services and t.get("service_id") not in services:errors.append("Trip references missing service_id")
    stop_sequences=defaultdict(list)
    for s in times:
        if s.get("trip_id") not in trip_ids:errors.append("Stop time references missing trip_id")
        if s.get("stop_id") not in stop_ids:errors.append("Stop time references missing stop_id")
        try:seq=int(s.get("stop_sequence",""));stop_sequences[s["trip_id"]].append(seq)
        except (ValueError,KeyError):errors.append("Invalid stop_sequence")
    for trip,seq in stop_sequences.items():
        if len(seq)!=len(set(seq)):errors.append("Duplicate stop_sequence in trip")
    for t in trips:
        if len(stop_sequences[t["trip_id"]])<2:warnings.append("Trip with fewer than two stop_times")
    frequency_trip_ids=set()
    for f in freq:
        tid=f.get("trip_id","");frequency_trip_ids.add(tid)
        if tid not in trip_ids:errors.append("Frequency references missing trip_id")
        if f.get("exact_times","0") not in ("","0","1"):errors.append("Invalid exact_times")
        if not (f.get("start_time") and f.get("end_time") and f.get("headway_secs")):
            errors.append("Incomplete frequency window")
    siu_rows=[]
    if Path(a.siu).exists():
        with open(a.siu,encoding="utf-8-sig",newline="") as f:siu_rows=list(csv.DictReader(f))
    crosswalk=[]
    for s in siu_rows:
        crosswalk.append({
            "siu_itinerary_uuid":s.get("siu_itinerary_uuid",""),
            "siu_base_route_uuid":s.get("siu_base_route_uuid",""),
            "siu_org_uuid":s.get("siu_org_uuid",""),
            "siu_company_names":s.get("siu_company_names",""),
            "gtfs_route_id":s.get("gtfs_route_id","") if s.get("gtfs_match_reviewed")=="yes" else "",
            "route_match_reviewed":s.get("gtfs_match_reviewed","no"),
            "gtfs_trip_id":"","siu_service_id":"","trip_match_status":"unresolved",
            "start_date":"","start_time":"","start_time_source":"",
        })
    with (out/"siu_trip_match_register.csv").open("w",encoding="utf-8",newline="") as f:
        fields=["siu_itinerary_uuid","siu_base_route_uuid","siu_org_uuid","siu_company_names","gtfs_route_id","route_match_reviewed","gtfs_trip_id","siu_service_id","trip_match_status","start_date","start_time","start_time_source"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(crosswalk)
    result={"static_routes":len(routes),"static_trips":len(trips),"static_stops":len(stops),
            "static_stop_times":len(times),"frequency_rows":len(freq),
            "frequency_template_trips":len(frequency_trip_ids),
            "siu_itineraries":len(siu_rows),"reviewed_route_matches":sum(x["gtfs_route_id"] in route_ids and bool(x["gtfs_route_id"]) for x in crosswalk),
            "resolved_trip_matches":0,"errors":sorted(set(errors)),"warnings":dict(Counter(warnings)),
            "requirements":["Stable IDs across generator runs","Map SIU itinerary to route and stop pattern",
                            "Match SIU service to unique trip instance","For frequencies supply immutable start_date/start_time",
                            "Validate ETA units, semantics and freshness before protobuf publication"]}
    (out/"report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"report.md").write_text("# Static GTFS / SIU TripUpdates readiness\n\n"+
       "\n".join(f"- {k}: {v}" for k,v in result.items() if k not in ("errors","warnings","requirements"))+
       "\n\nErrors: "+str(len(result["errors"]))+"; warnings: "+str(sum(result["warnings"].values()))+
       "\n\nTrip IDs are deliberately not guessed from itinerary IDs.\n",encoding="utf-8")
    print((out/"report.md").read_text())
    if errors:raise SystemExit("Static GTFS contract errors: "+str(len(set(errors))))
if __name__=="__main__":main()
