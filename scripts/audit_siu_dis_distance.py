#!/usr/bin/env python3
"""Audit SIU 'dis' against stop sequence and capture exact public JS context."""
import csv,collections,json,re,urllib.request,pathlib,statistics
root=pathlib.Path(__file__).resolve().parents[1]
out=root/"sources/siu/dis_distance_audit";out.mkdir(parents=True,exist_ok=True)
src=root/"sources/siu/public_extract/siu_route_stop_sequences.csv"
rows=list(csv.DictReader(src.open(encoding="utf-8-sig",newline="")))
groups=collections.defaultdict(list)
for x in rows:
 if x.get("likely_test_itinerary")!="true":groups[x["siu_itinerary_uuid"]].append(x)
details=[];examples=[]
for uid,group in sorted(groups.items()):
 group.sort(key=lambda x:int(x["siu_stop_sequence"]))
 values=[]
 for x in group:
  raw=x.get("source_dis_uninterpreted","")
  try: v=float(raw) if raw.strip() else None
  except ValueError:v=None
  values.append(v)
 valid=[(i,v) for i,v in enumerate(values) if v is not None]
 diffs=[b-a for (_,a),(_,b) in zip(valid,valid[1:])]
 details.append(dict(itinerary_uuid=uid,name=group[0]["siu_display_name"],stops=len(group),dis_present=len(valid),first_dis=valid[0][1] if valid else "",last_dis=valid[-1][1] if valid else "",min_dis=min((v for _,v in valid),default=""),max_dis=max((v for _,v in valid),default=""),increases=sum(d>0 for d in diffs),decreases=sum(d<0 for d in diffs),unchanged=sum(d==0 for d in diffs),median_delta=statistics.median(diffs) if diffs else ""))
 for i,x in enumerate(group[:12]):
  examples.append(dict(itinerary=group[0]["siu_display_name"],sequence=x["siu_stop_sequence"],name=x["stop_name"],dis=x.get("source_dis_uninterpreted","")))
with (out/"route_dis_summary.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=details[0]);w.writeheader();w.writerows(details)
with (out/"first_twelve_stops_per_route.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=examples[0]);w.writeheader();w.writerows(examples)
url="https://siu.ambq.gov.co/siu/static/js/37.4ac577f1.chunk.js"
result={"js_url":url,"module_1455_found":False,"expressions":[],"error":None}
try:
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
 with urllib.request.urlopen(req,timeout=35) as resp: js=resp.read(12000000).decode("utf-8","replace")
 # Match minified module 1455 and extract its body until next numbered module.
 m=re.search(r'(?:^|[,\\{])1455\\s*:\\s*function\\s*\\(',js)
 if m:
  result["module_1455_found"]=True
  segment=js[m.start():m.start()+150000]
 else: segment=js
 for match in list(re.finditer(r'\\.dis\\b|\\[["\\\']dis["\\\']\\]|\\.td\\b',segment))[:100]:
  s=max(0,match.start()-170);e=min(len(segment),match.end()+170)
  excerpt=segment[s:e]
  result["expressions"].append(excerpt)
except Exception as exc:result["error"]=type(exc).__name__+": "+str(exc)[:180]
(out/"javascript_distance_context.json").write_text(json.dumps(result,indent=2,ensure_ascii=False))
report={"itineraries":len(details),"stop_occurrences":len(rows),"non_test_stop_occurrences":sum(len(x) for x in groups.values()),"dis_present":sum(int(x["dis_present"]) for x in details),"routes_with_increasing_dis":sum(x["increases"]>0 for x in details),"routes_with_decreasing_dis":sum(x["decreases"]>0 for x in details),"js_context_count":len(result["expressions"]),"js_error":result["error"]}
(out/"summary.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
