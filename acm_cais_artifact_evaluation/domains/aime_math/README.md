# AIME Prompt Optimization (§5.4)

**Paper claim.** Optimizing a system prompt for GPT-4.1-mini on AIME (training set: AIME 2022–2024, test set: AIME 2025) raises test accuracy **46.67% → 60.00%** (+13.3pp). Validation reaches 57.78%.

## Code (this folder)

- `main.py`, `utils.py` — runnable `optimize_anything` pipeline (copied from `examples/aime_math/`).

## Reproduction

`main.py` is wired to use `./logs/` as the GEPA run directory. Because the bundled `logs/gepa_state.bin` already exists, GEPA will load that checkpoint and resume from the paper run rather than starting from scratch, letting users verify the optimized prompt immediately.

```bash
export OPENAI_API_KEY=<your-key>
uv run python main.py            # resumes from bundled state
```

To run a fresh optimization instead, delete (or move) `logs/gepa_state.bin` first.

**Note on LLM nondeterminism.** The optimized prompt is fixed (in `logs/best_prompt.txt`), but *evaluating* it against AIME 2025 calls `gpt-4.1-mini` at `temperature=1.0`, which is nondeterministic. The original Jan 2026 run logged in `run.log` produced **18/30 = 60.00%** (the paper number); re-running the eval today on the same prompt typically lands in the 50–60% range. The deterministic, paper-matching evidence is in `run.log` (see the line `Test score improved from 46.67% to 60.00%!`).

## `logs/`

| File | Purpose |
|---|---|
| `run.log` | Training trajectory + test eval. Reports `Iteration 0: Base program full valset score: 0.4666...` (baseline), `Iteration 33: Best valset aggregate score so far: 0.5777...` (val), `Average Metric: 14.00 / 30 (46.7%)` (base test), and `Test score improved from 46.67% to 60.00%!` (best test) |
| `best_prompt.txt` | The optimized system prompt — verbatim Figure 5 in the paper |
| `aime_plot.png` | Optimization-progress plot |
| `generated_best_outputs_valset/` | Per-validation-task JSON: prompt, model answer, ground truth, score, at tracked iterations |
| `gepa_state.bin` | Full GEPA optimizer checkpoint — restore with `gepa.GEPAState.load()` to inspect the candidate pool, Pareto frontier, and per-iteration scores |
