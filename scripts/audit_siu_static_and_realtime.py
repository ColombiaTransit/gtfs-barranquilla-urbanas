#!/usr/bin/env python3
"""Public SIU source completeness and privacy-preserving realtime feasibility probe.

Captures only the existing anonymous browser's GraphQL response; does not guess
endpoints, authenticate, retain vehicle identifiers, or publish live vehicle data.
"""
import argparse
import asyncio
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright
from extract_siu_public_itinerary_stops import PAGE, ENDPOINT, unpack

OUT = Path("build/siu-source-audit")
STATIC_FIELDS = ("id", "routeId", "orgId", "n", "comps", "active", "stops")
STOP_FIELDS = ("id", "n", "lat", "lng", "dis")
SERVICE_FIELDS = ("id", "vin", "vp", "s", "ts", "stops", "newETA", "td", "itt")
SERVICE_STOP_FIELDS = ("id", "eta", "realETA", "dts")

def fields(rows, names):
    return {name: sum(isinstance(x, dict) and x.get(name) is not None for x in rows) for name in names}

def csv_write(path, rows, cols):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

def inspect(itineraries, snapshot, sample_index):
    route_rows, stop_rows = [], []
    statuses, itinerary_keys, stop_keys, service_keys, service_stop_keys = (Counter() for _ in range(5))
    service_count = 0
    service_stop_count = 0
    eta_count = 0
    invalid_coords = 0
    service_itineraries = 0
    for item in itineraries:
        if not isinstance(item, dict):
            continue
        itinerary_keys.update(item.keys())
        stops = item.get("stops") or []
        services = item.get("servs") or []
        if not isinstance(stops, list): stops = []
        if not isinstance(services, list): services = []
        service_itineraries += bool(services)
        route_rows.append({
            "snapshot_utc": snapshot, "sample_index": sample_index,
            "siu_itinerary_uuid": str(item.get("id") or ""),
            "siu_base_route_uuid": str(item.get("routeId") or ""),
            "siu_org_uuid": str(item.get("orgId") or ""),
            "name": str(item.get("n") or ""),
            "companies": ";".join(map(str, item.get("comps") or [])),
            "active": str(item.get("active")),
            "stop_count": len(stops), "service_count": len(services),
            "has_stops": bool(stops), "has_services": bool(services),
        })
        for seq, stop in enumerate(stops, 1):
            if not isinstance(stop, dict): continue
            stop_keys.update(stop.keys())
            lat, lon = stop.get("lat"), stop.get("lng")
            valid = (isinstance(lat, (int,float)) and not isinstance(lat,bool) and
                     isinstance(lon, (int,float)) and not isinstance(lon,bool) and
                     -90 <= lat <= 90 and -180 <= lon <= 180)
            invalid_coords += not valid
            stop_rows.append({
                "snapshot_utc": snapshot, "siu_itinerary_uuid": str(item.get("id") or ""),
                "sequence": seq, "siu_stop_uuid": str(stop.get("id") or ""),
                "stop_name": str(stop.get("n") or ""), "lat": lat if valid else "",
                "lon": lon if valid else "", "source_distance_uninterpreted": stop.get("dis"),
            })
        for service in services:
            if not isinstance(service, dict): continue
            service_count += 1
            service_keys.update(service.keys())
            statuses[str(service.get("s") or "missing")] += 1
            for stop in service.get("stops") or []:
                if not isinstance(stop, dict): continue
                service_stop_count += 1
                service_stop_keys.update(stop.keys())
                eta_count += stop.get("eta") is not None
    return route_rows, stop_rows, {
        "snapshot_utc": snapshot, "sample_index": sample_index,
        "itinerary_count": len(route_rows), "active_itinerary_count": sum(r["active"] == "True" for r in route_rows),
        "itineraries_with_stops": sum(r["has_stops"] for r in route_rows),
        "itineraries_with_services": service_itineraries,
        "stop_occurrences": len(stop_rows), "unique_stop_ids": len({r["siu_stop_uuid"] for r in stop_rows if r["siu_stop_uuid"]}),
        "invalid_coordinates": invalid_coords,
        "service_records": service_count, "service_stop_records": service_stop_count,
        "service_stop_eta_present": eta_count, "service_status_counts": dict(statuses),
        "observed_field_keys": {k: sorted(v) for k,v in (
            ("itinerary", itinerary_keys), ("stop", stop_keys),
            ("service", service_keys), ("service_stop", service_stop_keys))},
        "static_field_coverage": fields(itineraries, STATIC_FIELDS),
        "stop_field_coverage": fields([s for x in itineraries for s in (x.get("stops") or []) if isinstance(s,dict)], STOP_FIELDS),
        "service_field_coverage": fields([s for x in itineraries for s in (x.get("servs") or []) if isinstance(s,dict)], SERVICE_FIELDS),
        "service_stop_field_coverage": fields([st for x in itineraries for s in (x.get("servs") or []) if isinstance(s,dict) for st in (s.get("stops") or []) if isinstance(st,dict)], SERVICE_STOP_FIELDS),
    }

