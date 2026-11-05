#!/usr/bin/env python3
"""Loop-aware SIU stop sequence vs KMZ: research diagnostic, never legal approval.

For each stop, find *all* plausible occurrences along each directed KMZ section,
rather than projecting to the single nearest point. Dynamic programming selects
a sequence balancing proximity, backward travel, and implausible jumps.
Independent KMZ sections are NOT automatically concatenated.
"""
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import Point,LineString
from shapely.strtree import STRtree

def read(path):
    with path.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))

def lines(path,project):
    data=json.loads(path.read_text(encoding="utf-8"))
    out=[]
    for f in data.get("features",[]):
        g=f.get("geometry") or {}
        parts=([g["coordinates"]] if g.get("type")=="LineString" else
               g["coordinates"] if g.get("type")=="MultiLineString" else [])
        for part in parts:
            if len(part)>1:
                line=LineString([project.transform(float(p[0]),float(p[1])) for p in part])
                if line.length>0:out.append(line)
    return out

def occurrences(points,line,buffer_m=50,max_options=12):
    coords=list(line.coords)
    edges=[];starts=[];distance=0
    for a,b in zip(coords,coords[1:]):
        edge=LineString([a,b])
        if edge.length>0:
            edges.append(edge);starts.append(distance)
        distance+=edge.length
    if not edges:return []
    tree=STRtree(edges)
    result=[]
    for point in points:
        found=[]
        for idx in tree.query(point.buffer(buffer_m)):
            edge=edges[int(idx)]
            d=point.distance(edge)
            if d<=buffer_m:
                pos=starts[int(idx)]+edge.project(point)
                found.append((round(pos,2),round(d,2)))
        found.sort(key=lambda v:v[1])
        unique=[]
        for pos,d in found:
            if all(abs(pos-p)>10 for p,_ in unique):
                unique.append((pos,d))
            if len(unique)>=max_options:break
        result.append(unique)
    return result

def align(choices,length,reverse=False):
    # Missing stops are explicitly excluded from pair statistics; do not
    # silently bridge across them. Penalize backward movement and jumps.
    previous=None;prev_index=None;backtrack=[];chosen=[None]*len(choices)
    # Each contiguous block of stops with available occurrences is independent.
    blocks=[];block=[]
    for i,options in enumerate(choices):
        if options:block.append(i)
        elif block:blocks.append(block);block=[]
    if block:blocks.append(block)
    total_pairs=0;backward=0;ambiguous=sum(len(x)>1 for x in choices)
    for block in blocks:
        states=[];parents=[]
        for k,i in enumerate(block):
            options=choices[i]
            positions=[length-p if reverse else p for p,_ in options]
            if k==0:
                states=[d for _,d in options];parents.append([-1]*len(options))
                continue
            old=choices[block[k-1]]
            oldpos=[length-p if reverse else p for p,_ in old]
            new=[];prev=[]
            for j,((pos,d),x) in enumerate(zip(options,positions)):
                costs=[]
                for q,y in enumerate(oldpos):
                    delta=x-y
                    penalty=max(0,-delta-20)*2.5
                    # Excessive leaps are suspicious but can reflect missing stops.
                    penalty+=max(0,delta-1500)*0.1
                    costs.append(states[q]+d+penalty)
                best=min(range(len(costs)),key=costs.__getitem__)
                new.append(costs[best]);prev.append(best)
            states=new;parents.append(prev)
        j=min(range(len(states)),key=states.__getitem__)
        for k in range(len(block)-1,-1,-1):
            i=block[k];chosen[i]=choices[i][j][0]
            j=parents[k][j]
        for a,b in zip(block,block[1:]):
            x=length-chosen[a] if reverse else chosen[a]
            y=length-chosen[b] if reverse else chosen[b]
            total_pairs+=1
            backward+=int(y+20<x)
    covered=sum(bool(c) for c in choices)
    return {"covered":covered,"pairs":total_pairs,"backward":backward,
            "ambiguous_stops":ambiguous,
            "backward_pct":round(100*backward/total_pairs,1) if total_pairs else None,
            "coverage_pct":round(100*covered/len(choices),1) if choices else 0,
            "orientation":"reverse" if reverse else "forward"}

