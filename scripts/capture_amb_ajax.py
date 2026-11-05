#!/usr/bin/env python3
"""Capture Ninja Tables AJAX data and diagnostics for AMB resolution years."""
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import requests
from bs4 import BeautifulSoup

BASE = "https://www.ambq.gov.co/secretaria-general/normatividad/resoluciones/"
OUT = Path("data/amb_ajax_diagnostic")
OUT.mkdir(parents=True, exist_ok=True)
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"})
summary = []
for year in range(2020, 2027):
    url = urljoin(BASE, f"resoluciones-{year}/")
    entry = {"year": year, "page_url": url}
    try:
        page = session.get(url, timeout=45)
        page.raise_for_status()
        html = page.text
        (OUT / f"{year}.html").write_bytes(page.content)
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.select("[data-ninja_table_id], [data-table_id], .ninja_table_wrapper, .nt_type_ajax_table")
        candidates = []
        for node in tables:
            for key, val in node.attrs.items():
                if "table" in key.lower() or "request" in key.lower():
                    candidates.append({"tag": node.name, "attribute": key, "value": str(val)[:1200]})
        # Extract table IDs from known Ninja Tables markup and from embedded configuration.
        ids = set()
        for node in soup.select("[data-ninja_table_id], [data-table_id], [data-footable_id]"):
            for key in ("data-ninja_table_id", "data-table_id", "data-footable_id"):
                if node.get(key) and str(node.get(key)).isdigit():
                    ids.add(str(node.get(key)))
        ids.update(re.findall(r'ninja_table_(\\d+)', html))
        ids.update(re.findall(r'["\\\']table_id["\\\']\\s*:\\s*["\\\']?(\\d+)', html))
        entry["table_ids"] = sorted(ids)
        entry["table_attributes"] = candidates[:30]
        (OUT / f"{year}.discovery.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
        # Discover AJAX URL directly in the page. A nonce is session/page-specific.
        request_urls = re.findall(r'"data_request_url"\s*:\s*"([^"]+)"', html)
        request_urls = [json.loads('"' + u + '"') for u in request_urls]
        urls = re.findall(r'https?[^"\\s<>]+admin-ajax\\.php[^"\\s<>]*', html)
        urls = [u.replace("&amp;", "&").replace("\\/", "/") for u in urls]
        urls = request_urls + urls
        ajax_base = "https://www.ambq.gov.co/wp-admin/admin-ajax.php"
        for table_id in sorted(ids):
            params = {"action": "wp_ajax_ninja_tables_public_action",
                      "table_id": table_id, "target_action": "get-all-data",
                      "default_sorting": "old_first", "skip_rows": "0", "limit_rows": "0"}
            matched = [u for u in urls if "table_id=" + table_id in u]
            if matched:
                parsed = urlparse(matched[0])
                for key, values in parse_qs(parsed.query).items():
                    if values:
                        params[key] = values[0]
                ajax_base = parsed.scheme + "://" + parsed.netloc + parsed.path
            # Look for nonce in inline JS if URL did not contain it.
            if "ninja_table_public_nonce" not in params:
                m = re.search(r'["\\\']ninja_table_public_nonce["\\\']\\s*:\\s*["\\\']([^"\\\']+)', html)
                if m:
                    params["ninja_table_public_nonce"] = m.group(1)
            headers = {"Referer": url, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json, text/javascript, */*; q=0.01"}
            response = session.get(ajax_base, params=params, headers=headers, timeout=90)
            prefix = f"{year}_table_{table_id}"
            (OUT / f"{prefix}.response.txt").write_bytes(response.content)
            result = {"table_id": table_id, "status": response.status_code, "final_url": response.url,
                      "content_type": response.headers.get("Content-Type"),
                      "bytes": len(response.content), "nonce_supplied": "ninja_table_public_nonce" in params}
            try:
                obj = response.json()
                (OUT / f"{prefix}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
                result["json_type"] = type(obj).__name__
                result["row_count"] = len(obj) if isinstance(obj, list) else None
                result["top_level_keys"] = list(obj)[:30] if isinstance(obj, dict) else None
            except ValueError:
                result["json_error"] = "Response was not JSON"
            entry.setdefault("requests", []).append(result)
        print(json.dumps({"year": year, "table_ids": entry["table_ids"], "requests": entry.get("requests", [])}, ensure_ascii=False), flush=True)
    except Exception as exc:
        entry["error"] = str(exc)
        print(f"{year}: ERROR {exc}", flush=True)
    if not entry.get("requests"):
        entry["error"] = entry.get("error", "No AJAX requests made")
    summary.append(entry)
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
