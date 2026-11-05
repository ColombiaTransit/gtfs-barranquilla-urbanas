#!/usr/bin/env python3
"""Archive AMB resolution PDFs for 2020–2026, with page-level OCR fallback."""
import argparse, csv, hashlib, json, re, subprocess, tempfile, time
from pathlib import Path
from urllib.parse import urljoin, urlparse
import fitz
import requests
from bs4 import BeautifulSoup

BASE = "https://www.ambq.gov.co/secretaria-general/normatividad/resoluciones/"
FIELDS = ["year","resolution","title","source_page","pdf_url","file","sha256","pages","ocr_pages","status","error"]

def fetch(session, url):
    for attempt in range(4):
        try:
            r = session.get(url, timeout=(20, 90))
            r.raise_for_status()
            return r
        except requests.RequestException:
            if attempt == 3: raise
            time.sleep(2 ** attempt)

def discover(session, year, out):
    """Read the actual Ninja Tables JSON, preserving original rows as evidence."""
    page = urljoin(BASE, f"resoluciones-{year}/")
    html = fetch(session, page).text
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("[data-footable_id]")
    if table is None:
        raise ValueError("Ninja Tables data-footable_id not found")
    table_id = str(table["data-footable_id"])
    import html as html_lib
    from urllib.parse import parse_qs, urlsplit
    matches = re.findall(r'data_request_url[^\n]{0,1500}', html)
    request_url = None
    for match in matches:
        decoded = html_lib.unescape(match).replace("\\/", "/")
        m = re.search(r'https?://[^"\s<>]+admin-ajax\\.php[^"\s<>]*', decoded)
        if m:
            request_url = m.group(0).rstrip('\\')
            break
    if not request_url:
        # The live page's Ninja Tables configuration includes the AJAX URL in JSON.
        m = re.search(r'"data_request_url"\s*:\s*"([^"]+)"', html)
        if m:
            request_url = json.loads('"' + m.group(1) + '"')
    if not request_url:
        raise ValueError("Ninja Tables data_request_url not found")
    request_url = html_lib.unescape(request_url)
    response = fetch(session, request_url)
    rows = response.json()
    if not isinstance(rows, list):
        raise ValueError("Unexpected Ninja Tables response: not a JSON list")
    evidence = out / "source_json"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / f"{year}_table_{table_id}.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    found = {}
    for row_index, row in enumerate(rows):
        value = row.get("value", {})
        title_html = str(value.get("ttulo", ""))
        title = BeautifulSoup(title_html, "html.parser").get_text(" ", strip=True)
        links = []
        for field in ("ttulo", "documento"):
            for a in BeautifulSoup(str(value.get(field, "")), "html.parser").select("a[href]"):
                link = urljoin(page, a["href"]).split("#")[0]
                if urlparse(link).path.lower().endswith(".pdf"):
                    links.append(link)
        for link in dict.fromkeys(links):
            m = re.search(r"(\\d{1,4})\\s*[-_/]\\s*(20\\d{2}|\\d{2})(?!\\d)", title + " " + link)
            code = ""
            if m:
                yy = m.group(2)
                code = f"{int(m.group(1)):03d}-{('20' + yy) if len(yy) == 2 else yy}"
            found[link] = dict(year=year, resolution=code, title=title[:1000],
                               source_page=page, pdf_url=link)
    (evidence / f"{year}_discovery.json").write_text(json.dumps(
        {"year": year, "table_id": table_id, "row_count": len(rows),
         "unique_pdf_count": len(found),
         "rows_without_pdf": [
             {"index": i, "value": row.get("value", {})}
             for i, row in enumerate(rows)
             if not any(urlparse(urljoin(page, a["href"])).path.lower().endswith(".pdf")
                        for field in ("ttulo", "documento")
                        for a in BeautifulSoup(str(row.get("value", {}).get(field, "")), "html.parser").select("a[href]"))
         ]}, ensure_ascii=False, indent=2), encoding="utf-8")
    if not rows or not found:
        raise ValueError(f"No rows or PDF links found in table {table_id}")
    print(f"{year}: table {table_id}, {len(rows)} rows, {len(found)} unique PDFs", flush=True)
    return list(found.values())

