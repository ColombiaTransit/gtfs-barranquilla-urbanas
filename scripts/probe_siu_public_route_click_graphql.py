#!/usr/bin/env python3
"""Passive anonymous SIU route-click GraphQL metadata study.

Observe only requests emitted by the public web UI. No direct API calls, login,
cookies, request variables, response values, vehicle IDs, plates or raw payloads
are stored. A route click may be unavailable in headless mode: report that
honestly rather than treating an empty capture as evidence of no endpoint.
"""
import asyncio
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright
from extract_siu_public_itinerary_stops import unpack

PAGE = "https://siu.ambq.gov.co/siu/schedule-mng/schedules"
ENDPOINT = "/api/pis-gateway/graphql/http"
OUT = Path("build/siu-route-click-graphql")
MAX_EVENTS = 80
SENSITIVE = re.compile(r"(token|cookie|authorization|secret|password|jwt|plate|placa|license|imei|phone|email|name|nombre|driver|conductor|vehicleid|deviceid)", re.I)
RELEVANT = re.compile(r"(arrival|departure|next|schedule|time|eta|vehicle|bus|fleet|route|itiner|status|prediction|tracking|dispatch|position|location|gps|horario|salida|llegada|proximo|vehiculo)", re.I)
SAFE_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,79}$")

def names_only(obj, depth=0):
    """Return bounded schema keys, never JSON values or array contents."""
    if depth > 5:
        return []
    if isinstance(obj, dict):
        out = []
        for key, value in list(obj.items())[:60]:
            if not isinstance(key, str) or not SAFE_NAME.fullmatch(key) or SENSITIVE.search(key):
                continue
            out.append(key)
            if isinstance(value, dict):
                out.extend(key + "." + x for x in names_only(value, depth + 1))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                out.extend(key + "[]." + x for x in names_only(value[0], depth + 1))
        return out[:100]
    return []

