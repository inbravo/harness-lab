"""S1 — five fixed LLM steps: classify → symptoms → runbook → draft → report. No branching, no tools."""
__author__ = "Amit Dixit"

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from _shared.budget import BudgetEnforcer
from _shared.ollama_client import DEFAULT_MODEL, get_llm
from _shared.tracer import Tracer

client = get_llm()
tracer = Tracer("s1-fixed-pipeline")

def _parse_json(text: str) -> dict:
    """Extract the first JSON object from an LLM response."""
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        return {"raw": text}
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {"raw": text[start:end]}


def _call(step_name: str, system: str, user: str, budget: BudgetEnforcer) -> tuple[dict, int, int]:
    """Single LLM call. Returns (parsed_json, prompt_tokens, completion_tokens)."""
    with tracer.span(step_name) as span:
        t0 = time.monotonic()
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        usage = response.usage
        pt = usage.prompt_tokens     if usage else 0
        ct = usage.completion_tokens if usage else 0
        budget.tick(prompt_tokens=pt, completion_tokens=ct)
        result = _parse_json(response.choices[0].message.content or "")
        span.set("step", step_name)
        span.set("prompt_tokens", pt)
        span.set("completion_tokens", ct)
        span.set("elapsed_ms", elapsed_ms)
        print(f"  [{step_name}]  {elapsed_ms} ms  |  {pt}+{ct} tokens")
        return result, pt, ct



def step_classify(alert: str, budget: BudgetEnforcer) -> dict:
    system = "You are an incident classifier. Respond only with a JSON object, no explanation."
    user = f"""Classify this incident alert.

Alert: {alert}

Return JSON with these exact keys:
{{
  "category": "network" or "database" or "deployment",
  "severity": "P1" or "P2" or "P3",
  "affected_service": "<service name extracted from the alert>",
  "confidence": <float 0.0 to 1.0>
}}"""
    return _call("classify", system, user, budget)


def step_symptoms(alert: str, classification: dict, budget: BudgetEnforcer) -> dict:
    system = "You are an incident analyst. Respond only with a JSON object, no explanation."
    user = f"""Extract symptoms from this incident alert.

Alert: {alert}
Category: {classification.get('category', 'unknown')}
Affected service: {classification.get('affected_service', 'unknown')}

Return JSON with these exact keys:
{{
  "symptoms": ["<symptom 1>", "<symptom 2>"],
  "error_code": "<exit code or error code if present, otherwise null>",
  "time_window": "<duration if mentioned, otherwise null>"
}}"""
    return _call("symptoms", system, user, budget)


def step_runbook(classification: dict, symptoms: dict, budget: BudgetEnforcer) -> dict:
    system = "You are a runbook librarian. Respond only with a JSON object, no explanation."
    user = f"""Identify the most relevant runbook procedure for this incident.

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
    return _call("runbook", system, user, budget)


def step_draft(classification: dict, symptoms: dict, runbook: dict, budget: BudgetEnforcer) -> dict:
    system = "You are an incident responder. Respond only with a JSON object, no explanation."
    user = f"""Given this incident analysis, identify the root cause and propose a fix.

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
    return _call("draft", system, user, budget)


def step_report(
    alert: str,
    classification: dict,
    symptoms: dict,
    runbook: dict,
    draft: dict,
    budget: BudgetEnforcer,
) -> str:
    system = "You are a technical writer. Write a concise incident report."
    user = f"""Write a one-paragraph incident report from this structured analysis.

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



def run(alert: str) -> dict:
    total_pt = total_ct = 0

    with BudgetEnforcer(max_steps=10) as budget:
        t_start = time.monotonic()

        c, pt, ct = step_classify(alert, budget);     total_pt += pt; total_ct += ct
        s, pt, ct = step_symptoms(alert, c, budget);  total_pt += pt; total_ct += ct
        r, pt, ct = step_runbook(c, s, budget);       total_pt += pt; total_ct += ct
        d, pt, ct = step_draft(c, s, r, budget);      total_pt += pt; total_ct += ct
        report    = step_report(alert, c, s, r, d, budget)

        elapsed = round(time.monotonic() - t_start, 2)

    return {
        "steps": 5,
        "result": report,
        "classification": c,
        "symptoms": s,
        "runbook": r,
        "draft": d,
        "total_prompt_tokens": total_pt,
        "total_completion_tokens": total_ct,
        "elapsed_s": elapsed,
    }


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
    print(f"\n--- Result ---\n{output['result']}")
    print(
        f"\nSteps: {output['steps']}  |  "
        f"Tokens: {output['total_prompt_tokens']}+{output['total_completion_tokens']}  |  "
        f"Time: {output['elapsed_s']}s"
    )
