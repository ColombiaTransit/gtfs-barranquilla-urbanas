#!/usr/bin/env python3
"""Review all 21 unresolved SIU→AMB route links using ordered stop data.

Evidence separation:
- SIU supplied actual route names, provider(s), and ordered GPS visits.
- AMB 256-2026 ORIGINAL PDF and curated table supplied PT4/PT5 titles, A/B street sequences, terminals and headways.
- GIS 2019/2023 supplied only geographic top/second candidates.
- No SIU itinerary contains a legal AMB route code or explicit A/B.
Never turn geographic/route-name candidates into confirmed legal matches.
"""
import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SIU=ROOT/"sources/siu"
REV=SIU/"gtfs_staging/siu_amb_route_crosswalk_review.csv"
STOPS=SIU/"public_extract/siu_route_stop_sequences.csv"
ROUTES=ROOT/"gtfs/routes.txt"
PILOT=ROOT/"sources/amb/details/resolucion_256-2026.csv"
PT_TERMINALS=ROOT/"sources/amb/details/coolitoral_192_2025_pt4_pt5_terminals_verified_2026-11-03.csv"
PILOT_STREETS=ROOT/"sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv"

def read(path):
    with path.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def write(path,rows,keys):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction="ignore");w.writeheader();w.writerows(rows)
def norm(s):
    s=unicodedata.normalize("NFKD",str(s or "").upper())
    return "".join(c for c in s if not unicodedata.combining(c))
def compact(s):return re.sub(r"[^A-Z0-9]","",norm(s))
def gtfs_base(short):
    return re.sub(r"(?<=\d{4})[- ]?[AB]$","",norm(short))
def gis_base(code):
    return re.sub(r"\s+","",norm(code))
def licensable(row):
    return row["route_id"].startswith("AMB_") and row["route_type"]=="3"

