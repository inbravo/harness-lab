# S3 — Tool Design (hand-built, Ollama)

Demonstrates how tool description quality affects agent behaviour.
Runs the same alert through three versions of each tool description:

| Version | Description quality | Expected behaviour |
|---|---|---|
| v1 | Name only: `search_logs` | Agent guesses when to call it |
| v2 | What it does | Agent calls it more reliably |
| v3 | What + when + what it returns | Agent calls it correctly with right args |

Outputs a table: tool description version → tool selection accuracy over 10 incidents.


## Step Diagram

```mermaid
flowchart LR
    A([P1 Alert]) --> B[ReAct Agent]
    B --> C{Tool description
quality}
    C -- vague --> D[Tool v1
vague desc]
    C -- typed --> E[Tool v2
typed schema]
    C -- exemplified --> F[Tool v3
examples + constraints]
    D & E & F --> G([Quality score comparison])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#c48a1a,stroke:#fff,color:#fff
    style D fill:#2e8b6e,stroke:#fff,color:#fff
    style E fill:#2e8b6e,stroke:#fff,color:#fff
    style F fill:#2e8b6e,stroke:#fff,color:#fff
    style G fill:#666666,stroke:#fff,color:#fff
```

> Same alert, three versions of tool descriptions — shows how description quality drives tool-call accuracy.

## Status

`TODO` — implement `tool_design.py`
