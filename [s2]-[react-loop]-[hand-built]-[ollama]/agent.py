"""
S2 — Bare ReAct loop, no framework.

while not done:
    reason  → LLM decides what to do next
    act     → pick and call a tool
    observe → append tool result to messages

Domain: incident investigator (see _shared/incident_generator.py)
Model:  llama3.1:8b via Ollama (tool-call support required)

Usage:
    python agent.py
    python agent.py "ALERT: payment-api pod restarted 3 times. Exit code 137. Severity: P1."
    TRACE=1 python agent.py      # emit JSONL trace to traces/
"""
import json
import sys
from pathlib import Path

# allow imports from _shared/ without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from _shared.budget import BudgetEnforcer, BudgetExceeded
from _shared.ollama_client import DEFAULT_MODEL, get_llm
from _shared.tracer import Tracer

client = get_llm()
tracer = Tracer("s2-react-loop")

# --- Tool definitions (OpenAI function-calling schema) ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_logs",
            "description": (
                "Search the incident log store for log lines matching a keyword. "
                "Use when you need raw log evidence for an alert. "
                "Returns a list of matching log lines with timestamps and severity."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword or error code to search for in logs",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max log lines to return",
                        "default": 10,
                    },
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_metrics",
            "description": (
                "Retrieve recent metric values for a named service or component. "
                "Use to check whether CPU, memory, latency, or error rate crossed a threshold "
                "around the alert time. "
                "Returns a dict of metric_name → value for the last 5 minutes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service name, e.g. 'payment-api' or 'db-primary'",
                    },
                },
                "required": ["service"],
            },
        },
    },
]

# --- Synthetic tool execution ---
def search_logs(keyword: str, limit: int = 10) -> list[dict]:
    store = {
        "OOM": [
            {"ts": "2026-11-17T10:01:22Z", "sev": "FATAL", "msg": "OOM Kill: process payment-api (4821) score 892"},
            {"ts": "2026-11-17T10:01:20Z", "sev": "ERROR", "msg": "GC overhead limit exceeded in payment-api"},
            {"ts": "2026-11-17T10:01:18Z", "sev": "WARN",  "msg": "Heap usage 98% in payment-api"},
        ],
        "137": [
            {"ts": "2026-11-17T10:01:22Z", "sev": "FATAL", "msg": "Process killed by SIGKILL (exit code 137) — OOM"},
        ],
        "timeout": [
            {"ts": "2026-11-17T10:01:15Z", "sev": "WARN", "msg": "DB query timeout after 30s on payment-api"},
            {"ts": "2026-11-17T10:01:10Z", "sev": "WARN", "msg": "Connection pool exhausted for db-primary"},
        ],
        "connection": [
            {"ts": "2026-11-17T10:01:10Z", "sev": "WARN", "msg": "Connection pool exhausted (498/500) for db-primary"},
        ],
    }
    results: list[dict] = []
    for key, lines in store.items():
        if keyword.lower() in key.lower() or keyword.lower() in " ".join(l["msg"] for l in lines).lower():
            results.extend(lines)
    seen = set()
    deduped = []
    for r in results:
        if r["msg"] not in seen:
            seen.add(r["msg"])
            deduped.append(r)
    return deduped[:limit] if deduped else [{"msg": f"No logs found for keyword '{keyword}'"}]


def check_metrics(service: str) -> dict:
    store = {
        "payment-api": {
            "cpu_pct": 97.3,
            "mem_used_mb": 3940,
            "mem_limit_mb": 4096,
            "mem_pct": 96.2,
            "error_rate_pct": 42.1,
            "p99_latency_ms": 8820,
            "restarts_last_10m": 3,
        },
        "db-primary": {
            "cpu_pct": 34.1,
            "mem_used_mb": 2100,
            "connections_active": 498,
            "connections_max": 500,
            "replication_lag_ms": 12,
        },
    }
    return store.get(service, {"error": f"No metrics found for service '{service}'"})


TOOL_DISPATCH = {
    "search_logs": lambda args: search_logs(**args),
    "check_metrics": lambda args: check_metrics(**args),
}

# --- System prompt ---
SYSTEM = """\
You are an incident investigator. When given an alert, use the available tools to gather evidence, \
then identify the root cause and propose a fix.

When you have enough evidence, respond with exactly this format:

FINAL_ANSWER: <root cause in one sentence>
EVIDENCE: <comma-separated list of tool names you used>
PROPOSED_FIX: <one-sentence remediation>

Rules:
- Do not guess before gathering evidence.
- Call search_logs before check_metrics if you see an exit code or error code in the alert.
- Stop as soon as you have the root cause and fix. Do not over-investigate.
"""


def run(alert: str, max_steps: int = 25) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Investigate this alert: {alert}"},
    ]
    tools_called: list[str] = []

    with BudgetEnforcer(max_steps=max_steps) as budget:
        for step in range(max_steps):
            with tracer.span(f"step_{step}") as span:
                try:
                    response = client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=messages,
                        tools=TOOLS,
                        tool_choice="auto",
                    )
                except Exception as e:
                    return {"error": str(e), "steps": step}

                usage = response.usage
                budget.tick(
                    prompt_tokens=usage.prompt_tokens if usage else 0,
                    completion_tokens=usage.completion_tokens if usage else 0,
                )
                msg = response.choices[0].message

                # Final answer in content
                if msg.content and "FINAL_ANSWER:" in msg.content:
                    span.set("type", "final_answer")
                    print(f"\n[step {step + 1}] ✓ Final answer")
                    return {
                        "steps": step + 1,
                        "result": msg.content,
                        "tools_called": tools_called,
                        "budget": budget.summary,
                    }

                # Tool calls
                if msg.tool_calls:
                    messages.append(msg)
                    for tc in msg.tool_calls:
                        fn = tc.function.name
                        args = json.loads(tc.function.arguments)
                        tools_called.append(fn)
                        print(f"[step {step + 1}] → {fn}({json.dumps(args)})")
                        span.set("tool", fn)
                        span.set("args", args)
                        result = TOOL_DISPATCH[fn](args)
                        span.set("result_len", len(str(result)))
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(result),
                        })
                elif msg.content:
                    # Reasoning step (no tool call, no final answer)
                    print(f"[step {step + 1}] reasoning: {msg.content[:100]}…")
                    span.set("type", "reasoning")
                    messages.append({"role": "assistant", "content": msg.content})
                else:
                    break

                try:
                    budget.tick()
                except BudgetExceeded as e:
                    return {"error": str(e), "steps": step + 1, "budget": budget.summary}

    return {
        "error": "max steps reached without final answer",
        "steps": max_steps,
        "tools_called": tools_called,
        "budget": budget.summary,
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

    if "error" in output:
        print(f"\n✗ {output['error']}")
    else:
        print(f"\n--- Result ---\n{output['result']}")

    print(f"\nSteps: {output.get('steps')}  |  Tools called: {output.get('tools_called', [])}")
    if "budget" in output:
        b = output["budget"]
        print(f"Budget: {b['elapsed_s']}s  |  ~${b['estimated_cost_usd']:.6f}")