def pairwise_metrics(a,b):
    """Evidence only: identical GPS or name, no inferred A/B direction."""
    def geopoint(r):
        try:return (round(float(r["stop_lat"]),6),round(float(r["stop_lon"]),6))
        except(ValueError,TypeError,KeyError):return None
    ai=[geopoint(x) for x in a]
    bi=[geopoint(x) for x in b]
    aa={x for x in ai if x};bb={x for x in bi if x}
    common=aa&bb
    namesa={compact(x["stop_name"]) for x in a}
    namesb={compact(x["stop_name"]) for x in b}
    idxa={p:i for i,p in enumerate(ai) if p in common}
    idxb={p:i for i,p in enumerate(bi) if p in common}
    ordered=sorted(common,key=lambda p:idxa[p])
    ahead=behind=0
    for p,q in zip(ordered,ordered[1:]):
        if idxb[q]>idxb[p]:ahead+=1
        elif idxb[q]<idxb[p]:behind+=1
    return {
      "same_gps_rounded_6_decimals":len(common),
      "gps_jaccard_pct":round(100*len(common)/len(aa|bb),1) if (aa|bb) else 0,
      "same_normalized_stop_names":len(namesa&namesb),
      "name_jaccard_pct":round(100*len(namesa&namesb)/len(namesa|namesb),1) if (namesa|namesb) else 0,
      "shared_gps_adjacent_same_order":ahead,
      "shared_gps_adjacent_reverse_order":behind,
      "route_a_stop_count":len(a),"route_b_stop_count":len(b),
    }

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    reviews=read(REV);routes=read(ROUTES);itinerary_stops=read(STOPS);legal=read(PILOT);verified_terminal_rows=read(PT_TERMINALS);legal_street_rows=read(PILOT_STREETS)
    assert len(reviews)==33,len(reviews)
    grouped=defaultdict(list)
    for s in itinerary_stops:
        if s["likely_test_itinerary"]!="true":
            grouped[s["siu_itinerary_uuid"]].append(s)
    for uid,stops in grouped.items():
        stops.sort(key=lambda x:int(x["siu_stop_sequence"]))
        assert [int(x["siu_stop_sequence"]) for x in stops]==list(range(1,len(stops)+1)),uid
    bybase=defaultdict(list)
    for r in routes:
        assert licensable(r)
        bybase[compact(gtfs_base(r["route_short_name"]))].append(r)
    pilot_bybase=defaultdict(list)
    for r in legal:
        pilot_bybase[r["codigo_base"]].append(r)
    assert set(pilot_bybase)=={"PT4-4104","PT5-4105"}
    terminal_bybase={r["route_code"]:r for r in verified_terminal_rows}
    assert set(terminal_bybase)=={"PT4-4104","PT5-4105"}
    assert all({r["itinerario"] for r in rs}=={"A","B"} for rs in pilot_bybase.values())
    street_bybase=defaultdict(dict)
    for row in legal_street_rows:street_bybase[row["route_code"]][row["itinerary"]]=row
    assert set(street_bybase)=={"PT4-4104","PT5-4105"}
    assert all(set(it)=={"A","B"} for it in street_bybase.values())

    # This is not inferred from GIS proximity: the *order of the terms* in
    # the SIU display name matches that of the curated resolution 256-2026
    # PT4 and PT5 'nombre_ruta'. A/B remains unknown for BOTH.
    title_order={
       "VIA 40 CIRCUNVALAR":("PT4-4104","route_title_matches_primary_192_2025_and_primary_256_2026"),
       "CIRCUNVALAR VIA 40":("PT5-4105","route_title_matches_192_2025_and_curated_256_2026")
    }
    # Verified terminal descriptions of BOTH original 192-2025 and 256-2026
    # PDFs point to the opposite route from SIU display-name order.
    # SIU first stop is not itself proven to be an official terminal.
    terminal_order={
        "VIA 40 CIRCUNVALAR":"PT5-4105",
        "CIRCUNVALAR VIA 40":"PT4-4104"
    }
    open_rows=[];proposals=[];proposals_stop_orders=[]
    by_uuid={r["siu_itinerary_uuid"]:r for r in reviews}
    def routeoptions(code):
        return bybase.get(compact(code),[])
    for it in reviews:
        if it["route_match_status"]=="high_confidence_provisional":
            continue
        uid=it["siu_itinerary_uuid"];name=it["siu_name"]
        company=[x.strip() for x in it["siu_companies"].split(";") if x.strip()]
        original_code=gis_base(it["candidate_amb_route_code"])
        base=original_code
        evidence="legacy_gis_code_best_spatial_match_not_current_legal_identity"
        special=title_order.get(norm(name))
        if special:
            base,evidence=special
        choices=routeoptions(base)
        options=[r["route_id"] for r in choices]
        one_company=len(company)==1
        status=it["route_match_status"]
        if special:
            verdict="primary_256_title_vs_first_siu_street_conflict"
            next_action="Original 256-2026 PDF inspected: SIU name matches one legal title while SIU first stop is on the street of the opposite legal dispatch terminal. A/B branch named stops were also compared; none provides proof. Inspect original 256 street path against complete SIU GPS route or clarify SIU naming conventions."
        elif not one_company:
            verdict="shared_operator_route_pattern_not_allocatable"
            next_action="Resolve operator-specific licensing and pattern/frequency shares; do not replicate one stop list to multiple companies."
        elif len(choices)>1:
            verdict="base_code_plausible_but_AB_pattern_unresolved"
            next_action="Extract direction A/B itinerary street sequences from applicable resolution; compare first/last SIU segments and return loop."
        elif not choices:
            verdict="no_matching_current_GTFS_base_code"
            next_action="Inspect current licensed route table; check GIS spelling and obsolete codes."
        elif it["route_match_status"]=="top_gis_operator_does_not_match_siu":
            verdict="operator_conflict_blocks_mapping"
            next_action="Find correct legal agency/route from licenses; top GIS candidate has a different operator."
        else:
            verdict="provisional_base_candidate_legal_review_required"
            next_action="Compare operator, route naming and full legal street itinerary; check stale GIS 2019/2023 versus current 2026 SIU."
        stopdata=grouped.get(uid,[])
        if len(stopdata)!=int(it["siu_stop_count"]):
            raise ValueError("SIU stop count mismatch for "+name)
        full={
          "siu_itinerary_uuid":uid,"siu_name":name,"siu_companies":it["siu_companies"],
          "siu_stop_count":len(stopdata),"prior_issue":status,
          "legacy_gis_top_code":it["candidate_amb_route_code"],
          "legacy_gis_top_coverage_pct":it["top_gis_coverage_pct"],
          "legacy_gis_runner_up":it["second_gis_name"],
          "proposed_amb_base_code":base,
          "base_code_evidence":evidence,
          "alternative_amb_base_by_2025_terminal":terminal_order.get(norm(name),""),
          "alternative_amb_base_by_2026_terminal":terminal_order.get(norm(name),""),
          "independent_2025_terminal_evidence":terminal_bybase[terminal_order[norm(name)]]["official_dispatch_terminal"] if special else "",
          "verified_2026_terminal_evidence":street_bybase[terminal_order[norm(name)]]["A"]["dispatch_terminal"] if special else "",
          "base_route_hypotheses_conflict":str(bool(special)).lower(),
          "possible_gtfs_route_ids":";".join(options),
          "resolved_amb_AB_itinerary":"",
          "can_assign_pattern_specific_GTFS_route_id":"no",
          "crosswalk_review_status":verdict,
          "first_siu_stop":stopdata[0]["stop_name"] if stopdata else "",
          "last_siu_stop":stopdata[-1]["stop_name"] if stopdata else "",
          "first_siu_lat":stopdata[0]["stop_lat"] if stopdata else "",
          "first_siu_lon":stopdata[0]["stop_lon"] if stopdata else "",
          "last_siu_lat":stopdata[-1]["stop_lat"] if stopdata else "",
          "last_siu_lon":stopdata[-1]["stop_lon"] if stopdata else "",
          "source_siu_snapshot_utc":it["source_siu_snapshot_utc"],
          "source_amb_resolution":"256-2026" if special else "",
          "source_legal_review_status":"192_2025_and_256_2026_primary_PDF_titles_terminals_and_AB_routes_verified;SIU_mapping_ambiguous" if special else "no_specific_legal_text_verified",
          "next_manual_evidence":next_action,
          "final_legal_route_match_confirmed":"no",
        }
        open_rows.append(full)
        if one_company and len(options)==1 and verdict=="provisional_base_candidate_legal_review_required":
            # Crosswalk only is stored as a proposal; do not overwrite the
            # canonical 12-match CSV or GTFS input until legal review.
            proposals.append({k:full[k] for k in ["siu_itinerary_uuid","siu_name","siu_companies",
                "proposed_amb_base_code","possible_gtfs_route_ids","base_code_evidence",
                "crosswalk_review_status","final_legal_route_match_confirmed"]})
            for stop in stopdata:
                proposals_stop_orders.append({
                    "siu_itinerary_uuid":uid,"siu_name":name,
                    "route_code_candidate":base,
                    "gtfs_route_id_candidate":options[0],
                    "stop_sequence":stop["siu_stop_sequence"],
                    "siu_stop_uuid":stop["siu_stop_uuid"],
                    "stop_name":stop["stop_name"],
                    "stop_lat":stop["stop_lat"],"stop_lon":stop["stop_lon"],
                    "source_status":"route_name_plus_legacy_GIS_proposal_not_legal_confirmation",
                })

    assert len(open_rows)==21,len(open_rows)
    tp=[r for r in open_rows if r["siu_name"] in title_order]
    assert len(tp)==2
    assert {r["siu_name"]:r["proposed_amb_base_code"] for r in tp}=={
        "VIA 40 CIRCUNVALAR":"PT4-4104",
        "CIRCUNVALAR VIA 40":"PT5-4105"
    }
    assert all(r["base_route_hypotheses_conflict"]=="true" and
               r["proposed_amb_base_code"]!=r["alternative_amb_base_by_2025_terminal"]
               for r in tp)

    names=["CIRCUNVALAR VIA 40","VIA 40 CIRCUNVALAR",
           "MIRAMAR ALAMEDA DEL RIO","LAS GAVIOTAS CALLE 76",
           "CENTRO CIRCUNVALAR","CIRCUNVALAR CENTRO",
           "CALLE 30","CALLE 17",
           "LAS PALMAS","LAS NIEVES"]
    pair_groups=[
       (names[0],names[1]),
       (names[2],names[3]),
       (names[4],names[5]),
       (names[6],names[7]),
       (names[8],names[9])
    ]
    by_name={r["siu_name"]:r for r in reviews}
    comparisons=[]
    for a,b in pair_groups:
        ra,rb=by_name[a],by_name[b]
        m=pairwise_metrics(grouped[ra["siu_itinerary_uuid"]],grouped[rb["siu_itinerary_uuid"]])
        comparisons.append({"siu_name_a":a,"siu_name_b":b,
            "siu_itinerary_uuid_a":ra["siu_itinerary_uuid"],
            "siu_itinerary_uuid_b":rb["siu_itinerary_uuid"],**m,
            "decision":"distinct_SIU_ordered_itineraries_not_evidence_of_legal_A_B_mapping"})
    for row in tp:
        row["comparison_pair_name"]="VIA 40 CIRCUNVALAR" if row["siu_name"]=="CIRCUNVALAR VIA 40" else "CIRCUNVALAR VIA 40"

    def writeout(name,rows):
        assert rows
        write(out/name,rows,list(rows[0]))
    writeout("open_21_route_crosswalk_review.csv",open_rows)
    writeout("provisional_base_route_code_candidates.csv",proposals)
    writeout("provisional_base_route_stop_sequences_NO_TIMES.csv",proposals_stop_orders)
    writeout("selected_siu_sequence_pair_comparison.csv",comparisons)
    fields=["siu_itinerary_uuid","siu_name","proposed_amb_base_code","possible_gtfs_route_ids",
            "source_amb_resolution","title_based_candidate","terminal_based_candidate",
            "official_192_terminal","official_256_terminal","legal_A_B_itinerary",
            "peak_minutes_each_AB","offpeak_minutes_each_AB","SIU_stop_count","review_status"]
    pt_rows=[]
    for r in tp:
        related=pilot_bybase[r["proposed_amb_base_code"]]
        pt_rows.append({
            "siu_itinerary_uuid":r["siu_itinerary_uuid"],
            "siu_name":r["siu_name"],
            "proposed_amb_base_code":r["proposed_amb_base_code"],
            "possible_gtfs_route_ids":r["possible_gtfs_route_ids"],
            "source_amb_resolution":"256-2026 (verified original PDF);192-2025 (verified original PDF)",
            "title_based_candidate":r["proposed_amb_base_code"],
            "terminal_based_candidate":r["alternative_amb_base_by_2025_terminal"],
            "official_192_terminal":r["independent_2025_terminal_evidence"],
            "official_256_terminal":r["verified_2026_terminal_evidence"],
            "legal_A_B_itinerary":"",
            "peak_minutes_each_AB":";".join(f'{x["itinerario"]}:{x["intervalo_pico_min"]}' for x in related),
            "offpeak_minutes_each_AB":";".join(f'{x["itinerario"]}:{x["intervalo_valle_min"]}' for x in related),
            "SIU_stop_count":r["siu_stop_count"],
            "review_status":"contradicting_title_and_terminal_base_codes_AB_unknown"
        })
    write(out/"pt4_pt5_pilot_specific_review.csv",pt_rows,fields)
    statuses=dict(Counter(r["crosswalk_review_status"] for r in open_rows))
    summary={
       "siu_open_records_reviewed":len(open_rows),
       "PT4_PT5_base_route_title_matches":len(tp),
       "PT4_PT5_terminal_conflicts_to_reconcile":len(tp),
       "PT4_PT5_AB_assignments_verified":0,
       "single_operator_single_route_base_proposals":len(proposals),
       "stop_occurrences_in_new_single_route_proposals":len(proposals_stop_orders),
       "shared_operator_or_AB_or_uncertain_remaining":len(open_rows)-len(proposals),
       "legally_confirmed_new_route_matches":0,
       "prior_high_confidence_geographic_candidates_untouched":12,
       "open_issue_statuses":statuses,
       "pairwise_stop_sequence_comparisons":len(comparisons),
       "source_legal_table":"sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv",
       "original_256_PDF_verified":True,
       "warning":"No legal A/B assignments, no TPC GTFS route_id modifications or stop_times; proposals only."
    }
    (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Review of 21 unresolved public SIU→AMB itinerary crosswalks","",
        "**All 21 cases processed. No assignment to an A/B route pattern has been verified.**","",
        "## Results",""]
    lines.extend(f"- {k}: {v}" for k,v in summary.items() if isinstance(v,(int,str)))
    lines+=["","## PT4/PT5 (source 256-2026)",""]
    for x in tp:
        lines.append(f'- SIU **{x["siu_name"]}** ({x["siu_stop_count"]} stops): '
                     f'**title suggests {x["proposed_amb_base_code"]}** while '
                     f'**2026 legal terminal street suggests {x["alternative_amb_base_by_2026_terminal"]}**. '
                     'This contradiction blocks any base or A/B confirmation.')
    lines+=["","For PT4 and PT5, each of A and B has **9 min peak / 14 min offpeak** according to the curated resolution table. "
            "A/B refers to a licensed pattern, not automatically the SIU route's outbound/return half. "
            "A 2019 GIS line that matches at 100% to both routes does not disambiguate direction.",
            "**Both original 192-2025 and 256-2026 PDFs have been checked:** PT4 A/B starts at Calle 17/Carrera 30 and PT5 A/B at Vía 40 No. 51-310. "
            "In 256 the B variants use distinct side-street branches; exact SIU A/B crosswalk still cannot be proven from available names.",
            "","## Other unresolved links",""]
    for x in open_rows:
        if x in tp:continue
        lines.append(f'- {x["siu_name"]} ({x["siu_companies"]}): '
                     f'{x["proposed_amb_base_code"] or "unknown"} — {x["crosswalk_review_status"]}')
    lines+=["","No timetable, stop_times, approved direction or final mapping added to GTFS.",
            "Original 256-2026 verified and compared; pilot starts 22 June 2026 for six months with possible extension. "
            "Continued legal applicability and SIU-to-licensed A/B ID assignment remain separate checks."]
    (out/"summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="build/siu-open-route-review")
    args=p.parse_args()
    run(args.out)
