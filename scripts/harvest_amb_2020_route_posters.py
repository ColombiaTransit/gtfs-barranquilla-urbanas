#!/usr/bin/env python3
"""Harvest AMB's July 2020 TPC route posters and OCR their printed dispatch tables.

This yields *historical* timetable evidence, NOT a 2026 timetable and NOT GTFS.
Preserve original poster images, table crops and OCR text for human verification.
"""
import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ARTICLE = "https://www.ambq.gov.co/continuan-las-rutas-y-frecuencias-del-transporte-publico-colectivo/"
BASE = "https://www.ambq.gov.co/wp-content/uploads/2020/07/"
# Ordered by the official gallery. Fallback is deliberately explicit to allow
# reproducible retrieval if WordPress lazy-loading strips gallery links.
FILES = [
"WhatsApp-Image-2020-07-17-at-11.31.15-AM-351x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.16-AM-351x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.16-AM-1-351x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.16-AM-2-351x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.17-AM-350x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.17-AM-1-350x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.17-AM-2-350x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.17-AM-3-350x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.18-AM-349x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.18-AM-1-350x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.18-AM-2-350x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.18-AM-3-351x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.19-AM-351x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.19-AM-3-350x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.19-AM-2-350x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.19-AM-1-349x350.jpeg",
"WhatsApp-Image-2020-07-17-at-11.31.20-AM-351x350.jpeg",
"WhatsApp-Image-2020-07-18-at-2.20.32-PM-351x350.jpeg",
"WhatsApp-Image-2020-07-18-at-2.20.31-PM-351x350.jpeg",
"WhatsApp-Image-2020-07-18-at-2.20.31-PM-1-351x350.jpeg",
"WhatsApp-Image-2020-07-18-at-2.20.31-PM-2-351x350.jpeg",
"WhatsApp-Image-2020-07-18-at-2.20.32-PM-1-351x350.jpeg",
"WhatsApp-Image-2020-07-18-at-2.20.32-PM-2-351x350.jpeg",
"WhatsApp-Image-2020-07-18-at-2.20.32-PM-3-351x350.jpeg",
]
def full_url(thumbnail):
    return re.sub(r"-\d{3,4}x\d{3,4}(?=\.(?:jpg|jpeg|png)$)", "", thumbnail, flags=re.I)
def try_get_image(http, urls):
    responses=[]
    for url in dict.fromkeys(urls):
        try:
            r=http.get(url,timeout=45)
            if r.status_code != 200:
                responses.append({"url":url,"http":r.status_code});continue
            if not r.content[:4] in (b"\xff\xd8\xff\xe0",b"\xff\xd8\xff\xe1") and not r.headers.get("Content-Type","").startswith("image/"):
                responses.append({"url":url,"error":"not_an_image"});continue
            img=Image.open(io.BytesIO(r.content)).convert("RGB")
            responses.append({"url":url,"http":200,"width":img.width,"height":img.height})
            if img.width >= 700:
                return url,img,responses
            if "small" not in locals():small=(url,img)
        except Exception as exc:
            responses.append({"url":url,"error":str(exc)[:160]})
    if "small" in locals():return small[0],small[1],responses
    return None,None,responses
def image_ocr(image_path,mode=6):
    try:
        r=subprocess.run(["tesseract",str(image_path),"stdout","-l","spa","--psm",str(mode)],
          capture_output=True,text=True,timeout=90)
        return r.stdout if r.returncode==0 else "[TESSERACT_ERROR] "+r.stderr[:200]
    except Exception as exc:return "[TESSERACT_ERROR] "+str(exc)
