# S6 — Replay Suite (custom, Ollama)

Runs all 30 synthetic incidents through the full agent stack (S3 tools + S4 memory + S5 workers).
Records per-layer pass rate and outputs a Markdown report.

```
Replay Suite Results — 2026-11-17
==================================
Category       Total   Tool ✓   Answer ✓   Trajectory ✓
network           10     9/10      8/10         8/10
database          10     8/10      7/10         7/10
deployment        10     9/10      8/10         8/10
TOTAL             30    26/30     23/30        23/30
```

Fail cases are listed with the gap: expected tools vs. actual tools called.


## Step Diagram

```mermaid
flowchart LR
    A([30 incidents]) --> B[Full stack
S3+S4+S5]
    B --> C[Tool grader]
    B --> D[Answer grader]
    C & D --> E[Per-layer
pass rate]
    E --> F([Markdown report])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#b54a4a,stroke:#fff,color:#fff
    style D fill:#b54a4a,stroke:#fff,color:#fff
    style E fill:#b54a4a,stroke:#fff,color:#fff
    style F fill:#666666,stroke:#fff,color:#fff
```

> Runs all 30 synthetic incidents through the full stack and reports per-layer pass rates.

## Status

`TODO` — implement `replay.py`
