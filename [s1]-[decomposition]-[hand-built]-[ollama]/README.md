# S1 — Task Decomposition (hand-built, Ollama)

Given an alert, asks the LLM to decompose the investigation into subtasks and label each one
`fixed` (deterministic lookup) or `open-ended` (requires reasoning). Outputs a JSON task graph.


## Step Diagram

```mermaid
flowchart LR
    A([P1 Alert]) --> B[LLM: Decompose]
    B --> C{Task type}
    C -- fixed --> D[Deterministic lookup]
    C -- open-ended --> E[LLM reasoning]
    D & E --> F([Task graph JSON])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#c48a1a,stroke:#fff,color:#fff
    style D fill:#2e8b6e,stroke:#fff,color:#fff
    style E fill:#4a7ab5,stroke:#fff,color:#fff
    style F fill:#666666,stroke:#fff,color:#fff
```

> LLM labels each subtask as fixed or open-ended and builds a JSON task graph before execution.

## Status

`TODO` — implement `decompose.py`
