# Cloud Scheduling — CloudCast & Can't Be Late (§5.2)

**Paper claim.** Two cloud-infrastructure algorithms from the ADRS benchmark, both optimized in generalization mode with train/val splits over infrastructure scenarios:

- **CloudCast** (broadcast routing): **40.2% cost savings** over Dijkstra, evolving a shortest-path baseline into a provider-aware Steiner-tree solver that jointly optimizes egress cost and transfer latency. (Figure 3a in the paper.)
- **Can't Be Late** (spot-vs-on-demand scheduling): **7.8% cost savings**, evolving a deadline-check heuristic into an adaptive strategy with state tracking for spot-unavailability patterns, break-even switching cost analysis, and graduated decision thresholds. (Figure 3b in the paper.)

Both top the ADRS leaderboard, outperforming OpenEvolve, ShinkaEvolve, and expert-designed heuristics.

## Offline Review

If you do not want to spend API credits, there is now a partial offline path:

- `cloudcast/offline_logs/cloudcast_output.log` — saved late-stage optimization log with candidate code proposals, score changes, and raw-cost numbers.
- `cloudcast/optimization_trajectory.png` / `.pdf` — paper plot.
- `can_be_late/simulator/real_traces.tar.gz` — real spot-availability trace archive.
- `can_be_late/simulator/scripts/results.csv` — simulator summary table for on-demand, greedy, time-sliced, and ideal strategies.
- `can_be_late/optimization_trajectory.png` / `.pdf` — paper plot.

The CloudCast log is the strongest offline evidence in this domain because it
contains a textual optimization segment with candidate code and score changes.
`Can't Be Late` has code, real traces, simulator summaries, and the paper plot,
but does not yet include an equally rich saved GEPA checkpoint or textual run
log in this artifact folder.

## Code (this folder)

| Subfolder | Contents |
|---|---|
| `cloudcast/` | `main.py` + `evaluator.py` + `cloudcast/` (broadcast simulator with provider profiles, throughput/cost CSVs, multi-cloud config), `requirements.txt` |
| `can_be_late/` | `main.py` + `evaluator.py` + `simulator/` (sky-spot scheduler with real availability traces in `simulator/real_traces.tar.gz`), `trace_dataset.py`, `trace_config.py` |

Each subfolder ships an `optimization_trajectory.png` / `.pdf` corresponding to Figure 3a / 3b in the paper.

## Reproduction

Each subfolder has its own `README.md` with model + dataset setup. Briefly:

```bash
# CloudCast
cd cloudcast
pip install -r requirements.txt
export OPENAI_API_KEY=<your-key>
python main.py --model openai/gpt-5.1

# Can't Be Late
cd can_be_late
tar -xzf simulator/real_traces.tar.gz -C simulator
export OPENAI_API_KEY=<your-key>
python main.py --model openai/gpt-5.1
```

The bundled `optimization_trajectory.png` / `.pdf` in each subfolder shows the score-vs-iteration curve for the paper run. Re-run `main.py` to regenerate an optimized solver.

For expected cost, rate-limit assumptions, and full resource requirements, see
`../../REEXECUTION_REQUIREMENTS.md`.
