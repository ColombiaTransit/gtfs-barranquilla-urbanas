#!/usr/bin/env python3
"""Extract six queued AMB PDF originals plus visual page evidence for review.

This does NOT interpret the actual operative articles legally. Spanish OCR
and page images are candidates for human/visual QA only. A listed URL doesn't
prove valid PDF identity; no route ID/frequency change is made.
"""
from __future__ import annotations
import argparse,csv,json,re,subprocess,sys
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"build/amb-legal-ocr-priority/six_ocr_visual_review_queue.csv"
OUT=ROOT/"build/amb-ocr-image-evidence"
def readcsv(p):
    with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def store(p,rows):
    if not rows:return
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction="ignore")
        w.writeheader();w.writerows(rows)
def call(command,timeout):
    return subprocess.run(command,check=False,capture_output=True,text=True,timeout=timeout)
def choose_pages(doc,record,limit):
    pages=record.get("pages",[])
    candidates=[]
    for pg in pages:
        number=int(pg["page"])
        text=(doc/("page_%03d.txt"%number)).read_text(encoding="utf-8",errors="replace")
        # Include original resolution cover and final operative section, plus
        # OCR-heavy and legal/routing pages. A machine-ranked page is NOT an
        # article verification.
        priority=(15 if number==1 else 0)+(10 if number==len(pages) else 0)
        if pg.get("method")=="ocr":priority+=5
        for marker in ("artículo","articulo","itinerario","horario","frecuencia","recorrido","considerando","resuelve","modifica","revoca","prórroga","vigencia"):
            if marker in text.casefold():priority+=1
        candidates.append((priority,number,text,pg))
    selected=sorted(sorted(candidates,key=lambda x:(-x[0],x[1]))[:limit],key=lambda x:x[1])
    return selected
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--queue",type=Path,default=QUEUE)
    a.add_argument("--out",type=Path,default=OUT)
    a.add_argument("--max-review-images",type=int,default=8)
    args=a.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    queue=readcsv(args.queue)
    if len(queue)!=6:raise ValueError("Expected six OCR queue cases")
    summary_rows=[]
    page_rows=[]
    for q in queue:
        agency,resolution=q["agency"],q["resolution"]
        case=f"{agency.lower()}_{resolution}"
        extract_dir=args.out/"pdf_extract"
        proc=call([sys.executable,str(ROOT/"scripts/extract_amb_pdfs.py"),
                   "--agency",agency,"--resolution",resolution,
                   "--out",str(extract_dir)],timeout=900)
        reports=extract_dir/"report.json"
        reported=[]
        if reports.exists():
            obj=json.loads(reports.read_text(encoding="utf-8"))
            reported=[r for r in obj if r.get("agency")==agency and r.get("resolution")==resolution]
        rec=reported[0] if len(reported)==1 else None
        status=(rec or {}).get("status","failed_or_missing_report")
        doc=extract_dir/case
        images=args.out/"review_page_images"/case
        images.mkdir(parents=True,exist_ok=True)
        extracted=0;review_images=0;page_count=0;methods=Counter();notes=[]
        if rec and status=="extracted_requires_review" and (doc/"source.pdf").exists():
            extracted=len(rec.get("pages",[]))
            page_count=extracted
            if extracted>0:
                chosen=choose_pages(doc,rec,args.max_review_images)
                for priority,number,page_text,method_rec in chosen:
                    target=images/("original_page_%03d.jpg"%number)
                    cmd=["pdftoppm","-f",str(number),"-l",str(number),
                         "-r","150","-singlefile","-jpeg","-jpegopt","quality=80",
                         str(doc/"source.pdf"),str(target.with_suffix(""))]
                    image=call(cmd,timeout=80)
                    if image.returncode==0 and target.is_file():
                        review_images+=1
                    else:
                        notes.append("page_image_failed_"+str(number))
                    marker_hits=[]
                    for pattern in ("ARTICULO","ARTÍCULO","ITINERARIO","FRECUENCIA","RESUELVE","VIGENCIA","REVOCAR","PRORROGA"):
                        if pattern.casefold() in page_text.casefold():marker_hits.append(pattern)
                    page_rows.append({
                        "agency":agency,"resolution":resolution,"original_pdf_page":number,
                        "machine_page_rank":priority,
                        "text_extraction_method":method_rec.get("method",""),
                        "text_characters":len(page_text),
                        "legal_keyphrases_found_NOT_VERIFIED":";".join(marker_hits),
                        "image_path_relative":str(target.relative_to(args.out)) if target.is_file() else "",
                        "image_manual_check_needed":"yes",
                        "source_sha256":rec.get("sha256",""),
                    })
            methods.update(p.get("method","unknown") for p in rec.get("pages",[]))
        if not rec and proc.stderr:notes.append("extract_report_failed_check_action_log")
        if rec and rec.get("error"):notes.append(str(rec["error"]).replace("\n"," ")[:180])
        summary_rows.append({
            "agency":agency,"resolution":resolution,"route":q["route"],
            "original_manifest_URL":q["manifest_url"],
            "download_status":status,
            "sha256":(rec or {}).get("sha256",""),
            "pdf_pages_extracted":page_count,
            "pages_with_native_text":methods["native"],
            "pages_using_spanish_OCR":methods["ocr"],
            "page_images_for_manual_review":review_images,
            "PDF_resolution_identity_verified":"no_manual_page_check_still_required",
            "operative_articles_legally_verified":"no",
            "frequency_changes_approved_from_OCR":"no",
            "open_action":q["visual_action"],
            "note":";".join(notes),
        })
        print(json.dumps({"document":case,"status":status,
                          "pages":page_count,"page_images":review_images},
                         ensure_ascii=False),flush=True)
    store(args.out/"six_pdf_extraction_results.csv",summary_rows)
    store(args.out/"image_review_page_index.csv",page_rows)
    success=sum(r["download_status"]=="extracted_requires_review" for r in summary_rows)
    summary={
        "queued":len(queue),
        "PDF_downloaded_and_extracted":success,
        "failed_or_unavailable_original_PDFs":len(queue)-success,
        "total_pages_text_extracted":sum(r["pdf_pages_extracted"] for r in summary_rows),
        "total_ocr_pages":sum(r["pages_using_spanish_OCR"] for r in summary_rows),
        "total_review_page_images":sum(r["page_images_for_manual_review"] for r in summary_rows),
        "any_legal_effect_from_OCR_approved":False,
        "original_PDF_identity_verified":False,
        "manual_article_and_scan_QA_still_required":True,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Do not persist PDFs or image binaries into Git history. Entire evidence
    # stays in Action artifact, audit files can be committed separately.
    lines=["# AMB OCR/beeldanalyse: zes oorspronkelijke resoluties","",
          "Dit is een technische uitlees-/beeldanalyseverzameling; **geen juridische verificatie**.",
          "",
          "| Bedrijf | Resolutie | Uitlezing | Pagina's | OCR-pagina's | Controlebeelden |",
          "|---|---|---|---:|---:|---:|"]
    for r in summary_rows:
        lines.append("| "+r["agency"]+" | "+r["resolution"]+" | "+r["download_status"]+
                     " | "+str(r["pdf_pages_extracted"])+" | "+str(r["pages_using_spanish_OCR"])+
                     " | "+str(r["page_images_for_manual_review"])+" |")
    lines+=["","Per-document SHA-256 en bron-URL staan in six_pdf_extraction_results.csv;",
             "de index image_review_page_index.csv beschrijft de concrete",
             "originele paginabeelden in de GitHub Actions-artifact.",
             "Geen extractie/OCR krijgt zonder menselijke broncontrole de status geverifieerd.",""]
    (args.out/"summary.md").write_text("\n".join(lines),encoding="utf-8")
    if not success:
        raise SystemExit("No queued PDFs extracted: review network access or manifest URLs")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
