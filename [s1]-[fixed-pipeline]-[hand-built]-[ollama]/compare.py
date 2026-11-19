"""
compare.py — S1 vs S2 side-by-side comparison (hand-built, Ollama).

Runs the same incident alert through both the S1 fixed pipeline and the S2 ReAct
loop, then prints a comparison table of LLM calls, tokens, elapsed time, and
keyword-overlap quality score. Use --all to run all 30 incidents and print
aggregate stats.

Usage:
    python compare.py
    python compare.py "ALERT: db-primary replication lag 45 minutes. Severity: P1."
    python compare.py --all
"""
# ─────────────────────────────────────────────────────
# Author   : Amit Dixit
# GitHub   : https://github.com/inbravo
# Web      : https://inbravo.github.io
# LinkedIn : https://www.linkedin.com/in/inbravo/
# ─────────────────────────────────────────────────────

from __future__ import annotations

import logging
import sys
from pathlib import Path

# ── path setup ────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_shared"))

# ── shared setup ──────────────────────────────────────
import logging_config
logging_config.setup()

import pipeline as s1

_s2_path = Path(__file__).parent.parent / "[s2]-[react-loop]-[hand-built]-[ollama]"
sys.path.insert(0, str(_s2_path))
import agent as s2

from grader             import answer_grader
from incident_generator import INCIDENTS

# ── logging ───────────────────────────────────────────
log = logging.getLogger("harness.s1.compare")


# ── helpers ───────────────────────────────────────────

def _extract_root_cause(result_text: str) -> str:
    """Pull the FINAL_ANSWER line from either agent's output.

    Args:
        result_text: Full agent response string.

    Returns:
        Root-cause sentence, or the first 120 chars of the response.
    """
    for line in result_text.splitlines():
        if line.startswith("FINAL_ANSWER:"):
            return line.replace("FINAL_ANSWER:", "").strip()
    return result_text[:120]


# ── comparison runner ─────────────────────────────────

def run_comparison(alert: str, ground_truth: str = "") -> dict:
    """Run S1 and S2 on the same alert and return comparable metrics.

    Args:
        alert:        Raw alert string.
        ground_truth: Expected root-cause string for quality scoring (optional).

    Returns:
        Dict with nested "s1" and "s2" metric dicts.
    """
    log.info("─── compare starting ───")
    log.info("alert: %s", alert)
    print(f"\nAlert: {alert}\n")

    print("── S1 Fixed Pipeline ──────────────────")
    s1_out  = s1.run(alert)
    s1_root = _extract_root_cause(s1_out["result"])

    print("\n── S2 ReAct Loop ──────────────────────")
    s2_out  = s2.run(alert)
    s2_root = _extract_root_cause(s2_out.get("result", ""))

    s1_quality = answer_grader(s1_out["result"],           ground_truth)["overlap_score"] if ground_truth else None
    s2_quality = answer_grader(s2_out.get("result", ""),   ground_truth)["overlap_score"] if ground_truth else None

    return {
        "s1": {
            "llm_calls":        s1_out["steps"],
            "prompt_tokens":    s1_out["total_prompt_tokens"],
            "completion_tokens":s1_out["total_completion_tokens"],
            "elapsed_s":        s1_out["elapsed_s"],
            "root_cause":       s1_root,
            "quality_score":    s1_quality,
        },
        "s2": {
            "llm_calls":        s2_out.get("steps", 0),
            "prompt_tokens":    0,
            "completion_tokens":0,
            "elapsed_s":        s2_out.get("budget", {}).get("elapsed_s", 0),
            "root_cause":       s2_root,
            "quality_score":    s2_quality,
            "tools_called":     s2_out.get("tools_called", []),
        },
    }


# ── display helpers ───────────────────────────────────

def print_table(result: dict) -> None:
    """Print a formatted side-by-side comparison table.

    Args:
        result: Output of run_comparison.
    """
    s1r = result["s1"]
    s2r = result["s2"]
    sep = "─" * 52

    print(f"\n{sep}")
    print(f"{'Metric':<28} {'S1 Pipeline':>10}  {'S2 ReAct':>10}")
    print(sep)
    print(f"{'LLM calls':<28} {s1r['llm_calls']:>10}  {s2r['llm_calls']:>10}")
    print(f"{'Prompt tokens':<28} {s1r['prompt_tokens']:>10}  {'—':>10}")
    print(f"{'Completion tokens':<28} {s1r['completion_tokens']:>10}  {'—':>10}")
    print(f"{'Elapsed (s)':<28} {s1r['elapsed_s']:>10.2f}  {s2r['elapsed_s']:>10.2f}")
    if s1r["quality_score"] is not None:
        print(f"{'Quality score':<28} {s1r['quality_score']:>10.3f}  {s2r['quality_score']:>10.3f}")
    print(sep)
    print(f"\nS1 root cause: {s1r['root_cause']}")
    print(f"S2 root cause: {s2r['root_cause']}")
    if s2r["tools_called"]:
        print(f"S2 tools used: {', '.join(s2r['tools_called'])}")


def run_all() -> None:
    """Run all 30 incidents and print aggregate statistics."""
    log.info("─── compare all 30 incidents ───")
    print("Running all 30 incidents…\n")

    s1_total_calls  = s1_total_tokens = 0
    s2_total_calls  = 0
    s1_quality_scores: list[float] = []
    s2_quality_scores: list[float] = []

    for inc in INCIDENTS:
        result = run_comparison(inc["alert"], inc["root_cause"])
        s1_total_calls  += result["s1"]["llm_calls"]
        s1_total_tokens += result["s1"]["prompt_tokens"] + result["s1"]["completion_tokens"]
        s2_total_calls  += result["s2"]["llm_calls"]
        if result["s1"]["quality_score"] is not None:
            s1_quality_scores.append(result["s1"]["quality_score"])
            s2_quality_scores.append(result["s2"]["quality_score"])

    sep = "─" * 52
    print(f"\n{'='*52}")
    print("AGGREGATE (30 incidents)")
    print(f"{'='*52}")
    print(f"{'Metric':<28} {'S1 Pipeline':>10}  {'S2 ReAct':>10}")
    print(sep)
    print(f"{'Total LLM calls':<28} {s1_total_calls:>10}  {s2_total_calls:>10}")
    print(f"{'Total tokens':<28} {s1_total_tokens:>10}  {'—':>10}")
    if s1_quality_scores:
        avg_s1 = sum(s1_quality_scores) / len(s1_quality_scores)
        avg_s2 = sum(s2_quality_scores) / len(s2_quality_scores)
        print(f"{'Avg quality score':<28} {avg_s1:>10.3f}  {avg_s2:>10.3f}")
    print(sep)


# ── entrypoint ────────────────────────────────────────

if __name__ == "__main__":
    if "--all" in sys.argv:
        run_all()
    else:
        alert = (
            sys.argv[1]
            if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
            else (
                "ALERT: payment-api pod restarted 3 times in 10 minutes. "
                "Last exit code 137. Severity: P1."
            )
        )
        ground_truth = "OOM kill: payment-api exceeded 4096 MB memory limit due to connection pool leak"
        result = run_comparison(alert, ground_truth)
        print_table(result)
