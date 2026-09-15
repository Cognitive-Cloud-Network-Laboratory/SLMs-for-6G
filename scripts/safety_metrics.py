#!/usr/bin/env python3
"""C) Safety & abstention analysis, computed from the per-intent result files.
abstain  = output not a parseable action (format invalid)
unsafe   = valid JSON but WRONG action (confident mis-actuation)
safe     = valid JSON with correct action
Run from repo root:  python3 scripts/safety_metrics.py
"""
import json, glob, os
def analyze(fn):
    its=json.load(open(fn))["results"]; n=len(its)
    absr =sum(1 for i in its if not i.get("format_valid"))
    unsafe=sum(1 for i in its if i.get("format_valid") and not i.get("action_correct"))
    safe  =sum(1 for i in its if i.get("format_valid") and i.get("action_correct"))
    conf=[i for i in its if i["domain"]=="Conflict Resolution"]
    cu=sum(1 for i in conf if i.get("format_valid") and not i.get("action_correct"))
    return dict(n=n, abstain_pct=round(100*absr/n,1), unsafe_pct=round(100*unsafe/n,1),
                safe_pct=round(100*safe/n,1), conflict_unsafe_pct=round(100*cu/len(conf),1))
if __name__=="__main__":
    for fn in sorted(glob.glob("results/temp0/benchmark_*_temp0.json")):
        name=os.path.basename(fn).replace("benchmark_","").replace("_temp0.json","")
        print(f"{name:30}", analyze(fn))