def evaluate(points,sections):
    options=[]
    for section_id,line in enumerate(sections,1):
        choices=occurrences(points,line)
        for rev in (False,True):
            result=align(choices,line.length,rev)
            result["section_id"]=section_id
            result["section_length_m"]=round(line.length,1)
            options.append(result)
    if not options:return {}
    # Coverage first, then fewest backward jumps; never merge disconnected sections.
    best=max(options,key=lambda x:(x["covered"],-x["backward_pct"] if x["backward_pct"] is not None else -100,
                                   x["pairs"]))
    best["kmz_sections"]=len(sections)
    best["whole_route_sequence_verified"]="no"
    return best

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",type=Path,default=Path("."))
    parser.add_argument("--out",type=Path,default=Path("build/siu-kmz-loop-aware-audit.csv"))
    args=parser.parse_args()
    root=args.repo.resolve()
    base=root/"sources/amb/kmz"
    manifest=read(base/"manifest.csv")
    scores=read(root/"sources/amb/kmz_stop_research/siu_crosswalk/all_siu_kmz_spatial_scores_NOT_CONFIRMED.csv")
    stops=read(root/"sources/siu/public_extract/siu_route_stop_sequences.csv")
    by_it=defaultdict(list)
    for row in stops:
        if row.get("likely_test_itinerary")!="true":by_it[row["siu_itinerary_uuid"]].append(row)
    for group in by_it.values():group.sort(key=lambda x:int(x["siu_stop_sequence"]))
    def norm(s):return "".join(c for c in str(s).upper() if c.isalnum()).replace("TRANSPORTESMONTERREY","MONTERREY")
    lookup={(norm(m["company"]),m["route_label"]):m for m in manifest}
    proj=Transformer.from_crs(4326,32618,always_xy=True)
    point_cache={};shape_cache={};results=[]
    for row in scores:
        uid=row["siu_itinerary_uuid"]
        if uid not in point_cache:
            point_cache[uid]=[Point(*proj.transform(float(s["stop_lon"]),float(s["stop_lat"]))) for s in by_it[uid]]
        m=lookup.get((norm(row["kmz_company"]),row["kmz_route_label"]))
        detail={};status="missing_manifest"
        if m:
            path=base/m["geojson_path"] if m.get("geojson_path") else None
            if not path or not path.is_file():status="missing_geometry"
            else:
                if path not in shape_cache:shape_cache[path]=lines(path,proj)
                detail=evaluate(point_cache[uid],shape_cache[path])
                status="loop_aware_section_diagnostic" if detail else "empty_geometry"
        results.append({
            "siu_itinerary_uuid":uid,"siu_name":row["siu_name"],
            "kmz_company":row["kmz_company"],"kmz_route_label":row["kmz_route_label"],
            "candidate_spatial_rank":row["candidate_spatial_rank"],
            "prior_50m_coverage_pct":row["share_of_SIU_stops_within_50m_pct"],
            "source_url_collision":row["official_source_KMZ_URL_collision"],
            "status":status,**detail,
            "legal_mapping_confirmed":"no","gtfs_stop_times_approved":"no"})
    args.out.parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for row in results for k in row))
    with args.out.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(results)
    statuses={s:sum(r["status"]==s for r in results) for s in sorted(set(r["status"] for r in results))}
    print(json.dumps({"comparisons":len(results),"itineraries":len(point_cache),"statuses":statuses},indent=2))
    if any(s!="loop_aware_section_diagnostic" for s in statuses):
        raise SystemExit("Incomplete diagnostic: missing or invalid source geometry")
if __name__=="__main__":main()
