"""
pipeline.py — S1: five fixed LLM steps for incident investigation (hand-built, Ollama).

Demonstrates a fixed pipeline where each stage is a hard-coded LLM call with no
branching or tool use. Steps run in order: classify → symptoms → runbook →
draft → report. Compare with S2 (ReAct loop) using compare.py.

Pattern  : Fixed Pipeline
Step     : S1
Framework: hand-built (no LangChain / CrewAI)
Backend  : Ollama (local)

Usage:
    python pipeline.py
    python pipeline.py "ALERT: db-primary replication lag 45 minutes. Severity: P1."
"""
# ─────────────────────────────────────────────────────
# Author   : Amit Dixit
# GitHub   : https://github.com/inbravo
# Web      : https://inbravo.github.io
# LinkedIn : https://www.linkedin.com/in/inbravo/
# ─────────────────────────────────────────────────────

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

# ── path setup ────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_shared"))

# ── shared setup ──────────────────────────────────────
import logging_config
logging_config.setup()

from budget        import BudgetEnforcer
from ollama_client import DEFAULT_MODEL, get_llm
from tracer        import Tracer

# ── logging ───────────────────────────────────────────
log = logging.getLogger("harness.s1.pipeline")

# ── module-level singletons ───────────────────────────
client = get_llm()
tracer = Tracer("s1-fixed-pipeline")


# ── internal helpers ──────────────────────────────────

def _parse_json(text: str) -> dict:
    """Extract the first JSON object from an LLM response string.

    Args:
        text: Raw LLM response content.

    Returns:
        Parsed dict, or {"raw": text} if no valid JSON object is found.
    """
    text  = text.strip()
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        return {"raw": text}
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {"raw": text[start:end]}


def _call(
    step_name: str,
    system:    str,
    user:      str,
    budget:    BudgetEnforcer,
) -> tuple[dict, int, int]:
    """Execute one LLM call, record a trace span, and tick the budget.

    Args:
        step_name: Label for this step (used in traces and console output).
        system:    System prompt for the LLM.
        user:      User-turn prompt for the LLM.
        budget:    Active BudgetEnforcer; raises BudgetExceeded if caps are hit.

    Returns:
        Tuple of (parsed_response_dict, prompt_tokens, completion_tokens).
    """
    with tracer.span(step_name) as span:
        t0       = time.monotonic()
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        usage      = response.usage
        pt         = usage.prompt_tokens     if usage else 0
        ct         = usage.completion_tokens if usage else 0
        budget.tick(prompt_tokens=pt, completion_tokens=ct)
        result = _parse_json(response.choices[0].message.content or "")
        span.set("step",             step_name)
        span.set("prompt_tokens",    pt)
        span.set("completion_tokens", ct)
        span.set("elapsed_ms",       elapsed_ms)
        log.info("%-12s  %d ms  |  %d+%d tokens", step_name, elapsed_ms, pt, ct)
        return result, pt, ct


# ── pipeline steps ────────────────────────────────────

def step_classify(alert: str, budget: BudgetEnforcer) -> dict:
    """Classify the incident category, severity, and affected service.

    Args:
        alert:  Raw alert string.
        budget: Active BudgetEnforcer.

    Returns:
        Dict with keys: category, severity, affected_service, confidence.
    """
    system = "You are an incident classifier. Respond only with a JSON object, no explanation."
    user   = f"""Classify this incident alert.

Alert: {alert}

Return JSON with these exact keys:
{{
  "category": "network" or "database" or "deployment",
  "severity": "P1" or "P2" or "P3",
  "affected_service": "<service name extracted from the alert>",
  "confidence": <float 0.0 to 1.0>
}}"""
    result, pt, ct = _call("classify", system, user, budget)
    return result


def step_symptoms(alert: str, classification: dict, budget: BudgetEnforcer) -> dict:
    """Extract symptoms, error codes, and time window from the alert.

    Args:
        alert:          Raw alert string.
        classification: Output of step_classify.
        budget:         Active BudgetEnforcer.

    Returns:
        Dict with keys: symptoms, error_code, time_window.
    """
    system = "You are an incident analyst. Respond only with a JSON object, no explanation."
    user   = f"""Extract symptoms from this incident alert.

Alert: {alert}
Category: {classification.get('category', 'unknown')}
Affected service: {classification.get('affected_service', 'unknown')}

Return JSON with these exact keys:
{{
  "symptoms": ["<symptom 1>", "<symptom 2>"],
  "error_code": "<exit code or error code if present, otherwise null>",
  "time_window": "<duration if mentioned, otherwise null>"
}}"""
    result, pt, ct = _call("symptoms", system, user, budget)
    return result


def step_runbook(classification: dict, symptoms: dict, budget: BudgetEnforcer) -> dict:
    """Identify the most relevant runbook procedure for this incident.

    Args:
        classification: Output of step_classify.
        symptoms:       Output of step_symptoms.
        budget:         Active BudgetEnforcer.

    Returns:
        Dict with keys: runbook_title, investigation_steps, escalation_path.
    """
    system = "You are a runbook librarian. Respond only with a JSON object, no explanation."
    user   = f"""Identify the most relevant runbook procedure for this incident.

Category: {classification.get('category')}
Affected service: {classification.get('affected_service')}
Symptoms: {json.dumps(symptoms.get('symptoms', []))}
Error code: {symptoms.get('error_code')}

Return JSON with these exact keys:
{{
  "runbook_title": "<short descriptive title>",
  "investigation_steps": ["<step 1>", "<step 2>", "<step 3>"],
  "escalation_path": "<team or on-call rotation to page>"
}}"""
    result, pt, ct = _call("runbook", system, user, budget)
    return result


