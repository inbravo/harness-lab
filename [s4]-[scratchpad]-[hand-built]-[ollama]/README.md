# S4 — Scratchpad Memory (hand-built, Ollama)

In-context scratchpad: the agent appends observations to a running JSON block in the system prompt.
When the scratchpad exceeds 1000 tokens, a compaction step drops resolved observations and
keeps only open questions and confirmed facts.

Demonstrates working memory management without any external store.


## Step Diagram

```mermaid
flowchart TD
    A([P1 Alert]) --> B[ReAct Agent]
    B --> C[Scratchpad
in system prompt]
    C --> D{> 1000 tokens?}
    D -- No --> E[Append observation]
    D -- Yes --> F[Compact: drop resolved
keep open + confirmed]
    E & F --> G{Done?}
    G -- No --> B
    G -- Yes --> H([Report])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#7a5ba8,stroke:#fff,color:#fff
    style D fill:#c48a1a,stroke:#fff,color:#fff
    style E fill:#7a5ba8,stroke:#fff,color:#fff
    style F fill:#7a5ba8,stroke:#fff,color:#fff
    style G fill:#c48a1a,stroke:#fff,color:#fff
    style H fill:#666666,stroke:#fff,color:#fff
```

> In-context scratchpad compacted when it exceeds 1 000 tokens — keeps only open questions and confirmed facts.

## Status

`TODO` — implement `agent.py`
