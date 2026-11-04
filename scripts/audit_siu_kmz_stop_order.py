#!/usr/bin/env python3
"""Read-only diagnostic: SIU stop order vs official AMB KMZ line sections.
Does NOT establish legal route/variant identity or GTFS stop_times.
"""
import argparse,csv,json,re,unicodedata
from pathlib import Path
from collections import defaultdict
from shapely.geometry import LineString,Point
from pyproj import Transformer

def read(path):
    with open(path,encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def norm(v):
    s=unicodedata.normalize("NFKD",str(v or "").upper())
    return re.sub("[^A-Z0-9]","", "".join(c for c in s if not unicodedata.combining(c)))
def company(v):
    n=norm(v)
    return "MONTERREY" if n=="TRANSPORTESMONTERREY" else n
def geometry(path,proj):
    features=json.loads(path.read_text(encoding="utf-8"))["features"]
    lines=[]
    for f in features:
        g=f.get("geometry") or {}
        t=g.get("type")
        parts=[g["coordinates"]] if t=="LineString" else g["coordinates"] if t=="MultiLineString" else []
        for part in parts:
            if len(part)>1:
                line=LineString([proj.transform(float(p[0]),float(p[1])) for p in part])
                if line.length:lines.append(line)
    return lines
def audit(points,segments):
    # Independent line sections can be out of order or disconnected. Therefore
    # this is a per-section monotonicity diagnostic, NOT a whole-route verdict.
    candidates=[]
    for line in segments:
        along=[line.project(p) for p in points]
        distances=[line.distance(p) for p in points]
        for direction,positions in (("forward",along),("reverse",[line.length-x for x in along])):
            pairs=[(a,b) for a,b,da,db in zip(positions,positions[1:],distances,distances[1:]) if da<=50 and db<=50]
            backward=sum(b+20<a for a,b in pairs)
            covered=sum(d<=50 for d in distances)
            candidates.append((covered,-(backward/len(pairs) if pairs else 1),len(pairs),
                {"segment_orientation":direction,"segment_length_m":round(line.length,1),
                 "stops_near_segment_pct":round(100*covered/len(points),1),
                 "comparable_consecutive_pairs":len(pairs),"backward_jumps_gt20m":backward,
                 "backward_jump_ratio_pct":round(100*backward/len(pairs),1) if pairs else ""}))
    return max(candidates,key=lambda x:x[:3])[3] if candidates else {}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,default=Path("."))
    p.add_argument("--out",type=Path,default=Path("build/siu-kmz-ordered-audit.csv"))
    args=p.parse_args();root=args.repo.resolve()
    manifest=read(root/"sources/amb/kmz/manifest.csv")
    stops=read(root/"sources/siu/public_extract/siu_route_stop_sequences.csv")
    scores=read(root/"sources/amb/kmz_stop_research/siu_crosswalk/all_siu_kmz_spatial_scores_NOT_CONFIRMED.csv")
    by_it=defaultdict(list)
    for row in stops:
        if row.get("likely_test_itinerary")!="true":by_it[row["siu_itinerary_uuid"]].append(row)
    for v in by_it.values():v.sort(key=lambda r:int(r["siu_stop_sequence"]))
    by_manifest={(company(m["company"]),m["route_label"]):m for m in manifest}
    proj=Transformer.from_crs(4326,32618,always_xy=True)
    output=[];cache={}
    for score in scores:
        uid=score["siu_itinerary_uuid"]
        m=by_manifest.get((company(score["kmz_company"]),score["kmz_route_label"]))
        status="missing_manifest";detail={}
        if m:
            path=root/"sources/amb/kmz"/m["geojson_path"] if m.get("geojson_path") else None
            if not path or not path.is_file():status="geometry_not_local"
            elif not by_it.get(uid):status="missing_siu_stops"
            else:
                if path not in cache:cache[path]=geometry(path,proj)
                pts=[Point(*proj.transform(float(s["stop_lon"]),float(s["stop_lat"]))) for s in by_it[uid]]
                detail=audit(pts,cache[path])
                status="segment_diagnostic_only" if detail else "no_lines"
        output.append({
            "siu_itinerary_uuid":uid,"siu_name":score["siu_name"],
            "siu_companies":score["siu_companies"],"kmz_company":score["kmz_company"],
            "kmz_route_label":score["kmz_route_label"],
            "candidate_spatial_rank":score["candidate_spatial_rank"],
            "overall_50m_coverage_pct":score["share_of_SIU_stops_within_50m_pct"],
            "official_source_KMZ_URL_collision":score["official_source_KMZ_URL_collision"],
            "status":status,**detail,"full_route_order_confirmed":"no",
            "legal_mapping_confirmed":"no","allowed_for_GTFS_stop_times":"no"})
    if not output:raise SystemExit("No candidates")
    args.out.parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for row in output for k in row))
    with args.out.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(output)
    statuses={s:sum(row["status"]==s for row in output) for s in sorted({row["status"] for row in output})}
    print(json.dumps({"comparisons":len(output),"itineraries":len({x["siu_itinerary_uuid"] for x in output}),"statuses":statuses,"output":str(args.out)},indent=2))
    if statuses.get("geometry_not_local") or statuses.get("missing_manifest"):
        raise SystemExit("Audit incomplete: missing geometry or manifest entries; do not treat as complete")
if __name__=="__main__":main()
