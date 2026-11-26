# S4 — Episodic Memory (SQLite, Ollama)

SQLite table of solved incidents. After each run the agent writes:
`(alert_hash, root_cause, fix, tools_used, quality_score, ts)`

On a new alert, retrieves the top-3 most similar past incidents by keyword match
and injects them into the system prompt as "similar past incidents".

Compares pass rate with and without memory on the 30-incident replay set.


## Step Diagram

```mermaid
flowchart LR
    A([P1 Alert]) --> B[ReAct Agent]
    B --> C{Similar incident
in memory?}
    C -- Yes --> D[(SQLite
episodic store)]
    C -- No --> E[Run investigation]
    D --> F[Retrieve past fix]
    E --> G[Write to SQLite]
    F & G --> H([Report])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#c48a1a,stroke:#fff,color:#fff
    style D fill:#7a5ba8,stroke:#fff,color:#fff
    style E fill:#4a7ab5,stroke:#fff,color:#fff
    style F fill:#7a5ba8,stroke:#fff,color:#fff
    style G fill:#7a5ba8,stroke:#fff,color:#fff
    style H fill:#666666,stroke:#fff,color:#fff
```

> SQLite stores alert_hash, root_cause, fix, tools_used, quality_score — keyword match for retrieval.

## Status

`TODO` — implement `agent.py` and `memory_store.py`
