# S5 — Orchestrator-Worker (LangGraph, Ollama)

Orchestrator receives an alert and fans out to three parallel workers:

| Worker | Job | Output |
|---|---|---|
| `triage_worker` | Classify severity and category | `{severity, category, confidence}` |
| `log_worker` | Search logs for evidence | `{log_lines, keywords_found}` |
| `runbook_worker` | Fetch relevant procedure | `{runbook_title, steps}` |

Workers run in parallel (LangGraph `Send` API). Orchestrator merges results and writes
the final `RootCauseReport` as structured JSON.


## Step Diagram

```mermaid
flowchart TD
    A([P1 Alert]) --> B[Orchestrator
LangGraph]
    B --> C[Log Worker
llama3.1:8b]
    B --> D[Metrics Worker
llama3.1:8b]
    B --> E[Trace Worker
llama3.1:8b]
    C & D & E --> F[Merge + synthesise]
    F --> G([Root-cause report])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#4a7ab5,stroke:#fff,color:#fff
    style D fill:#4a7ab5,stroke:#fff,color:#fff
    style E fill:#4a7ab5,stroke:#fff,color:#fff
    style F fill:#2e8b6e,stroke:#fff,color:#fff
    style G fill:#666666,stroke:#fff,color:#fff
```

> Orchestrator fans out to three parallel workers then merges their evidence into one report.

## Status

`TODO` — implement `agent.py`
