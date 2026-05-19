# CUDA Kernel Generation — KernelBench (§5.5)

**Paper claim.** `optimize_anything` generates CUDA kernels for 31 reference PyTorch operations from KernelBench, evaluated on a V100 32GB GPU.

- **87%** of generated kernels match or beat the PyTorch baseline (`Fast_p(1.0) = 0.87`)
- **48%** achieve ≥10× speedup
- **25%** achieve ≥20× speedup
- Multi-task search consistently outperforms single-task at every speedup threshold (§5.8 ablation)

The evolved kernels use `float4` vectorization, two-pass algorithms (compute statistics, then normalize), warp-shuffle reductions, and shared-memory tiling.

## ⚠️ Hardware requirement

Reproducing this domain requires:

- **NVIDIA V100 32GB GPU** (paper used SXM2). Other Volta-family GPUs (V100 16GB, Titan V) should work but speedup numbers will differ. Ampere/Hopper GPUs will work but the V100-tuned kernels won't be the optimal artifact.
- **CUDA 12.1+**, NVCC compiler, cuBLAS, NCCL.
- **PyTorch ≥ 2.1** with CUDA support.

The bundled `logs/` directory contains the full optimization output that produced the paper numbers.

## Code (this folder)

| File | Purpose |
|---|---|
| `main.py` | Entrypoint. Optimizes `KERNEL_GEN_PROMPT` and `REFINER_PROMPT` jointly via multi-task search across the 31 problems |
| `eval.py` | KernelBench evaluator: NVCC compilation, correctness checks (max-abs-error vs PyTorch reference), wall-clock benchmarking, GPU lock manager |
| `agentic_rag.py` | RAG retrieval over CUDA documentation (`rag_content/`) for kernel writing patterns |
| `prompts.py` | Seed prompts (`BACKGROUND`, `KERNEL_GEN_PROMPT`, `REFINER_PROMPT`) and DSPy signatures |
| `rag_content/` | CUDA reference docs the agent retrieves over: V100 spec sheet, CUDA C++ Programming Guide / Best Practices, cuBLAS GEMM patterns, CUTLASS patterns, PyTorch CUDA extension guide, Volta tuning guide, full `cuda_runtime_api/` and `cuda_math_api/` HTML docs |

## `logs/`

| File | What it shows |
|---|---|
| `gepa_state.bin` | Full GEPA optimizer checkpoint (15 MB) — restore with `gepa.GEPAState.load()` to inspect every candidate kernel and per-problem score across iterations |
| `best_kernels.json` | Best generated CUDA kernel source per problem (850 KB) |
| `best_kernels_aggregated.json` | Aggregated per-problem best score (correctness flag, speedup vs PyTorch baseline) |
| `fast_p_score.png` | Figure 7 in the paper: Fast_p(s) curve (fraction of kernels achieving speedup ≥ s) |
| `fast_p_curve.png` | Higher-resolution version of the same |
| `speedup.png` | Per-problem speedup bar chart |

## Reproduction (V100)

### Environment

```bash
# 1. Get the upstream KernelBench dataset (referenced by main.py via load_dataset())
git clone https://github.com/ScalingIntelligence/KernelBench.git

# 2. Create a Python venv with required packages.
#    The package set below was sufficient on our V100 host (Ubuntu 22.04 + CUDA 12.1).
python3.11 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Plus this artifact's gepa package, installed from the repo root:
pip install -e ../../..
```

### NVCC

The harness invokes `nvcc` directly to compile each generated kernel:

```bash
which nvcc       # must be in PATH
nvcc --version   # CUDA 12.1+ recommended
```

### GPU access

```bash
nvidia-smi       # confirm V100 visible
export CUDA_VISIBLE_DEVICES=0    # if multiple GPUs, pin to one V100
```

### Run

```bash
export OPENAI_API_KEY=<your-key>
export GEMINI_API_KEY=<your-key>     # paper used GPT-5 + Gemini for proposer/reflector

python main.py             # auto-resumes from bundled logs/gepa_state.bin
```

`main.py` is wired to use `./logs/` as the GEPA run directory, so it auto-resumes from the bundled paper checkpoint. To start a fresh optimization, pass `--run-name <name>` (writes to `./outputs/<name>/`) or move/delete `logs/gepa_state.bin` first.

### Expected wall time and cost

The full 31-problem multi-task run took ~6 hours on the paper host with `max_metric_calls=900`. LLM cost was ~$200 USD with GPT-5 + Gemini 3 Flash.