def extract(pdf, txt, min_chars):
    doc = fitz.open(pdf)
    parts, ocr_pages = [], []
    for i, page in enumerate(doc):
        native = page.get_text("text", sort=True).strip()
        content = native
        if len(re.sub(r"\s", "", native)) < min_chars:
            with tempfile.TemporaryDirectory() as tmp:
                png = Path(tmp) / "page.png"
                page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(png)
                proc = subprocess.run(["tesseract", str(png), "stdout", "-l", "spa", "--psm", "3"], capture_output=True, text=True, timeout=180)
                if proc.returncode == 0 and len(proc.stdout.strip()) > len(native):
                    content = proc.stdout.strip()
                    ocr_pages.append(i + 1)
        parts.append(f"\n\n===== PAGE {i+1} =====\n{content}")
    txt.write_text("".join(parts).lstrip(), encoding="utf-8")
    return len(doc), ocr_pages

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2020)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--out", default="data/amb_resolutions")
    ap.add_argument("--min-chars", type=int, default=100)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "ColombiaTransit-AMB-archive/1.0"
    manifest_path = out / "manifest.json"
    old = {r["pdf_url"]: r for r in json.loads(manifest_path.read_text())} if manifest_path.exists() else {}
    records = dict(old)
    errors = []
    for year in range(args.start, args.end + 1):
        try:
            entries = discover(session, year, out)
            print(f"{year}: {len(entries)} PDF links", flush=True)
            if not entries: errors.append({"year": year, "error": "No PDF links found"})
        except Exception as exc:
            errors.append({"year": year, "error": str(exc)})
            continue
        for item in entries:
            url = item["pdf_url"]
            ident = hashlib.sha256(url.encode()).hexdigest()[:12]
            folder = out / str(year)
            folder.mkdir(exist_ok=True)
            stem = f"{item['resolution'] or 'unnumbered'}_{ident}"
            pdf, txt = folder / f"{stem}.pdf", folder / f"{stem}.txt"
            record = dict(**item, file=str(pdf.relative_to(out)), sha256="", pages="", ocr_pages=[], status="", error="")
            try:
                if not pdf.exists() or not pdf.stat().st_size:
                    body = fetch(session, url).content
                    if not body.startswith(b"%PDF-"): raise ValueError("Not a PDF response")
                    pdf.write_bytes(body)
                record["sha256"] = hashlib.sha256(pdf.read_bytes()).hexdigest()
                prior = old.get(url, {})
                if txt.exists() and prior.get("sha256") == record["sha256"] and prior.get("status") == "ok":
                    record.update({k: prior[k] for k in ("pages", "ocr_pages", "status")})
                else:
                    record["pages"], record["ocr_pages"] = extract(pdf, txt, args.min_chars)
                    record["status"] = "ok"
            except Exception as exc:
                record.update(status="error", error=str(exc))
                print(f"ERROR {url}: {exc}", flush=True)
            records[url] = record
            time.sleep(.5)
        manifest_path.write_text(json.dumps(sorted(records.values(), key=lambda r: (r["year"], r["pdf_url"])), ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_path.write_text(json.dumps(sorted(records.values(), key=lambda r: (r["year"], r["pdf_url"])), ensure_ascii=False, indent=2), encoding="utf-8")
    with (out / "manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for r in records.values():
            writer.writerow({**r, "ocr_pages": ",".join(map(str, r.get("ocr_pages", [])))})
    (out / "year_errors.json").write_text(json.dumps(errors, indent=2), encoding="utf-8")
    if errors or any(r["status"] != "ok" for r in records.values()): raise SystemExit(1)

if __name__ == "__main__": main()