async def run(samples, interval):
    OUT.mkdir(parents=True, exist_ok=True)
    captured = []
    tasks = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width":1366,"height":880}, locale="es-CO")
        async def observe(resp):
            if urlsplit(resp.url).path != ENDPOINT or resp.status != 200:
                return
            try:
                data = await resp.json()
                obj = (data.get("data") or {}).get("ServiceMngCompressedItineraryListing")
                if isinstance(obj, dict) and isinstance(obj.get("compressedModsBase64"), str):
                    itineraries, packed, unpacked = unpack(obj)
                    captured.append((datetime.now(timezone.utc).isoformat(timespec="seconds"), itineraries, packed, unpacked))
            except Exception as exc:
                print("SIU decode failure:", type(exc).__name__)
        page.on("response", lambda resp: tasks.append(asyncio.create_task(observe(resp))))
        for index in range(samples):
            await page.goto(PAGE, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(10000)
            if index + 1 < samples:
                await page.wait_for_timeout(interval * 1000)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        await browser.close()
    if not captured:
        raise SystemExit("No anonymous compressed itinerary response captured")
    reports, latest_routes, latest_stops = [], [], []
    for i, (timestamp, data, packed, unpacked) in enumerate(captured, 1):
        routes, stops, report = inspect(data, timestamp, i)
        report["compressed_bytes"] = packed
        report["uncompressed_bytes"] = unpacked
        reports.append(report)
        latest_routes, latest_stops = routes, stops
    csv_write(OUT/"static_itineraries.csv", latest_routes, list(latest_routes[0]))
    csv_write(OUT/"static_route_stop_sequences.csv", latest_stops, list(latest_stops[0]))
    csv_write(OUT/"sample_metrics.csv", [
        {k:v for k,v in report.items() if isinstance(v,(str,int,float))}
        for report in reports
    ], ["snapshot_utc","sample_index","itinerary_count","active_itinerary_count",
        "itineraries_with_stops","itineraries_with_services","stop_occurrences",
        "unique_stop_ids","invalid_coordinates","service_records","service_stop_records",
        "service_stop_eta_present","compressed_bytes","uncompressed_bytes"])
    result = {
        "method": "Anonymous browser GraphQL observation; full responses and vehicle identifiers not stored",
        "source_url": PAGE, "graphql_path": ENDPOINT,
        "sample_count": len(reports), "samples": reports,
        "interpretation": {
            "static": "Route/stop source candidates, not a complete GTFS timetable; compare against AMB legal register and other sources",
            "realtime": "Presence of ETA/status data does not establish trip_id, start_date, schedule relationship or GTFS-RT validity",
            "time": "Source timestamps and ETA epoch units require explicit validation before feed generation",
            "license": "Public visibility does not establish redistribution rights",
        },
    }
    (OUT/"audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    first, last = reports[0], reports[-1]
    md = [
        "# SIU static completeness and dynamic GTFS-RT probe", "",
        f"Captured **{len(reports)}** anonymous GraphQL response(s) from {PAGE}.",
        "No vehicle identifiers, raw responses, cookies or tokens are persisted.", "",
        "## Static source (latest sample)", "",
        f"- Itineraries: **{last['itinerary_count']}**; active: **{last['active_itinerary_count']}**",
        f"- Route-stop occurrences: **{last['stop_occurrences']}**; unique stop IDs: **{last['unique_stop_ids']}**",
        f"- Missing/invalid stop coordinates: **{last['invalid_coordinates']}**",
        "- Exports: static_itineraries.csv, static_route_stop_sequences.csv", "",
        "## Dynamic sample coverage", "",
        f"- First sample: {first['service_records']} service records / {first['service_stop_eta_present']} stop ETAs",
        f"- Last sample: {last['service_records']} service records / {last['service_stop_eta_present']} stop ETAs",
        f"- Status counts (last): {json.dumps(last['service_status_counts'], ensure_ascii=False)}",
        "- Detailed field presence per sample in audit.json; no individual vehicle traces.", "",
        "## GTFS and GTFS-RT readiness", "",
        "- SIU does not by itself prove complete AMB route coverage, operating calendars, trip times, shapes or agency mapping.",
        "- ETA and vehicle status may support future TripUpdates, but trip matching, prediction semantics, timestamp units, freshness, coverage and publication rights are not verified.",
        "- VehiclePositions require observed geolocation and a stable vehicle-to-trip association; these have not been established.",
        "- No GTFS-RT feed is generated by this probe.",
    ]
    (OUT/"report.md").write_text("\n".join(md)+"\n", encoding="utf-8")
    print(json.dumps({"sample_count":len(reports),"last_sample":{k:v for k,v in last.items() if k in ("itinerary_count","stop_occurrences","service_records","service_stop_eta_present")}}, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--interval-seconds", type=int, default=60)
    args = parser.parse_args()
    if not 1 <= args.samples <= 8 or not 0 <= args.interval_seconds <= 300:
        parser.error("samples must be 1..8 and interval-seconds 0..300")
    asyncio.run(run(args.samples, args.interval_seconds))
