#!/usr/bin/env python3
"""Passive discovery of PUBLIC SIU JavaScript assets and route/stop path strings.

GET only publicly served HTML/asset-manifest/JS. Does NOT use user cookies,
tokens, authentication, protected APIs or requests to discovered endpoints.
Does not save full proprietary JS bundles, session information or secrets.
"""
import csv
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup

ORIGIN = "https://siu.ambq.gov.co"
ENTRY = ORIGIN + "/siu/schedule-mng/schedules"
MANIFEST = ORIGIN + "/siu/asset-manifest.json"

def allowed_asset(url):
    parsed = urlsplit(url)
    return parsed.scheme == "https" and parsed.hostname == "siu.ambq.gov.co" and parsed.path.endswith(".js")

def collect_literals(bundle):
    # Limit to URL-shaped strings / paths likely to identify schedule, route,
    # stop or geometry endpoints. Never emit headers, keys or auth data.
    vals=set()
    for match in re.finditer(r"""(?:"([^"\\\r\n]{2,210})"|'([^'\\\r\n]{2,210})')""",bundle):
        v=match.group(1) or match.group(2)
        if not re.search(r"(route|ruta|schedule|horario|stop|parada|paradero|itinerar|line|station|stationary|geoloc|location)",v,re.I):
            continue
        if re.search(r"(token|authorization|bearer|client_secret|password|cookie|keycloak|session|secret|api_key)",v,re.I):
            continue
        # Record API-like paths / method names, not user messages or HTML.
        if not (v.startswith("/") or v.startswith("http") or re.fullmatch(r"[a-zA-Z][\w./_-]{2,100}",v)):
            continue
        if v.startswith("http") and urlsplit(v).hostname not in ("siu.ambq.gov.co","sibus.ambq.gov.co"):
            continue
        vals.add(v)
    return sorted(vals)

def main():
    out=Path("build/siu-public-asset-audit")
    out.mkdir(parents=True,exist_ok=True)
    http=requests.Session()
    http.headers.update({"User-Agent":"ColombiaTransit-SIU-PublicAsset-Audit/1.0","Accept":"text/html,application/json,text/javascript,*/*"})
    errors=[];scripts=[]
    try:
        r=http.get(ENTRY,timeout=35);r.raise_for_status()
        soup=BeautifulSoup(r.text,"html.parser")
        scripts += [urljoin(ORIGIN,x["src"]) for x in soup.select("script[src]")]
    except requests.RequestException as e:
        errors.append({"step":"page","error_type":type(e).__name__})
    try:
        r=http.get(MANIFEST,timeout=35);r.raise_for_status()
        info=r.json()
        files=info.get("files",{})
        if isinstance(files,dict):
            scripts += [urljoin(ORIGIN,v) for v in files.values()
                if isinstance(v,str) and v.split("?")[0].endswith(".js")]
    except (requests.RequestException,ValueError,KeyError) as e:
        errors.append({"step":"asset_manifest","error_type":type(e).__name__})
    scripts=list(dict.fromkeys(u for u in scripts if allowed_asset(u)))
    assets=[];candidates=[]
    total=0
    for url in scripts[:100]:
        if total>40_000_000:break
        rec={"path":urlsplit(url).path}
        try:
            r=http.get(url,timeout=55);r.raise_for_status()
            js=r.text
            total+=len(r.content)
            rec["bytes"]=len(r.content)
            found=collect_literals(js)
            rec["candidate_literals"]=len(found)
            for val in found:
                candidates.append({"asset_path":rec["path"],"public_path_or_method":val})
        except requests.RequestException as e:
            rec["error_type"]=type(e).__name__
        assets.append(rec)
        print(f"{rec['path']}: {rec.get('candidate_literals',0)} relevant strings",flush=True)
    with (out/"public_string_candidates.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["asset_path","public_path_or_method"]);w.writeheader();w.writerows(candidates)
    summary={"entry":ENTRY,"asset_manifest":MANIFEST,"public_js_assets_discovered":len(scripts),
             "public_js_assets_scanned":len(assets),"js_bytes_scanned":total,
             "route_stop_string_candidates":len(candidates),"errors":errors,
             "note":"Passive public JS asset inspection ONLY. Paths are unverified API possibilities. No network calls to those endpoints."}
    (out/"summary.json").write_text(json.dumps({"summary":summary,"assets":assets},indent=2)+"\n",encoding="utf-8")
    (out/"summary.md").write_text(
        "# SIU public JavaScript research\n\n"+
        "\n".join(f"- {k}: {v}" for k,v in summary.items() if k not in ("errors",))+
        "\n\nRaw JS, login tokens and authenticated requests are NOT archived.\n",
        encoding="utf-8")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":
    main()
