#!/usr/bin/env python3
"""Verify bundled ACM CAIS artifacts without API calls.

This script intentionally uses only the Python standard library. It is meant to
run in a clean checkout before installing any domain-specific packages.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def read_text(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> Any:
    if not path.is_file():
        raise AssertionError(f"missing file: {path.relative_to(ROOT)}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise AssertionError(f"missing file: {path.relative_to(ROOT)}")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_aime() -> str:
    log = read_text(ROOT / "domains/aime_math/logs/run.log")
    best_prompt = read_text(ROOT / "domains/aime_math/logs/best_prompt.txt")
    required = [
        "Iteration 0: Base program full valset score: 0.4666666666666667",
        "Iteration 33: Best valset aggregate score so far: 0.5777777777777777",
        "Average Metric: 14.0 / 30 (46.7%)",
        "Average Metric: 18.0 / 30 (60.0%)",
        "Test score improved from 46.67% to 60.00%!",
    ]
    for needle in required:
        require(needle in log, f"AIME run.log missing expected line: {needle}")
    require(len(best_prompt.strip()) > 1000, "AIME best_prompt.txt is unexpectedly short")
    return "run.log confirms 46.67% -> 60.00%; optimized prompt is present"


def check_arc_agi() -> str:
    run_log = read_text(ROOT / "domains/arc_agi/logs/run.log")
    test_log = read_text(ROOT / "domains/arc_agi/logs/test_run.log")
    test_results = read_json(ROOT / "domains/arc_agi/logs/test_results.json")
    require("Iteration 0: Base program full valset score: 0.565" in run_log, "ARC run.log missing base val score")
    require("Iteration 30: Best valset aggregate score so far: 0.935" in run_log, "ARC run.log missing best val score")
    for needle in ["Seed:  130/400 (32.5%)", "Best:  358/400 (89.5%)", "Δ:     +57.0%"]:
        require(needle in test_log, f"ARC test_run.log missing expected line: {needle}")
    require(test_results["seed"]["solved"] == 34, "ARC saved JSON seed solved count mismatch")
    require(test_results["seed"]["total"] == 80, "ARC saved JSON seed total mismatch")
    require(test_results["best"]["solved"] == 73, "ARC saved JSON best solved count mismatch")
    require(test_results["best"]["total"] == 80, "ARC saved JSON best total mismatch")
    return "run.log/test_run.log confirm headline trajectory; saved JSON confirms 34/80 -> 73/80 subset"


def check_circle_packing() -> str:
    logs = read_json(ROOT / "domains/circle_packing/logs/state_tracker_logs.json")
    require(isinstance(logs, list) and logs, "circle packing state_tracker_logs.json is empty")
    best = max(float(row.get("best_score", float("-inf"))) for row in logs)
    last_calls = int(logs[-1].get("metric_calls", 0))
    require(best >= 2.63598, f"circle packing best score too low: {best}")
    require(last_calls >= 100, f"circle packing metric call count too low: {last_calls}")
    require((ROOT / "domains/circle_packing/logs/gepa_state.bin").is_file(), "circle packing gepa_state.bin missing")
    return f"state tracker has {len(logs)} entries; best score {best:.12f}"


def check_cloudcast() -> str:
    log = read_text(ROOT / "domains/cloud_scheduling/cloudcast/offline_logs/cloudcast_output.log")
    base_match = re.search(r"Iteration 143: Base program full valset score: ([0-9.]+)", log)
    best_match = re.search(r"Iteration 165: Found a better program on the valset with score ([0-9.]+)", log)
    raw_new_match = re.search(r"Iteration 165: Objective aggregate scores for new program: .*'raw_cost': ([0-9.]+)", log)
    raw_ref_match = re.search(r"Iteration 147: Objective pareto front scores: .*'raw_cost': ([0-9.]+)", log)
    require(base_match is not None, "CloudCast base score line missing")
    require(best_match is not None, "CloudCast improved score line missing")
    base = float(base_match.group(1))
    best = float(best_match.group(1).rstrip("."))
    require(best > base, f"CloudCast score did not improve: {base} -> {best}")
    require(raw_new_match is not None, "CloudCast new raw_cost line missing")
    require(raw_ref_match is not None, "CloudCast reference raw_cost line missing")
    raw_new = float(raw_new_match.group(1))
    raw_ref = float(raw_ref_match.group(1))
    require(raw_new < raw_ref, f"CloudCast raw_cost did not decrease: {raw_ref} -> {raw_new}")
    return f"saved log improves score {base:.6f} -> {best:.6f} and raw cost {raw_ref:.3f} -> {raw_new:.3f}"


def check_gskill_training() -> str:
    expected = {
        "run_blevesearch_20260131_131944_d7b877": (0.19, 0.85, 300),
        "run_pallets_20260131_152447_4347c2": (0.38, 0.59, 307),
    }
    base = ROOT / "domains/gskill/offline_runs/gepa_skills_training"
    details: list[str] = []
    for run_name, (baseline, optimized, calls) in expected.items():
        summary = read_json(base / run_name / "summary.json")
        info = summary["extra_info"]
        require(info["baseline_test_score"] == baseline, f"{run_name} baseline mismatch")
        require(info["optimized_test_score"] == optimized, f"{run_name} optimized score mismatch")
        require(info["total_metric_calls"] == calls, f"{run_name} metric call count mismatch")
        require((base / run_name / "gepa_state.bin").is_file(), f"{run_name} gepa_state.bin missing")
        details.append(f"{run_name}: {baseline:.2f}->{optimized:.2f}")
    return "; ".join(details)


def check_gskill_claude_eval() -> str:
    expected = {
        "run_blevesearch_haiku": (46, 58),
        "run_blevesearch_haiku_with_real_skills": (58, 58),
        "run_blevesearch_sonnet": (55, 58),
        "run_blevesearch_sonnet_with_real_skills": (58, 58),
        "run_pallets_haiku": (62, 66),
        "run_pallets_haiku_with_real_skills": (65, 66),
        "run_pallets_sonnet": (66, 66),
        "run_pallets_sonnet_with_real_skills": (66, 66),
    }
    base = ROOT / "domains/gskill/offline_runs/claude_code_eval"
    for run_name, (passed, total) in expected.items():
        summary = read_json(base / run_name / "summary.json")
        results = read_jsonl(base / run_name / "results.jsonl")
        require(summary["passed"] == passed, f"{run_name} passed count mismatch")
        require(summary["total"] == total, f"{run_name} total count mismatch")
        require(len(results) == total, f"{run_name} results.jsonl length mismatch")
    require(expected["run_blevesearch_haiku_with_real_skills"][0] > expected["run_blevesearch_haiku"][0], "blevesearch haiku skills did not improve")
    require(expected["run_blevesearch_sonnet_with_real_skills"][0] > expected["run_blevesearch_sonnet"][0], "blevesearch sonnet skills did not improve")
    require(expected["run_pallets_haiku_with_real_skills"][0] > expected["run_pallets_haiku"][0], "pallets haiku skills did not improve")
    return "8 saved Claude Code evaluation summaries and result files verified"


def check_blackbox() -> str:
    problems = [9, 10, 24, 31, 38, 45, 46, 51, 53, 54]
    base = ROOT / "domains/blackbox/logs"
    gepa_root = base / "optimize_anything_b2000"
    optuna_root = base / "optuna_b2000"
    require(gepa_root.is_dir(), "blackbox optimize_anything_b2000 directory missing")
    require(optuna_root.is_dir(), "blackbox optuna_b2000 directory missing")
    for problem in problems:
        gepa_results = sorted((gepa_root / f"problem_{problem}").glob("gpt-5.1/*/*/results.json"))
        optuna_results = sorted((optuna_root / f"problem_{problem}").glob("seed_*/*.json"))
        require(len(gepa_results) == 10, f"problem {problem}: expected 10 optimize_anything results, found {len(gepa_results)}")
        require(len(optuna_results) == 10, f"problem {problem}: expected 10 Optuna seed results, found {len(optuna_results)}")
        for result_path in gepa_results:
            result = read_json(result_path)
            require(result["problem_index"] == problem, f"{result_path}: problem index mismatch")
            require(0 < result["total_evals"] <= 2000, f"{result_path}: total_evals out of range")
            eval_log = result_path.with_name("eval_log.jsonl")
            rows = read_jsonl(eval_log)
            require(len(rows) == result["total_evals"], f"{eval_log}: row count does not match total_evals")
            require(rows[-1]["budget_total"] == 2000, f"{eval_log}: budget_total mismatch")
            require(rows[-1]["budget_used"] == result["total_evals"], f"{eval_log}: final budget_used mismatch")
    return "10 hardest problems verified with 10 optimize_anything and 10 Optuna seed logs each"


def check_kernelbench() -> str:
    aggregated = read_json(ROOT / "domains/kernelbench/logs/best_kernels_aggregated.json")
    require(len(aggregated) == 31, f"KernelBench expected 31 tasks, found {len(aggregated)}")
    speedups = [float(item["speedup"]) for item in aggregated.values()]
    fast_1_count = sum(speed >= 1.0 for speed in speedups)
    require(fast_1_count >= 26, f"KernelBench expected at least 26 kernels at speedup >= 1.0, found {fast_1_count}")
    require(max(speedups) >= 30.0, "KernelBench expected at least one 30x saved speedup")
    return f"31 saved kernels; {fast_1_count}/31 have speedup >= 1.0; max speedup={max(speedups):.2f}"


CHECKS = [
    ("AIME", check_aime),
    ("ARC-AGI", check_arc_agi),
    ("Circle Packing", check_circle_packing),
    ("CloudCast", check_cloudcast),
    ("gskill Training", check_gskill_training),
    ("gskill Claude Code Eval", check_gskill_claude_eval),
    ("Blackbox", check_blackbox),
    ("KernelBench Saved Results", check_kernelbench),
]


def main() -> int:
    results: list[CheckResult] = []
    for name, fn in CHECKS:
        try:
            detail = fn()
            results.append(CheckResult(name, True, detail))
        except Exception as exc:  # noqa: BLE001 - report all verifier failures uniformly
            results.append(CheckResult(name, False, str(exc)))

    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"[{status}] {result.name}: {result.detail}")

    passed = sum(result.ok for result in results)
    print(f"\nSummary: {passed}/{len(results)} checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
