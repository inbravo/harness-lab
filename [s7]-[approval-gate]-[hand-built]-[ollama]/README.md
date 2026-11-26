# S7 — Approval Gate (hand-built, Ollama)

Separates tools into read-only and write categories. Before any write tool call,
the loop pauses and emits an approval request to stdout. Resumes on `yes`, aborts on `no`.

| Category | Tools | Gate |
|---|---|---|
| Read-only | `search_logs`, `check_metrics`, `get_deploy_history`, `lookup_runbook`, `query_incident_db` | None — auto-approved |
| Write | `draft_fix` | Requires human `yes` before execution |

Demonstrates HITL (Human-in-the-loop) for the write path only.


## Step Diagram

```mermaid
flowchart TD
    A([P1 Alert]) --> B[ReAct Agent]
    B --> C{Write tool
call?}
    C -- No read tool --> D[Execute]
    C -- Yes --> E[Approval request
stdout]
    E --> F{Human decision}
    F -- yes --> D
    F -- no --> G[Abort tool call]
    D --> H{Done?}
    G --> H
    H -- No --> B
    H -- Yes --> I([Report])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#c48a1a,stroke:#fff,color:#fff
    style D fill:#2e8b6e,stroke:#fff,color:#fff
    style E fill:#c48a1a,stroke:#fff,color:#fff
    style F fill:#c48a1a,stroke:#fff,color:#fff
    style G fill:#b54a4a,stroke:#fff,color:#fff
    style H fill:#c48a1a,stroke:#fff,color:#fff
    style I fill:#666666,stroke:#fff,color:#fff
```

> Loop pauses before any write-category tool call and waits for human yes / no on stdin.

## Status

`TODO` — implement `agent.py`
