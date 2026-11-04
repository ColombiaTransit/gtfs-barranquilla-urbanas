#!/usr/bin/env python3
"""Prepare GTFS headway/service-window candidates without inventing stops or trips.

Inputs: official AMB resolution research tables, historic July 2020 route
dispatch windows explicitly adopted as provisional model, gtfs/routes.txt.
Outputs: one candidate per GTFS route_id, weekday time periods, unresolved
route issues, and machine-readable summary.

This is NOT a GTFS feed. Actual GTFS needs stops, stop_times, trips and a
calendar; no synthetic geometries, GPS points or trip running times are made.
"""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sources" / "amb"
MODEL = "AMB_WEEKDAY_0709_1720_V1"
WINDOW_MODEL = "AMB_2020_DISPATCH_PROVISIONAL_2026_V1"
PERIODS = [
    ("early_offpeak", 0, 420, "offpeak"),
    ("morning_peak", 420, 540, "peak"),
    ("daytime_offpeak", 540, 1020, "offpeak"),
    ("evening_peak", 1020, 1200, "peak"),
    ("late_offpeak", 1200, 1440, "offpeak"),
]

def load(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))

def n(s):
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper())

def short_parts(short):
    # Routes use "A1-4106 A", "PT2-4102-A", etc.  Numeric code is always the suffix.
    m = re.fullmatch(r"(.+?-\d+)(?:[\s-]+([AB]))?", short.strip(), re.I)
    return (m.group(1), m.group(2).upper() if m.group(2) else "") if m else (short.strip(), "")

def minute(x):
    if x is None or str(x).strip() == "":
        return None
    try:
        result = float(str(x).strip().replace(",", "."))
        return result if result > 0 else None
    except ValueError:
        return None

def as_seconds(x):
    v = minute(x)
    return int(round(v * 60)) if v is not None else None

def clock(s):
    m = re.fullmatch(r"(\d{1,2}):(\d\d)(?::(\d\d))?", (s or "").strip())
    if not m:
        return None
    h,mi,se = [int(i or 0) for i in m.groups()]
    return h*3600 + mi*60+se if h <= 24 and mi < 60 and se < 60 else None

def fmt(t):
    return f"{t//3600:02d}:{t%3600//60:02d}:{t%60:02d}"

def push(table,agency,code,res,peak,off,source,scope="route",variant="",note="",status="authoritative"):
    if not code:
        return
    table.append(dict(agency=agency,code=code,normalized=n(code),
        resolution=res,peak=as_seconds(peak),offpeak=as_seconds(off),
        source=source,scope=scope,variant=variant,note=note,status=status))

