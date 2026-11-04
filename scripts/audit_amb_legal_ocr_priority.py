#!/usr/bin/env python3
"""Build evidence-aware AMB legal validity chains and the six-document OCR queue.

Never infer that the largest resolution number or newest year automatically
replaces all older permits. Route codes are only grouped when EXACTLY equal
within an agency. No headway, GTFS route, operator, or legal date is modified.
"""
from __future__ import annotations
import argparse,csv,json,re
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"sources/amb/pdf_manifest.csv"
OCR=ROOT/"docs/ocr_wachtrij.md"
DEST=ROOT/"build/amb-legal-ocr-priority"
# Verified findings from preexisting in-repo source/page-reviewed files.
# The act modifying a route can be evidenced, while current legal validity
# or extension of a limited-term pilot can still be unknown.
PRIORITY=[
 dict(agency="COOLITORAL",route="PT4-4104;PT5-4105",decisions="192-2025;256-2026",observed="256-2026 pilot starts 2026-06-22 for six months; PT4/PT5 A/B four itineraries; 9/14 min each",status="verified_article_effect_pilot_extension_unknown",question="Confirm any subsequent act extending or ending pilot; verify PT4/PT5 A/B current applicability",evidence="docs/siu_remaining_21_route_links_review_2026-11-03.md"),
 dict(agency="COOLITORAL",route="PT2-4102;PT3-4103",decisions="192-2025;210-2026",observed="210-2026 modifies PT2/PT3, 256-2026 pertains PT4/PT5",status="article_effect_documented_current_validity_unverified",question="Check later amendments, complete article effect and current legal service",evidence="sources/amb/coolitoral_resolution_legal_index_2026-11-02.csv"),
 dict(agency="COOLITORAL",route="C19-4178",decisions="192-2025;199-2025",observed="199-2025 corrects formal C19 route code from 192-2025; not an extra route",status="formal_correction_documented",question="Do not create a second route for code typo; check subsequent legal effects",evidence="sources/amb/coolitoral_resolution_legal_index_2026-11-02.csv"),
 dict(agency="SOBUSA",route="B18-4175",decisions="225-2025;466-2025;082-2026",observed="466-2025 B18 5/7 min; later 082-2026 gives A/B each 10/12, jointly 5/6 on busiest shared segment",status="specific_later_amendment_verified",question="Check effective date, further amendments, phased operation and A/B boundaries",evidence="docs/amb_bedrijven/sobusa_466_2025_analysis_2026-11-03.md"),
 dict(agency="SOBUSA",route="C12-4169;C16-4167",decisions="349-2024;466-2025",observed="466-2025 separate A/B headways; combined corridor intervals are not itinerary headways",status="variant_parameters_article_reviewed",question="Check whether intervening/later acts change corridor shares or timetable; establish A/B route boundaries",evidence="docs/amb_bedrijven/sobusa_466_2025_analysis_2026-11-03.md"),
 dict(agency="EMBUSA",route="B9-4125",decisions="113-2012;231-2025;010-2026",observed="010-2026 Article 1 modifies B9-4125, 4/6 min; 00:00-24:00 is conditional on demand",status="latest_documented_amendment_chain_unfinished",question="Compare explicit articles of 231-2025 and 113-2012 for effectivity, revocations, and supersession",evidence="docs/embusa_010_2026_validatie.md"),
 dict(agency="COOTRAB",route="C5-4136;C6-4137",decisions="200-2019;378-2023;358-2024",observed="358-2024 modifies C5/C6 to 8/10 min and adds A1 shared operation with COOLITORAL",status="articles_reviewed_cross_agency_current_status_open",question="Compare A1 joint operation with COOLITORAL 192-2025; keep both operators attributable",evidence="sources/amb/cootrab_resolution_legal_index_2026-11-02.csv"),
 dict(agency="COOTRANTICO",route="B20",decisions="331-2010;025-2011",observed="025-2011 manifest URL points to document titled 331-2010; the original 025 was not inspected",status="WRONG_SOURCE_BLOCKER",question="Locate and validate exact original 025-2011 PDF, then determine legal effect on B20",evidence="sources/amb/resolution_gap_audit_2026-11-02.csv"),
 dict(agency="COOCHOFAL",route="C2-4133;C3-4134;C9-4140;C18-4141",decisions="407-2013;387-2018;242-2025",observed="2025 eight route tables scan checked; potential internal legal/document conflicts remain",status="latest_article_tables_reviewed_aliases_canonicalized",question="Compare operative wording with historical amendments; A15-4159 and C2-B-4188 aliases already resolved",evidence="docs/amb_bedrijven/coochofal_route_frequencies_2026-11-02.md"),
 dict(agency="TRASALIANCO",route="B19-4176;D12-4154;D17-4158;D18-4179",decisions="265-2010;266-2010;268-2010;408-2013",observed="265/266/268-2010 and 408-2013 original article/table pages visually checked; historical D12/B19 4/6, D17 5/7, D18 7/10",status="HISTORICAL_ARTICLES_AND_INTERVALS_VISUALLY_VERIFIED",question="Only later amendments and current route-ID correspondence remain; do not repeat OCR",evidence="docs/amb_ocr_visual_verification_results_2026-11-04.md"),
 dict(agency="TRANSMECAR",route="C17-4160",decisions="324-2010",observed="324-2010 original article/table pages visually verified: historical C17 4/6; implementation conditional on AMB notice",status="HISTORICAL_ARTICLES_AND_INTERVALS_VISUALLY_VERIFIED",question="Only later amendments and current route-ID correspondence remain; do not repeat OCR",evidence="docs/amb_ocr_visual_verification_results_2026-11-04.md"),
 dict(agency="LA_CAROLINA",route="A16-4161",decisions="173-2010;067-2011;204-2012;199-2019",observed="067-2011 articles 2/3 visually verified: route changed; 173-2010 technical parameters retained; 2011-03-30 notifications recorded",status="067_ARTICLES_VISUALLY_VERIFIED_LATER_CHAIN_SEPARATE",question="Only compare 204-2012/199-2019 effect; do not repeat 067 OCR",evidence="docs/amb_ocr_visual_verification_results_2026-11-04.md"),
 dict(agency="ALL_OPERATORS",route="unknown",decisions="448-2025",observed="General metropolitan pilot appears in source audit; affected routes are not identified",status="SCOPE_UNKNOWN_BLOCKER",question="Obtain original act and identify concrete route effects before assigning to any agency",evidence="sources/amb/resolution_gap_audit_2026-11-02.csv"),
]
OVERRIDES={
 ("COOLITORAL","256-2026"):{"url":"https://www.ambq.gov.co/wp-content/uploads/2026/06/RESOLUCION-256-2026-PILOTO-COOLITORAL-1.pdf","evidence":"docs/siu_remaining_21_route_links_review_2026-11-03.md","status":"verified_original_pdf_not_missing"},
 ("COOTRANTICO","025-2011"):{"status":"manifest_wrong_pdf_original_recovered_articles_visually_checked","evidence":"sources/amb/legal_validity_ocr_review/priority_legal_decision_chains.csv"},
 ("MONTERREY","437-2016"):{"status":"manifest_link_corrected_original_pdf_identified","url":"https://www.ambq.gov.co/wp-content/uploads/2017/01/REOLUCION-437-16-MONTERREY..pdf","evidence":"sources/amb/details/resolucion_437-2016_monterrey.csv"},
}
def records(p):
    with p.open("r",newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
def store(p,rows,cols=None):
    if not rows: return
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols or list(rows[0]),extrasaction="ignore")
        w.writeheader();w.writerows(rows)
