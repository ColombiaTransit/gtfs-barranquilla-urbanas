#!/usr/bin/env python3
"""Find real official AMB PDF URLs for Flota Angulo; never fabricate links."""
import csv, json, re, sys
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import requests
from bs4 import BeautifulSoup

ARCHIVE="https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-flota-angulo/"
KNOWN_301="https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/FLOTA-ANGULO/301-14-RESOLUCION-FLOTA-ANGULO.pdf"
RES={
 "232-2025":r"\b232\s*[-–/]\s*(?:20)?25\b",
 "265-2019":r"\b265\s*[-–/]\s*(?:20)?19\b",
 "301-2014":r"\b301\s*[-–/]\s*(?:20)?14\b",
 "242-2010":r"\b242\s*[-–/]\s*(?:20)?10\b",
 "157-2010":r"\b157\s*[-–/]\s*(?:20)?10\b",
 "242-2012":r"\b242\s*[-–/]\s*(?:20)?12\b"
}
def extract_links(row):
    result=[]
    for tag in [row,*row.find_all(True)]:
        for key in ("href","data-href","data-url","data-pdf","onclick"):
            raw=tag.get(key) or ""
            if not isinstance(raw,str): continue
            if key=="onclick":
                values=re.findall(r"""(?:https?://|/wp-content/)[^'"\s)]+""",raw)
            else: values=[raw]
            for raw_url in values:
                url=urljoin(ARCHIVE,unquote(raw_url.strip()))
                host=urlparse(url).hostname or ""
                if not (host=="ambq.gov.co" or host.endswith(".ambq.gov.co")): continue
                if ".pdf" not in url.lower() and "/wp-content/uploads/" not in url.lower(): continue
                if url not in result: result.append(url)
    return result


def resolution_matches(text, resolution):
    if re.search(RES[resolution], text, re.I):
        return True
    number, year = resolution.split("-")
    # AMB's dynamic index may use 'Resolución No. 232 de 2025'
    return bool(re.search(r"\b" + re.escape(number) + r"\b.{0,32}\b" +
                          r"(?:20)?" + re.escape(year[-2:]) + r"\b", text, re.I | re.S))

