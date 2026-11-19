"""
grader.py — Per-layer graders for harness-lab trajectory evaluation.

Four graders at increasing granularity:
  tool_selection_grader — did the agent call the right tools?
  argument_grader       — were each tool's arguments valid JSON with required keys?
  answer_grader         — does the agent's output overlap enough with the ground truth?
  trajectory_grader     — composite: all three layers must pass.

Usage:
    from _shared.grader import trajectory_grader
    result = trajectory_grader(
        tool_calls=["search_logs", "check_metrics"],
        expected_tools=["search_logs", "check_metrics"],
        agent_output="FINAL_ANSWER: OOM kill ...",
        ground_truth_root_cause="OOM kill: payment-api exceeded 4096 MB ...",
    )
"""
# ─────────────────────────────────────────────────────
# Author   : Amit Dixit
# GitHub   : https://github.com/inbravo
# Web      : https://inbravo.github.io
# LinkedIn : https://www.linkedin.com/in/inbravo/
# ─────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
from typing import Any

# ── required argument keys per tool ──────────────────
REQUIRED_KEYS: dict[str, list[str]] = {
    "search_logs":       ["keyword"],
    "check_metrics":     ["service"],
    "get_deploy_history":["service"],
    "lookup_runbook":    ["topic"],
    "query_incident_db": ["query"],
    "draft_fix":         ["root_cause", "proposed_fix"],
}


# ── graders ───────────────────────────────────────────

def tool_selection_grader(
    tool_calls:     list[str],
    expected_tools: list[str],
) -> dict:
    """Check that every expected tool was called at least once.

    Args:
        tool_calls:     Ordered list of tool names the agent actually called.
        expected_tools: Tools listed in the incident's evidence_sources field.

    Returns:
        Dict with keys: pass, called, expected, missing.
    """
    called_set = set(tool_calls)
    missing    = [t for t in expected_tools if t not in called_set]
    return {
        "pass":     len(missing) == 0,
        "called":   tool_calls,
        "expected": expected_tools,
        "missing":  missing,
    }


def argument_grader(
    tool_name:      str,
    arguments_json: str,
    required_keys:  list[str],
) -> dict:
    """Validate that a tool call's arguments are valid JSON and contain all required keys.

    Args:
        tool_name:      Name of the tool being checked.
        arguments_json: Raw JSON string from the tool call.
        required_keys:  Keys that must be present in the parsed arguments.

    Returns:
        Dict with keys: pass, tool, args (or error), missing_keys.
    """
    try:
        args = json.loads(arguments_json)
    except json.JSONDecodeError as e:
        return {"pass": False, "error": f"invalid JSON: {e}", "tool": tool_name}
    missing = [k for k in required_keys if k not in args]
    return {
        "pass":         len(missing) == 0,
        "tool":         tool_name,
        "args":         args,
        "missing_keys": missing,
    }


def answer_grader(
    agent_output:            str,
    ground_truth_root_cause: str,
    min_keyword_overlap:     float = 0.4,
) -> dict:
    """Score answer quality by token overlap with the ground-truth root cause.

    Uses simple token overlap (no LLM required). For LLM-judge grading see
    the s6 answer_grader_llm module.

    Args:
        agent_output:            The agent's full text response.
        ground_truth_root_cause: Expected root cause string from the incident record.
        min_keyword_overlap:     Fraction of ground-truth tokens that must appear in output.

    Returns:
        Dict with keys: pass, overlap_score, matched_keywords, threshold.
    """
    def tokens(text: str) -> set[str]:
        return set(re.findall(r"\b\w+\b", text.lower()))

    gt_tokens  = tokens(ground_truth_root_cause)
    out_tokens = tokens(agent_output)
    overlap    = gt_tokens & out_tokens
    score      = len(overlap) / len(gt_tokens) if gt_tokens else 0.0
    return {
        "pass":             score >= min_keyword_overlap,
        "overlap_score":    round(score, 3),
        "matched_keywords": sorted(overlap),
        "threshold":        min_keyword_overlap,
    }


def trajectory_grader(
    tool_calls:              list[str],
    expected_tools:          list[str],
    agent_output:            str,
    ground_truth_root_cause: str,
) -> dict:
    """Composite grader: tool selection + answer quality must both pass.

    Args:
        tool_calls:              Ordered list of tool names the agent called.
        expected_tools:          Expected tools from the incident record.
        agent_output:            The agent's full text response.
        ground_truth_root_cause: Expected root cause string.

    Returns:
        Dict with keys: pass, tool_selection, answer.
    """
    tool   = tool_selection_grader(tool_calls, expected_tools)
    answer = answer_grader(agent_output, ground_truth_root_cause)
    return {
        "pass":           tool["pass"] and answer["pass"],
        "tool_selection": tool,
        "answer":         answer,
    }
