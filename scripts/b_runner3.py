# B (pinned): isolate BANDWIDTH from CPU contention.
# Inference pinned to cores 0-7 (num_thread=8); memory hog pinned to cores 8-15.
# Inference NEVER loses its cores, so any tok/s drop = shared memory-bus contention.
import urllib.request,json,subprocess,time,statistics
MODELS=["qwen2.5-7b-q8_0:latest","qwen2.5:0.5b"]   # bandwidth-heavy vs light
LEVELS=[0,2,4,8]
PROMPT="Create a URLLC slice for autonomous vehicles in Bangkok with 1 Gbps and sub-1 ms latency, high priority."
def gen(m,npredict=64):
    body=json.dumps({"model":m,"prompt":PROMPT,"stream":False,
        "options":{"temperature":0,"num_ctx":2048,"num_predict":npredict,"num_thread":8}}).encode()
    try:
        r=json.loads(urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/generate",
            data=body,headers={"Content-Type":"application/json"}),timeout=400).read())
        ed=r.get("eval_duration",1) or 1
        return r.get("eval_count",0)/(ed/1e9)
    except Exception: return None
def stop_all():
    try:
        for l in subprocess.check_output(["ollama","ps"]).decode().splitlines()[1:]:
            if l.strip(): subprocess.run(["ollama","stop",l.split()[0]],timeout=30)
    except Exception: pass
    time.sleep(2)
res={}
for m in MODELS:
    stop_all()
    gen(m)                                   # load
    try: pid=subprocess.check_output(["pgrep","-f","llama-server"]).decode().split()[0]
    except Exception: pid=None
    if pid: subprocess.run(["taskset","-a","-cp","0-7",pid])   # pin inference to cores 0-7
    gen(m)                                   # warm after pin
    res[m]={}
    for L in LEVELS:
        subprocess.run(["pkill","-9","-f","hog.py"])
        hog=subprocess.Popen(["taskset","-c","8-15","python3","scripts/hog.py",str(L)]) if L>0 else None
        if hog: time.sleep(3)
        vals=[gen(m) for _ in range(2)]
        subprocess.run(["pkill","-9","-f","hog.py"])
        good=[v for v in vals if v]
        res[m][L]=round(statistics.mean(good),2) if good else 0.0
        print(f"{m:26} hog_threads(cores8-15)={L}  tok/s={res[m][L]}",flush=True)
        time.sleep(2)
open("results/b3_result.json","w").write(json.dumps(res))
print("B3DONE",json.dumps(res),flush=True)