def build_sources():
    data=[]
    source="sources/amb/gtfs_route_frequency_candidates_no_fleet_2026-11-02.csv"
    for r in load(BASE/"gtfs_route_frequency_candidates_no_fleet_2026-11-02.csv"):
        push(data,r["agency"],r["route_id"],r["source_resolution"],
            r["peak_minutes"],r["offpeak_minutes"],source,r["headway_scope"],note=r["evidence_note"],
            status="interval_missing" if not (r["peak_minutes"] and r["offpeak_minutes"]) else "authoritative")

    source="sources/amb/coolitoral_latest_route_parameters_2026-11-02.csv"
    for r in load(BASE/"coolitoral_latest_route_parameters_2026-11-02.csv"):
        code=r["route_id"].replace("B2-A-4177","B2A-4177")
        push(data,"COOLITORAL",code,r["authorization_resolution"],
            r["peak_headway_minutes"],r["offpeak_headway_minutes"],source,r["headway_scope"],
            note="Route-wide values; A/B-specific headways supersede aggregate values where documented.")
        if code.startswith("A1-4106"):
            # 192-2025 source extracts disagree with other summary tables;
            # retain pattern values but flag source conflict, do not authorize.
            for variant in "AB":
                push(data,"COOLITORAL",code,"192-2025",r["itinerary_A_peak_minutes"] if variant=="A" else r["itinerary_B_peak_minutes"],
                    r["itinerary_A_offpeak_minutes"] if variant=="A" else r["itinerary_B_offpeak_minutes"],
                    source,"per_itinerary",variant,
                    "Crosscheck with sources/amb/details/resolucion_192-2025.csv: A1 pattern headways differ from this table",
                    "conflicting_official_extractions")
        elif code.startswith(("PT2-4102","PT3-4103")):
            for variant in "AB":
                push(data,"COOLITORAL",code,r["authorization_resolution"],
                    r[f"itinerary_{variant}_peak_minutes"],r[f"itinerary_{variant}_offpeak_minutes"],
                    source,"per_itinerary",variant)
    # Official original 256-2026 pilot PDF has now been recovered and verified
    # (7 pages, four PT4/PT5 A/B variants); six months from 22 June 2026.
    # SIU-to-license pattern assignment and any extension remain unverified.
    source="sources/amb/details/resolucion_256-2026.csv"
    for r in load(BASE/"details/resolucion_256-2026.csv"):
        push(data,"COOLITORAL",r["codigo_base"],r["resolucion"],
            r["intervalo_pico_min"],r["intervalo_valle_min"],source,
            "per_itinerary",r["itinerario"],
            "PT4/PT5 pilot begins 2026-06-22; original official PDF verified with 9/14 min per A/B; SIU-to-A/B crosswalk and later extensions remain unknown",
            "pilot_256_primary_pdf_verified_pattern_link_pending")
    specs=[
      ("cootrab_latest_route_parameters_2026-11-02.csv","COOTRAB","route_id","latest_reviewed_resolution","peak_minutes","offpeak_minutes"),
      ("cootransnorte_latest_route_parameters_2026-11-02.csv","COOTRANSNORTE","route_id","latest_route_resolution_in_manifest","peak_headway_minutes","offpeak_headway_minutes"),
      ("cootrantico_latest_route_parameters_2026-11-02.csv","COOTRANTICO","route_id","latest_reviewed_resolution","peak_interval_minutes","offpeak_interval_minutes"),
      ("cootransporcar_latest_route_parameters_2026-11-02.csv","COOTRANSPORCAR","route_id","resolution","peak_interval_min","offpeak_interval_min"),
      ("cootrasol_route_parameters_2026-11-02.csv","COOTRASOL","route_id","resolution","peak_headway_minutes","offpeak_headway_minutes"),
      ("details/resolucion_369-2025_cooasoatlan.csv","COOASOATLAN","route_code","resolution","peak_headway_min","offpeak_headway_min"),
    ]
    for file,agency,key,res,peak,off in specs:
        for row in load(BASE/file):
            if agency=="COOTRANSPORCAR" and row[res]!="389-2025":continue
            if agency=="COOTRASOL" and row[res]!="467-2025":continue
            if agency=="COOTRAB" and row[key].startswith("A1-"):continue # shared line, not yet in routes.txt for COOTRAB
            push(data,agency,row[key],row[res],row[peak],row[off],"sources/amb/"+file)
    # 2026 priority: latest independently reviewed acts.
    push(data,"FLOTA_ANGULO","A7-4112","232-2025",3,5,
        "sources/amb/flota_angulo_route_frequency_history_2026-11-03.csv")
    push(data,"EMBUSA","B9-4125","010-2026",4,6,
        "docs/embusa_010_2026_validatie.md")
    # Per-itinerary licensed headways explicitly printed in route decisions.
    # Combined overlap headways from the 44-route research file must never
    # be copied onto both patterns.
    for agency,code,res,variant,peak,off,ref in [
        ("SOBUSA","B18-4175","082-2026","A",10,12,"082-2026 p6"),
        ("SOBUSA","B18-4175","082-2026","B",10,12,"082-2026 p6"),
        ("SOBUSA","C12-4169","466-2025","A",6,9,"466-2025 p11"),
        ("SOBUSA","C12-4169","466-2025","B",3,6,"466-2025 p11"),
        ("TRANSDIAZ","A10-4114","501-2025","A",8,10,"501-2025 p5"),
        ("TRANSDIAZ","A10-4114","501-2025","B",4,6,"501-2025 p5"),
    ]:
        push(data,agency,code,res,peak,off,
            "docs/amb_bedrijven/"+agency.lower()+"_route_frequencies_2026-11-02.md",
            "per_itinerary",variant,"Original route table "+ref)
    # LA CAROLINA A16-4161: Resolucion 199-2019 gives combined
    # route headways 3.5 min peak and 5 min offpeak. Model an even
    # alternating A/B split, not independently authorized intervals.
    for variant in ("A","B"):
        push(data,"LA_CAROLINA","A16-4161","199-2019",7,10,
             "sources/amb/gtfs_route_frequency_candidates_no_fleet_2026-11-02.csv",
             "per_itinerary",variant,
             "50/50 split of 199-2019 route-wide 3.5/5-minute headways; not a verified per-variant timetable",
             "model_assumption_50_50_split")
    # B15-4129: 458-2010 p7 existing OCR: peak 4 minutes,
    # offpeak '5 mido' (OCR typo; digit 5 legible). This is a historical
    # route-wide headway, split evenly across A/B for research GTFS.
    # Review: Actions run 41818536403, artifact 13315847754.
    for variant in ("A","B"):
        push(data,"SODETRANS","B15-4129","458-2010",8,10,
             "sources/amb/pdf_manifest.csv",
             "per_itinerary",variant,
             "50/50 modelling split of historical 458-2010 p7 route-wide 4/5 minutes; offpeak OCR reads '5 mido'; not confirmed 2026 operations",
             "model_assumption_50_50_split_historical")
    # C21-4182: 719-2018 states a route-wide 4/6-minute interval.
    # Alternate A/B departures evenly, yielding 8/12 minutes per variant.
    # This is a transparent modelling assumption, not an observed timetable.
    for variant in ("A","B"):
        push(data,"SODETRANS","C21-4182","719-2018",8,12,
             "sources/amb/gtfs_route_frequency_candidates_no_fleet_2026-11-02.csv",
             "per_itinerary",variant,
             "50/50 split of route-wide 4/6-minute licensed headway; not an independent A/B authorization",
             "model_assumption_50_50_split")
    # SOBUSA C16-4167 A/B is already recorded in the legal period register.
    # This source has an explicit per-variant scope (not a combined corridor).
    for row in load(BASE/"legal_validity_ocr_review/route_variant_legal_periods.csv"):
        if row["agency"]=="SOBUSA" and row["route"]=="C16-4167" and row["variant"] in ("A","B"):
            push(data,"SOBUSA","C16-4167",row["source_resolution"],
                 row["peak_headway_min"],row["offpeak_headway_min"],
                 "sources/amb/legal_validity_ocr_review/route_variant_legal_periods.csv",
                 "per_itinerary",row["variant"],
                 "Previously researched per-variant resolution table; operational dates modelled",
                 "legal_period_checked_staging_only")
    # COOTRANSCO 098-2026 pilot has A/B each 5/7 and common 2.5/3.5.
    # Permit says six months after 2026-03-02; on 2026-11-03 extension
    # has not been established, so do not silently use pilot or superseded
    # permanent values.
    push(data,"COOTRANSCO","C7-4138","098-2026",5,7,
        "sources/amb/cootransco_route_parameters_2026-11-02.csv",
        "per_itinerary","A",status="pilot_extension_unverified")
    push(data,"COOTRANSCO","C7-4138","098-2026",5,7,
        "sources/amb/cootransco_route_parameters_2026-11-02.csv",
        "per_itinerary","B",status="pilot_extension_unverified")
    push(data,"COOTRANSCO","C7-4138","258-2024",3,5,
        "sources/amb/cootransco_route_parameters_2026-11-02.csv",
        "route",status="permanent_backup_pending_pilot_expiry_check")
    # Reviewed route-wide tables from 462-2025 and 242-2025.
    # Canonical route aliases are applied here, without creating duplicate trips.
    alias_rows=load(BASE/"legal_validity_ocr_review/coochofal_242_route_code_aliases.csv")
    aliases={r["source_route_code"]:r["canonical_route_code"] for r in alias_rows}
    legal_source="sources/amb/legal_validity_ocr_review/verified_462_242_route_headways_2026-11-04.csv"
    for row in load(BASE/"legal_validity_ocr_review/verified_462_242_route_headways_2026-11-04.csv"):
        code=aliases.get(row["route_code"],row["route_code"])
        push(data,row["agency"],code,row["resolution"],
            row["peak_min"],row["offpeak_min"],legal_source,
            "route",note="Official route-wide headway; 242/462 presumed current authorization for provisional GTFS staging (not proof of finality or actual operation)",
            status="presumed_current_authorization")
    return data

