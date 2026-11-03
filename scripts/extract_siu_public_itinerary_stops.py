#!/usr/bin/env python3
"""Export *publicly displayed* SIU itinerary stop records through its own GraphQL load.

No login, no cookies from users, no guessed GraphQL operation, no raw response
storage. This runs a fresh anonymous Chromium page; it observes the GraphQL
response the web app itself issues. 'SIU public' is NOT automatically an open
data license, nor evidence of route operation or 2026 legal status.
"""
import asyncio
import base64
import csv
import json
import re
import zlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright

PAGE="https://siu.ambq.gov.co/siu/schedule-mng/schedules"
ENDPOINT="/api/pis-gateway/graphql/http"
OUT=Path("build/siu-gtfs-stops")
MHT_ROUTE_UUID="6948fedb-74b6-4a1f-9c33-dcac379a736b"
MHT_STOP_UUIDS=[
"a8d2fb20-4815-456d-85fa-aab56dbbfa84",
"4f2ab563-423a-416a-b8ec-4b4f7c4048a5",
"f4dd2c0d-696d-4ccb-a4f2-ea57de85fe68",
"cf007398-09de-4fd7-8c84-d963f5a6c0a6",
"43d1617f-996f-48fe-8b0a-77488eff8df6",
"0776208b-2fb7-424c-82db-35eb7ccf0bcd",
"8c244cf3-96c7-4f63-a1be-17759d6a370f",
"f70469ee-97ef-4172-b87d-6efb0112dfcd",
"7bca28d4-a661-4914-a5b7-3b86d2237d57",
"ea68bc06-6dea-4370-aec5-204668966312",
]


