# S2 — Failure Modes (hand-built, Ollama)

Five deliberate failure injections into the ReAct loop from `[s2]-[react-loop]`, each with a first fix:

| # | Failure | Symptom | Fix |
|---|---|---|---|
| 1 | Malformed arguments | JSON parse error on tool call | Catch + retry with schema hint in next message |
| 2 | Repeated identical calls | Same tool + same args twice | Detect repeat, inject "you already called this" message |
| 3 | Early final answer | FINAL_ANSWER before any tool call | Require at least one tool call before accepting final answer |
| 4 | Runaway loop | No progress after 5 steps | Force a summary prompt if no FINAL_ANSWER after N steps |
| 5 | Hallucinated tool name | LLM invents a tool not in TOOLS | Reject unknown tool name, return error observation |


## Step Diagram

```mermaid
flowchart TD
    A([P1 Alert]) --> B[ReAct Loop]
    B --> C{Failure injected?}
    C -- hallucinated tool --> D[Fix: tool validation]
    C -- infinite loop --> E[Fix: max-turn guard]
    C -- missing arg --> F[Fix: schema check]
    C -- bad JSON --> G[Fix: retry + repair]
    C -- context overflow --> H[Fix: truncation]
    D & E & F & G & H --> I([Recovered output])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#c48a1a,stroke:#fff,color:#fff
    style D fill:#b54a4a,stroke:#fff,color:#fff
    style E fill:#b54a4a,stroke:#fff,color:#fff
    style F fill:#b54a4a,stroke:#fff,color:#fff
    style G fill:#b54a4a,stroke:#fff,color:#fff
    style H fill:#b54a4a,stroke:#fff,color:#fff
    style I fill:#666666,stroke:#fff,color:#fff
```

> Five deliberate failure injections into the ReAct loop, each with a targeted fix.

## Status

`TODO` — implement `failure_modes.py`
