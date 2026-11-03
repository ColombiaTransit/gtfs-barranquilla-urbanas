#!/usr/bin/env python3
"""Compare two full SIU stop sequences with the actual 256-2026 pilot street acts.

Read the CURRENT 256 pilot structured from the recovered original PDF, not the
2019 GIS. Recognize legal route start corridor versus first SIU stop and search
for B-only detour street names with their original SIU sequence numbers.
These clues are NOT enough by themselves to certify A/B pattern mapping.
"""
import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"sources/siu/public_extract/siu_route_stop_sequences.csv"
LEGAL=ROOT/"sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv"
OUT=Path("build/siu-coolitoral-256-street-audit")
MAP=[
 ("CIRCUNVALAR VIA 40","PT4-4104","PT5-4105","Calle 17","Calle 17 con Carrera 30"),
 ("VIA 40 CIRCUNVALAR","PT5-4105","PT4-4104","Via 40","Via 40 No 51-310"),
]
PATTERNS={
 "CALLE 17":r"\bCALLE\s*17\b",
 "VIA 40":r"\bVIA\s*40\b",
 "CIRCUNVALAR":r"\bCIRCUNVALAR\b",
 "CALLE 19":r"\bCALLE\s*19\b",
 "CALLE 30":r"\bCALLE\s*30\b",
 "CARRERA 30":r"\bCARRERA\s*30\b",
 "CARRERA 38":r"\bCARRERA\s*38\b",
 "CARRERA 44":r"\bCARRERA\s*44\b",
 "CALLE 10":r"\bCALLE\s*10\b",
 "CARRERA 41B":r"\bCARRERA\s*41B\b",
 "CALLE 8":r"\bCALLE\s*8\b",
 "CARRERA 43":r"\bCARRERA\s*43\b",
 "CALLE 4":r"\bCALLE\s*4\b",
}
def read(path):
    with open(path,newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def write(path,rows,cols):
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore");w.writeheader();w.writerows(rows)
def norm(text):
    s=unicodedata.normalize("NFKD",str(text or "").upper())
    return "".join(c for c in s if not unicodedata.combining(c))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    all_stops=[x for x in read(SRC) if x.get("likely_test_itinerary")=="false"]
    legal=read(LEGAL);bylegal=defaultdict(dict)
    for row in legal:bylegal[row["route_code"]][row["itinerary"]]=row
    assert sorted(bylegal)==["PT4-4104","PT5-4105"]
    assert all(set(v)=={"A","B"} for v in bylegal.values())
    byname=defaultdict(list)
    for row in all_stops:byname[row["siu_display_name"]].append(row)
    results=[];examples=[]
    for siu_name,base,other,street,terminal in MAP:
        stoprows=sorted(byname[siu_name],key=lambda r:int(r["siu_stop_sequence"]))
        assert len(stoprows) in (124,132),len(stoprows)
        for streetname,pattern in PATTERNS.items():
            hits=[r for r in stoprows if re.search(pattern,norm(r["stop_name"]))]
            # Include up to 5 representative matching stop names; specific street
            # visits may appear on both outbound and return, so retain sequence.
            for r in hits[:5]:
                examples.append({
                    "siu_name":siu_name,"legal_base_hypothesis":base,
                    "street_name":streetname,
                    "stop_sequence":r["siu_stop_sequence"],
                    "siu_stop_uuid":r["siu_stop_uuid"],
                    "siu_stop_name":r["stop_name"],
                    "gps_lat":r["stop_lat"],"gps_lon":r["stop_lon"],
                })
        count={}
        for k,pattern in PATTERNS.items():
            hit=[r for r in stoprows if re.search(pattern,norm(r["stop_name"]))]
            count[k]={"n_stopnames":len(hit),"sequence_numbers":[int(r["siu_stop_sequence"]) for r in hit]}
        uniqueB=bylegal[base]["B"]["exclusive_branch_streets"].split("; ")
        Bcount=sum(count[x]["n_stopnames"]>0 for x in uniqueB)
        notes=(
            "First visible SIU stop lies on the same main street as the 2026 pilot's dispatch terminal, "
            "but differing intersection/address means NOT a proven exact terminal; "
            "2026 legal route TITLE order suggests the opposite PT4/PT5 code. "
            "B-only corridor named stops may be sparse or ambiguous, so do not auto-assign A or B."
        )
        results.append({
            "siu_name":siu_name,"siu_itinerary_uuid":stoprows[0]["siu_itinerary_uuid"],
            "siu_stop_count":len(stoprows),
            "first_stop":stoprows[0]["stop_name"],"last_stop":stoprows[-1]["stop_name"],
            "2026_legal_base_from_initial_street_hypothesis":base,
            "2026_legal_base_from_title_order_hypothesis":other,
            "2026_dispatch_terminal_on_base":terminal,
            "initial_main_street_in_source":street,
            "legal_B_specific_branch_streets":";".join(uniqueB),
            "B_specific_branches_with_named_SIU_stops":Bcount,
            "B_named_branch_support":";".join(k for k in uniqueB if count[k]["n_stopnames"]),
            "2026_legal_A_B_resolution":"not_decidable_from_stopname_street_tokens",
            "current_legal_base_status":"competing_title_vs_initial_street_hypotheses",
            "review_notes":notes,
            **{f"siu_named_{k.lower().replace(' ','_')}":v["n_stopnames"] for k,v in count.items()},
        })
    write(OUT/"pt4_pt5_street_sequence_review.csv",results,list(results[0]))
    write(OUT/"sample_matched_siu_street_landmarks.csv",examples,list(examples[0]))
    summary={
      "original_256_2026_pdf_verified":True,
      "route_variants_in_pdf":4,
      "regular_siu_itineraries_reviewed":2,
      "siu_route_stop_occurrences":sum(x["siu_stop_count"] for x in results),
      "source_legal_street_reference":"sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv",
      "source_pdf":"https://www.ambq.gov.co/wp-content/uploads/2026/06/RESOLUCION-256-2026-PILOTO-COOLITORAL-1.pdf",
      "A_B_legal_itineraries_verified_in_pdf":4,
      "PT4_PT5_siu_base_assignments_legally_confirmed":0,
      "SIU_to_A_B_variant_assignments_legally_confirmed":0,
      "warning":"Not enough evidence that the first SIU stop is an official terminal, and street-name tokens are not an authoritative path ordering."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# SIU PT4/PT5 vs ORIGINAL 256-2026 street trajectories","",
           "The complete original 7-page PDF was verified; PT4 and PT5 each have A/B with different side-street branches.",""]
    for row in results:
        lines += [f'- **{row["siu_name"]}**: {row["siu_stop_count"]} stops; '
                  f'first SIU stop **{row["first_stop"]}**; '
                  f'initial-street candidate **{row["2026_legal_base_from_initial_street_hypothesis"]}** '
                  f'versus title-order candidate **{row["2026_legal_base_from_title_order_hypothesis"]}**; '
                  f'B-only named street markers {row["B_specific_branches_with_named_SIU_stops"]} '
                  f'out of {len(bylegal[row["2026_legal_base_from_initial_street_hypothesis"]]["B"]["exclusive_branch_streets"].split("; "))}.']
    lines += ["","**Neither A/B nor base route legally confirmed** from these clues alone. "
              "Actual GIS/route sequencing and clarification on SIU naming conventions still required."]
    (OUT/"summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
