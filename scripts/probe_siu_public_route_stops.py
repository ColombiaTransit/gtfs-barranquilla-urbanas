#!/usr/bin/env python3
"""Read ONE public SIU route's virtualized stop list with an anonymous browser.

No accounts/tokens, no guessed API calls, no scraping other users, no raw
response bodies/headers archived. Only public DOM stop labels/UUIDs and
sanitized XHR/FETCH endpoint metadata. Pilot limit: Alameda del Rio only.
"""
import asyncio
import csv
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright

URL = "https://siu.ambq.gov.co/siu/schedule-mng/schedules"
TARGET = "ALAMEDA DEL RIO"
OUT=Path("build/siu-public-route-probe")


async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    responses=[]
    pending=[]
    rows={}
    summary={"source_url":URL, "route_display_name":TARGET,
             "method":"anonymous_browser_public_DOM_virtual_scroll",
             "login_used":False,
             "status":"not_yet_attempted","route_uuid":None,
             "stop_count_discovered":0,"scroll_height":None,
             "viewport_height":None,"expected_count_from_pixels_not_verified":None,
             "response_endpoint_metadata_count":0,
             "coordinates_from_DOM":False}
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(headless=True,args=["--no-sandbox"])
        page=await browser.new_page(viewport={"width":1380,"height":950}, locale="es-CO")
        async def inspect(response):
            try:
                parsed=urlsplit(response.url)
                if parsed.hostname not in ("siu.ambq.gov.co","sibus.ambq.gov.co"):
                    return
                if response.request.resource_type not in ("xhr","fetch"):
                    return
                item={"endpoint_path":parsed.path,"status":response.status,
                      "method":response.request.method,
                      "resource_type":response.request.resource_type}
                if "/graphql/" in parsed.path:
                    try:
                        post = response.request.post_data_json or {}
                        if isinstance(post,dict):
                            item["graphql_operation_name"] = str(post.get("operationName") or "")
                            query = str(post.get("query") or "")
                            field_match = __import__("re").search(r"\\b(?:query|mutation)\\s+(\\w+)",query)
                            item["graphql_query_operation"] = field_match.group(1) if field_match else ""
                            item["graphql_variable_names"] = ";".join((post.get("variables") or {}).keys())
                    except Exception: pass
                ctype=(response.headers.get("content-type") or "").lower()
                if "json" in ctype:
                    try:
                        data=await asyncio.wait_for(response.json(),timeout=8)
                        if isinstance(data,dict):
                            item["json_type"]="object"
                            item["top_level_keys"]=";".join(str(k) for k in list(data)[:25])
                            payload=data.get("data")
                            if isinstance(payload,dict):
                                item["data_keys"]=";".join(str(k) for k in list(payload)[:25])
                                item["data_shapes"]=";".join(
                                    f"{k}:{'list_'+str(len(v)) if isinstance(v,list) else 'object' if isinstance(v,dict) else type(v).__name__}"
                                    for k,v in list(payload.items())[:16])
                        elif isinstance(data,list):
                            item["json_type"]="array"
                            item["root_array_length"]=len(data)
                        else:item["json_type"]=type(data).__name__
                    except Exception:item["json_type"]="unavailable"
                responses.append(item)
            except Exception:pass
        page.on("response",lambda r:pending.append(asyncio.create_task(inspect(r))))
        try:
            nav=await page.goto(URL,wait_until="domcontentloaded",timeout=60000)
            summary["page_http_status"]=nav.status if nav else None
            await page.get_by_text(TARGET,exact=True).first.wait_for(timeout=50000)
            summary["status"]="route_listing_loaded"
            # Virtualized Material-UI cards can be obstructed by an animation;
            # activate React's real li onClick via DOM instead of coordinates.
            label=page.get_by_text(TARGET,exact=True).first
            await label.evaluate("(el)=>{const li=el.closest('li'); if(li)li.click();else el.click();}")
            await page.wait_for_timeout(1600)
            await page.locator(".l-card__inner .title").first.wait_for(timeout=20000)
            summary["detail_title"]=await page.locator(".l-card__inner .title").first.inner_text()
            scrollers=page.locator(".l-card__inner div[style*='overflow: auto']")
            if await scrollers.count()==0:
                raise RuntimeError("Detail list lacks expected scroll container")
            scroll=scrollers.first
            dim=await scroll.evaluate("(el)=>({scrollHeight:el.scrollHeight,clientHeight:el.clientHeight})")
            summary["scroll_height"]=dim["scrollHeight"]
            summary["viewport_height"]=dim["clientHeight"]
            summary["expected_count_from_pixels_not_verified"]=round((dim["scrollHeight"]-10)/106)
            async def record_visible():
                visible=await page.evaluate("""() =>
                [...document.querySelectorAll('li[style*="position: absolute"]')]
                 .map(el => {
                  let wrapper=el.querySelector('[id^="js-stops-wrapper-"]');
                  let name=el.querySelector('.stops-details .name');
                  if(!wrapper||!name)return null;
                  let m=wrapper.id.match(/^js-stops-wrapper-([^/]+)\\/(.+)$/);
                  if(!m)return null;
                  return {route_uuid:m[1],stop_uuid:m[2],name:name.innerText,
                          offset_px:parseInt(el.style.top,10),
                          row_height_px:parseInt(el.style.height,10)};
                 }).filter(Boolean)""")
                for stop in visible:
                    idx=round(stop["offset_px"]/stop["row_height_px"])+1
                    stop["order_index_from_pixel_offset"]=idx
                    stop["route_name"]=TARGET
                    stop["gps_status"]="not_in_DOM"
                    stop["source_url"]=URL
                    rows[stop["stop_uuid"]]=stop
                    summary["route_uuid"]=stop["route_uuid"]
            await record_visible()
            maximum=max(0,dim["scrollHeight"]-dim["clientHeight"])
            stride=max(120,int(dim["clientHeight"]*.72))
            for offset in range(0,maximum+stride,stride):
                await scroll.evaluate("(el,offset)=>{el.scrollTop=offset}",min(offset,maximum))
                await page.wait_for_timeout(110)
                await record_visible()
            await scroll.evaluate("(el)=>{el.scrollTop=el.scrollHeight}")
            await page.wait_for_timeout(350)
            await record_visible()
            summary["status"]="virtual_scroll_completed"
        except Exception as exc:
            summary["status"]="failed_or_partial"
            summary["error_type"]=type(exc).__name__
            summary["error_short"]=str(exc)[:220]
        finally:
            if pending:
                await asyncio.gather(*pending,return_exceptions=True)
            await browser.close()
    ordered=sorted(rows.values(),key=lambda x:x["order_index_from_pixel_offset"])
    summary["stop_count_discovered"]=len(ordered)
    summary["unique_order_indices"]=len({x["order_index_from_pixel_offset"] for x in ordered})
    summary["response_endpoint_metadata_count"]=len(responses)
    if ordered:
        with (OUT/"alameda_rio_public_stops.csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(ordered[0]))
            w.writeheader();w.writerows(ordered)
    if responses:
        # Keep only safe endpoint path/method/metadata. Never cookies, querystrings,
        # response JSON, HTTP headers or credentials.
        unique=list({(r["endpoint_path"],r["method"],r["status"]):r for r in responses}.values())
        with (OUT/"public_xhr_endpoint_metadata.csv").open("w",newline="",encoding="utf-8") as f:
            keys=["endpoint_path","method","status","resource_type","json_type","top_level_keys","root_array_length","data_keys","data_shapes","graphql_operation_name","graphql_query_operation","graphql_variable_names"]
            w=csv.DictWriter(f,fieldnames=keys,extrasaction="ignore");w.writeheader();w.writerows(unique)
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (OUT/"summary.md").write_text(
        "# Anonymous SIU Alameda del Rio route-stop list probe\n\n"+
        "\n".join(f"- {k}: {v}" for k,v in summary.items())+
        "\n\nData comes from the public DOM; MHT UUIDs serve as a cross-check.\n"+
        "No login, unauthorized calls, secrets, request querystrings, raw responses or cookies archived.\n"+
        "No GTFS stops.txt or geographic coordinates inferred from names.\n",
        encoding="utf-8")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":
    asyncio.run(main())
