"""
Per-layer graders for incident investigator agent outputs.

Graders:
  tool_selection_grader  — did the agent call the expected tools?
  argument_grader        — are tool arguments valid JSON with required keys?
  answer_grader          — does the final answer contain the root cause keywords?
  trajectory_grader      — combine all three into a single pass/fail
"""
import json
import re
from typing import Any


def tool_selection_grader(
    tool_calls: list[str],
    expected_tools: list[str],
) -> dict:
    """
    Returns pass=True if all expected tools were called at least once.
    tool_calls: list of tool names actually called (in order)
    expected_tools: list from incident_generator evidence_sources
    """
    called_set = set(tool_calls)
    missing = [t for t in expected_tools if t not in called_set]
    return {
        "pass": len(missing) == 0,
        "called": tool_calls,
        "expected": expected_tools,
        "missing": missing,
    }


def argument_grader(
    tool_name: str,
    arguments_json: str,
    required_keys: list[str],
) -> dict:
    """
    Returns pass=True if arguments_json is valid JSON and contains all required_keys.
    """
    try:
        args = json.loads(arguments_json)
    except json.JSONDecodeError as e:
        return {"pass": False, "error": f"invalid JSON: {e}", "tool": tool_name}
    missing = [k for k in required_keys if k not in args]
    return {
        "pass": len(missing) == 0,
        "tool": tool_name,
        "args": args,
        "missing_keys": missing,
    }


REQUIRED_KEYS: dict[str, list[str]] = {
    "search_logs": ["keyword"],
    "check_metrics": ["service"],
    "get_deploy_history": ["service"],
    "lookup_runbook": ["topic"],
    "query_incident_db": ["query"],
    "draft_fix": ["root_cause", "proposed_fix"],
}


def answer_grader(
    agent_output: str,
    ground_truth_root_cause: str,
    min_keyword_overlap: float = 0.4,
) -> dict:
    """
    Returns pass=True if the agent output contains enough keywords from the
    ground truth root cause. Uses simple token overlap (no LLM required).
    For LLM judge grading see s6/answer_grader_llm.py.
    """
    def tokens(text: str) -> set[str]:
        return set(re.findall(r"\b\w+\b", text.lower()))

    gt_tokens = tokens(ground_truth_root_cause)
    out_tokens = tokens(agent_output)
    overlap = gt_tokens & out_tokens
    score = len(overlap) / len(gt_tokens) if gt_tokens else 0.0
    return {
        "pass": score >= min_keyword_overlap,
        "overlap_score": round(score, 3),
        "matched_keywords": sorted(overlap),
        "threshold": min_keyword_overlap,
    }


def trajectory_grader(
    tool_calls: list[str],
    expected_tools: list[str],
    agent_output: str,
    ground_truth_root_cause: str,
) -> dict:
    """Composite grader. All three layers must pass for trajectory to pass."""
    tool = tool_selection_grader(tool_calls, expected_tools)
    answer = answer_grader(agent_output, ground_truth_root_cause)
    passed = tool["pass"] and answer["pass"]
    return {
        "pass": passed,
        "tool_selection": tool,
        "answer": answer,
    }
