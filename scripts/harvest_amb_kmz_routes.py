#!/usr/bin/env python3
"""Harvest official public AMB KMZ links and convert their KML lines into research GeoJSON.
Does not edit or approve GTFS shapes or any legal route identity.
"""
import argparse
import csv
import hashlib
import html
import io
import json
import re
import time
import unicodedata
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

PAGE = "https://www.ambq.gov.co/transporte/transporte-publico-colectivo/"
HOSTS = {"ambq.gov.co", "www.ambq.gov.co"}
COMPANIES = """FLOTA-ANGULO TRANSMECAR FLOTA-ROJA TRANSDIAZ COOTRAB EMBUSA
MONTERREY LA-CAROLINA COOTRANSPORCAR COOCHOFAL TRASALFA COOLITORAL
COOTRANTICO LOLAYA COOTRANSCO COOTRASOL SOBUSA TRANSOLEDAD TRANSURBAR
SODETRANS COOTRANSNORTE TRASALIANCO COOASOATLAN""".split()
FIELDS = """company route_label route_code base_route_id_candidate variant source_attribute
kmz_url final_url http_last_modified sha256 size_bytes raw_kmz_path geojson_path
kml_members linestring_count point_count bbox status error legal_route_verified
siu_variant_verified source_url_collision source_page snapshot_utc""".split()

def normalize(s):
    s = unicodedata.normalize("NFKD", s.upper())
    return re.sub("[^A-Z0-9]", "", "".join(x for x in s if not unicodedata.combining(x)))

NAME_MAP = {normalize(n): n for n in COMPANIES}
NAME_MAP["TRANSPORTESMONTERREY"] = "MONTERREY"

def links_from_html(source):
    soup = BeautifulSoup(source, "html.parser")
    company = ""
    out = []
    for item in soup.descendants:
        if isinstance(item, NavigableString):
            maybe = NAME_MAP.get(normalize(str(item).strip()))
            if maybe:
                company = maybe
        elif isinstance(item, Tag) and item.name == "a":
            name = item.get_text(" ", strip=True) or item.get("title") or item.get("aria-label") or ""
            for key, val in item.attrs.items():
                val = html.unescape(" ".join(val) if isinstance(val, list) else str(val)).strip()
                if ".kmz" not in val.lower():
                    continue
                if not re.search(r"\.kmz(?:[?#]|$)", val, re.I):
                    found = re.search(r"(https?://[^\s\"'<>]+?\.kmz|/[^\s\"'<>]+?\.kmz)", val, re.I)
                    if not found:
                        continue
                    val = found.group(0)
                out.append((company, name, key, val.strip("\"' ")))
    return out

def possible_urls(raw, company):
    # AMB page data-kmz stores paths such as "SOBUSA/C12-4169 A.kmz",
    # relative to /ruta-de-buses/, NOT relative to the HTML page.
    if raw.startswith(("https://", "http://", "/")):
        options = [urljoin(PAGE, raw)]
    else:
        options = []
        relative = raw.lstrip("./")
        if relative.startswith(("ruta-de-buses/", "rutas-de-buses/")):
            options.append("https://www.ambq.gov.co/" + relative)
        else:
            for directory in ("ruta-de-buses", "rutas-de-buses"):
                suffix = relative if "/" in relative else company + "/" + relative if company else relative
                options.append("https://www.ambq.gov.co/" + directory + "/" + suffix)
        options.append(urljoin(PAGE, relative))
    result = []
    for link in options:
        s = urlsplit(link)
        if s.scheme != "https" or s.hostname not in HOSTS:
            continue
        link = urlunsplit((s.scheme, s.netloc, quote(unquote(s.path), safe="/._-()"), s.query, ""))
        if link not in result:
            result.append(link)
    return result

def get_download(session, link):
    r = session.get(link, timeout=(12, 35), stream=True, allow_redirects=True)
    try:
        if urlsplit(r.url).hostname not in HOSTS:
            raise ValueError("external redirect rejected")
        r.raise_for_status()
        data = bytearray()
        for chunk in r.iter_content(65536):
            data.extend(chunk)
            if len(data) > 8_000_000:
                raise ValueError("file exceeds 8 MB limit")
        return bytes(data), r.url, r.headers.get("Last-Modified", "")
    finally:
        r.close()