def find(records,agency,base,variant):
    candidates=[r for r in records if r["agency"]==agency and r["normalized"]==n(base)]
    if not candidates:
        return None,"missing_headway_source"
    exact=[r for r in candidates if r["variant"]==variant] if variant else []
    if variant:
        if exact:
            return select(exact),"matched_variant"
        # A/B-specific route listed in GTFS, but an aggregate corridor value
        # does NOT define the frequency of the itinerary.
        return None,"variant_headway_not_documented"
    if any(r["variant"] for r in candidates) and not any(not r["variant"] for r in candidates):
        return None,"only_A_B_itineraries_exist_route_id_unsplit"
    return select([r for r in candidates if not r["variant"]]),"matched_base_route"

def select(records):
    # Dedicated precedence only where newer amendments are explicitly known.
    priorities={"256-2026":10,"210-2026":9,"232-2025":9,
                "010-2026":9,"462-2025":10,"242-2025":10,"098-2026":8,"258-2024":7}
    # Other inputs are latest per-company tables as pre-reviewed.
    return sorted(records,key=lambda r:(priorities.get(r["resolution"],6),
       int(bool(r["peak"] and r["offpeak"])),r["source"]),reverse=True)[0]

def match_window(windows,agency,base):
    candidates=[x for x in windows if x["agency"]==agency and n(x["route_id"])==n(base)]
    if not candidates:
        return None,"historic_window_not_found"
    rec=candidates[0]
    if rec.get("assumption_status")!="accepted_as_provisional_2026_schedule_assumption":
        return None,"historic_last_dispatch_invalid"
    start,end=clock(rec["first_dispatch_model_local"]),clock(rec["last_dispatch_model_local"])
    if start is None or end is None or end<=start:
        return None,"historic_window_invalid"
    return rec,"historic_2020_window_accepted_as_model"

