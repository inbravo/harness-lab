# S2 — Bare ReAct Loop (hand-built, Ollama)

Implements the Reason-Act-Observe loop from scratch — no LangGraph, no CrewAI, no LangChain.

```
while not done:
    reason  → LLM decides next action via tool_choice="auto"
    act     → dispatch to synthetic tool
    observe → append tool result to messages as role=tool
```

## What it covers

- OpenAI-compatible tool-calling against local Ollama
- Bare `messages` list as the loop's only state
- `BudgetEnforcer` from `_shared/budget.py` for step and time cap
- Optional JSONL tracing via `_shared/tracer.py`
- Deterministic synthetic tools (no live services needed)

## Run

```bash
# default alert (payment-api OOM)
python agent.py

# custom alert
python agent.py "ALERT: db-primary replication lag 45 minutes. Severity: P1."

# with tracing
TRACE=1 python agent.py
```

Expected output:

```
Alert: ALERT: payment-api pod restarted 3 times in 10 minutes. Last exit code 137. Severity: P1.

[step 1] → search_logs({"keyword": "137"})
[step 2] → check_metrics({"service": "payment-api"})
[step 3] ✓ Final answer

--- Result ---
FINAL_ANSWER: payment-api was OOM-killed (exit code 137) because heap usage reached 96% of its 4096 MB limit
EVIDENCE: search_logs, check_metrics
PROPOSED_FIX: Increase payment-api memory limit to 6144 MB and investigate heap leak

Steps: 3  |  Tools called: ['search_logs', 'check_metrics']
```

## Model requirement

Requires a model with native tool-call support. `llama3.1:8b` works. `phi3` does not.

## Next steps

- **S2 failure modes** — `[s2]-[failure-modes]-[hand-built]-[ollama]`: inject each of the five failure modes (malformed args, repeated calls, early answer, runaway loop, hallucinated tool)
- **S2 loop tracing** — `[s2]-[loop-tracing]-[hand-built]-[ollama]`: span viewer for the JSONL trace
- **S3 MCP server** — replace synthetic tools with a real MCP stdio server
