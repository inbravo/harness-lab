# S5 — Parallel Workers (CrewAI, Ollama)

Same three workers as `[s5]-[orchestrator-worker]` implemented as a CrewAI Crew
with `Process.hierarchical`. Benchmarks latency vs. sequential CrewAI execution.


## Step Diagram

```mermaid
flowchart TD
    A([P1 Alert]) --> B[CrewAI Crew
Process.hierarchical]
    B --> C[Log Agent]
    B --> D[Metrics Agent]
    B --> E[Trace Agent]
    C & D & E --> F([Root-cause report])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#4a7ab5,stroke:#fff,color:#fff
    style D fill:#4a7ab5,stroke:#fff,color:#fff
    style E fill:#4a7ab5,stroke:#fff,color:#fff
    style F fill:#666666,stroke:#fff,color:#fff
```

> Same three workers as orchestrator-worker, implemented as a CrewAI hierarchical Crew.

## Status

`TODO` — implement `crew.py`