def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    routes=load(ROOT/"gtfs/routes.txt")
    agencies={a["agency_id"] for a in load(ROOT/"gtfs/agency.txt")}
    windows=load(BASE/"amb_dispatch_window_assumptions_2026-11-03.csv")
    sources=build_sources()
    legal_rows=load(BASE/"legal_validity_ocr_review/route_variant_legal_periods.csv")
    for lr in legal_rows:
        if lr["variant"] not in ("A","B") or ";" in lr["agency"]:
            continue  # joint-operation sources need a composite agency, never separate trips
        if lr["legal_status"]=="article_verified_ocr_table_review":
            continue  # keep PT3 pending until visual table review
        if lr["legal_status"] not in ("pilot_article_verified","article_verified_effective_date_unverified"):
            continue
        push(sources,lr["agency"],lr["route"],lr["source_resolution"],
             lr["peak_headway_min"],lr["offpeak_headway_min"],
             "sources/amb/legal_validity_ocr_review/route_variant_legal_periods.csv",
             "per_itinerary",lr["variant"],
             "Legal article source; period must be checked before publication",
             "legal_period_checked_staging_only")
    candidates=[];periods=[];issues=[]
    seen=set()
    for rt in routes:
        gid=rt["route_id"];agency=rt["agency_id"].removeprefix("AMB_")
        base,variant=short_parts(rt["route_short_name"])
        if gid in seen:
            raise ValueError("Duplicate route_id: "+gid)
        seen.add(gid)
        if rt["agency_id"] not in agencies:
            raise ValueError("Missing agency for route "+gid)
        source,match=find(sources,agency,base,variant)
        window,wstatus=match_window(windows,agency,base)
        blockers=[]
        if not source:blockers.append(match)
        else:
            if source["peak"] is None or source["offpeak"] is None:blockers.append("official_interval_missing")
            if source["scope"] in ("shared_corridor_effective_not_per_itinerary","effective_combined_section"):
                blockers.append("effective_combined_corridor_not_pattern")
            if source["status"] in ("conflicting_official_extractions","pilot_extension_unverified","permanent_backup_pending_pilot_expiry_check"):
                blockers.append(source["status"])
            if source["status"]=="pilot_256_primary_pdf_verified_pattern_link_pending":
                blockers.append("pilot_SIU_to_legal_AB_mapping_unresolved")
        if source and source["scope"] in ("shared_corridor_effective_not_per_itinerary","effective_combined_section"):
            blockers.append("combined_corridor_not_per_itinerary")
        if source and source["variant"] and source["variant"]!=variant:
            blockers.append("itinerary_mismatch")
        if source and source["status"]=="legal_table_reviewed_scope_pending":
            blockers.append("route_variant_scope_and_legal_effect_unverified")
        if source and source["status"]=="legal_period_checked_staging_only":
            # Latest reviewed AMB acts presumed current for provisional staging.
            # Pilot 256-2026 runs 2026-06-22 to 2026-12-22, not indefinitely.
            if source["resolution"]=="256-2026":
                blockers.append("pilot_SIU_to_legal_AB_mapping_unresolved")
        if not window:blockers.append(wstatus)
        if agency=="COOTRAB" and n(base)==n("C5-4135"):
            blockers.append("route_code_4135_vs_official_4136")
        if agency=="COOTRANSCO" and n(base)==n("C7-4138"):
            blockers.append("pilot_A_B_not_in_routes_txt")
        row={
            "gtfs_route_id":gid, "agency_id":rt["agency_id"],"route_short_name":rt["route_short_name"],
            "base_route_code":base,"itinerary":variant,"official_resolution":source["resolution"] if source else "",
            "peak_headway_secs":source["peak"] if source else "",
            "offpeak_headway_secs":source["offpeak"] if source else "",
            "source_type":source["status"] if source else "none",
            "source_scope":source["scope"] if source else "",
            "source_file":source["source"] if source else "",
            "first_dispatch_model":window["first_dispatch_model_local"] if window else "",
            "last_dispatch_model":window["last_dispatch_model_local"] if window else "",
            "dispatch_window_source_year":"2020" if window else "",
            "weekday_period_model_id":MODEL,"model_timezone":"America/Bogota",
            "source_window_model_id":WINDOW_MODEL if window else "",
            "period_staging_status":"ready_to_stage" if not blockers else "held_for_review",
            "blockers":";".join(dict.fromkeys(blockers)),
            "publication_status":"NOT_A_COMPLETE_GTFS",
        }
        candidates.append(row)
        if blockers:
            issues.append({"gtfs_route_id":gid,"agency":agency,"base_route_code":base,
                "resolution":row["official_resolution"],"blockers":row["blockers"],
                "next_step":"Check cited license and itinerary / add missing route source. Do not fabricate stop_times or shapes."})
            continue
        start,end=clock(window["first_dispatch_model_local"]),clock(window["last_dispatch_model_local"])
        for name,lower,upper,kind in PERIODS:
            begin=max(start,lower*60);finish=min(end,upper*60)
            if finish<=begin:continue
            periods.append({"gtfs_route_id":gid,"agency":agency,"route_code":rt["route_short_name"],
                "service_id_model":"AMB_MON_FRI_MODEL","period":name,
                "frequency_kind":kind,"period_start_boundary_local":fmt(begin),
                "period_end_boundary_local":fmt(finish),
                "headway_secs":source["peak"] if kind=="peak" else source["offpeak"],
                "exact_times":0,"source_resolution":source["resolution"],
                "headway_source":source["source"],
                "window_source":"AMB_2020_ROUTE_POSTERS_2020_07_MODEL",
                "first_departure_inclusive":fmt(start),
                "last_departure_inclusive":fmt(end),
                "not_gtfs_frequencies_txt":"yes_requires_trip_id_and_stop_times_last_dispatch_handling"
            })
    # A single route/variant may have one service owner only. Shared agencies
    # must be consolidated upstream, not emitted as separate identical trips.
    owner={}
    for row in candidates:
        key=(n(row["base_route_code"]),row["itinerary"])
        if row["period_staging_status"]!="ready_to_stage":
            continue
        previous=owner.get(key)
        if previous and previous!=row["agency_id"]:
            raise ValueError("Duplicate route variant across agencies; consolidate shared operation: "+str(key))
        owner[key]=row["agency_id"]
    write(output/"route_headway_candidates.csv",candidates)
    write(output/"weekday_period_staging.csv",periods)
    write(output/"unresolved_route_issues.csv",issues)
    summary={"routes_in_routes_txt":len(routes),
      "routes_ready_to_stage":sum(r["period_staging_status"]=="ready_to_stage" for r in candidates),
      "routes_held_for_review":len(issues),"staged_weekday_periods":len(periods),
      "source_records_considered":len(sources),"blocker_counts":dict(Counter(k for x in issues for k in x["blockers"].split(";"))) }
    (output/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (output/"summary.md").write_text(
       "# AMB GTFS headway staging — preliminary, NOT a GTFS ZIP\n\n"+
       "\n".join(f"- {k}: **{v}**" for k,v in summary.items() if k!="blocker_counts")+
       "\n\n## Reasons routes were held\n\n"+
       "\n".join(f"- {k}: {v}" for k,v in sorted(summary["blocker_counts"].items()))+
       "\n\nNo stops.txt, trips.txt, stop_times.txt or route geometry was invented.\n"+
       "The 2020 first/last departures are a reversible model assumption and\n"+
       "the official applicable AMB resolutions determine the headways.\n"+
       "frequencies.txt.end_time is exclusive while last despacho on the posters is inclusive;\n"+
       "the staging boundaries must be translated carefully after stop_times templates exist.\n",
       encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if len(candidates)<1:raise SystemExit("No candidate routes")
    return summary

def write(path, rows):
    if not rows:
        path.write_text("route_id\n",encoding="utf-8");return
    with path.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="build/gtfs-frequency-staging")
    args=ap.parse_args()
    run(args.out)
