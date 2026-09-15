# Edge-Native SLMs for 6G Intent-Driven Slicing: Replication Package

This artifact repository provides the dataset, execution engine scripts, raw hardware telemetry profiles, and statistical reproduction pipelines for the empirical study:

"Edge-Native Small Language Models for 6G Intent-Driven Slicing: A Hardware-Grounded Empirical Study" (Under Review).

All evaluations enforce deterministic decoding (`temperature = 0`, greedy argmax) on bare-metal x86-64 server infrastructure without GPU acceleration. Hardware energy and DRAM memory transactions are captured directly from Intel RAPL and uncore Integrated Memory Controller (IMC) hardware performance counters.

---
1. Directory Structure
   
==========================

`dataset/`
 	`intents.jsonl`: Complete 200-intent benchmark across 3 lifecycle domains (`PROV`, `SCAL`, `CONF`) and 3 complexity tiers (Simple, Complex, Ambiguous).

`prompts/`
  	`system_prompt.txt`: Production system prompt defining schema constraints, operational rules, and valid action primitives.

scripts/`
 	`benchmark_runner_v2.py`: Main orchestration harness executing inference, JSON parsing, metric extraction, and socket telemetry.
 	`mem_measure2.py`: Standalone memory profiling harness using isolated `llama-server` processes under fixed context limits (`num_ctx = 2048`).
 	`b_runner3.py` / `hog.py`: Core-pinned memory-bus contention stress harness evaluating DRAM bandwidth saturation.
 	`a_runner.py`: Comparative evaluation script running the 3-shot retrieval-augmented (RAG) baseline.
 	`safety_metrics.py`: Script extracting confident mis-actuations and abstention rates across intent domains.
 	`consolidate.py`: Aggregates per-intent JSON logs into structured analysis matrices.
 	`plot_fig2.py`, `plot_fig3.py`: Generates publication-grade Pareto frontiers and distribution plots (300 DPI, vector-compatible).

`results/`
 	`temp0/`: Per-intent execution traces and telemetry logs (n = 200 per model configuration).
 	`summary_temp0.json`: Aggregated metrics including 95% Student's-t confidence intervals.
 	`mem_result.json`: Verified process-isolated RSS/PSS footprints from `mem_measure2.py`.
  	`b3_result.json`: Hardware telemetry logs under varying synthetic memory-bus contention (0 to 8 threads).
  	`a_result.json`: Empirical outputs from the retrieval-augmented baseline.
  	`analysis_notes.json`: Statistical pairing logs (McNemar tests with continuity corrections).


2. Hardware and Environment Requirements
   
=============================================

Host Platform: Dual-socket Intel Xeon E5-2690 (Sandy Bridge-EP, 16 physical cores, DDR3-1333, 64 GB RAM).
OS: Bare-metal Linux host with direct access to:
-	Intel RAPL MSR interfaces (`/sys/class/powercap/intel-rapl*`)
  	- Linux `perf` uncore IMC events (`uncore_imc_0/cas_count_read/`, `uncore_imc_0/cas_count_write/`)
Software Dependencies: Python 3.10+ (standard libraries, `matplotlib`), Ollama daemon, and compiled `llama-server` binaries.


3. Reproduction Workflow

==========================

Step 1: Reproduce Statistical Figures and Tables (Zero-Inference)
All raw per-intent execution traces (3,200 inference logs) are pre-compiled under `results/temp0/`. To regenerate all tables and figures without re-executing inference:

```bash
# Consolidate raw traces into structured metrics
python3 scripts/consolidate.py

# Recompute safety profiles and abstention rates (Table 12)
python3 scripts/safety_metrics.py

# Generate Pareto plots (Figures 2 and 3)
python3 scripts/plot_fig2.py
python3 scripts/plot_fig3.py
