#!/usr/bin/env python3
"""Inspect the anonymized structure of the public SIU compressed itinerary response.

Observes a GraphQL response issued automatically by a fresh anonymous page.
No guessed API calls, authentication tokens, cookies or raw responses stored.
"""
import asyncio
import base64
import bz2
import gzip
import json
import lzma
import zlib
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright

PAGE="https://siu.ambq.gov.co/siu/schedule-mng/schedules"
ENDPOINT="/api/pis-gateway/graphql/http"
OUT=Path("build/siu-public-compressed-listing")


def describe(data, depth=0, max_depth=4):
    if depth>max_depth:return type(data).__name__
    if isinstance(data,dict):
        return {"type":"object","keys":list(data)[:100],
                "examples":{str(k):describe(v,depth+1,max_depth) for k,v in list(data.items())[:10]}}
    if isinstance(data,list):
        return {"type":"array","length":len(data),
                "first_item":describe(data[0],depth+1,max_depth) if data else None}
    if isinstance(data,str):return {"type":"string","length":len(data)}
    return {"type":type(data).__name__}


def collect_key_counts(value,counts,depth=0):
    if depth>12:return
    if isinstance(value,dict):
        for k,v in value.items():
            counts[str(k)]+=1
            collect_key_counts(v,counts,depth+1)
    elif isinstance(value,list):
        for v in value[:50000]:collect_key_counts(v,counts,depth+1)


def decode_compressed(blob):
    raw=base64.b64decode(blob,validate=True)
    methods=[
        ("gzip",gzip.decompress),
        ("zlib",zlib.decompress),
        ("raw_deflate",lambda x:zlib.decompress(x,-zlib.MAX_WBITS)),
        ("bz2",bz2.decompress),
        ("lzma",lzma.decompress),
        ("base64_uncompressed",lambda x:x),
    ]
    errors=[]
    for method,decoder in methods:
        try:
            decoded=decoder(raw)
            if len(decoded)>80_000_000:raise ValueError("uncompressed content too large")
            obj=json.loads(decoded.decode("utf-8-sig"))
            return method,decoded,obj,len(raw),errors
        except (ValueError,EOFError,OSError,UnicodeError,zlib.error) as exc:
            errors.append(method+":"+type(exc).__name__)
    return None,None,None,len(raw),errors


async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    summary={"page":PAGE,"graphql_endpoint_path":ENDPOINT,"page_load_http":None,
             "response_found":False,"status":"not_started",
             "no_authentication":True,"raw_response_archived":False}
    tasks=[]
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(headless=True,args=["--no-sandbox"])
        page=await browser.new_page(viewport={"width":1366,"height":880},locale="es-CO")
        async def on_response(response):
            if urlsplit(response.url).path!=ENDPOINT or response.status!=200:return
            try:
                payload=await response.json()
                source=((payload.get("data") or {}).get("ServiceMngCompressedItineraryListing") or {})
                b64=source.get("compressedModsBase64")
                if not isinstance(b64,str) or not b64:return
                summary["response_found"]=True
                summary["declared_base64_length"]=source.get("compressedModsBase64Length")
                summary["declared_uncompressed_length"]=source.get("modsStrLength")
                summary["declared_compression_ratio"]=source.get("compressionRatio")
                method,decoded,obj,compressed,errors=decode_compressed(b64)
                summary.update({"decode_method":method,"compressed_bytes":compressed,"tried_methods":errors})
                if method:
                    summary["status"]="decoded_json_successfully"
                    summary["uncompressed_bytes"]=len(decoded)
                    summary["root_structure"]=describe(obj)
                    counts=Counter()
                    collect_key_counts(obj,counts)
                    summary["frequent_data_keys"]=counts.most_common(80)
                    summary["route_stop_related_keys"]=[{"key":k,"count":n} for k,n in counts.items()
                        if any(part in k.casefold() for part in
                            ("stop","parada","lat","lon","coord","itiner","rout","ruta","path","name","nombre"))][:100]
                else:
                    summary["status"]="compressed_payload_decode_unknown"
            except Exception as exc:
                summary["status"]="response_read_error"
                summary["error_type"]=type(exc).__name__
        page.on("response",lambda resp:tasks.append(asyncio.create_task(on_response(resp))))
        try:
            r=await page.goto(PAGE,wait_until="domcontentloaded",timeout=65000)
            summary["page_load_http"]=r.status if r else None
            await page.wait_for_timeout(8500)
        except Exception as exc:
            summary["navigation_error_type"]=type(exc).__name__
        if tasks:await asyncio.gather(*tasks,return_exceptions=True)
        await browser.close()
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    compact={k:v for k,v in summary.items() if k not in ("root_structure","frequent_data_keys","route_stop_related_keys")}
    (OUT/"summary.md").write_text(
        "# SIU anonymous compressed itinerary response structure\n\n"+
        "\n".join(f"- {k}: {v}" for k,v in compact.items())+
        "\n\nOnly structural metadata is archived: no raw GraphQL response, compressed payload, account or token.\n",encoding="utf-8")
    print(json.dumps(compact,ensure_ascii=False,indent=2))
if __name__=="__main__":
    asyncio.run(main())
