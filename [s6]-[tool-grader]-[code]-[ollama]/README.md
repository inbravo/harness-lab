# S6 — Tool Grader (code, Ollama)

Code-based grader (no LLM judge). For 10 incidents from `_shared/incident_generator.py`:

1. **Tool selection** — did the agent call the expected tools from `evidence_sources`?
2. **Argument schema** — are tool arguments valid JSON with required keys?

Outputs a Markdown table: incident ID → tool_selection pass/fail → argument pass/fail.

Uses `_shared/grader.py::tool_selection_grader` and `argument_grader`.


## Step Diagram

```mermaid
flowchart LR
    A([10 incidents]) --> B[Full agent stack]
    B --> C[Code grader]
    C --> D{Tool selection
correct?}
    D --> E{Args within
schema?}
    E --> F([Pass / Fail
per incident])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#b54a4a,stroke:#fff,color:#fff
    style D fill:#c48a1a,stroke:#fff,color:#fff
    style E fill:#c48a1a,stroke:#fff,color:#fff
    style F fill:#666666,stroke:#fff,color:#fff
```

> Code-based grader — no LLM. Checks tool selection and argument schema against expected values.

## Status

`TODO` — implement `run_grader.py`
