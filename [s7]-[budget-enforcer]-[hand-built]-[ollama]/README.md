# S7 — Budget Enforcer (hand-built, Ollama)

Wraps any agent with `_shared/budget.py::BudgetEnforcer`. Demonstrates three caps:

| Cap | Default | On exceed |
|---|---|---|
| Step count | 25 | `BudgetExceeded: step cap reached` |
| Wall-clock time | 300 s | `BudgetExceeded: time cap reached` |
| Estimated token cost | $0.50 proxy | `BudgetExceeded: cost cap reached` |

Runs the same alert with caps set low to trigger each failure. Shows the error and partial result.


## Step Diagram

```mermaid
flowchart TD
    A([P1 Alert]) --> B[BudgetEnforcer
context manager]
    B --> C[ReAct Agent]
    C --> D{Cap hit?}
    D -- token cap --> E[Abort: token limit]
    D -- cost cap --> F[Abort: cost limit]
    D -- turn cap --> G[Abort: turn limit]
    D -- No --> H([Report])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#c48a1a,stroke:#fff,color:#fff
    style C fill:#4a7ab5,stroke:#fff,color:#fff
    style D fill:#c48a1a,stroke:#fff,color:#fff
    style E fill:#b54a4a,stroke:#fff,color:#fff
    style F fill:#b54a4a,stroke:#fff,color:#fff
    style G fill:#b54a4a,stroke:#fff,color:#fff
    style H fill:#666666,stroke:#fff,color:#fff
```

> BudgetEnforcer wraps any agent and enforces token, cost, and turn caps — raises on exceed.

## Status

`TODO` — implement `budget_demo.py`
