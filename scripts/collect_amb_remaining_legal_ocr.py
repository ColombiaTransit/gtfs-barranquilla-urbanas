#!/usr/bin/env python3
"""Download AMB resolution PDFs from official operator indexes and stage OCR evidence.

Never assert legal validity automatically. Every item records discovery/download
status, SHA256, pages, and article candidates for later primary-source review.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from html.parser import HTMLParser

TARGETS = {
    "COOTRANTICO": ("462-2025", "025-2011"),
    "COOLITORAL": ("210-2026", "256-2026", "192-2025", "199-2025"),
    "SOBUSA": ("082-2026", "466-2025"),
    "EMBUSA": ("231-2025", "010-2026"),
    "COOTRAB": ("358-2024", "378-2023"),
    "COOCHOFAL": ("242-2025",),
    "LA-CAROLINA": ("067-2011", "199-2019"),
    "TRASALIANCO": ("408-2013", "411-2010"),
    "TRANSMECAR": ("324-2010",),
}
BASE = "https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-{}/"
HEADERS = {"User-Agent": "ColombiaTransit-legal-evidence-research/1.0 (+https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas)"}

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.href = None
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.parts = []
    def handle_data(self, data):
        if self.href is not None:
            self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            self.links.append((" ".join(" ".join(self.parts).split()), self.href))
            self.href = None

def fetch(url):
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=50) as response:
        return response.read(), response.headers.get("Content-Type", "")

def match_resolution(label, resolution):
    number, year = resolution.split("-")
    shortyear = year[-2:]
    return bool(re.search(r"(?<!\\d)0*"+str(int(number))+r"\\s*[-–/]\\s*(?:"+year+"|"+shortyear+r")(?!\\d)", label, re.I))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="build/amb-remaining-legal-ocr")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for agency, resolutions in TARGETS.items():
        index = BASE.format(agency.lower())
        try:
            html, _ = fetch(index)
            parser_html = Anchors()
            parser_html.feed(html.decode("utf-8", "replace"))
            links = parser_html.links
            index_error = ""
        except Exception as exc:
            links = []
            index_error = str(exc)
        for resolution in resolutions:
            record = {"agency": agency, "resolution": resolution, "index_url": index,
                      "source_url": "", "status": "missing_link", "sha256": "",
                      "pages": "", "article_hits": "", "error": index_error}
            matches = [(label, urljoin(index, href)) for label, href in links
                       if match_resolution(label+" "+href, resolution)]
            if matches:
                record["source_url"] = matches[0][1]
                try:
                    raw, mime = fetch(matches[0][1])
                    if not raw.startswith(b"%PDF-"):
                        raise ValueError(f"Response is not PDF (mime={mime}, prefix={raw[:40]!r})")
                    folder = out / agency / resolution
                    folder.mkdir(parents=True, exist_ok=True)
                    pdf = folder / "original.pdf"
                    pdf.write_bytes(raw)
                    record["sha256"] = hashlib.sha256(raw).hexdigest()
                    page_text = folder / "text.txt"
                    subprocess.run(["pdftotext", "-layout", str(pdf), str(page_text)], check=True, timeout=60)
                    extracted = page_text.read_text(encoding="utf-8", errors="replace")
                    if len(extracted.strip()) < 250:
                        subprocess.run(["ocrmypdf", "--skip-text", "-l", "spa", "--jobs", "2",
                                        str(pdf), str(folder / "ocr.pdf")],
                                       check=True, timeout=1200)
                        subprocess.run(["pdftotext", "-layout", str(folder / "ocr.pdf"), str(page_text)],
                                       check=True, timeout=60)
                        extracted = page_text.read_text(encoding="utf-8", errors="replace")
                    record["pages"] = str(extracted.count("\\f") or 1)
                    hits = []
                    for page, text in enumerate(extracted.split("\\f"), 1):
                        if re.search(r"ART[IÍ]CULO\\s+(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|\\d+)", text, re.I):
                            hits.append(page)
                    record["article_hits"] = ";".join(map(str, hits))
                    record["status"] = "ocr_staged_review_pending"
                except Exception as exc:
                    record["status"] = "download_or_ocr_failed"
                    record["error"] = str(exc)[:500]
            rows.append(record)
            print(agency, resolution, record["status"], flush=True)
            time.sleep(0.2)
    fields = list(rows[0])
    with (out / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {"total": len(rows), "ocr_staged": sum(r["status"]=="ocr_staged_review_pending" for r in rows),
               "missing_or_failed": [r for r in rows if r["status"] != "ocr_staged_review_pending"],
               "human_article_review_complete": False, "legal_effect_verified": False}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({"total": summary["total"], "ocr_staged": summary["ocr_staged"],
                      "missing_or_failed_count": len(summary["missing_or_failed"])}, indent=2))

if __name__ == "__main__":
    main()
