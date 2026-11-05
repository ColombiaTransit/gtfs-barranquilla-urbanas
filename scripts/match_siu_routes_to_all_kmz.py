#!/usr/bin/env python3
"""Rank every SIU itinerary against every available AMB KMZ geometry (research only)."""
import argparse,csv,json,math
from pathlib import Path
from collections import defaultdict
from pyproj import Transformer
from shapely.geometry import Point
from audit_siu_kmz_loop_aware import read,lines,occurrences
from review_four_siu_kmz_routes import solve

def write(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,default=Path("."))
    ap.add_argument("--out",type=Path,default=Path("build/siu_kmz_all_matches"))
    ap.add_argument("--top",type=int,default=5)
    args=ap.parse_args()
    root=args.repo.resolve();out=root/args.out
    source=root/"sources/siu/public_extract/siu_route_stop_sequences.csv"
    manifest=root/"sources/amb/kmz/manifest.csv"
    stops=read(source);kmzs=read(manifest)
    if not stops:raise SystemExit(f"No SIU stop sequences in {source}; run SIU source extraction first")
    required={"siu_itinerary_uuid","siu_stop_sequence","stop_lat","stop_lon"}
    if not required.issubset(stops[0]):raise SystemExit("Missing SIU columns: "+str(required-set(stops[0])))
    groups=defaultdict(list)
    for s in stops:
        if str(s.get("likely_test_itinerary","")).lower()=="true":continue
        try:
            float(s["stop_lat"]);float(s["stop_lon"]);int(s["siu_stop_sequence"])
        except (ValueError,KeyError):continue
        groups[s["siu_itinerary_uuid"]].append(s)
    for group in groups.values():group.sort(key=lambda s:int(s["siu_stop_sequence"]))
    proj=Transformer.from_crs(4326,32618,always_xy=True)
    shapes=[]
    for m in kmzs:
        p=root/"sources/amb/kmz"/m.get("geojson_path","")
        if not p.is_file():continue
        try:parts=lines(p,proj)
        except (ValueError,KeyError,TypeError) as e:
            print("Skipping malformed geometry",p,e);continue
        if parts:shapes.append((m,parts))
    if not shapes:raise SystemExit("No KMZ GeoJSON geometries found")
    ranking=[];exceptions=[]
    for uid,group in groups.items():
        pts=[Point(*proj.transform(float(s["stop_lon"]),float(s["stop_lat"]))) for s in group]
        for m,parts in shapes:
            # Geographical coverage across the union of all parts; no artificial stitching.
            dists=[min(p.distance(line) for line in parts) for p in pts]
            covered=sum(d<=50 for d in dists)
            if covered==0:continue
            # Sequence alignment per individual part, forward and reverse.
            # A closed loop can start anywhere: rotate positions at every wrap and
            # score nondecreasing progress; repeated occurrences remain candidates.
            best=None
            for section,line in enumerate(parts,1):
                for reverse in (False,True):
                    res=solve(pts,line,reverse,True)
                    candidate=(res["covered"],-res["backward_gt20m"]-res["implausible_forward_gt_max500m_or_5x"],res["pairs"],section,reverse,res)
                    if best is None or candidate[:3]>best[:3]:best=candidate
            _,_,_,section,reverse,seq=best
            total=len(group);pct=100*covered/total
            seqcov=100*seq["covered"]/total
            errors=seq["backward_gt20m"]+seq["implausible_forward_gt_max500m_or_5x"]
            status=("strong" if pct>=98 and seqcov>=98 and errors==0 else
                    "probable" if pct>=90 and seqcov>=90 and errors==0 else
                    "partial" if pct>=70 else "weak")
            ranking.append(dict(siu_itinerary_uuid=uid,siu_name=group[0].get("siu_name",""),
                siu_stop_count=total,kmz_company=m.get("company",""),kmz_route_label=m.get("route_label",""),
                kmz_geojson_path=m["geojson_path"],covered_50m=covered,coverage_50_pct=round(pct,2),
                sequence_coverage_pct=round(seqcov,2),backward_gt20m=seq["backward_gt20m"],
                implausible_forward=seq["implausible_forward_gt_max500m_or_5x"],
                chosen_section=section,orientation="reverse" if reverse else "forward",
                is_ring=seq["is_ring"],ring_wrap_count=seq["ring_wrap_count"],
                sequence_violations=seq["sequence_violations"],
                median_distance_m=round(sorted(dists)[total//2],1),max_distance_m=round(max(dists),1),
                match_class=status,legal_mapping_confirmed="no",gtfs_approved="no"))
            for s,d in zip(group,dists):
                if d>50:
                    exceptions.append(dict(siu_itinerary_uuid=uid,siu_name=group[0].get("siu_name",""),
                        kmz_company=m.get("company",""),kmz_route_label=m.get("route_label",""),
                        stop_sequence=s["siu_stop_sequence"],stop_name=s.get("stop_name",""),
                        stop_lat=s["stop_lat"],stop_lon=s["stop_lon"],distance_to_kmz_m=round(d,1)))
    ranking.sort(key=lambda r:(r["siu_itinerary_uuid"],-r["coverage_50_pct"],-r["sequence_coverage_pct"],
                               r["backward_gt20m"]+r["implausible_forward"],r["median_distance_m"]))
    for row in ranking:row["rank"]=1+sum(1 for other in ranking if other["siu_itinerary_uuid"]==row["siu_itinerary_uuid"] and (
        other["coverage_50_pct"],other["sequence_coverage_pct"],-other["backward_gt20m"]-other["implausible_forward"],-other["median_distance_m"])>(
        row["coverage_50_pct"],row["sequence_coverage_pct"],-row["backward_gt20m"]-row["implausible_forward"],-row["median_distance_m"]))
    top=[r for r in ranking if r["rank"]<=args.top]
    keys=list(top[0]) if top else ["siu_itinerary_uuid","rank"]
    write(out/"ranked_candidates.csv",top,keys)
    selected={(r["siu_itinerary_uuid"],r["kmz_company"],r["kmz_route_label"]) for r in top}
    filtered=[e for e in exceptions if (e["siu_itinerary_uuid"],e["kmz_company"],e["kmz_route_label"]) in selected]
    write(out/"stop_exceptions.csv",filtered,list(filtered[0]) if filtered else
          ["siu_itinerary_uuid","siu_name","kmz_company","kmz_route_label","stop_sequence","stop_name","stop_lat","stop_lon","distance_to_kmz_m"])
    byid=defaultdict(list)
    for r in top:byid[r["siu_itinerary_uuid"]].append(r)
    overview=[]
    for uid,g in groups.items():
        candidates=byid[uid]
        first=next((r for r in candidates if r["rank"]==1),None)
        tied=bool(first and sum(r["coverage_50_pct"]>=first["coverage_50_pct"]-2 and
             r["sequence_coverage_pct"]>=first["sequence_coverage_pct"]-2 for r in candidates)>1)
        overview.append(dict(siu_itinerary_uuid=uid,siu_name=g[0].get("siu_name",""),
            siu_stop_count=len(g),best_kmz=first["kmz_route_label"] if first else "",
            best_coverage_50_pct=first["coverage_50_pct"] if first else 0,
            best_sequence_coverage_pct=first["sequence_coverage_pct"] if first else 0,
            status="ambiguous" if tied else first["match_class"] if first else "unmatched"))
    write(out/"route_overview.csv",overview,list(overview[0]) if overview else ["siu_itinerary_uuid"])
    print(json.dumps({"siu_itineraries":len(groups),"kmz_files":len(shapes),
        "ranked_candidates":len(top),"exceptions":len(filtered),"output":str(out)},indent=2))
if __name__=="__main__":main()
