# S5 — Worker Briefs (hand-built, Ollama)

Documents and validates the worker brief template:

```
objective:      what this worker must produce
output_format:  exact JSON schema the orchestrator expects
allowed_tools:  list of tool names this worker may call
scope_boundary: what this worker must NOT do
```

Runs the same alert with and without the brief. Scores output schema adherence
(does the JSON match the expected schema?) and root cause quality.


## Step Diagram

```mermaid
flowchart LR
    A([P1 Alert]) --> B[Orchestrator]
    B --> C[Worker Brief
template]
    C --> D[Log Worker]
    C --> E[Metrics Worker]
    C --> F[Trace Worker]
    D & E & F --> G([Validated briefs
+ merged report])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#2e8b6e,stroke:#fff,color:#fff
    style D fill:#4a7ab5,stroke:#fff,color:#fff
    style E fill:#4a7ab5,stroke:#fff,color:#fff
    style F fill:#4a7ab5,stroke:#fff,color:#fff
    style G fill:#666666,stroke:#fff,color:#fff
```

> Documents and validates the worker brief template — the contract between orchestrator and workers.

## Status

`TODO` — implement `worker_briefs.py`
