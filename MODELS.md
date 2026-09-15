# Models & Environment

All models are open-weight, served locally with Ollama (CPU-only, no GPU),
decoded deterministically (`temperature=0`, greedy).

## Phase 1 — cross-family (~8B, Q4_K_M parity)
| Model | Ollama tag | Ollama ID | Params | Quant | Source |
|---|---|---|---|---|---|
| Llama 3.1 8B | `llama3.1:8b` | 46e0c10c039e | 8.0B | Q4_K_M | Ollama registry |
| Qwen 2.5 7B | `qwen2.5:7b` | 845dbda0ea48 | 7.6B | Q4_K_M | Ollama registry |
| Gemma 2 9B | `gemma2:9b-q4_K_M` | 970f9a9e7fa3 | 9.4B | Q4_K_M | HF Q4_K_M GGUF, re-built via Modelfile |
| GLM-4 9B | `glm4:9b-q4_K_M` | — | 9.4B | Q4_K_M | HF Q4_K_M GGUF, re-built via Modelfile |

Gemma 2 and GLM-4 default Ollama builds use Q4_0; they were re-quantised/rebuilt
from their Hugging Face Q4_K_M GGUF repositories via custom Ollama `Modelfile`s
so that all Phase-1 models share Q4_K_M for a fair comparison.

## Phase 2 — Qwen 2.5 size × K-quant (12 configs)
| Size | Q2_K | Q4_K_M | Q8_0 |
|---|---|---|---|
| 0.5B | `qwen2_5-0_5b-q2k:latest` | `qwen2.5:0.5b` | `qwen2.5-0.5b-q8_0:latest` |
| 1.5B | `qwen2_5-1_5b-q2k:latest` | `qwen2.5:1.5b` | `qwen2.5-1.5b-q8_0:latest` |
| 3B   | `qwen2_5-3b-q2k:latest`   | `qwen2.5:3b`   | `qwen2.5-3b-q8_0:latest` |
| 7B   | `qwen2.5-7b-q2k:latest`   | `qwen2.5:7b`   | `qwen2.5-7b-q8_0:latest` |

Q2_K and Q8_0 variants were built from upstream Hugging Face GGUF checkpoints with
the same Modelfile execution template.

## Inference parameters
`stream=false`, `num_predict=1024` (benchmark) / `256` (aux experiments),
`temperature=0`, `num_ctx=2048`, 2 warm-up inferences, each intent evaluated once.

## Hardware
Bare-metal host: 2× Intel Xeon E5-2690 (16 physical cores / 32 threads total),
DDR3-1333 (two populated channels, ~21.3 GB/s theoretical ceiling), Ubuntu 24.04,
Proxmox VE. Inference in a 16-vCPU / 31 GiB VM. Energy via Intel RAPL package
counters; DRAM bandwidth via uncore IMC (CAS read/write × 64 B) — both read on the
bare-metal host.
