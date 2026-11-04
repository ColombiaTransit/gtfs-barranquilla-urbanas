#!/usr/bin/env python3
"""Index article and frequency evidence from existing OCR text; never run OCR."""
import csv
import json
import re
from pathlib import Path

source = Path("build/amb-remaining-legal-ocr")
out = Path("build/amb-ocr-review")
out.mkdir(parents=True, exist_ok=True)
targets = {
    "COOTRANTICO": ["462-2025"],
    "EMBUSA": ["231-2025", "010-2026"],
    "COOCHOFAL": ["242-2025"],
    "TRASALIANCO": ["411-2010"],
    "COOLITORAL": ["210-2026"],
}
pattern = re.compile(r"ART[IÍ]CULO|FRECUENCIA|INTERVALO|HORA PICO|HORA VALLE|VIGENCIA|NOTIF[IÍ]QUESE|EJECUTORIA|DEROGA|MODIFICA|A15-41(?:29|59)|C2-B-418[78]", re.I)
rows = []
missing = []
for agency, resolutions in targets.items():
    for resolution in resolutions:
        file = source / agency / resolution / "text.txt"
        if not file.exists():
            missing.append(str(file))
            continue
        for page_number, page in enumerate(file.read_text(encoding="utf-8", errors="replace").split("\f"), 1):
            lines = page.splitlines()
            for i, line in enumerate(lines):
                if pattern.search(line):
                    rows.append({"agency": agency, "resolution": resolution, "pdf_page": page_number,
                                 "line": i + 1, "ocr_excerpt": " ".join(" ".join(lines[max(0,i-1):i+2]).split())[:500],
                                 "review_status": "human_review_required"})
with (out / "article_candidates.csv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["agency","resolution","pdf_page","line","ocr_excerpt","review_status"])
    writer.writeheader()
    writer.writerows(rows)
summary = {"candidates": len(rows), "missing": missing, "ocr_reexecuted": False, "legal_effect_verified": False}
(out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
if missing:
    raise SystemExit("Existing OCR artifact incomplete")
