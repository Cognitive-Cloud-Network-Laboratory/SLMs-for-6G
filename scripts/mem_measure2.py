#!/usr/bin/env python3
# D) peak-memory re-measurement, ISOLATED per model (fixed num_ctx).
# Ensures exactly ONE llama-server process is loaded before sampling, so
# VmRSS/Pss belong to a single process (PSS <= RSS by construction).
import urllib.request, json, time, threading, subprocess, sys
MODELS = sys.argv[1].split(",")
NUM_CTX = 2048
PROMPT = "Create a new URLLC slice for autonomous vehicles in Bangkok with 1 Gbps and 1 ms latency."

def gen(m):
    body=json.dumps({"model":m,"prompt":PROMPT,"stream":False,
        "options":{"temperature":0,"num_ctx":NUM_CTX,"num_predict":256}}).encode()
    urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/generate",
        data=body,headers={"Content-Type":"application/json"}),timeout=180).read()

def llama_pids():
    try: return subprocess.check_output(["pgrep","-f","llama-server"]).decode().split()
    except Exception: return []

def stop_all():
    try:
        for line in subprocess.check_output(["ollama","ps"]).decode().splitlines()[1:]:
            if line.strip(): subprocess.run(["ollama","stop",line.split()[0]],timeout=30)
    except Exception: pass
    for _ in range(90):
        if not llama_pids(): return True
        time.sleep(1)
    return False

def mem_of(pid):
    rss=pss=0
    try:
        for l in open(f"/proc/{pid}/status"):
            if l.startswith("VmRSS"): rss=int(l.split()[1])
    except Exception: pass
    try:
        for l in open(f"/proc/{pid}/smaps_rollup"):
            if l.startswith("Pss:"): pss=int(l.split()[1])
    except Exception: pass
    return rss//1024, pss//1024

res={}
for m in MODELS:
    stop_all()
    gen(m)                       # load target
    pids=llama_pids()
    pid=pids[0] if pids else None
    if len(pids)!=1: print(m,"WARN pids=",pids,flush=True)
    peak=[0,0]; stop=[False]
    def sample():
        while not stop[0] and pid:
            r,p=mem_of(pid); peak[0]=max(peak[0],r); peak[1]=max(peak[1],p); time.sleep(0.25)
    t=threading.Thread(target=sample); t.start()
    try:
        for _ in range(12): gen(m)
    except Exception as e: print(m,"ERR",e,flush=True)
    stop[0]=True; t.join()
    res[m]={"rss":peak[0],"pss":peak[1]}
    print(f"{m:26} num_ctx={NUM_CTX} peak_RSS={peak[0]}MB peak_PSS={peak[1]}MB",flush=True)
open("results/mem_result.json","w").write(json.dumps(res))
print("DONE",json.dumps(res),flush=True)
