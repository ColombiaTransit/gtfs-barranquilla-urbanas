#!/usr/bin/env python3
"""Extract visible route and stop snapshots from a Chromium SIU MHTML archive.

This reads local browser snapshots only: no login, network or API.
Virtualized lists store ONLY the visible items; list pixel height is not a
verified record count. Output must not be mistaken for full SIU datasets.
"""
import argparse
import csv
import re
from email import policy
from email.parser import BytesParser
from pathlib import Path

from bs4 import BeautifulSoup

SOURCE = "https://siu.ambq.gov.co/siu/schedule-mng/schedules"


def archive_html(path):
    with Path(path).open("rb") as handle:
        msg = BytesParser(policy=policy.default).parse(handle)
    for part in msg.walk():
        if part.get_content_type() == "text/html" and SOURCE in (part.get("Content-Location") or ""):
            return BeautifulSoup(part.get_content(), "html.parser")
    raise ValueError("No SIU route HTML part in MHTML")


def parse_routes(soup, file):
    rows=[]
    for li in soup.select('li[style*="position: absolute"]'):
        name=li.select_one(".details .name")
        company=li.select_one(".details b")
        identifier=li.select_one("[id]")
        if name and company and identifier:
            style=li.get("style","")
            top=re.search(r"top:\s*(\d+)px",style)
            height=re.search(r"height:\s*(\d+)px",style)
            rows.append({
                "capture_file":Path(file).name,"route_display_name":name.get_text(" ",strip=True),
                "company_display_name":company.get_text(" ",strip=True),
                "siu_route_uuid":identifier.get("id",""),
                "visible_list_offset_px":top.group(1) if top else "",
                "visible_list_row_height_px":height.group(1) if height else "",
                "gtfs_route_code":"", "route_code_verified":"no",
                "source_page":SOURCE,
            })
    return rows


def parse_stops(soup, file):
    title=soup.select_one(".l-card__inner .title")
    name=title.get_text(" ",strip=True) if title else ""
    rows=[]
    for li in soup.select('li[style*="position: absolute"]'):
        stop=li.select_one(".stops-details .name")
        wrapper=li.select_one('[id^="js-stops-wrapper-"]')
        if not stop or not wrapper: continue
        found=re.fullmatch(r"js-stops-wrapper-([^/]+)/(.+)",wrapper.get("id",""))
        if not found: continue
        style=li.get("style","")
        top=re.search(r"top:\s*(\d+)px",style)
        height=re.search(r"height:\s*(\d+)px",style)
        position=int(top.group(1))//int(height.group(1))+1 if top and height else ""
        rows.append({
            "capture_file":Path(file).name,"route_display_name":name,
            "siu_route_uuid":found.group(1),"siu_stop_uuid":found.group(2),
            "stop_name":stop.get_text(" ",strip=True),"visible_order_index_estimate":position,
            "list_offset_px":top.group(1) if top else "",
            "row_height_px":height.group(1) if height else "",
            "stop_lat":"","stop_lon":"","coordinates_present_in_html":"no",
            "route_code_verified":"no","gtfs_route_code_candidate":"A7-4112",
            "source_page":SOURCE
        })
    return rows


def save(rows, path):
    if not rows:return
    with Path(path).open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def main():
    a=argparse.ArgumentParser()
    a.add_argument("snapshots",nargs="+",help="Local .mht files, not uploaded to GitHub")
    a.add_argument("--out",default="build/siu-snapshot")
    args=a.parse_args()
    output=Path(args.out);output.mkdir(parents=True,exist_ok=True)
    routes=[];stops=[]
    for file in args.snapshots:
        soup=archive_html(file)
        routes.extend(parse_routes(soup,file))
        stops.extend(parse_stops(soup,file))
    save(routes,output/"visible_siu_route_names.csv")
    save(stops,output/"visible_siu_route_stops.csv")
    print(f"Visible routes {len(routes)}; visible route-stops {len(stops)}. "
          "No entire-list claim; not a complete GTFS.")


if __name__=="__main__":main()
