# End-to-End Re-execution Requirements

This artifact is designed to support both offline inspection and live reruns.
The table below documents the resources needed for independent end-to-end
re-execution. Costs are approximate because provider pricing and cache hit rates
change over time.

## General Setup

From the repository root:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --extra dev
```

Common requirements:

- Python `>=3.10,<3.15`
- `git`
- `uv`
- Provider API keys for the selected model backend
- Stable outbound network access to the model provider
- Enough provider quota to sustain parallel workers, or lower `max_workers`

## Live Rerun Matrix

| Domain | Main command | LLM config in artifact | Budget / parallelism | Hardware | Expected time / cost | Notes |
|---|---|---|---|---|---|---|
| AIME | `uv run python acm_cais_artifact_evaluation/domains/aime_math/main.py` | Solver `gpt-4.1-mini`; reflector `openai/gpt-5.1`; solver temperature `1.0`, max tokens `32000` | `max_metric_calls=500`, `max_workers=32` | CPU | Hours; tens to low hundreds USD | Requires `OPENAI_API_KEY`. Bundled `logs/` resume from the paper run unless `logs/gepa_state.bin` is moved. |
| ARC-AGI | `uv run python acm_cais_artifact_evaluation/domains/arc_agi/main.py` | `openrouter/google/gemini-3-flash-preview` for agent calls and reflection | `max_metric_calls=3000`, `max_workers=64`; each evaluation allows up to 10 LLM calls | CPU | Many hours; hundreds USD | Requires OpenRouter or compatible provider credentials. Full test rerun is expensive. |
| CloudCast | `cd acm_cais_artifact_evaluation/domains/cloud_scheduling/cloudcast && uv run python main.py --model <model>` | User-specified `--model`; paper run used a GPT/Gemini-class reflection model | default `max_metric_calls=100`, minibatch `3` | CPU | Hours; low to moderate API cost | Small config dataset. Offline log contains a saved late-stage trajectory segment. |
| Can't Be Late | `cd acm_cais_artifact_evaluation/domains/cloud_scheduling/can_be_late && tar -xzf simulator/real_traces.tar.gz -C simulator && uv run python main.py --model <model>` | User-specified `--model`; paper run used a GPT/Gemini-class reflection model | default `max_metric_calls=100`, minibatch `3`, `max_workers=128` | CPU, high parallelism helpful | Hours; moderate API cost | Real traces are bundled as `simulator/real_traces.tar.gz`. Lower `max_workers` if rate-limited. |
| gskill | See `domains/gskill/README.md` | Agent model `gpt-5-mini`; reflection model `gpt-5.2-pro` in documented full run | `workers=6`, `max_metric_calls=600` in documented full run | CPU plus Docker | Long-running; high API cost | Requires Docker, SWE-smith images, and model API access. |
| KernelBench | `cd acm_cais_artifact_evaluation/domains/kernelbench && python main.py` | GPT-5 + Gemini-class proposer/reflector as documented in the domain README | `max_metric_calls=900` in paper run | NVIDIA V100 32GB, CUDA 12.1+, NVCC | ~6 hours; about $200 API cost on paper host | Performance claims are V100-specific. Other GPUs can run but speedups will differ. |
| Circle Packing | `uv run python acm_cais_artifact_evaluation/domains/circle_packing/main.py --run-name fresh --model openai/gpt-5.1` | default `openai/gpt-5.1` | default `max_metric_calls=150`, timeout `600s` per candidate | CPU | Hours; low to moderate API cost | Requires `OPENAI_API_KEY`. |
| Blackbox | See `domains/blackbox/README.md` | `openai/gpt-5.1` via OpenRouter in the documented command | 2,000 objective evaluations per problem, 10 proposals | CPU | Long-running across 10 problems; moderate API cost | Offline bundle contains 10 hardest problems and Optuna comparisons. |

## Rate Limit Assumptions

The paper runs used high parallelism to finish in a reasonable wall-clock time.
If provider rate limits are lower than the settings above, use one of these
workarounds:

- Lower `max_workers`.
- Lower `--max-metric-calls` for a smoke test.
- Use a smaller `--max-traces` value for Can't Be Late.
- Set `GEPA_SKIP_TEST=1` when only the optimization trajectory is needed.

Lowering these settings changes wall-clock time and may change final quality, so
the exact paper numbers should be expected only under comparable budgets.

## Offline Coverage Boundary

The no-API verifier is intentionally not a substitute for full live reruns. It
checks that the bundled evidence is present and internally consistent. The
strongest offline-supported domains include AIME, ARC-AGI, Blackbox, Circle
Packing, CloudCast, gskill, and KernelBench saved results. Can't Be Late has
code, real traces, simulator summaries, and the paper trajectory plot, but this
artifact does not currently include a full GEPA checkpoint or text log for that
run.
