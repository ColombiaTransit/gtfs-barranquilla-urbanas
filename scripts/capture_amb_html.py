#!/usr/bin/env python3
"""Save unmodified HTTP HTML responses from the AMB archive for inspection."""
import json
from pathlib import Path
from urllib.parse import urljoin
import requests

BASE = "https://www.ambq.gov.co/secretaria-general/normatividad/resoluciones/"
OUT = Path("data/amb_html_diagnostic")
OUT.mkdir(parents=True, exist_ok=True)
session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (compatible; ColombiaTransit-archive-diagnostic/1.0)"
report = []
for year, url in [("index", BASE)] + [(str(y), urljoin(BASE, f"resoluciones-{y}/")) for y in range(2020, 2027)]:
    item = {"year": year, "requested_url": url}
    try:
        response = session.get(url, timeout=60, allow_redirects=True)
        item.update(status_code=response.status_code, final_url=response.url,
                    content_type=response.headers.get("content-type"),
                    encoding=response.encoding, byte_count=len(response.content),
                    response_headers=dict(response.headers),
                    redirect_history=[{"status": x.status_code, "url": x.url} for x in response.history])
        (OUT / f"{year}.html").write_bytes(response.content)
        (OUT / f"{year}.headers.json").write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        print(year, response.status_code, len(response.content), response.url, flush=True)
    except requests.RequestException as exc:
        item["error"] = str(exc)
        print(year, "ERROR", exc, flush=True)
    report.append(item)
(OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