def main():
    out=Path(sys.argv[1] if len(sys.argv)>1 else "amb-2020-posters")
    (out/"posters").mkdir(parents=True,exist_ok=True)
    (out/"tables").mkdir(parents=True,exist_ok=True)
    (out/"ocr").mkdir(parents=True,exist_ok=True)
    http=requests.Session()
    http.headers.update({"User-Agent":"Mozilla/5.0 ColombiaTransit-GTFS-Archive/1.0"})
    gallery=[]
    try:
        page=http.get(ARTICLE,timeout=50)
        page.raise_for_status()
        (out/"article.html").write_text(page.text,encoding="utf-8")
        bs=BeautifulSoup(page.text,"html.parser")
        for a in bs.select("a[href], img[data-src], img[src]"):
            u=a.get("href") or a.get("data-src") or a.get("src") or ""
            if "/2020/07/WhatsApp-Image-" in u and u.lower().endswith((".jpg",".jpeg",".png")):
                gallery.append(u)
    except Exception as exc:
        (out/"article-fetch-error.txt").write_text(str(exc),encoding="utf-8")
    # The gallery has 24 ordered entries. The stable fallback guarantees coverage
    # when the WordPress page exposes only lazy placeholders.
    cards=[];summary=[];links=gallery[:]
    fallback=[BASE+x for x in FILES]
    for u in fallback:
        if not any(full_url(x)==full_url(u) for x in links):links.append(u)
    for idx, thumbnail in enumerate(links,1):
        canonical=full_url(thumbnail)
        url,img,attempts=try_get_image(http,[canonical,thumbnail])
        rec={"poster_no":idx,"poster_url":url or canonical,"thumbnail_url":thumbnail,
             "source_article":ARTICLE,"source_period":"2020-07",
             "source_is_historical":True,"downloaded":bool(img),
             "attempts":attempts}
        if img:
            rec["width"]=img.width;rec["height"]=img.height
            basename=f"poster_{idx:02d}"
            img.save(out/"posters"/(basename+".png"))
            top=int(img.height*.77)
            # Footer contains route / first / last / peak / valley. 4x enlargement
            # improves OCR of 1000x1000 maps even with fine table text.
            footer=img.crop((0,top,img.width,img.height))
            footer=ImageOps.grayscale(footer)
            footer=ImageEnhance.Contrast(footer).enhance(2.1)
            footer=footer.resize((footer.width*3,footer.height*3))
            footer=footer.filter(ImageFilter.UnsharpMask(radius=1.4,percent=140,threshold=2))
            footer.save(out/"tables"/(basename+"_footer.png"))
            plain=image_ocr(out/"tables"/(basename+"_footer.png"),6)
            sparse=image_ocr(out/"tables"/(basename+"_footer.png"),11)
            (out/"ocr"/(basename+"_table_psm6.txt")).write_text(plain,encoding="utf-8")
            (out/"ocr"/(basename+"_table_psm11.txt")).write_text(sparse,encoding="utf-8")
            rec["ocr_text_psm6"]=plain
            rec["ocr_text_psm11"]=sparse
            heading=image_ocr(out/"posters"/(basename+".png"),11)
            rec["title_ocr"]=heading[:800]
        else:
            rec["ocr_text_psm6"]=""
            rec["ocr_text_psm11"]=""
        cards.append(rec)
        print(f"{idx:02d}/{len(links)} {img.width if img else 0}x{img.height if img else 0} {url}",flush=True)
    (out/"report.json").write_text(json.dumps(cards,ensure_ascii=False,indent=2),encoding="utf-8")
    cols=["poster_no","poster_url","source_period","width","height","downloaded","first_last_headway_ocr_needs_manual_review"]
    with (out/"poster_index.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for r in cards:w.writerow({**{k:r.get(k,"") for k in cols},
                         "first_last_headway_ocr_needs_manual_review":"yes"})
    summary=["# AMB TPC 2020 poster extraction","",
             f"Article: {ARTICLE}",
             f"Gallery posters inspected: {len(cards)}",
             f"Images downloaded: {sum(r['downloaded'] for r in cards)}",
             "**These are July 2020 historical timings, NOT a current 2026 operating schedule.**",
             "OCR must be verified against poster table images; header/footer or map text can create false matches.","",
             "| Poster | Download | Source |","|---|---|---|"]
    summary += [f"| {r['poster_no']} | {'yes' if r['downloaded'] else 'no'} | {r['poster_url']} |" for r in cards]
    (out/"summary.md").write_text("\n".join(summary)+"\n",encoding="utf-8")
    print(json.dumps({"posters":len(cards),"downloaded":sum(r["downloaded"] for r in cards)},ensure_ascii=False))
if __name__=="__main__":main()