def step_draft(
    classification: dict,
    symptoms:       dict,
    runbook:        dict,
    budget:         BudgetEnforcer,
) -> dict:
    """Identify the root cause and propose a fix from the aggregated analysis.

    Args:
        classification: Output of step_classify.
        symptoms:       Output of step_symptoms.
        runbook:        Output of step_runbook.
        budget:         Active BudgetEnforcer.

    Returns:
        Dict with keys: root_cause, proposed_fix, escalation_needed, confidence.
    """
    system = "You are an incident responder. Respond only with a JSON object, no explanation."
    user   = f"""Given this incident analysis, identify the root cause and propose a fix.

Classification: {json.dumps(classification)}
Symptoms: {json.dumps(symptoms)}
Runbook procedure: {json.dumps(runbook)}

Return JSON with these exact keys:
{{
  "root_cause": "<one-sentence root cause>",
  "proposed_fix": "<one-sentence remediation action>",
  "escalation_needed": true or false,
  "confidence": <float 0.0 to 1.0>
}}"""
    result, pt, ct = _call("draft", system, user, budget)
    return result


def step_report(
    alert:          str,
    classification: dict,
    symptoms:       dict,
    runbook:        dict,
    draft:          dict,
    budget:         BudgetEnforcer,
) -> str:
    """Write the final incident report in FINAL_ANSWER format.

    Args:
        alert:          Raw alert string.
        classification: Output of step_classify.
        symptoms:       Output of step_symptoms.
        runbook:        Output of step_runbook.
        draft:          Output of step_draft.
        budget:         Active BudgetEnforcer.

    Returns:
        Formatted report string starting with "FINAL_ANSWER:".
    """
    system = "You are a technical writer. Write a concise incident report."
    user   = f"""Write a one-paragraph incident report from this structured analysis.

Alert: {alert}
Root cause: {draft.get('root_cause')}
Proposed fix: {draft.get('proposed_fix')}
Escalation needed: {draft.get('escalation_needed')}
Runbook used: {runbook.get('runbook_title')}

Format:
FINAL_ANSWER: <root cause>
EVIDENCE: classification, symptom-analysis, runbook-lookup, draft-response
PROPOSED_FIX: <fix>"""
    result, pt, ct = _call("report", system, user, budget)
    raw = result.get("raw", "")
    if not raw:
        raw = (
            f"FINAL_ANSWER: {draft.get('root_cause', 'unknown')}\n"
            f"EVIDENCE: classification, symptom-analysis, runbook-lookup, draft-response\n"
            f"PROPOSED_FIX: {draft.get('proposed_fix', 'unknown')}"
        )
    return raw


# ── public API ────────────────────────────────────────

def run(alert: str) -> dict:
    """Run the full five-step pipeline for a single incident alert.

    Args:
        alert: Raw alert string (e.g. from incident_generator.get_all()).

    Returns:
        Dict with keys: steps, result, classification, symptoms, runbook, draft,
        total_prompt_tokens, total_completion_tokens, elapsed_s.
    """
    log.info("─── s1 / fixed-pipeline starting ───")
    log.info("alert: %s", alert)

    total_pt = total_ct = 0

    with BudgetEnforcer(max_steps=10) as budget:
        t_start = time.monotonic()

        c, pt, ct = step_classify(alert, budget);     total_pt += pt; total_ct += ct
        s, pt, ct = step_symptoms(alert, c, budget);  total_pt += pt; total_ct += ct
        r, pt, ct = step_runbook(c, s, budget);       total_pt += pt; total_ct += ct
        d, pt, ct = step_draft(c, s, r, budget);      total_pt += pt; total_ct += ct
        report    = step_report(alert, c, s, r, d, budget)

        elapsed = round(time.monotonic() - t_start, 2)

    log.info("─── s1 / fixed-pipeline done: %ss  %d+%d tokens ───", elapsed, total_pt, total_ct)
    return {
        "steps":                   5,
        "result":                  report,
        "classification":          c,
        "symptoms":                s,
        "runbook":                 r,
        "draft":                   d,
        "total_prompt_tokens":     total_pt,
        "total_completion_tokens": total_ct,
        "elapsed_s":               elapsed,
    }


# ── entrypoint ────────────────────────────────────────

if __name__ == "__main__":
    alert = (
        sys.argv[1]
        if len(sys.argv) > 1
        else (
            "ALERT: payment-api pod restarted 3 times in 10 minutes. "
            "Last exit code 137. Severity: P1."
        )
    )
    print(f"Alert: {alert}\n")
    output = run(alert)
    print(f"\n── result ──────────────────────────────────────")
    print(output["result"])
    print(
        f"\nSteps: {output['steps']}  |  "
        f"Tokens: {output['total_prompt_tokens']}+{output['total_completion_tokens']}  |  "
        f"Time: {output['elapsed_s']}s"
    )
