#!/usr/bin/env python3
"""Observe public SIU route UI and GraphQL metadata without archiving values."""
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright

PAGE = "https://siu.ambq.gov.co/siu/schedule-mng/schedules"
ENDPOINT = "/api/pis-gateway/graphql/http"
OUT = Path("build/siu-mht-route-graphql")
ROUTE = "VILLA CAROLINA ZOOLOGICO"
SENSITIVE = re.compile(r"token|cookie|authorization|secret|password|jwt|plate|placa|imei|phone|email|driver|conductor", re.I)

def fields(obj, depth=0):
    if depth > 4 or not isinstance(obj, dict):
        return []
    result = []
    for key, value in list(obj.items())[:80]:
        if not isinstance(key, str) or SENSITIVE.search(key):
            continue
        result.append(key)
        if isinstance(value, dict):
            result.extend(key + "." + item for item in fields(value, depth + 1))
    return result[:120]

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events, tasks, ui = [], [], []
    phase = {"value": "initial"}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1366, "height": 880}, locale="es-CO")
        async def capture(response):
            if urlsplit(response.url).path != ENDPOINT or len(events) >= 100:
                return
            record = {"phase": phase["value"], "status": response.status, "method": response.request.method}
            try:
                request = response.request.post_data_json
                if isinstance(request, dict):
                    record["operation"] = str(request.get("operationName") or "unknown")[:100]
                    record["variable_names"] = sorted(k for k in (request.get("variables") or {}) if isinstance(k, str) and not SENSITIVE.search(k))
                    query = request.get("query")
                    if isinstance(query, str):
                        record["query_operation_names"] = re.findall(r"\\b(?:query|mutation|subscription)\\s+([A-Za-z][A-Za-z0-9_]*)", query)[:20]
            except Exception:
                record["request_parse"] = "unavailable"
            try:
                body = await response.json()
                record["response_field_names"] = fields(body)
            except Exception:
                record["response_parse"] = "unavailable"
            events.append(record)
        page.on("response", lambda response: tasks.append(asyncio.create_task(capture(response))))
        try:
            await page.goto(PAGE, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(10000)
            ui.append({"stage": "initial", "route_titles": await page.locator(".l-card__inner .title").count(),
                       "stop_cards": await page.locator(".stops-card").count(),
                       "mui_selects": await page.locator('[role="button"][aria-haspopup="listbox"]').count()})
            phase["value"] = "route_select"
            # The user-supplied MHT identifies the route title and rendered stop card.
            title = page.locator(".l-card__inner .title").filter(has_text=ROUTE)
            if await title.count():
                ui.append({"stage": "route_select", "outcome": "already_open"})
            else:
                # Only interact with visible public controls; no speculative API calls.
                route_text = page.get_by_text(ROUTE, exact=True)
                if await route_text.count() and await route_text.first.is_visible():
                    await route_text.first.click(timeout=5000)
                    ui.append({"stage": "route_select", "outcome": "clicked_visible_route_text"})
                else:
                    ui.append({"stage": "route_select", "outcome": "route_not_visible"})
            await page.wait_for_timeout(4000)
            phase["value"] = "stop_select"
            cards = page.locator(".stops-card")
            if await cards.count():
                await cards.first.click(timeout=5000)
                ui.append({"stage": "stop_select", "outcome": "clicked_first_stop"})
            else:
                ui.append({"stage": "stop_select", "outcome": "no_stop_cards"})
            await page.wait_for_timeout(6000)
            ui.append({"stage": "final", "route_titles": await page.locator(".l-card__inner .title").count(),
                       "stop_cards": await page.locator(".stops-card").count()})
        except Exception as exc:
            ui.append({"stage": "browser", "error_type": type(exc).__name__})
        finally:
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            await browser.close()
    report = {"snapshot_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "public_page": PAGE, "graphql_path": ENDPOINT,
              "mht_reference_route": ROUTE, "ui_steps": ui,
              "graphql_events": events, "event_count": len(events),
              "operation_names": sorted(set(e.get("operation", "unknown") for e in events)),
              "note": "Anonymous public browser observations; no query variables, response values, cookies or vehicle identifiers archived."}
    (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# SIU MHT-based route and stop GraphQL metadata", "",
             f"Events: {len(events)}", "", "## UI actions", ""]
    lines += ["- " + json.dumps(step, ensure_ascii=False) for step in ui]
    lines += ["", "## GraphQL operations", ""]
    lines += ["- " + name for name in report["operation_names"]]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"event_count": len(events), "ui_steps": ui, "operation_names": report["operation_names"]}, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
