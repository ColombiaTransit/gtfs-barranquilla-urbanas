#!/usr/bin/env python3
"""Test SIU organization GraphQL operations extracted from user-provided JS bundles.

No credentials; no introspection; no guessed IDs; read-only operations only.
"""
import csv
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://siu.ambq.gov.co/api/pis-gateway/graphql/http"
OUT = Path("build/siu-organization-probe")
QUERIES = {
    "OrganizationMngOrganizationWithoutAuthListing": """
query OrganizationMngOrganizationWithoutAuthListing($filterInput:OrganizationMngOrganizationFilterInput,$paginationInput:OrganizationMngOrganizationPaginationInput,$sortInput:OrganizationMngOrganizationSortInput) {
 OrganizationMngOrganizationWithoutAuthListing(filterInput:$filterInput,paginationInput:$paginationInput,sortInput:$sortInput) {
  listing { id name active logoUrl attributes }
  queryTotalResultCount
 }
}""",
    "OrganizationMngOrganizationListing": """
query OrganizationMngOrganizationListing($filterInput:OrganizationMngOrganizationFilterInput,$paginationInput:OrganizationMngOrganizationPaginationInput,$sortInput:OrganizationMngOrganizationSortInput) {
 OrganizationMngOrganizationListing(filterInput:$filterInput,paginationInput:$paginationInput,sortInput:$sortInput) {
  listing { id name active logoUrl }
  queryTotalResultCount
 }
}""",
    "OrganizationMngCompany": """
query OrganizationMngCompany($id:ID!,$organizationId:String!) {
 OrganizationMngCompany(id:$id,organizationId:$organizationId) { id name logoUrl }
}""",
}

def call(name, variables):
    payload=json.dumps({"operationName":name,"query":QUERIES[name],"variables":variables}).encode()
    req=urllib.request.Request(ENDPOINT,data=payload,headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"ColombiaTransit-SIU-organization-research/1.0"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=35) as resp:
            status=resp.status
            data=json.loads(resp.read(3_000_000).decode("utf-8"))
    except urllib.error.HTTPError as e:
        status=e.code
        try:data=json.loads(e.read(100_000).decode("utf-8"))
        except Exception:data={}
    except Exception as e:
        return {"operation":name,"status":"network_error","error_type":type(e).__name__},None
    errors=data.get("errors") if isinstance(data,dict) else None
    result=data.get("data",{}).get(name) if isinstance(data,dict) and isinstance(data.get("data"),dict) else None
    return {"operation":name,"http_status":status,"status":"graphql_errors" if errors else ("ok" if status==200 and result is not None else "empty_or_unexpected"),
            "error_messages":[str(x.get("message",""))[:250] for x in errors[:5] if isinstance(x,dict)] if isinstance(errors,list) else [],
            "result_type":type(result).__name__},result

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    reports=[]
    rows=[]
    for name in ("OrganizationMngOrganizationWithoutAuthListing","OrganizationMngOrganizationListing"):
        status,result=call(name,{})
        if isinstance(result,dict):
            listing=result.get("listing")
            if isinstance(listing,list):
                status["returned_count"]=len(listing)
                status["query_total_result_count"]=result.get("queryTotalResultCount")
                for obj in listing:
                    if isinstance(obj,dict):
                        rows.append({"operation":name,"org_id":str(obj.get("id") or ""),"name":str(obj.get("name") or ""),"active":str(obj.get("active") or ""),"attributes_present":str(obj.get("attributes") is not None)})
        reports.append(status)
    company_id=os.getenv("SIU_COMPANY_ID","").strip()
    org_id=os.getenv("SIU_ORGANIZATION_ID","").strip()
    if company_id and org_id:
        status,result=call("OrganizationMngCompany",{"id":company_id,"organizationId":org_id})
        if isinstance(result,dict):
            status["company"]={"id":result.get("id"),"name":result.get("name")}
        reports.append(status)
    else:
        reports.append({"operation":"OrganizationMngCompany","status":"not_tested","reason":"Both SIU_COMPANY_ID and SIU_ORGANIZATION_ID are required; no IDs guessed"})
    with (OUT/"organizations.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["operation","org_id","name","active","attributes_present"])
        writer.writeheader()
        writer.writerows(rows)
    data={"timestamp_utc":datetime.now(timezone.utc).isoformat(),"endpoint":ENDPOINT,
          "source":"Queries transcribed from user-supplied main.3437e7aa.chunk.js",
          "results":reports,"organization_rows":len(rows)}
    (OUT/"results.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# SIU organization GraphQL probe","",f"Endpoint: {ENDPOINT}","","| Operation | Status | HTTP | Rows |","|---|---|---|---:|"]
    for r in reports:
        lines.append(f"| {r['operation']} | {r['status']} | {r.get('http_status','—')} | {r.get('returned_count','—')} |")
        for msg in r.get("error_messages",[]):lines.append(f"  - GraphQL error: {msg}")
    lines.extend(["","The company lookup is deliberately skipped without an independently established company ID and organization ID.","No mutations or subscriptions were executed."])
    (OUT/"report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))
    if all(r["status"]=="network_error" for r in reports[:2]):
        raise SystemExit("Both organization list probes failed at network level")

if __name__=="__main__":
    main()