def operation_name(request):
    # Metadata only. No variables, query text or headers are saved.
    try:
        data = request.post_data_json
        if isinstance(data, dict):
            value = data.get("operationName")
            if isinstance(value, str) and SAFE_NAME.fullmatch(value) and not SENSITIVE.search(value):
                return value
    except Exception:
        pass
    return "unknown"

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events, pending, listing_labels = [], [], []
    state = {"phase": "initial", "clicked": False, "click_target": "none", "route_cards_seen": 0}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 390, "height": 844}, locale="es-CO")
        async def capture(response):
            if urlsplit(response.url).path != ENDPOINT or len(events) >= MAX_EVENTS:
                return
            event = {
                "phase": state["phase"],
                "method": response.request.method,
                "http_status": response.status,
                "operation_name": operation_name(response.request),
                "response_field_names": [],
                "relevant_field_names": [],
            }
            if response.status == 200:
                try:
                    body = await response.json()
                    if event["operation_name"] == "ServiceMngCompressedItineraryListing":
                        record = (body.get("data") or {}).get("ServiceMngCompressedItineraryListing") if isinstance(body, dict) else None
                        if isinstance(record, dict) and isinstance(record.get("compressedModsBase64"), str):
                            itineraries, _, _ = unpack(record)
                            for item in itineraries:
                                if not isinstance(item, dict):
                                    continue
                                label = item.get("n")
                                if isinstance(label, str) and 2 <= len(label) <= 75 and label not in listing_labels:
                                    listing_labels.append(label)
                            event["decoded_itinerary_count"] = len(itineraries)
                            event["decoded_route_labels_count"] = len(listing_labels)
                    fields = sorted(set(names_only(body)))
                    event["response_field_names"] = fields[:100]
                    event["relevant_field_names"] = [x for x in fields if RELEVANT.search(x)][:60]
                except Exception as exc:
                    event["response_parse"] = "decode_or_parse_failed"
                    event["parse_error_type"] = type(exc).__name__
            events.append(event)
        page.on("response", lambda r: pending.append(asyncio.create_task(capture(r))))
        try:
            await page.goto(PAGE, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(10000)
            state["phase"] = "route_click"
            # User confirms the vehicle display appears after clicking a route.
            # Prefer visible route cards; do not click login, maps, or vehicle buttons.
            candidates = [
                page.locator("mat-card").filter(has_text=re.compile(r"ruta|pr[oó]ximo|itiner", re.I)),
                page.locator(".route-card"),
                page.locator("[class*='route-card']"),
                page.locator("[class*='route-item']"),
                page.locator("mat-card"),
            ]
            for selector in candidates:
                try:
                    count = await selector.count()
                    state["route_cards_seen"] = max(state["route_cards_seen"], count)
                    if count:
                        item = selector.first
                        if await item.is_visible(timeout=1500):
                            await item.click(timeout=5000)
                            state["clicked"] = True
                            state["click_target"] = "public_route_card"
                            break
                except Exception:
                    continue
            if not state["clicked"] and listing_labels:
                # Use route names observed in the public listing; no IDs or values are persisted.
                for label in listing_labels[:20]:
                    try:
                        target = page.get_by_text(label, exact=False)
                        if await target.count() and await target.first.is_visible():
                            await target.first.click(timeout=3500)
                            state["clicked"] = True
                            state["click_target"] = "graphql_listing_matched_visible_route"
                            break
                    except Exception:
                        continue
            if not state["clicked"]:
                # Fallback: visible route heading or link, not arbitrary controls.
                for selector in [page.get_by_text("VILLA CAROLINA ZOOLOGICO", exact=False),
                                 page.get_by_text("PUERTA DORADA", exact=False)]:
                    try:
                        if await selector.count() and await selector.first.is_visible():
                            await selector.first.click(timeout=5000)
                            state["clicked"] = True
                            state["click_target"] = "visible_public_route_title"
                            break
                    except Exception:
                        continue
            await page.wait_for_timeout(10000 if state["clicked"] else 3000)
        except Exception as e:
            state["browser_error_type"] = type(e).__name__
        finally:
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)
            await browser.close()
    initial = [x for x in events if x["phase"] == "initial"]
    after = [x for x in events if x["phase"] == "route_click"]
    baseline = {(x["operation_name"], tuple(x["response_field_names"])) for x in initial}
    new = [x for x in after if (x["operation_name"], tuple(x["response_field_names"])) not in baseline]
    summary = {
        "snapshot_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "public_page": PAGE, "graphql_path": ENDPOINT,
        "clicked": state["clicked"], "click_target": state["click_target"],
        "route_cards_seen": state["route_cards_seen"],
        "graphql_listing_candidate_count": len(listing_labels),
        "decoded_itinerary_count": max((e.get("decoded_itinerary_count", 0) for e in events), default=0),
        "initial_graphql_responses": len(initial),
        "after_click_graphql_responses": len(after),
        "new_operation_or_schema_responses": len(new),
        "observed_operation_names_initial": sorted(set(x["operation_name"] for x in initial)),
        "observed_operation_names_after_click": sorted(set(x["operation_name"] for x in after)),
        "new_relevant_schema_fields": sorted(set(f for x in new for f in x["relevant_field_names"])),
        "capture_limit": MAX_EVENTS,
        "interpretation": "Metadata only; no proof that times are actual departures, predictions or schedules.",
        "status": "clicked_and_observed" if state["clicked"] and after else "inconclusive",
    }
    if "browser_error_type" in state:
        summary["browser_error_type"] = state["browser_error_type"]
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "graphql_schema_metadata.json").write_text(json.dumps(events, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = [
        "# Publieke SIU-routeklik — GraphQL metadata", "",
        f"Moment: {summary['snapshot_utc']}",
        f"Route aangeklikt: {state['clicked']} ({state['click_target']})",
        f"GraphQL-antwoorden vóór/na klik: {len(initial)} / {len(after)}",
        f"Nieuwe operaties of schemastructuren na klik: {len(new)}", "",
        "## Operatienamen na routeklik", "",
        *["- " + x for x in summary["observed_operation_names_after_click"]],
        "", "## Relevante nieuwe veldnamen", "",
        *["- " + x for x in summary["new_relevant_schema_fields"]],
        "", "## Grenzen", "",
        "- Alleen browser-veroorzaakte openbare requests; geen direct geconstrueerde GraphQL-query.",
        "- Openbare listinglabels worden uitsluitend tijdelijk gebruikt voor UI-matching, niet opgeslagen.",
        "- Geen requestvariabelen, ruwe responses, kentekens, voertuig-ID's, cookies of tokens opgeslagen.",
        "- Een mislukte klik of lege capture betekent **onbeslist**, niet dat het endpoint ontbreekt.",
        "- Geen gevolgtrekking over feitelijke ritten of dienstregeling zonder semantische validatie.",
    ]
    (OUT / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
