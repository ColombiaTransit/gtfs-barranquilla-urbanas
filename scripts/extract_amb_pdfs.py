#!/usr/bin/env python3
"""Download registered AMB PDFs, extract native text, OCR pages needing it.
Outputs are review artifacts, never GTFS modifications.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request

def run(*args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kwargs).stdout

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="sources/amb/pdf_manifest.csv")
    ap.add_argument("--agency", default="")
    ap.add_argument("--resolution", default="")
    ap.add_argument("--out", default="ocr-output")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    with open(args.manifest, newline="", encoding="utf-8") as f:
        entries = list(csv.DictReader(f))
    for item in entries:
        if args.agency and item["agency"].casefold() != args.agency.casefold():
            continue
        if args.resolution and item["resolution"] != args.resolution:
            continue
        key = item["agency"].lower() + "_" + item["resolution"].replace("/", "-")
        folder = out / key
        folder.mkdir(exist_ok=True)
        record = {**item, "id": key, "pages": [], "error": None}
        try:
            req = urllib.request.Request(item["url"], headers={"User-Agent": "Mozilla/5.0 GTFS-research/1.0"})
            with urllib.request.urlopen(req, timeout=90) as response:
                data = response.read(35_000_001)
            if len(data) > 35_000_000 or not data.startswith(b"%PDF"):
                raise ValueError("Invalid or oversized PDF")
            pdf = folder / "source.pdf"
            pdf.write_bytes(data)
            record["sha256"] = hashlib.sha256(data).hexdigest()
            n = int(run("pdfinfo", str(pdf)).split("Pages:")[1].splitlines()[0].strip())
            if n > 150:
                raise ValueError("Too many pages")
            for p in range(1, n + 1):
                native = run("pdftotext", "-f", str(p), "-l", str(p), "-layout", str(pdf), "-")
                # Short pages and image-only pages go through OCR.
                needs_ocr = len(native.strip()) < 180
                method = "native"
                text = native
                if needs_ocr:
                    prefix = folder / ("page_%03d" % p)
                    subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-r", "220",
                                    "-singlefile", "-png", str(pdf), str(prefix)],
                                   check=True, stdout=subprocess.DEVNULL)
                    text = run("tesseract", str(prefix) + ".png", "stdout", "-l", "spa", "--psm", "3")
                    method = "ocr"
                    (prefix.with_suffix(".png")).unlink(missing_ok=True)
                (folder / ("page_%03d.txt" % p)).write_text(text, encoding="utf-8")
                record["pages"].append({"page": p, "method": method, "characters": len(text)})
            record["status"] = "extracted_requires_review"
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = str(exc)
        results.append(record)
    (out / "report.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    if not results:
        raise SystemExit("No matching documents in manifest")
    if all(r["status"] == "failed" for r in results):
        raise SystemExit("All downloads or extractions failed")

if __name__ == "__main__":
    main()