def find_dynamic_archive_rows(http, html, out):
    """The AMB index is a Ninja Tables AJAX table, not a static HTML <table>."""
    data_urls=[]
    for match in re.finditer(r'"data_request_url"\s*:\s*("(?:\\.|[^"\\])*")', html):
        try:
            endpoint=json.loads(match.group(1))
            parsed=urlparse(endpoint)
            if parsed.scheme=="https" and parsed.hostname in ("ambq.gov.co","www.ambq.gov.co"):
                if endpoint not in data_urls: data_urls.append(endpoint)
        except (ValueError, TypeError):
            continue
    results=[]; diagnostics=[]
    for endpoint in data_urls:
        try:
            response=http.get(endpoint,timeout=90,headers={"Referer":ARCHIVE})
            response.raise_for_status()
            payload=response.json()
            (out/"ninja_table_rows.json").write_text(
                json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
            if isinstance(payload,list): data=payload
            elif isinstance(payload,dict):
                data=payload.get("data",payload.get("rows",[]))
                if isinstance(data,dict): data=data.get("data",data.get("rows",[]))
            else: data=[]
            if not isinstance(data,list): data=[]
            results.extend(r for r in data if isinstance(r,dict))
            diagnostics.append({"endpoint":endpoint.split("&ninja_table_public_nonce=")[0],
                                "status":"ok","rows":len(data)})
        except (requests.RequestException, ValueError) as exc:
            diagnostics.append({"endpoint":endpoint.split("&ninja_table_public_nonce=")[0],
                                "status":"error","message":str(exc)[:300]})
    (out/"ninja_table_status.json").write_text(
        json.dumps(diagnostics,ensure_ascii=False,indent=2),encoding="utf-8")
    return results

def main():
    out=Path(sys.argv[1] if len(sys.argv)>1 else "flota-link-results")
    out.mkdir(parents=True,exist_ok=True)
    http=requests.Session()
    http.headers.update({"User-Agent":"Mozilla/5.0 ColombiaTransit-GTFSResearch/1.0"})
    response=http.get(ARCHIVE,timeout=60)
    response.raise_for_status()
    (out/"archive_page.html").write_text(response.text,encoding="utf-8")
    soup=BeautifulSoup(response.text,"html.parser")
    links={k:[] for k in RES}
    for row in soup.select("tr, li, div.wp-block-file"):
        label=row.get_text(" ",strip=True)
        found=[k for k in RES if resolution_matches(label,k)]
        if len(found)!=1: continue
        for url in extract_links(row):
            if url not in links[found[0]]: links[found[0]].append(url)
    # Fallback for markup without table rows.
    for node in soup.find_all(string=re.compile(r"232|265|301|242|157")):
        if not node.parent: continue
        row=node.parent.find_parent("tr") or node.parent.parent
        label=row.get_text(" ",strip=True)
        found=[k for k in RES if resolution_matches(label,k)]
        if len(found)==1:
            for url in extract_links(row):
                if url not in links[found[0]]: links[found[0]].append(url)
    # WordPress Ninja Tables: rows are loaded from the embedded AJAX data_request_url.
    # Without this request the archive HTML is empty and the recovery appears to
    # succeed while never discovering its five missing resolutions.
    for item in find_dynamic_archive_rows(http, response.text, out):
        html_cells=" ".join(str(v) for v in item.values())
        row=BeautifulSoup(html_cells,"html.parser")
        label=row.get_text(" ",strip=True)
        found=[k for k in RES if resolution_matches(label,k)]
        if len(found)!=1: continue
        candidates=extract_links(row)
        # Also handle a raw PDF URL held in a Ninja Tables text column.
        for value in item.values():
            raw=str(value).strip()
            if raw.startswith("https://") and ".pdf" in raw.lower():
                if raw not in candidates: candidates.append(raw)
        for url in candidates:
            if url not in links[found[0]]:links[found[0]].append(url)
    links["301-2014"].append(KNOWN_301)
    output=[]
    with (out/"resolved_manifest.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["agency","resolution","route_codes","url","status"]);w.writeheader()
        for resolution, candidates in links.items():
            chosen=""; checked=[]
            for url in dict.fromkeys(candidates):
                try:
                    with http.get(url,timeout=50,headers={"Range":"bytes=0-31"},stream=True) as r:
                        r.raise_for_status()
                        ok=next(r.iter_content(32),b"").startswith(b"%PDF")
                        checked.append({"url":url,"http":r.status_code,"is_pdf":ok})
                        if ok: chosen=url; break
                except requests.RequestException as e:
                    checked.append({"url":url,"error":str(e)[:150]})
            status="pdf_url_verified" if chosen else "listed_but_pdf_not_verified"
            output.append({"resolution":resolution,"status":status,"pdf_url":chosen,"attempted_urls":checked})
            if chosen:w.writerow({"agency":"FLOTA_ANGULO","resolution":resolution,"route_codes":"1302" if resolution=="242-2010" else "A7-4112","url":chosen,"status":"verified"})
    (out/"link_report.json").write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
    summary=["# AMB FLOTA ANGULO URL-recovery","",f"Official archive: {ARCHIVE}","",
             "| Resolution | PDF verified | Official PDF URL |","|---|---|---|"]
    summary += [f"| {r['resolution']} | {r['status']} | {r['pdf_url']} |" for r in output]
    summary += ["","Missing PDFs remain open; no guessed URLs are treated as valid."]
    (out/"summary.md").write_text("\n".join(summary)+"\n",encoding="utf-8")
    print(json.dumps({"verified":sum(bool(r["pdf_url"]) for r in output),"total":len(output),"out":str(out)}))
if __name__=="__main__":main()
