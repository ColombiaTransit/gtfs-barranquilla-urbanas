#!/usr/bin/env python3
"""Build evidence-based SIU organization/itinerary/company-name crosswalk."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from probe_siu_organization_graphql import call

ROOT=Path("sources/siu/public_extract")
OUT=Path("build/siu-org-itinerary-crosswalk")
QUERY="OrganizationMngOrganizationWithoutAuthListing"

def write_csv(path,fields,rows):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=ROOT/"siu_itineraries.csv"
    if not source.exists():
        raise SystemExit("Missing committed SIU itinerary export: "+str(source))
    with source.open(encoding="utf-8-sig",newline="") as f:
        itineraries=list(csv.DictReader(f))
    if not itineraries:raise SystemExit("No itinerary rows")
    orgs={}
    pages=[]
    for page in range(0,3):
        st,result=call(QUERY,{"paginationInput":{"page":page,"count":100}})
        pages.append({"page":page,"status":st["status"],"http_status":st.get("http_status"),
                      "total":result.get("queryTotalResultCount") if isinstance(result,dict) else None})
        if st["status"]!="ok" or not isinstance(result,dict):
            if page==0:raise SystemExit("Public SIU organization query failed")
            break
        listing=result.get("listing") or []
        for org in listing:
            if isinstance(org,dict) and org.get("id"):
                orgs[str(org["id"])]=org
        if not listing or len(listing)<100:break
    crosswalk=[]
    companies=defaultdict(lambda:{"itineraries":set(),"orgs":set()})
    unknown_orgs=set()
    for route in itineraries:
        org_id=(route.get("siu_org_uuid") or "").strip()
        obj=orgs.get(org_id)
        if org_id and obj is None:unknown_orgs.add(org_id)
        names=[n.strip() for n in (route.get("siu_company_names") or "").split(";") if n.strip()]
        for name in names:
            companies[name]["itineraries"].add(route.get("siu_itinerary_uuid") or "")
            if org_id:companies[name]["orgs"].add(org_id)
        crosswalk.append({
            "siu_itinerary_uuid":route.get("siu_itinerary_uuid",""),
            "siu_base_route_uuid":route.get("siu_base_route_uuid",""),
            "siu_route_name":route.get("siu_display_name",""),
            "siu_org_uuid":org_id,
            "siu_organization_name":obj.get("name","") if obj else "",
            "org_match_status":"confirmed_uuid" if obj else "not_in_public_org_listing",
            "siu_company_names":route.get("siu_company_names",""),
            "siu_company_id":"",
            "company_id_status":"not_observed",
            "source_snapshot_utc":route.get("source_snapshot_utc",""),
        })
    write_csv(OUT/"siu_org_itinerary_crosswalk.csv",
              list(crosswalk[0]),crosswalk)
    company_rows=[{"siu_company_name":name,
                   "itinerary_count":len(data["itineraries"]),
                   "organization_ids":";".join(sorted(data["orgs"])),
                   "siu_company_id":"","company_id_status":"not_observed",
                   "match_status":"name_observed_in_itinerary_not_company_id"}
                  for name,data in sorted(companies.items())]
    write_csv(OUT/"siu_company_candidates.csv",
              ["siu_company_name","itinerary_count","organization_ids","siu_company_id",
               "company_id_status","match_status"],company_rows)
    summary={"itineraries":len(itineraries),"public_organizations":len(orgs),
             "matched_itineraries":sum(x["org_match_status"]=="confirmed_uuid" for x in crosswalk),
             "unmatched_org_ids":sorted(unknown_orgs),"company_name_candidates":len(company_rows),
             "pages":pages,"company_ids_observed":0,
             "note":"Company names are not SIU company IDs; no OrganizationMngCompany lookup attempted."}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# SIU organization and itinerary crosswalk","",
           f"- Itineraries: {len(itineraries)}",
           f"- Matched by organization UUID: {summary['matched_itineraries']}",
           f"- Public organizations returned: {len(orgs)}",
           f"- Distinct observed company-name candidates: {len(company_rows)}",
           f"- Unmatched organization IDs: {len(unknown_orgs)}","",
           "Company IDs are not available in these sources; no company ID has been inferred.",
           "The matching only establishes equality of SIU organization UUIDs, not legal operator identity.",
           "Public access does not establish reuse or redistribution rights."]
    (OUT/"report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))

if __name__=="__main__":main()