def parse_kmz(content):
    if not zipfile.is_zipfile(io.BytesIO(content)):
        raise ValueError("not KMZ ZIP")
    features, members = [], []
    with zipfile.ZipFile(io.BytesIO(content)) as zipf:
        files = [x for x in zipf.infolist() if x.filename.lower().endswith(".kml") and not x.is_dir()]
        if not files:
            raise ValueError("no KML found")
        if sum(x.file_size for x in files) > 30_000_000:
            raise ValueError("KML uncompressed size too large")
        for f in files:
            members.append(f.filename)
            if f.file_size > 15_000_000:
                raise ValueError("large KML member")
            root = ET.fromstring(zipf.read(f))
            for pm in root.iter():
                if pm.tag.rsplit("}", 1)[-1] != "Placemark":
                    continue
                name = next((x.text or "" for x in pm if x.tag.rsplit("}", 1)[-1] == "name"), "")
                for node in pm.iter():
                    kind = node.tag.rsplit("}", 1)[-1]
                    if kind not in ("LineString", "Track"):
                        continue
                    coords = []
                    for x in node.iter():
                        k = x.tag.rsplit("}", 1)[-1]
                        if not x.text or (kind == "LineString" and k != "coordinates") or (kind == "Track" and k != "coord"):
                            continue
                        for item in x.text.split() if kind == "LineString" else [x.text]:
                            try:
                                lon, lat = map(float, (item.split(",") if kind == "LineString" else item.split())[:2])
                                if -180 <= lon <= 180 and -90 <= lat <= 90:
                                    coords.append([round(lon, 7), round(lat, 7)])
                            except (ValueError, TypeError):
                                continue
                    if len(coords) > 1:
                        features.append({"type":"Feature",
                          "properties":{"placemark":name, "kml_member":f.filename},
                          "geometry":{"type":"LineString","coordinates":coords}})
    return features, members

def split_variant(label, raw):
    label = label.strip() or Path(unquote(urlsplit(raw).path)).stem
    m = re.fullmatch(r"(.+?)\s+([AB])", label, re.I)
    if not m:
        m = re.fullmatch(r"(.+?)\s+([AB])", Path(unquote(urlsplit(raw).path)).stem, re.I)
    return (label, m.group(1), m.group(2).upper()) if m else (label, label, "")

