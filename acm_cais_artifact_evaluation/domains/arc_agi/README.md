# ARC-AGI Agent Architecture (§5.3)

**Paper claim.** Using Gemini 3 Flash as both proposer and underlying agent model, `optimize_anything` evolves a naive 10-line agent seed (one LLM call) into a 300+ line, 4-component architecture with fallbacks. Test accuracy rises **32.5% → 89.5%** (+57pp); validation reaches 93.5%.

## Code (this folder)

- `main.py`, `utils.py` — runnable `optimize_anything` pipeline (copied from `examples/arc_agi/`).

## Reproduction

`main.py` is wired to use `./logs/` as the GEPA run directory. Because the bundled `logs/gepa_state.bin` already exists, GEPA will load that checkpoint and resume from the paper run rather than starting from scratch, letting users verify the optimized agent immediately.

```bash
export OPENROUTER_API_KEY=<your-key>
uv run python main.py            # resumes from bundled state
```

To run a fresh optimization instead, delete (or move) `logs/gepa_state.bin` first.

## `logs/`

| File | Purpose |
| --- | --- |
| `test_run.log` | Test-set evaluation. Reports `Seed: 130/400 (32.5%)`, `Best: 358/400 (89.5%)`, `Δ: +57.0%` |
| `run.log` | Full training trajectory |
| `agent_architecture.md` | Human-readable description of the evolved 4-component agent |
| `best_agent.py` | The final optimized agent code |
| `all_candidates.json`, `candidate_eval_results.json` | Per-iteration candidates with per-task scores |
| `test_results.json` | Per-task test outcomes |
| `*.png` | Optimization-progress and candidate cost/accuracy plots |
| `generated_best_outputs_valset/` | Validation outputs from the best candidate |
| `gepa_state.bin` | Full GEPA optimizer checkpoint — restore with `gepa.GEPAState.load()` to inspect the candidate pool, Pareto frontier, and per-iteration scores |
