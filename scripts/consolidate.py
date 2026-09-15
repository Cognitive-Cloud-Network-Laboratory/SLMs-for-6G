import json, glob, os, statistics as st
D="results/temp0"
summ=json.load(open(os.path.join("results","summary_temp0.json")))
rows_by_model={r["model"]:r for r in summ["rows"]}

# filename -> meta
FILES={
 "benchmark_llama3_1_8b_temp0.json":        ("llama3.1:8b","P1","Llama 3.1 8B","8B","Q4_K_M"),
 "benchmark_qwen2_5_7b_temp0.json":         ("qwen2.5:7b","P1","Qwen 2.5 7B","7B","Q4_K_M"),
 "benchmark_gemma2_9b-q4_K_M_temp0.json":   ("gemma2:9b-q4_K_M","P1","Gemma 2 9B","9B","Q4_K_M"),
 "benchmark_glm4_9b-q4_K_M_temp0.json":     ("glm4:9b-q4_K_M","P1","GLM-4 9B","9B","Q4_K_M"),
 "benchmark_qwen2_5_0_5b_temp0.json":       ("qwen2.5:0.5b","P2","0.5B","0.5B","Q4_K_M"),
 "benchmark_qwen2_5_1_5b_temp0.json":       ("qwen2.5:1.5b","P2","1.5B","1.5B","Q4_K_M"),
 "benchmark_qwen2_5_3b_temp0.json":         ("qwen2.5:3b","P2","3B","3B","Q4_K_M"),
 "benchmark_qwen2_5-0_5b-q2k_latest_temp0.json":("qwen2_5-0_5b-q2k:latest","P2","0.5B","0.5B","Q2_K"),
 "benchmark_qwen2_5-1_5b-q2k_latest_temp0.json":("qwen2_5-1_5b-q2k:latest","P2","1.5B","1.5B","Q2_K"),
 "benchmark_qwen2_5-3b-q2k_latest_temp0.json":  ("qwen2_5-3b-q2k:latest","P2","3B","3B","Q2_K"),
 "benchmark_qwen2_5-7b-q2k_latest_temp0.json":  ("qwen2.5-7b-q2k:latest","P2","7B","7B","Q2_K"),
 "benchmark_qwen2_5-0_5b-q8_0_latest_temp0.json":("qwen2.5-0.5b-q8_0:latest","P2","0.5B","0.5B","Q8_0"),
 "benchmark_qwen2_5-1_5b-q8_0_latest_temp0.json":("qwen2.5-1.5b-q8_0:latest","P2","1.5B","1.5B","Q8_0"),
 "benchmark_qwen2_5-3b-q8_0_latest_temp0.json":  ("qwen2.5-3b-q8_0:latest","P2","3B","3B","Q8_0"),
 "benchmark_qwen2_5-7b-q8_0_latest_temp0.json":  ("qwen2.5-7b-q8_0:latest","P2","7B","7B","Q8_0"),
}
def mean(xs):
    xs=[x for x in xs if isinstance(x,(int,float))]
    return round(st.mean(xs),2) if xs else None

out={"theoretical_peak_bw":summ.get("peak_bw_gbps_theoretical"),"locality":summ.get("locality"),"configs":[]}
for fn,(model,phase,label,size,quant) in FILES.items():
    d=json.load(open(os.path.join(D,fn)))
    s=d["summary"]; its=d["results"]
    r=rows_by_model.get(model,{})
    # domain action-correct + provisioning exact
    dom={}; provexact=[]
    for name in ["Slicing Provisioning","Scaling Request","Conflict Resolution"]:
        sub=[i for i in its if i["domain"]==name]
        dom[name]=round(100*sum(1 for i in sub if i.get("action_correct"))/len(sub),1) if sub else None
    prov=[i for i in its if i["domain"]=="Slicing Provisioning"]
    provexact=round(mean([i.get("match_pct") for i in prov]),1) if prov else None
    # complexity match%
    comp={}
    for c in ["Simple","Complex","Ambiguous"]:
        sub=[i for i in its if i.get("complexity")==c]
        comp[c]=round(mean([i.get("match_pct") for i in sub]),1) if sub else None
    ci=r.get("ci",{})
    out["configs"].append({
        "model":model,"phase":phase,"label":label,"size":size,"quant":quant,
        "format":s.get("format_valid_pct"),"action":s.get("action_correct_pct"),
        "match":round(s.get("avg_match_pct"),1),"time_s":round(s.get("avg_time_s"),2),
        "tps":round(s.get("avg_tokens_per_sec"),1),"total_tokens":s.get("total_tokens"),
        "avg_tokens":round(s.get("avg_tokens"),1),
        "cpu":round(s.get("avg_cpu_pct"),1),"peak_mem_mb":round(s.get("avg_peak_memory_mb")),
        "e_rapl":round(r.get("energy_j_rapl_avg")) if r.get("energy_j_rapl_avg") else None,
        "e_rapl_marg":round(r.get("energy_j_rapl_marginal")) if r.get("energy_j_rapl_marginal") else None,
        "e_pkg0_marg":round(r.get("energy_j_pkg0_marginal")) if r.get("energy_j_pkg0_marginal") else None,
        "e_est":round(r.get("energy_j_est")) if r.get("energy_j_est") else None,
        "bw":r.get("mem_bw_gbps"),"bw_peak":r.get("mem_bw_peak_gbps"),"bw_pct":r.get("mem_bw_pct_peak"),
        "ci_match":ci.get("match_pct"),"ci_time":ci.get("duration_s"),
        "ci_erapl":ci.get("energy_j_rapl"),"ci_bw":ci.get("mem_bw_gbps"),
        "ci_cpu":ci.get("cpu_pct"),"ci_peakmem":ci.get("peak_memory_mb"),
        "domain":dom,"prov_exact":provexact,"complexity":comp,
    })
json.dump(out,open(os.path.join("results","consolidated.json"),"w"),indent=1)
print("wrote consolidated.json with",len(out["configs"]),"configs")
# quick sanity print
for c in out["configs"]:
    print(c["phase"],c["label"],c["quant"],"fmt",c["format"],"act",c["action"],"match",c["match"],"t",c["time_s"],"E_rapl",c["e_rapl"],"bw",c["bw"],"pk",c["bw_peak"])