def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--output", default="build/amb-kmz")
    arg.add_argument("--page-html", help="Optional local HTML fixture")
    args = arg.parse_args()
    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "ColombiaTransit research: public AMB route KMZ archival"
    if args.page_html:
        source = Path(args.page_html).read_text(encoding="utf-8")
    else:
        page = session.get(PAGE, timeout=(12, 45))
        page.raise_for_status()
        source = page.text
    discovered = links_from_html(source)
    if not discovered:
        raise SystemExit("AMB page contains no .kmz in href/data-* attributes; page format changed")
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    seen, rows = set(), []
    for idx, (company, name, attribute, raw) in enumerate(discovered, 1):
        urls = possible_urls(raw, company)
        if not urls:
            continue
        label, base, variant = split_variant(name, raw)
        key = (company, label, urls[0])
        if key in seen:
            continue
        seen.add(key)
        row = dict.fromkeys(FIELDS, "")
        row.update(company=company, route_label=label, route_code=label,
                   base_route_id_candidate=base, variant=variant,
                   source_attribute=attribute, kmz_url=urls[0],
                   legal_route_verified="no", siu_variant_verified="no",
                   source_page=PAGE, snapshot_utc=stamp)
        failures = []
        for link in urls:
            try:
                data, final, modified = get_download(session, link)
                features, members = parse_kmz(data)
                sha = hashlib.sha256(data).hexdigest()
                filename = re.sub(r"[^A-Za-z0-9_-]+", "_", label)[:80] + "_" + sha[:10]
                folder = re.sub(r"[^A-Za-z0-9_-]+", "_", company or "UNKNOWN")
                rawfile = outdir/"raw"/folder/(filename+".kmz")
                rawfile.parent.mkdir(parents=True, exist_ok=True)
                rawfile.write_bytes(data)
                row.update(kmz_url=link, final_url=final, http_last_modified=modified,
                           sha256=sha, size_bytes=len(data),
                           raw_kmz_path=rawfile.relative_to(outdir).as_posix(),
                           kml_members=";".join(members), linestring_count=len(features),
                           point_count=sum(len(x["geometry"]["coordinates"]) for x in features))
                if features:
                    points = [p for x in features for p in x["geometry"]["coordinates"]]
                    bounds = [min(p[0] for p in points),min(p[1] for p in points),
                              max(p[0] for p in points),max(p[1] for p in points)]
                    geo = outdir/"geojson"/folder/(filename+".geojson")
                    geo.parent.mkdir(parents=True, exist_ok=True)
                    fc = {"type":"FeatureCollection",
                          "metadata":{"source_url":link,"source_sha256":sha,"company":company,
                                      "route_label":label,"route_id_candidate":base,
                                      "variant":variant,"last_modified":modified,
                                      "legal_route_verified":False},"features":features}
                    geo.write_text(json.dumps(fc, ensure_ascii=False, separators=(",",":"))+"\n", encoding="utf-8")
                    row.update(geojson_path=geo.relative_to(outdir).as_posix(),
                               bbox=";".join(map(str,bounds)),status="geometry_imported")
                else:
                    row["status"] = "no_linestring"
                break
            except (requests.RequestException, ValueError, ET.ParseError, zipfile.BadZipFile) as exc:
                failures.append(type(exc).__name__+":"+str(exc)[:100])
        if not row["status"]:
            row["status"] = "download_or_parse_failed"
            row["error"] = " | ".join(failures)
        rows.append(row)
        print("[%s/%s] %s / %s: %s" % (idx, len(discovered), company, label, row["status"]), flush=True)
        if not args.page_html:
            time.sleep(0.1)
    # A successful download does NOT prove that the route label points to its own geometry.
    # The AMB HTML sometimes points different legal routes to the exact same KMZ file.
    by_final_url = {}
    for row in rows:
        if row["status"] in ("geometry_imported", "no_linestring"):
            by_final_url.setdefault(row["final_url"] or row["kmz_url"], []).append(row)
    collisions = []
    for url, group in by_final_url.items():
        if len(group) < 2:
            continue
        for row in group:
            row["source_url_collision"] = "yes"
            collisions.append({"company":row["company"], "route_label":row["route_label"],
                               "base_route_id_candidate":row["base_route_id_candidate"],
                               "variant":row["variant"], "kmz_url":row["kmz_url"],
                               "sha256":row["sha256"], "issue":"same_source_url_used_by_multiple_route_labels",
                               "gtfs_shape_mapping_approved":"no"})
    for row in rows:
        if not row["source_url_collision"]:
            row["source_url_collision"] = "no"
    if collisions:
        with (outdir/"source_url_collisions.csv").open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, list(collisions[0]))
            writer.writeheader()
            writer.writerows(collisions)
    with (outdir/"manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    states = Counter(row["status"] for row in rows)
    summary = {"source_page":PAGE,"snapshot_utc":stamp,"page_kmz_attributes":len(discovered),
               "unique_route_files":len(rows),"companies":sorted(set(x["company"] for x in rows)),
               "file_statuses":dict(states),"explicit_AB_variants":sum(bool(x["variant"]) for x in rows),
               "total_linestrings":sum(int(x["linestring_count"] or 0) for x in rows),
               "total_line_vertices":sum(int(x["point_count"] or 0) for x in rows),
               "unique_download_urls":len(by_final_url),
               "source_url_collision_groups":sum(len(v)>1 for v in by_final_url.values()),
               "source_url_collision_route_entries":len(collisions),
               "gtfs_export_approved":False}
    (outdir/"summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
    (outdir/"summary.md").write_text(
        "# AMB officiële TPC-routeviewer — KMZ bronimport\n\n"+
        "Bron: "+PAGE+"\n\n"+
        "**"+str(len(rows))+" bestanden**; **"+str(states.get("geometry_imported",0))+
        " met lijngeometrie**; **"+str(summary["explicit_AB_variants"])+" expliciete A/B-vermeldingen**.\n\n"+
        "## Importstatus\n"+ "".join("- "+k+": "+str(v)+"\n" for k,v in states.items())+
        "\nOriginele KMZ, geconverteerde GeoJSON en manifest bewaren de provenance en variant.\n"+
        "LET OP: "+str(summary["source_url_collision_groups"])+" gedeelde KMZ-URL's bij "+
        str(summary["source_url_collision_route_entries"])+" routelabels; zie source_url_collisions.csv. "+
        "Deze mapping is NIET gevalideerd, ook als de KMZ downloadt.\n"+
        "Historische geometrie: controleer tegen toepasselijke vergunning en SIU. "+
        "**Niet rechtstreeks naar GTFS shapes.txt publiceren.**\n", encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    if not states.get("geometry_imported"):
        raise SystemExit("No valid KMZ route geometries imported")

if __name__ == "__main__":
    main()
