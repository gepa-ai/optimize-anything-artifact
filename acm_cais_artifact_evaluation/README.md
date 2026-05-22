# ACM CAIS '26 Artifact Evaluation — `optimize_anything`

Artifact for the paper **"optimize_anything: Unified Text Optimization can Outperform Specialized Systems"** (ACM CAIS 2026).

## Review Modes

This artifact supports two review modes:

1. **Offline mode (recommended if you do not have API credits).**
   Inspect bundled trajectories, checkpoints, saved outputs, and post-hoc evaluations without making any model calls.
2. **Live rerun mode.**
   Re-run selected domains with your own API keys and hardware.

## What this artifact contains

- `domains/` — one self-contained subdirectory per experimental domain claimed in the paper. Each domain folder is independent and includes its own `README.md`, runnable code, and any artifacts needed to verify the paper's claims.
- `REEXECUTION_REQUIREMENTS.md` — end-to-end live-rerun requirements, including model configuration, API-cost expectations, rate-limit assumptions, GPU requirements, and per-domain commands.
- `OFFLINE_ARTIFACTS.md` — zero-API guide to bundled trajectories, checkpoints, and saved evaluations.
- `verify_offline_artifacts.py` — no-API verifier for the bundled logs, trajectories, and saved outputs.
- `offline_verification_logs/` — saved output from running the verifier after `uv sync --extra dev`.
- `../LICENSE` — MIT license file for the artifact repository.

## System Requirements

Tested on macOS and Linux.

Required for the general artifact:

- Python `>=3.10,<3.15`
- `git`
- `uv`

Install `uv` if it is not already available:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your shell or add the printed `uv` install directory to `PATH`.

Additional requirements for selected live reruns:

- API keys for the model provider named in each domain README.
- NVIDIA V100 32GB GPU, CUDA 12.1+, and NVCC for KernelBench.
- Docker for full gskill training/evaluation reruns.

For per-domain live-rerun costs, model settings, rate-limit assumptions, and
hardware needs, see `REEXECUTION_REQUIREMENTS.md`.

## Quick repository map

| Paper section | Folder |
|---|---|
| §5.1 Coding Agent Skills | `domains/gskill/` |
| §5.2 Cloud Scheduling (CloudCast, Can't Be Late) | `domains/cloud_scheduling/` |
| §5.3 ARC-AGI Agent Architecture | `domains/arc_agi/` |
| §5.4 AIME Prompt Optimization | `domains/aime_math/` |
| §5.5 CUDA Kernel Generation (KernelBench) | `domains/kernelbench/` |
| §5.6 Circle Packing (n=26) | `domains/circle_packing/` |
| §5.7 SVG / CAD Image Generation | `domains/svg_cad/` |
| Appendix B Black-box Math Optimization | `domains/blackbox/` |
| Appendix C 3D Modeling (seedless) | `domains/modeling_3d/` |

## Offline-First Review Path

If you do not have API credits, start here:

```bash
uv sync --extra dev
uv run python acm_cais_artifact_evaluation/verify_offline_artifacts.py
```

Then inspect the files named in `OFFLINE_ARTIFACTS.md` if you want to audit individual claims:

1. `domains/aime_math/logs/`
2. `domains/arc_agi/logs/`
3. `domains/blackbox/logs/`
4. `domains/circle_packing/logs/`
5. `domains/cloud_scheduling/cloudcast/offline_logs/cloudcast_output.log`
6. `domains/gskill/offline_runs/`

These paths let users inspect saved trajectories, checkpoints, best artifacts, and post-hoc evaluations without making model calls.
The expected verifier output is saved in `offline_verification_logs/verification_v1.4.log`.

Best offline-supported domains:

- `domains/aime_math/`
- `domains/arc_agi/`
- `domains/blackbox/`
- `domains/circle_packing/`
- `domains/gskill/`
- `domains/cloud_scheduling/cloudcast/`

Still primarily live-rerun dependent or only partially supported offline:

- `domains/cloud_scheduling/can_be_late/` — code, real traces, simulator summary CSVs, and plots are bundled, but not a full saved GEPA trajectory checkpoint/log bundle.
- `domains/kernelbench/` — saved kernels and aggregate speedups are bundled, but independent performance reproduction still requires a V100-class GPU.
- `domains/svg_cad/` and `domains/modeling_3d/` — useful tutorial assets are present, but they are not the strongest no-API validation path.

## License

This artifact repository is released under the MIT license. The root license file is `../LICENSE` from this directory, or `LICENSE` from the repository root.

## Live Rerun Mode

For domains you want to re-run, first install dependencies:

```bash
uv sync --extra dev
```

Then follow the domain-specific README:

```bash
cd domains/<name>
export <PROVIDER>_API_KEY=<your-key>     # see the domain README
uv run python main.py
```

Where bundled state is provided, `main.py` is wired so `EngineConfig.run_dir` points at `./logs/`, and GEPA resumes from that checkpoint rather than starting from scratch. To run a fresh optimization, move or delete `logs/gepa_state.bin` first.

§5.5 (CUDA Kernel Generation, KernelBench) requires a V100 32GB GPU to re-run; see `domains/kernelbench/README.md`.

## Badges requested

Artifact Available, Functional, and Results Reproduced.
