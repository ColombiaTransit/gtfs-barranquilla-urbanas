#!/usr/bin/env python3
"""Produce page-linked legal article candidates from OCR; never auto-approve legal effect."""
import csv,json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"build/amb-nine-resolution-ocr"
OUT=ROOT/"build/amb-legal-article-verification"
PAT=re.compile(r"(?im)^\\s*(?:ART[IÍ]CULO|ART\\.?|RESUELVE|RESUELVEN|PAR[AÁ]GRAFO|VIGENCIA|NOTIF[IÍ]QUESE|COMUN[IÍ]QUESE|REVOCAR|MODIFICAR|DEROGAR)\\b[^\\n]{0,140}")
NUM=re.compile(r"\\b(?:025|331|462|267|408|411|173|067|204|199|137|192|358)[\\s\\-./]*(?:20)?(?:10|11|12|13|19|24|25|26)\\b")
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with (BASE/"resolution_results.csv").open(encoding="utf-8",newline="") as f:docs=list(csv.DictReader(f))
 hits=[];ident=[]
 for d in docs:
  agency,res=d["agency"],d["resolution"]
  folder=BASE/"extract"/(agency.lower()+"_"+res)
  pdf=folder/"source.pdf"
  digest=hashlib.sha256(pdf.read_bytes()).hexdigest() if pdf.exists() else ""
  sha_match=bool(digest) and digest==d["sha256"]
  page_files=sorted(folder.glob("page_*.txt"))
  cover=page_files[0].read_text(encoding="utf-8",errors="replace") if page_files else ""
  number=res.split("-")[0].lstrip("0")
  # OCR evidence only: presence of number in cover is not legal identity proof.
  number_candidate=bool(re.search(r"(?<!\\d)0*"+re.escape(number)+r"(?!\\d)",cover))
  ident.append({"agency":agency,"resolution":res,"pdf_sha256":digest,
    "sha256_matches_ocr_index":str(sha_match).lower(),
    "ocr_cover_mentions_resolution_number":str(number_candidate).lower(),
    "pdf_identity_manual_verified":"no","legal_effect_verified":"no",
    "current_service_verified":"no","gtfs_approved":"no"})
  for p in page_files:
   page=int(p.stem.split("_")[-1])
   text=p.read_text(encoding="utf-8",errors="replace")
   for m in list(PAT.finditer(text))[:18]:
    start=max(0,m.start()-90);end=min(len(text),m.end()+600)
    snippet=re.sub(r"\\s+"," ",text[start:end]).strip()
    hits.append({"agency":agency,"resolution":res,"page":page,
      "marker":re.sub(r"\\s+"," ",m.group()).strip()[:140],
      "ocr_context_UNVERIFIED":snippet[:700],"manual_visual_verification":"pending",
      "sha256":digest})
 for name,rows in (("source_identity_candidates.csv",ident),("operative_article_candidates.csv",hits)):
  with (OUT/name).open("w",encoding="utf-8",newline="") as f:
   if rows:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary={"documents":len(ident),"sha256_matches":sum(r["sha256_matches_ocr_index"]=="true" for r in ident),
 "cover_number_candidates":sum(r["ocr_cover_mentions_resolution_number"]=="true" for r in ident),
 "article_candidates":len(hits),"human_visual_review_complete":False,
 "legal_effect_verified":False,"current_service_verified":False,"gtfs_approved":False}
 (OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\\n",encoding="utf-8")
 (OUT/"summary.md").write_text("# AMB juridische verificatie — OCR-bewijskandidaten\\n\\n"
 +"Dit zijn paginagebonden **OCR-kandidaten**, geen juridisch vastgestelde artikelen. "
 +"Controleer elke kandidaat tegen het originele paginabeeld en vergelijk de besluitketen.\\n\\n"
 +f"- Documenten: {summary['documents']}\\n- SHA-256 overeenkomsten: {summary['sha256_matches']}\\n"
 +f"- Mogelijke besluitnummers op voorpagina: {summary['cover_number_candidates']}\\n"
 +f"- Artikel-/wijzigingskandidaten: {summary['article_candidates']}\\n"
 +"\\nGeen huidige dienstregeling of GTFS-wijziging automatisch goedgekeurd.\\n",encoding="utf-8")
 print(json.dumps(summary,indent=2))
 if len(ident)!=9 or summary["sha256_matches"]!=9:raise SystemExit("Incomplete nine-document source integrity check")
if __name__=="__main__":main()
