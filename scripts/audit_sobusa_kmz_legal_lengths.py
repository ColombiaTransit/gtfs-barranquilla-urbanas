#!/usr/bin/env python3
"""Compare the SOBUSA 2026 KMZ distances with visually checked official resolution lengths.

Route length alone cannot prove a KMZ A/B label; suspicious swaps require legal street-trace review.
"""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"build/amb-sobusa-pattern-review"
OFFICIAL={
"B18-4175 A":(73.6,"082-2026 p6"),
"B18-4175 B":(75.6,"082-2026 p6"),
"C11-4168":(62.7,"466-2025 p8"),
"C12-4169 A":(47.8,"466-2025 p11"),
"C12-4169 B":(48.6,"466-2025 p11"),
"C13-4143":(48.0,"466-2025 p13"),
"C14-4170":(56.3,"466-2025 p15"),
"C16-4167 A":(63.5,"466-2025 p18"),
"C16-4167 B":(63.3,"466-2025 p18"),
}
def main():
    with (TARGET/"sobusa_variant_candidate_summary.csv").open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    out=[]
    for row in rows:
        label=row["route"]
        if label not in OFFICIAL:raise ValueError("No legal length documented: "+label)
        official,ref=OFFICIAL[label]
        measured=float(row["kmz_length_m"])/1000
        error=measured-official
        base=row["route_id_candidate"]
        variant=row["variant"]
        alternate=None
        if variant in ("A","B"):
            other=base+" "+("B" if variant=="A" else "A")
            if other in OFFICIAL:alternate=OFFICIAL[other][0]
        fits_other= (alternate is not None and
                     abs(measured-alternate)+.25 < abs(measured-official))
        issue=(
            "serious_legal_KMZ_length_mismatch_possible_AB_swap" if abs(error)>=1.0 and fits_other else
            "legal_KMZ_length_difference_over_500m" if abs(error)>=.5 else
            "legal_KMZ_length_difference_250_to_500m" if abs(error)>=.25 else
            "length_reasonably_consistent"
        )
        out.append({
            "company":"SOBUSA","kmz_route_label":label,"legal_resolution":ref,
            "legal_length_km":official,"kmz_length_km":round(measured,3),
            "kmz_minus_legal_km":round(error,3),
            "alternate_variant_legal_length_km":alternate if alternate is not None else "",
            "kmz_nearer_other_AB_length_by_at_least_250m":"yes" if fits_other else "no",
            "length_QA_status":issue,
            "legal_geometry_verified":"no",
            "manual_review_required":"yes" if issue!="length_reasonably_consistent" else "no",
            "interpretation":"A/B length correspondence alone cannot prove a wrong map link",
        })
    if len(out)!=len(OFFICIAL):raise ValueError("Expected 9 SOBUSA legal route-length checks")
    with (TARGET/"sobusa_official_length_vs_kmz_QA.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(out[0]))
        writer.writeheader();writer.writerows(out)
    flag=[x for x in out if x["manual_review_required"]=="yes"]
    text=["# SOBUSA — aanvullende broncontrole: officiële afstand versus KMZ-lengte","",
          "**Waarschuwing:** afstand kan een A/B-omwisseling suggereren maar bewijst die niet. De geordende wettelijke straatbeschrijving is leidend.","",
          "| KMZ-label | Officiële lengte | KMZ-lengte | Verschil | Beoordeling |","|---|---:|---:|---:|---|"]
    for r in out:
        text.append("| {} | {:.1f} km | {:.2f} km | {:+.2f} km | {} |".format(
                    r["kmz_route_label"],r["legal_length_km"],r["kmz_length_km"],
                    r["kmz_minus_legal_km"],r["length_QA_status"]))
    text.extend(["",
      "**B18:** resolutie 082-2026 p6 vermeldt A 73,6 km en B 75,6 km. "
      "De huidige officiële KMZ-data lijkt precies omgekeerd: A ~75,6 km en B ~73,6 km. "
      "Dit is een ernstige **broninconsistentie**; geen automatische correctie van A/B toepassen.",
      "**C16:** 466-2025 p18 vermeldt A 63,5 km en B 63,3 km; KMZ A ~63,2 km en B ~63,9 km. "
      "Dit is een verschil groter dan eenvoudige afronding voor ten minste B. Controleer eerst de straatroute.",
      "",f"**{len(flag)} van {len(out)}** afstandsvergelijkingen verdienen extra handmatige controle.",
      "De primaire brongeometrieën zijn niet veranderd, en er zijn geen GTFS shapes gepubliceerd.",""])
    (TARGET/"legal_length_QA.md").write_text("\n".join(text),encoding="utf-8")
    print(json.dumps({"compared":len(out),"manual_review":len(flag),"warnings":[f["kmz_route_label"] for f in flag]},indent=2))
if __name__=="__main__":
    main()
