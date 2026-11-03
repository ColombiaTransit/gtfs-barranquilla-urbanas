#!/usr/bin/env python3
"""Recover *actual* AMB COOLITORAL 256-2026 pilot PDF URL from Ninja Tables.

Do not invent PDF URLs. Only follow official ambq.gov.co links appearing in
the dynamic archive (public AJAX table). Check PDF signature and metadata;
store the actual PDF in the Action artifact, plus native extracted text and
source diagnostics. OCR of scanned PDF is kept as a separate backlog item.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import requests
from bs4 import BeautifulSoup
import fitz

ARCHIVE="https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-coolitoral/"
NEEDLE=re.compile(r"\b256\s*[-–/]?\s*(?:20)?26\b",re.I)

def pdf_links(node):
    out=[]
    for tag in [node,*node.find_all(True)]:
        for key in ("href","data-url","data-href","data-pdf","onclick"):
            v=tag.get(key) or ""
            if not isinstance(v,str):continue
            urls=re.findall(r"""(?:https?://|/wp-content/)[^'"\s)]+""",v) if key=="onclick" else [v]
            for raw in urls:
                url=urljoin(ARCHIVE,unquote(raw.strip()))
                parsed=urlparse(url)
                if parsed.scheme!="https" or parsed.hostname not in ("www.ambq.gov.co","ambq.gov.co"):continue
                if ".pdf" not in parsed.path.lower():continue
                if url not in out:out.append(url)
    return out

def fetch_dynamic(s,html):
    endpoints=[]
    for match in re.finditer(r'"data_request_url"\s*:\s*("(?:\\.|[^"\\])*")',html):
        try:
            endpoint=json.loads(match.group(1))
            if urlparse(endpoint).hostname in ("ambq.gov.co","www.ambq.gov.co"):
                endpoints.append(endpoint)
        except ValueError:pass
    records=[]
    for url in dict.fromkeys(endpoints):
        try:
            r=s.get(url,headers={"Referer":ARCHIVE},timeout=60);r.raise_for_status()
            j=r.json()
            payload=j if isinstance(j,list) else j.get("data",j.get("rows",[]))
            if isinstance(payload,dict):payload=payload.get("data",payload.get("rows",[]))
            records.extend(x for x in payload if isinstance(x,dict))
        except (requests.RequestException,ValueError) as exc:
            print("Public Ninja Table fetch failed:",type(exc).__name__)
    return records,len(endpoints)

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    s=requests.Session()
    s.headers.update({"User-Agent":"Mozilla/5.0 ColombiaTransit-AMB-Source-Retrieval/1.0"})
    resp=s.get(ARCHIVE,timeout=60);resp.raise_for_status()
    soup=BeautifulSoup(resp.text,"html.parser")
    candidates=[];rows=0
    for elem in soup.select("tr,li,div.wp-block-file"):
        if NEEDLE.search(elem.get_text(" ",strip=True)):
            rows+=1
            candidates+=pdf_links(elem)
    dynamic,n_sources=fetch_dynamic(s,resp.text)
    for item in dynamic:
        vals=" ".join(str(v) for v in item.values())
        fragment=BeautifulSoup(vals,"html.parser")
        if not NEEDLE.search(fragment.get_text(" ",strip=True)):continue
        rows+=1
        candidates+=pdf_links(fragment)
        for raw in item.values():
            v=str(raw).strip()
            if v.startswith("https://") and ".pdf" in v.lower() and urlparse(v).hostname in ("ambq.gov.co","www.ambq.gov.co"):
                candidates.append(v)
    candidates=list(dict.fromkeys(candidates))
    attempts=[];selected=None
    for url in candidates:
        try:
            r=s.get(url,stream=True,timeout=90)
            r.raise_for_status()
            buf=bytearray()
            for chunk in r.iter_content(65536):
                buf.extend(chunk)
                if len(buf)>45_000_000:raise ValueError("PDF too large")
            signature=bytes(buf[:5])==b"%PDF-"
            attempts.append({"url":url,"http":r.status_code,"bytes":len(buf),"pdf_header":signature})
            if signature and not selected:
                selected=(url,bytes(buf))
        except(requests.RequestException,ValueError) as exc:
            attempts.append({"url":url,"error":type(exc).__name__})
    summary={
      "archive":ARCHIVE,"ninja_dynamic_endpoints":n_sources,
      "dynamic_rows_total":len(dynamic),"matching_256_rows":rows,
      "candidate_pdf_urls":candidates,"attempts":attempts,
      "verified_source_url":selected[0] if selected else None,
      "original_pdf_retrieved":bool(selected),
      "native_text_available":False,"requires_separate_ocr":False,
      "pt4_pt5_legal_A_B_text_identified":False
    }
    if selected:
        (out/"original_256_2026.pdf").write_bytes(selected[1])
        doc=fitz.open(stream=selected[1],filetype="pdf")
        page_texts=[page.get_text("text") for page in doc]
        text="\n\n".join(f"=== PAGE {i+1} ===\n{v}" for i,v in enumerate(page_texts))
        (out/"original_native_text.txt").write_text(text,encoding="utf-8")
        summary["pdf_pages"]=len(doc)
        summary["native_text_chars"]=len(text)
        summary["native_text_available"]=len(text)>1500
        summary["requires_separate_ocr"]=len(text)<=1500
        summary["mentions_PT4"]=bool(re.search(r"PT4\s*[-–]?\s*4104",text,re.I))
        summary["mentions_PT5"]=bool(re.search(r"PT5\s*[-–]?\s*4105",text,re.I))
        summary["mentions_itinerario_A"]=bool(re.search(r"itinerari[oa]\s*A",text,re.I))
        summary["mentions_itinerario_B"]=bool(re.search(r"itinerari[oa]\s*B",text,re.I))
        summary["pt4_pt5_legal_A_B_text_identified"]=summary["mentions_PT4"] and summary["mentions_PT5"] and summary["mentions_itinerario_A"] and summary["mentions_itinerario_B"]
    (out/"source_report.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# AMB COOLITORAL 256-2026 original PDF source recovery",""]
    lines+=[f"- {k}: {v}" for k,v in summary.items() if k not in ("attempts","candidate_pdf_urls")]
    lines+=["","Archive links are extracted from AMB's live public Ninja Tables response, not guessed. "
            "An unavailable source or scanned PDF remains in a separate legal/OCR backlog."]
    (out/"summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("attempts","candidate_pdf_urls")},ensure_ascii=False,indent=2))
if __name__=="__main__":
    run(sys.argv[1] if len(sys.argv)>1 else "build/amb-coolitoral-pilot-recovery")