def resolution_parts(x):
    m=re.fullmatch(r"(\d{1,3})-(\d{4})(?:-v\d+)?",x.strip())
    return (int(m.group(2)),int(m.group(1))) if m else (-1,-1)
def parse_queue():
    rows=[]
    for raw in OCR.read_text(encoding="utf-8").splitlines():
        if not raw.startswith("|") or raw.startswith("| Bedrijf") or raw.startswith("|---"):
            continue
        parts=[s.strip() for s in raw.strip("|").split("|")]
        if len(parts)==5:
            agency,resolution,route,reason,required=parts
            rows.append(dict(agency=agency.upper().replace(" ","_"),
                             resolution=resolution,route=route,
                             original_queue_reason=reason,visual_action=required))
    if len(rows)!=6:
        raise ValueError("Expected six separate central OCR workqueue rows; verify input")
    return rows
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=DEST)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    manifest=records(MANIFEST)
    byid=defaultdict(list)
    byroute=defaultdict(list)
    for r in manifest:
        key=(r["agency"],r["resolution"])
        byid[key].append(r)
        for code in (s.strip() for s in r["route_codes"].split(";")):
            if code:byroute[(r["agency"],code)].append(r)
    ocr_queue=parse_queue()
    backlog=[]
    for q in ocr_queue:
        candidates=byid[(q["agency"],q["resolution"])]
        # Existing manifest URL ≠ downloaded/verified PDF.
        if len(candidates)!=1:
            raise ValueError("Ambiguous or missing OCR manifest identity: "+str(q))
        src=candidates[0]
        backlog.append({
            **q,
            "manifest_url":src["url"],
            "pdf_download_confirmed_this_run":"not_checked",
            "pdf_identity_confirmed_this_run":"not_checked",
            "text_or_OCR_confirmed_this_run":"not_checked",
            "image_review_status":"human_verification_required",
            "legal_classification":"not_confirmed_by_OCR",
            "gtfs_approved":"no",
        })
    store(args.out/"six_ocr_visual_review_queue.csv",backlog)
    anomalies=[]
    for (agency,res),entries in sorted(byid.items()):
        if len(entries)>1 and len({r["url"] for r in entries})>1:
            anomalies.append({"agency":agency,"resolution":res,"problem":"multiple_distinct_manifest_URLs",
                              "manifest_URLs":";".join(sorted({r["url"] for r in entries})),
                              "verified_replacement_URL":"","evidence":"manifest_duplicate_identity",
                              "next_action":"review_pdf_id_not_automatic_merge",
                              "gtfs_legal_status":"unverified"})
        if (agency,res) in OVERRIDES:
            correction=OVERRIDES[agency,res]
            manifest_url=entries[0]["url"]
            anomalies.append({
                "agency":agency,"resolution":res,"problem":correction["status"],
                "manifest_URLs":manifest_url,
                "verified_replacement_URL":correction.get("url",""),
                "evidence":correction["evidence"],
                "next_action":(
                    "replace_stale_document_gap_label_with_verified_article_source" if res=="256-2026" else
                    "original_page_review_pending_for_monterrey" if agency=="MONTERREY" else
                    "original_025_articles_checked_current_effect_separate"),
                "gtfs_legal_status":"still_requires_current_validity_check",
            })
    store(args.out/"manifest_document_identity_and_stale_gap_review.csv",anomalies)
    chains=[]
    for (agency,route),items in sorted(byroute.items()):
        sorted_src=sorted(items,key=lambda x:resolution_parts(x["resolution"]))
        if len(sorted_src)<2:continue
        unique=list(dict.fromkeys(x["resolution"] for x in sorted_src))
        for x in sorted_src:
            y=resolution_parts(x["resolution"])
            newer=[n for n in sorted_src if resolution_parts(n["resolution"])>y]
            chains.append({
                "agency":agency,"exact_route_token_in_manifest":route,
                "resolution":x["resolution"],"manifest_url":x["url"],
                "year":y[0] if y[0]>0 else "",
                "newer_same_exact_route_token_candidates":";".join(dict.fromkeys(n["resolution"] for n in newer)),
                "automatic_supersession_proven":"no",
                "route_code_variant_or_alias_may_change":"yes",
                "article_and_legal_effect_recheck":"required",
                "source_quality":"manifest_only_not_a_legal_verdict",
            })
    store(args.out/"same_exact_route_token_chronology_REVIEW_ONLY.csv",chains)
    selected=[]
    for x in PRIORITY:
        selected.append({
            "agency":x["agency"],"route_codes_to_review":x["route"],
            "decisions_to_compare":x["decisions"],
            "evidenced_legal_finding_from_existing_repo":x["observed"],
            "verification_status":x["status"],
            "open_legal_question":x["question"],
            "source_evidence_path":x["evidence"],
            "current_operation_verified":"no",
            "route_legal_status_auto_approved":"no",
            "next_stage":"inspect_original_operational_articles_plus_last_amendments",
        })
    store(args.out/"priority_legal_decision_chains.csv",selected)
    c=Counter(r["agency"] for r in manifest)
    summary={
        "manifest_rows":len(manifest),
        "manifest_agencies":len(c),
        "distinct_agency_resolution_keys":len(byid),
        "exact_route_token_chronology_rows_for_article_review":len(chains),
        "priority_legal_cases":len(selected),
        "ocr_visual_queue_cases":len(backlog),
        "manifest_identity_and_outdated_gap_flags":len(anomalies),
        "coolitoral_256_2026_recovered_official_pdf":True,
        "cootrantico_025_2011_original_articles_visually_checked":True,
        "all_new_juridical_supersession_conclusions_require_original_articles":True,
        "current_service_or_publication_auto_approved":False,
    }
    (args.out/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    md=["# AMB — juridische besluitketens en OCR/beeldanalyse, onderzoek",
        "",
        "Deze registers zijn **geen** automatische juridische geldigheidsverklaringen.",
        "Een latere resolutie betekent niet noodzakelijk dat elke bepaling van een oudere resolutie is vervallen.",
        "De vergunningstekst, artikel, toepasselijke routevariant, duur, ingang en eventuele intrekking moeten per geval worden aangetoond.",
        "",
        "## Omvang","",
        *("- "+k.replace("_"," ")+": **"+str(v)+"**"
          for k,v in summary.items() if isinstance(v,int) and not isinstance(v,bool)),
        "",
        "## Hoogste prioriteit","",
        "| Vervoerder | Besluitketen | Bevestigd bronfeit / open vraag |",
        "|---|---|---|"]
    for x in selected[:9]:
        md.append("| "+x["agency"]+" "+x["route_codes_to_review"]+" | "+x["decisions_to_compare"]+
                  " | "+x["evidenced_legal_finding_from_existing_repo"].replace("|","/")+
                  "; **open:** "+x["open_legal_question"].replace("|","/")+" |")
    md+=["","## Bron-/OCR-regels","",
         "- 256-2026 COOLITORAL: **niet langer ontbrekend**; pilot-PDF is teruggevonden en eerder inhoudelijk gecontroleerd.",
         "- 025-2011 COOTRANTICO: oude manifestlink is onjuist; het origineel en artikelen 3/6 zijn eerder visueel gecontroleerd. Latere rechtswerking apart.",
         "- 437-2016 MONTERREY: manifest-URL is gecorrigeerd; nieuwe volledige OCR/beeldcontrole volgt via de workflow.",
         "- De zes documenten in de centrale OCR-wachtrij hebben alle een manifest-URL, maar dit bewijst geen feitelijke download of bronidentiteit.",
         "- OCR + beelden moeten met de originele resolutie, datum, route en artikeltekst worden gecontroleerd voordat een rechtsgevolg wordt bevestigd.",
         "- Vloot-/capaciteitscijfers zijn buiten de GTFS-scope; ze blijven slechts ongewijzigd als historisch brongegeven.",
         "- Geen GTFS-productiebronnen, fysieke SIU-haltes of vergunde frequenties gewijzigd.",
         ""]
    (args.out/"summary.md").write_text("\n".join(md),encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
if __name__=="__main__":
    main()
