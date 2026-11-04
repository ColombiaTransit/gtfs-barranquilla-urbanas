#!/usr/bin/env python3
"""Fetch selected unresolved AMB original PDFs into an Actions artifact; never approve legal content."""
import csv,hashlib,json,os,subprocess,time,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"sources/amb/pdf_manifest.csv"
OUT=ROOT/"build/amb-open-resolution-originals"
TARGETS=[
("TRASALIANCO","267-2010"),("TRASALIANCO","411-2010"),
("LA_CAROLINA","173-2010"),("LA_CAROLINA","204-2012"),("LA_CAROLINA","199-2019"),
("COOLITORAL","137-2011"),("COOLITORAL","192-2025"),
("COOTRAB","358-2024"),("COOTRANTICO","025-2011"),
("ALL_OPERATORS","448-2025")]
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with MANIFEST.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
 print("manifest columns:",list(rows[0]))
 results=[]
 for agency,resolution in TARGETS:
  matches=[r for r in rows if r.get("agency")==agency and r.get("resolution")==resolution]
  rec={"agency":agency,"resolution":resolution,"status":"not_in_manifest","url":"","sha256":"","pages":"","bytes":0,"notes":""}
  if len(matches)!=1:
   rec["notes"]=f"matching manifest records: {len(matches)}";results.append(rec);continue
  url=matches[0].get("url","")
  if not url:
   url=next((v for k,v in matches[0].items() if "http" in str(v)),"")
  rec["url"]=url
  folder=OUT/f"{agency.lower()}_{resolution}";folder.mkdir(exist_ok=True)
  for attempt in range(3):
   try:
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (AMB-source-audit; GitHub Actions)"})
    with urllib.request.urlopen(req,timeout=75) as resp: data=resp.read(60*1024*1024)
    if not data.startswith(b"%PDF-"):raise ValueError("response not PDF")
    p=folder/"source.pdf";p.write_bytes(data)
    rec.update(status="downloaded_pdf_identity_unverified",sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
    try:
     meta=subprocess.run(["pdfinfo",str(p)],capture_output=True,text=True,timeout=30)
     for line in meta.stdout.splitlines():
      if line.startswith("Pages:"):rec["pages"]=line.split(":",1)[1].strip()
     if meta.returncode:rec["notes"]="pdfinfo returned nonzero; metadata incomplete"
    except (FileNotFoundError,subprocess.TimeoutExpired):
     rec["notes"]="pdfinfo unavailable; PDF preserved for later metadata extraction"
    try:
     txt=subprocess.run(["pdftotext","-layout",str(p),str(folder/"native.txt")],capture_output=True,text=True,timeout=60)
     if txt.returncode:rec["notes"]+="; pdftotext failed or scanned PDF needs OCR"
    except (FileNotFoundError,subprocess.TimeoutExpired):
     rec["notes"]+="; pdftotext unavailable; PDF preserved"
    break
   except Exception as exc:
    rec.update(status="download_failed",notes=f"{type(exc).__name__}: {str(exc)[:160]}")
    if attempt<2:time.sleep(3)
  results.append(rec);print(agency,resolution,rec["status"],rec["bytes"],flush=True)
 fields=["agency","resolution","status","url","sha256","pages","bytes","notes"]
 with (OUT/"download_index.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(results)
 (OUT/"summary.json").write_text(json.dumps({"total":len(results),"downloaded":sum(x["status"]=="downloaded_pdf_identity_unverified" for x in results),"results":results},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__":main()
