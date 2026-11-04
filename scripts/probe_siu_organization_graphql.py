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
    OUT.mkdir(parents=True, exist_ok=True)
    reports = []
    rows = []
    seen = set()
    public_name = "OrganizationMngOrganizationWithoutAuthListing"

    # First obtain an actual organization ID from the server, not from a guessed value.
    initial, result = call(public_name, {})
    reports.append(initial)
    total = None
    if isinstance(result, dict):
        total = result.get("queryTotalResultCount")
        for obj in result.get("listing") or []:
            if isinstance(obj, dict) and obj.get("id"):
                seen.add(str(obj["id"]))
                rows.append({"operation": public_name, "org_id": str(obj["id"]),
                             "name": str(obj.get("name") or ""), "active": str(obj.get("active") or ""),
                             "attributes_present": str(obj.get("attributes") is not None)})
    initial["returned_count"] = len(rows)
    initial["query_total_result_count"] = total

    # PaginationInput fields are not established by the supplied bundles.
    # Try a bounded set of common shapes; record GraphQL validation errors instead
    # of treating any rejected shape as a working pagination contract.
    pagination_attempts = [
        {"page": 0, "count": 100},
        {"page": 1, "count": 100},
    ]
    successful_pagination = None
    for pg in pagination_attempts:
        status, result = call(public_name, {"paginationInput": pg})
        status["pagination_input"] = pg
        if status["status"] == "ok" and isinstance(result, dict) and isinstance(result.get("listing"), list):
            successful_pagination = pg
            status["returned_count"] = len(result["listing"])
            for obj in result["listing"]:
                if isinstance(obj, dict) and obj.get("id") and str(obj["id"]) not in seen:
                    seen.add(str(obj["id"]))
                    rows.append({"operation": public_name, "org_id": str(obj["id"]),
                                 "name": str(obj.get("name") or ""), "active": str(obj.get("active") or ""),
                                 "attributes_present": str(obj.get("attributes") is not None)})
            reports.append(status)
            break
        reports.append(status)

    # The authenticated listing was already proven to require a token.
    reports.append({"operation": "OrganizationMngOrganizationListing", "status": "previously_confirmed_auth_required",
                    "reason": "Run 41882834699: No authorization token"})
    company_id = os.getenv("SIU_COMPANY_ID", "").strip()
    explicit_org = os.getenv("SIU_ORGANIZATION_ID", "").strip()
    org_id = explicit_org or (next(iter(sorted(seen))) if len(seen) == 1 else "")
    if company_id and org_id:
        status, company = call("OrganizationMngCompany", {"id": company_id, "organizationId": org_id})
        if isinstance(company, dict):
            status["company"] = {"id": company.get("id"), "name": company.get("name")}
        reports.append(status)
    else:
        reports.append({"operation": "OrganizationMngCompany", "status": "not_tested",
                        "reason": "A verified company ID is still required; organization ID alone is insufficient",
                        "organization_id_available": bool(org_id)})

    with (OUT / "organizations.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["operation", "org_id", "name", "active", "attributes_present"])
        writer.writeheader()
        writer.writerows(rows)
    data = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "endpoint": ENDPOINT,
            "source": "User-supplied SIU JavaScript bundles", "results": reports,
            "organization_rows": len(rows), "organization_ids": sorted(seen),
            "pagination_confirmed": successful_pagination}
    (OUT / "results.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# SIU organization GraphQL probe", "",
             f"Unique organizations: {len(rows)}", f"Known org IDs: {', '.join(sorted(seen)) or 'none'}",
             f"Working pagination: {successful_pagination or 'not established'}", "",
             "| Operation | Status | HTTP | Rows |", "|---|---|---|---:|"]
    for r in reports:
        lines.append(f"| {r['operation']} | {r['status']} | {r.get('http_status', '—')} | {r.get('returned_count', '—')} |")
        for msg in r.get("error_messages", []):
            lines.append(f"  - GraphQL error: {msg}")
    lines.extend(["", "Company lookup requires an independently verified company ID.",
                  "Only read-only queries are executed."])
    (OUT / "report.md").write_text("\\n".join(lines) + "\n", encoding="utf-8")
    print("\\n".join(lines))
    if initial["status"] == "network_error":
        raise SystemExit("Public organization query failed at network level")


if __name__ == "__main__":
    main()
