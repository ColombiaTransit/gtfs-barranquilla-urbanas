#!/usr/bin/env python3
"""Static, anonymous inspection of JavaScript served by the public SIU page.

No API requests, credentials, cookies or raw bundles are archived.
"""
import hashlib
import html.parser
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PAGE = "https://siu.ambq.gov.co/siu/schedule-mng/schedules"
OUT = Path("build/siu-javascript-research")
MAX_BUNDLES = 30
MAX_BYTES = 12_000_000
TERMS = re.compile(r"ServiceMngCompressedItineraryListing|OrganizationMngOrganizationWithoutAuthListing|graphql|itinerary|routeId|orgId|schedule|departure|frequency|arrival|vehicle", re.I)
OPERATIONS = re.compile(r"\b(?:query|mutation|subscription)\s+([A-Za-z][A-Za-z0-9_]{2,90})\b")
GRAPHQL_NAMES = re.compile(r"\b(?:ServiceMng|OrganizationMng|VehicleMng|RouteMng|ScheduleMng)[A-Za-z0-9_]{3,100}\b")
SAFE = re.compile(r"^[A-Za-z0-9_./-]{1,160}$")

class Scripts(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            src = dict(attrs).get("src")
            if src:
                self.sources.append(src)

def get(url, limit):
    request = urllib.request.Request(url, headers={"User-Agent": "ColombiaTransit-SIU-Public-JS-Research/1.0", "Accept": "text/html,application/javascript,*/*"})
    with urllib.request.urlopen(request, timeout=45) as response:
        content = response.read(limit + 1)
        if len(content) > limit:
            raise ValueError("download_size_limit")
        return content

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    page = get(PAGE, 2_000_000).decode("utf-8", "replace")
    parser = Scripts()
    parser.feed(page)
    origin = urllib.parse.urlsplit(PAGE)
    urls = []
    for source in parser.sources:
        url = urllib.parse.urljoin(PAGE, source)
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme == "https" and parsed.netloc == origin.netloc and url not in urls:
            urls.append(url)
    findings = []
    errors = []
    operation_names = set()
    for url in urls[:MAX_BUNDLES]:
        try:
            payload = get(url, MAX_BYTES)
            content = payload.decode("utf-8", "replace")
            names = sorted(set(OPERATIONS.findall(content)) | set(GRAPHQL_NAMES.findall(content)))
            operation_names.update(names)
            hits = []
            for match in list(TERMS.finditer(content))[:120]:
                # Keep only match names and offsets; raw JS can contain tokens or user data.
                hits.append({"term": match.group(0), "offset": match.start()})
            findings.append({"url": url, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "operation_candidates": names[:150], "term_hits": hits})
        except Exception as exc:
            errors.append({"url": url, "error_type": type(exc).__name__})
    report = {
        "snapshot_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": PAGE,
        "method": "public same-origin static script inspection, no GraphQL calls",
        "discovered_script_count": len(urls),
        "inspected_script_count": len(findings),
        "operation_candidates": sorted(operation_names),
        "bundles": findings,
        "errors": errors,
        "limitations": "Minified bundles may use persisted queries, dynamically loaded chunks or encoded strings; names are candidates, not confirmed callable operations.",
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# SIU public JavaScript and GraphQL static research", "",
             "Snapshot: " + report["snapshot_utc"], "",
             f"Scripts found: {len(urls)}; inspected: {len(findings)}.", "",
             "## Candidate operation names", ""]
    lines.extend("- `" + name + "`" for name in sorted(operation_names))
    lines.extend(["", "## Bundle matches", ""])
    for item in findings:
        lines.append(f"- {item['url']}: {len(item['term_hits'])} term hits; SHA-256 `{item['sha256']}`")
    lines.extend(["", "## Limitations", "", report["limitations"], "",
                  "No bundles, API responses, credentials, cookies or personal data are saved."])
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"scripts_found": len(urls), "inspected": len(findings), "operation_candidates": sorted(operation_names), "errors": errors}, indent=2))
    if not findings:
        raise SystemExit("No public JS bundles inspected; see report.json")

if __name__ == "__main__":
    main()
