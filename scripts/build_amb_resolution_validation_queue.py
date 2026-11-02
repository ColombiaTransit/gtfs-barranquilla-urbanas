#!/usr/bin/env python3
"""Audit AMB PDF manifest and extraction artifacts without asserting GTFS validity."""
import argparse, csv, json, pathlib, collections

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="sources/amb/pdf_manifest.csv")
    p.add_argument("--reports",default="ocr-output",help="Directory containing extracted report.json files")
    p.add_argument("--out",default="sources/amb/resolution_validation_queue.csv")
    a=p.parse_args()
    with open(a.manifest,encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
    reports={}
    for path in pathlib.Path(a.reports).rglob("report.json"):
        try:
            obj=json.loads(path.read_text(encoding="utf-8"))
        except (ValueError,OSError): continue
        records=obj if isinstance(obj,list) else obj.get("results",obj.get("documents",[]))
        if not isinstance(records,list): continue
        for item in records:
            if not isinstance(item,dict): continue
            agency=str(item.get("agency","")).upper()
            resolution=str(item.get("resolution",""))
            if agency and resolution: reports[(agency,resolution)]=item
    output=[]
    for r in rows:
        key=(r["agency"].upper(),r["resolution"])
        result=reports.get(key)
        extraction="not_checked" if result is None else str(result.get("status","unknown"))
        issue="download_or_extraction_failed" if extraction in ("failed","error") else ("missing_artifact_report" if result is None else "needs_human_legal_and_table_review")
        output.append({"agency":r["agency"],"resolution":r["resolution"],"route_codes":r["route_codes"],"url":r["url"],"extraction_status":extraction,"review_issue":issue,"legal_status":"unverified","current_operation":"unverified","gtfs_approved":"no"})
    pathlib.Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    with open(a.out,"w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(output[0]));writer.writeheader();writer.writerows(output)
    counts=collections.Counter(r["agency"] for r in output)
    print(json.dumps({"registered":len(output),"companies":len(counts),"reports_matched":len(reports),"out":a.out},ensure_ascii=False))
if __name__=="__main__": main()
