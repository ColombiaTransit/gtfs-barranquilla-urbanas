#!/usr/bin/env python3
"""Merge accepted route-specific frequency evidence into the GTFS build, preserving conflicts."""
import csv,json,re
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parents[1]
out=root/"build/gtfs-v2"
canonical=root/"build/registries"
def read(p):
 with (root/p).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def norm(x):return re.sub("[^A-Z0-9]","",str(x or "").upper())
def valid(r):
 try:return int(r.get("peak_headway_secs") or 0)>0 and int(r.get("offpeak_headway_secs") or 0)>0
 except ValueError:return False
# Closed legal research: original 2010 route tables visually checked.
# D17 retains a caveat: 411-2010 changes its itinerary, not a proven new headway.
CLOSED_RESEARCH_HEADWAYS = {
 "AMB_TRASALIANCO_B19_4176": ("266-2010", 240, 360),
 "AMB_TRASALIANCO_D12_4154": ("265-2010", 240, 360),
 "AMB_TRASALIANCO_D17_4158": ("268-2010", 300, 420),
}
CLOSED_RESEARCH_SOURCE = "docs/amb_research_phase_closure_2026-11-04.md"
# Explicitly approved provisional windows for 13 routes with missing/invalid dispatch times.
# Only applied where the source window cannot be parsed; source staging stays unchanged.
PROVISIONAL_WINDOW_ROUTES = {
 "C2B4188","C34134","C94140","C184141","D154157","D144156",
 "B2B4118","A184183","D34147","D44148","D54149","A64111","A54110",
}
PROVISIONAL_FIRST = "05:00:00"
PROVISIONAL_LAST = "21:00:00"
def valid_window(r):
 try:
  def seconds(v):
   parts=[int(p) for p in v.split(":")]
   if len(parts) not in (2,3):return -1
   return parts[0]*3600+parts[1]*60+(parts[2] if len(parts)==3 else 0)
  return 0<=seconds(r["first_dispatch_model"])<seconds(r["last_dispatch_model"])<=30*3600
 except (ValueError,KeyError,TypeError):return False

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
  if r["gtfs_route_id"] in CLOSED_RESEARCH_HEADWAYS:
   resolution,peak,offpeak=CLOSED_RESEARCH_HEADWAYS[r["gtfs_route_id"]]
   r.update(peak_headway_secs=str(peak),offpeak_headway_secs=str(offpeak),
    official_resolution=resolution,source_type="authoritative_historical",
    source_scope="per_route",source_file=CLOSED_RESEARCH_SOURCE)
   status="recovered_closed_research"
  r["consolidation_status"]=status
  audit.append({"route_id":r["gtfs_route_id"],"status":status,"source_file":r.get("source_file","")})
 # Canonical operational register; legacy staging is only an input.
 ids=[r["gtfs_route_id"] for r in staged]
 if len(ids)!=len(set(ids)):raise ValueError("Duplicate route IDs in frequency register")
 for r in staged:
  window_ok=valid_window(r)
  r["dispatch_window_model_status"]="source_window" if window_ok else "invalid_or_missing"
  r["dispatch_window_original_first"]=r.get("first_dispatch_model","")
  r["dispatch_window_original_last"]=r.get("last_dispatch_model","")
  if not window_ok and norm(r.get("route_short_name","")) in PROVISIONAL_WINDOW_ROUTES:
   r["first_dispatch_model"]=PROVISIONAL_FIRST
   r["last_dispatch_model"]=PROVISIONAL_LAST
   r["dispatch_window_model_status"]="provisional_dispatch_window"
   window_ok=True
  r["operational_status"]="ready" if valid(r) and window_ok and r.get("consolidation_status")!="conflict_held" else "held"
 assert len(PROVISIONAL_WINDOW_ROUTES)==13
 print("Provisional dispatch windows:", [r["route_short_name"] for r in staged if r["dispatch_window_model_status"]=="provisional_dispatch_window"])
 out.mkdir(parents=True,exist_ok=True)
 canonical.mkdir(parents=True,exist_ok=True)
 with (canonical/"route_service.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(staged[0]));w.writeheader();w.writerows(staged)
 for filename,rows,fields in [
  ("consolidated_route_headways.csv",staged,list(staged[0])),
  ("frequency_consolidation_audit.csv",audit,["route_id","status","source_file"]),
  ("frequency_consolidation_conflicts.csv",conflicts,["route_id","reason"])]:
  with (out/filename).open("w",newline="",encoding="utf-8") as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 print(json.dumps({"routes":len(staged),"statuses":dict(Counter(x["status"] for x in audit)),"conflicts":len(conflicts),"operational_statuses":dict(Counter(r["operational_status"] for r in staged))},indent=2))
if __name__=="__main__":main()
