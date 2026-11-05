#!/usr/bin/env python3
"""Merge accepted route-specific frequency evidence into the GTFS build, preserving conflicts."""
import csv,json,re
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parents[1]
out=root/"build/gtfs-v2"
def read(p):
 with (root/p).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def norm(x):return re.sub("[^A-Z0-9]","",str(x or "").upper())
def valid(r):
 try:return int(r.get("peak_headway_secs") or 0)>0 and int(r.get("offpeak_headway_secs") or 0)>0
 except ValueError:return False
def main():
 source="sources/amb/gtfs_route_frequency_candidates_no_fleet_2026-11-02.csv"
 staged=read("sources/amb/gtfs_staging/route_headway_candidates.csv")
 candidates={}
 for x in read(source):
  candidates.setdefault((norm(x["agency"]),norm(x["route_id"])),[]).append(x)
 audit=[];conflicts=[]
 for r in staged:
  key=(norm(r["agency_id"].removeprefix("AMB_")),norm(r["route_short_name"]))
  found=[x for x in candidates.get(key,[]) if x.get("official_headway_accepted")=="yes_official_resolution" and x.get("peak_headway_secs") and x.get("offpeak_headway_secs")]
  status="retained_staging"
  if len(found)==1:
   x=found[0]
   new=(x["peak_headway_secs"],x["offpeak_headway_secs"])
   old=(r.get("peak_headway_secs",""),r.get("offpeak_headway_secs",""))
   if not valid(r) or (old!=new and norm(r.get("official_resolution"))==norm(x.get("source_resolution"))):
    r.update(peak_headway_secs=new[0],offpeak_headway_secs=new[1],official_resolution=x.get("source_resolution",""),source_type="authoritative",source_file=source)
    status="recovered_accepted_source"
   elif old!=new:
    status="conflict_held";conflicts.append({"route_id":r["gtfs_route_id"],"reason":"resolution_precedence_requires_review"})
  elif len(found)>1:
   status="conflict_held";conflicts.append({"route_id":r["gtfs_route_id"],"reason":"multiple_accepted_candidates"})
  elif not valid(r):status="missing_verified_headway"
  r["consolidation_status"]=status
  audit.append({"route_id":r["gtfs_route_id"],"status":status,"source_file":r.get("source_file","")})
 out.mkdir(parents=True,exist_ok=True)
 for filename,rows,fields in [
  ("consolidated_route_headways.csv",staged,list(staged[0])),
  ("frequency_consolidation_audit.csv",audit,["route_id","status","source_file"]),
  ("frequency_consolidation_conflicts.csv",conflicts,["route_id","reason"])]:
  with (out/filename).open("w",newline="",encoding="utf-8") as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 print(json.dumps({"routes":len(staged),"statuses":dict(Counter(x["status"] for x in audit)),"conflicts":len(conflicts)},indent=2))
if __name__=="__main__":main()