def to_csv(path,rows,columns):
    with path.open("w",encoding="utf-8",newline="") as handle:
        w=csv.DictWriter(handle,fieldnames=columns,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def unpack(response_obj):
    b64=response_obj["compressedModsBase64"]
    packed=base64.b64decode(b64,validate=True)
    uncompressed=zlib.decompress(packed)
    if len(uncompressed)>80_000_000:
        raise ValueError("Response exceeds safe decompression limit")
    decoded=json.loads(uncompressed.decode("utf-8-sig"))
    if not isinstance(decoded,list) or not decoded or not isinstance(decoded[0],list):
        raise ValueError("Unknown SIU compressed itinerary root schema")
    if not decoded[0] or not isinstance(decoded[0][0],dict):
        raise ValueError("Missing SIU itinerary objects")
    return decoded[0],len(packed),len(uncompressed)


async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    tasks=[]
    results=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        page=await browser.new_page(viewport={"width":1366,"height":880},locale="es-CO")
        async def observe(resp):
            if urlsplit(resp.url).path!=ENDPOINT or resp.status!=200:return
            try:
                payload=await resp.json()
                record=(payload.get("data") or {}).get("ServiceMngCompressedItineraryListing")
                if isinstance(record,dict) and isinstance(record.get("compressedModsBase64"),str):
                    results.append(unpack(record))
            except Exception as e:
                print("Public data packet could not be decoded:",type(e).__name__)
        page.on("response",lambda r:tasks.append(asyncio.create_task(observe(r))))
        await page.goto(PAGE,wait_until="domcontentloaded",timeout=60000)
        await page.wait_for_timeout(10000)
        if tasks: await asyncio.gather(*tasks,return_exceptions=True)
        await browser.close()
    if not results:raise SystemExit("No public SIU itinerary packet; inspect portal availability")
    itineraries,compressed_size,uncompressed_size=results[0]
    snapshot=datetime.now(timezone.utc).isoformat(timespec="seconds")
    routes=[]
    all_stops=[]
    stops_by_uuid=defaultdict(list)
    invalid_coordinates=[]
    for item in itineraries:
        route_uuid=str(item.get("id") or "")
        base_uuid=str(item.get("routeId") or "")
        company=";".join(str(n) for n in (item.get("comps") or []))
        name=str(item.get("n") or "")
        entries=item.get("stops") or []
        is_test=(name.strip().casefold()=="1234" or "PRUEBAS" in company.upper())
        routes.append({
            "siu_itinerary_uuid":route_uuid,"siu_base_route_uuid":base_uuid,
            "siu_org_uuid":str(item.get("orgId") or ""),
            "siu_display_name":name,"siu_company_names":company,
            "siu_active":str(bool(item.get("active"))).lower(),
            "likely_test_itinerary":str(is_test).lower(),
            "stop_count":len(entries),"first_stop_name":str(entries[0].get("n") or "") if entries else "",
            "last_stop_name":str(entries[-1].get("n") or "") if entries else "",
            "gtfs_route_id":"", "gtfs_match_reviewed":"no",
            "source_snapshot_utc":snapshot,"source_url":PAGE
        })
        for index,stop in enumerate(entries,1):
            stop_uuid=str(stop.get("id") or "")
            lat=stop.get("lat");lon=stop.get("lng")
            lat_ok=isinstance(lat,(float,int)) and -90<=lat<=90
            lon_ok=isinstance(lon,(float,int)) and -180<=lon<=180
            if not lat_ok or not lon_ok:
                invalid_coordinates.append({"route_uuid":route_uuid,"stop_uuid":stop_uuid,"stop_sequence":index})
            row={
                "siu_itinerary_uuid":route_uuid,"siu_base_route_uuid":base_uuid,
                "siu_display_name":name,"siu_companies":company,
                "siu_stop_sequence":index,"siu_stop_uuid":stop_uuid,
                "stop_name":str(stop.get("n") or ""),
                "stop_lat":lat if lat_ok else "", "stop_lon":lon if lon_ok else "",
                "source_dis_uninterpreted":str(stop.get("dis") or ""),
                "siu_active":str(bool(item.get("active"))).lower(),
                "likely_test_itinerary":str(is_test).lower(),
                "gtfs_route_code_verified":"no",
                "source_url":PAGE,"source_snapshot_utc":snapshot
            }
            all_stops.append(row)
            stops_by_uuid[stop_uuid].append(row)

    unique_stops=[]
    coordinate_discrepancies=0
    for stop_uuid,occurrences in sorted(stops_by_uuid.items()):
        coords={(x["stop_lat"],x["stop_lon"]) for x in occurrences}
        names={x["stop_name"] for x in occurrences}
        if len(coords)>1:coordinate_discrepancies+=1
        unique_stops.append({
            "siu_stop_uuid":stop_uuid,"stop_name":occurrences[0]["stop_name"],
            "stop_lat":occurrences[0]["stop_lat"],"stop_lon":occurrences[0]["stop_lon"],
            "stop_name_variants":";".join(sorted(names)),
            "route_occurrences":len(occurrences),
            "number_of_itineraries":len({x["siu_itinerary_uuid"] for x in occurrences}),
            "coordinate_variants":len(coords),
            "source_snapshot_utc":snapshot,
            "gtfs_stop_id_candidate":"SIU_"+stop_uuid,
            "source_is_public_SIU":"yes",
            "source_reuse_license_verified":"no"
        })

    to_csv(OUT/"siu_itineraries.csv",routes,list(routes[0]))
    to_csv(OUT/"siu_route_stop_sequences.csv",all_stops,list(all_stops[0]))
    to_csv(OUT/"siu_unique_stops.csv",unique_stops,list(unique_stops[0]))
    target=next((r for r in itineraries if str(r.get("id"))==MHT_ROUTE_UUID),None)
    mht_comparison={"mht_route_uuid_found":target is not None,"mht_route_name":target.get("n") if target else None,
                    "mht_stop_sample_count":len(MHT_STOP_UUIDS),"matched_uuid_in_target_route":0,
                    "matched_uuid_at_expected_position_75_84":0,
                    "mht_sample_position_in_latest_route":[]}
    if target:
        ids=[str(x.get("id")) for x in (target.get("stops") or [])]
        for i,uid in enumerate(MHT_STOP_UUIDS):
            if uid in ids:
                mht_comparison["matched_uuid_in_target_route"]+=1
                seq=ids.index(uid)+1
                mht_comparison["mht_sample_position_in_latest_route"].append(seq)
                if seq==75+i:mht_comparison["matched_uuid_at_expected_position_75_84"]+=1
    s={
        "source":"Anonymous SIU public GraphQL generated by the original browser",
        "source_url":PAGE,"source_graphql_path":ENDPOINT,
        "snapshot_utc":snapshot,
        "compression":"base64+zlib",
        "compressed_bytes":compressed_size,"decompressed_bytes":uncompressed_size,
        "siu_itineraries":len(routes),
        "siu_active_itineraries":sum(x["siu_active"]=="true" for x in routes),
        "likely_test_itineraries":sum(x["likely_test_itinerary"]=="true" for x in routes),
        "route_stop_occurrences":len(all_stops),
        "unique_stop_uuids":len(unique_stops),
        "stops_without_valid_lat_lon":len(invalid_coordinates),
        "unique_stops_with_coordinate_conflicts":coordinate_discrepancies,
        "companies_in_siu":sorted(set(x["siu_company_names"] for x in routes)),
        "mht_crosscheck":mht_comparison,
        "note":"SIU itinerary coverage is not the entire 97-route AMB license register; GTFS code mapping/geometry and publication rights require review.",
    }
    (OUT/"summary.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# SIU TPC haltegegevens — publieke gecomprimeerde itinerarylijst","",
           f"**Vastlegging:** {snapshot}. **Bron:** {PAGE}. Anonieme openbare browser zonder account.",
           f"**{len(routes)} SIU-itineraries, {len(all_stops)} route-haltevermeldingen, {len(unique_stops)} unieke halte-UUID's.**",
           f"**GPS-validatie:** {len(invalid_coordinates)} ontbrekende of ongeldige coördinaten; {coordinate_discrepancies} UUID's met uiteenlopende coördinaten.",
           "",
           "## Twee MHT-opnamen als tegencontrole", "",
           f"- SIU-route-UUID gevonden: {mht_comparison['mht_route_uuid_found']}",
           f"- Tien zichtbare stop-UUID's gevonden binnen SIU-route: {mht_comparison['matched_uuid_in_target_route']}/10",
           f"- Exact dezelfde posities als de virtuele browserlijst 75–84: {mht_comparison['matched_uuid_at_expected_position_75_84']}/10",
           "", "## Beperkingen", "",
           "- De officiële SIU-weergavenamen mogen niet zonder expliciete crosswalk gelijkgesteld worden met AMB-routecodes.",
           "- SIU is geen GTFS op zichzelf. De data levert GPS-haltes en routevolgorde, nog geen gevalideerde trip times of huidige vergunningstatus.",
           "- Testitineraries zijn apart gemarkeerd. Combinatietrajecten en A/B-varianten vereisen aparte beoordeling.",
           "- Bron is publiek leesbaar, maar **hergebruik- en publicatierechten zijn nog niet bevestigd**.",
           "- Geen response-JSON, login/cookies, JWT's of GraphQL-authgegevens zijn opgeslagen.",
           "- Geen voertuigaantallen verwerkt."]
    (OUT/"summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in s.items() if k not in ("companies_in_siu",)},ensure_ascii=False,indent=2))
if __name__=="__main__":
    asyncio.run(main())
