import urllib.request,json,re,sys
MODEL=sys.argv[1] if len(sys.argv)>1 else "qwen2.5:3b"
SYSTEM_PROMPT="""You are a 6G Core Network Slice Management Agent. 
Your job is to translate natural language intents into JSON commands for network orchestration.

Rules:
1. Respond ONLY with a valid JSON object — no markdown, no explanations, no code fences
2. The JSON MUST contain an "action" field
3. Use these slice types when appropriate: "eMBB" (enhanced Mobile Broadband), "URLLC" (Ultra-Reliable Low Latency), "mMTC" (massive Machine Type Communications)
4. For ambiguous requests, infer the best configuration based on context
5. Include all relevant parameters: latency_ms, bandwidth_gbps, device_density, priority, etc.

Example:
Input: "Create a URLLC slice with 1ms latency for robot control"
Output: {"action": "CREATE", "slice_type": "URLLC", "latency_ms": 1}"""
def parse_json(text):
    if not text: return None
    c=text.strip()
    if c.startswith("```"):
        p=c.split("\n"); c="\n".join(p[1:-1]) if len(p)>2 else c[3:]
        if c.endswith("```"): c=c[:-3]
    c=re.sub(r"<think>.*?</think>","",c.strip(),flags=re.DOTALL).strip()
    try:
        r=json.loads(c)
        if isinstance(r,dict): return r
    except Exception: pass
    for m in re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',c):
        try:
            r=json.loads(m)
            if isinstance(r,dict): return r
        except Exception: pass
    return None
def score(parsed,truth):
    if not parsed: return (False,False,0.0)
    action_ok=str(parsed.get("action","")).lower()==truth["action"].lower()
    exact=sum(1 for k in truth if k in parsed and str(parsed[k]).lower()==str(truth[k]).lower())
    return (True,action_ok,round(exact/len(truth)*100,1) if truth else 0.0)
intents=[json.loads(l) for l in open("dataset/intents.jsonl") if l.strip()]
def toks(s): return set(re.findall(r"[a-z0-9]+",s.lower()))
TK=[toks(it["input_text"]) for it in intents]
def retrieve(idx,k=3):
    q=TK[idx]
    sims=sorted(((len(q&TK[j])/(len(q|TK[j]) or 1),j) for j in range(len(intents)) if j!=idx),reverse=True)
    return [intents[j] for _,j in sims[:k]]
def call(prompt):
    body=json.dumps({"model":MODEL,"prompt":prompt,"system":SYSTEM_PROMPT,"stream":False,
        "options":{"temperature":0,"num_ctx":2048,"num_predict":256}}).encode()
    r=json.loads(urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/generate",
        data=body,headers={"Content-Type":"application/json"}),timeout=180).read())
    return r.get("response","")
def run(mode):
    f=a=0; ms=[]
    for i,it in enumerate(intents):
        if mode=="rag":
            ex=retrieve(i,3)
            exs="\n".join('Input: %s\nOutput: %s'%(e["input_text"].split(chr(10))[0], json.dumps(e["ground_truth"])) for e in ex)
            prompt="Similar solved examples:\n%s\n\nNow translate this intent to JSON:\nInput: %s\nOutput:"%(exs,it["input_text"])
        else:
            prompt=it["input_text"]
        fv,ac,mp=score(parse_json(call(prompt)),it["ground_truth"])
        f+=fv; a+=ac; ms.append(mp)
    n=len(intents)
    r=dict(format=round(100*f/n,1),action=round(100*a/n,1),exact=round(sum(ms)/n,1))
    print("%s %-9s format=%s action=%s exact=%s"%(MODEL,mode,r["format"],r["action"],r["exact"]),flush=True)
    return r
res={m:run(m) for m in ["zeroshot","rag"]}
open("results/a_result.json","w").write(json.dumps(res))
print("ADONE",json.dumps(res),flush=True)
