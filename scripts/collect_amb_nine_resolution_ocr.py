#!/usr/bin/env python3
"""OCR and visual-review evidence for nine newly recovered AMB resolutions.

Never infer current legal validity or approve GTFS data from OCR.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/amb-nine-resolution-ocr"
TARGETS=[
 ("TRASALIANCO","267-2010"),("TRASALIANCO","411-2010"),
 ("LA_CAROLINA","173-2010"),("LA_CAROLINA","204-2012"),("LA_CAROLINA","199-2019"),
 ("COOLITORAL","137-2011"),("COOLITORAL","192-2025"),
 ("COOTRAB","358-2024"),("COOTRANTICO","025-2011")]
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 manifest=ROOT/"sources/amb/pdf_manifest.csv"
 with manifest.open(encoding="utf-8-sig",newline="") as f: entries=list(csv.DictReader(f))
 rows=[];pages=[]
 for agency,resolution in TARGETS:
  matches=[x for x in entries if x["agency"]==agency and x["resolution"]==resolution]
  row={"agency":agency,"resolution":resolution,"source_url":matches[0]["url"] if len(matches)==1 else "",
       "status":"not_in_manifest","sha256":"","pdf_pages":0,"ocr_pages":0,"native_pages":0,
       "review_images":0,"source_identity_verified":"no","operative_articles_verified":"no",
       "current_operation_verified":"no","gtfs_release_approved":"no","error":""}
  if len(matches)!=1:
   row["error"]=f"manifest matches: {len(matches)}";rows.append(row);continue
  proc=subprocess.run([sys.executable,str(ROOT/"scripts/extract_amb_pdfs.py"),
    "--manifest",str(manifest),"--agency",agency,"--resolution",resolution,
    "--out",str(OUT/"extract")],capture_output=True,text=True,timeout=1500)
  report=OUT/"extract"/"report.json"
  records=json.loads(report.read_text(encoding="utf-8")) if report.exists() else []
  matches2=[r for r in records if r.get("agency")==agency and r.get("resolution")==resolution]
  rec=matches2[0] if len(matches2)==1 else {}
  row["status"]=rec.get("status","failed")
  row["sha256"]=rec.get("sha256","")
  row["error"]=rec.get("error") or (proc.stderr[-300:] if proc.returncode else "")
  doc=OUT/"extract"/(agency.lower()+"_"+resolution)
  if row["status"]=="extracted_requires_review":
   pgs=rec.get("pages",[])
   row["pdf_pages"]=len(pgs)
   row["ocr_pages"]=sum(x["method"]=="ocr" for x in pgs)
   row["native_pages"]=sum(x["method"]=="native" for x in pgs)
   scores=[]
   for pg in pgs:
    n=pg["page"];content=(doc/("page_%03d.txt"%n)).read_text(encoding="utf-8",errors="replace")
    score=(12 if n==1 else 0)+(10 if n==len(pgs) else 0)+(4 if pg["method"]=="ocr" else 0)
    score+=sum(word in content.casefold() for word in ("resuelve","artículo","articulo","frecuencia","itinerario","modifica","vigencia","revoca","horario","prórroga"))
    scores.append((score,n,pg,content))
   chosen=sorted(sorted(scores,key=lambda x:(-x[0],x[1]))[:8],key=lambda x:x[1])
   folder=OUT/"review_page_images"/(agency.lower()+"_"+resolution)
   folder.mkdir(parents=True,exist_ok=True)
   for score,n,pg,content in chosen:
    target=folder/("page_%03d.jpg"%n)
    try:
     p=subprocess.run(["pdftoppm","-f",str(n),"-l",str(n),"-r","150",
      "-singlefile","-jpeg","-jpegopt","quality=80",str(doc/"source.pdf"),str(target.with_suffix(""))],
      capture_output=True,text=True,timeout=100)
     ok=p.returncode==0 and target.is_file()
    except (OSError,subprocess.TimeoutExpired):ok=False
    row["review_images"]+=int(ok)
    pages.append({"agency":agency,"resolution":resolution,"page":n,"method":pg["method"],
      "rank":score,"characters":len(content),"image_path":str(target.relative_to(OUT)) if ok else "",
      "source_sha256":row["sha256"],"manual_visual_check_needed":"yes"})
  rows.append(row)
  print(json.dumps({"agency":agency,"resolution":resolution,"status":row["status"],
   "pages":row["pdf_pages"],"ocr_pages":row["ocr_pages"],"review_images":row["review_images"]}),flush=True)
 for filename,data in (("resolution_results.csv",rows),("review_page_index.csv",pages)):
  with (OUT/filename).open("w",encoding="utf-8",newline="") as f:
   if data:
    w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 summary={"targeted":len(TARGETS),"extracted":sum(r["status"]=="extracted_requires_review" for r in rows),
  "failed":sum(r["status"]!="extracted_requires_review" for r in rows),
  "pages":sum(r["pdf_pages"] for r in rows),"ocr_pages":sum(r["ocr_pages"] for r in rows),
  "review_images":sum(r["review_images"] for r in rows),
  "legal_validity_approved":False,"gtfs_release_approved":False,
  "still_missing_original":["ALL_OPERATORS 448-2025"]}
 (OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 lines=["# Negen aanvullende AMB-resoluties — OCR en beeldcontrole","",
 "Technische extractie, **geen juridische goedkeuring**.","",
 "| Vervoerder | Resolutie | Status | Pagina's | OCR | Beelden |",
 "|---|---|---|---:|---:|---:|"]
 for r in rows:lines.append(f'| {r["agency"]} | {r["resolution"]} | {r["status"]} | {r["pdf_pages"]} | {r["ocr_pages"]} | {r["review_images"]} |')
 lines+=["","Controleer de oorspronkelijke artikelen en eventuele latere wijzigingen voordat GTFS-waarden worden vrijgegeven.",
 "448-2025 heeft nog geen geverifieerde bron-URL.",""]
 (OUT/"summary.md").write_text("\n".join(lines),encoding="utf-8")
 print(json.dumps(summary,indent=2))
 if summary["extracted"]!=len(TARGETS):raise SystemExit("One or more resolution OCR cases failed; inspect artifact")
if __name__=="__main__":main()
