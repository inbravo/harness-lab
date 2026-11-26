# S1 — Dynamic Agent (LangGraph, Ollama)

The same five steps as `[s1]-[fixed-pipeline]` but as a LangGraph agent with open-ended routing.
Outputs a side-by-side comparison: steps taken, token count, and quality score for both approaches.


## Step Diagram

```mermaid
flowchart LR
    A([P1 Alert]) --> B[LangGraph Agent]
    B --> C{Next step?}
    C -- classify --> D[Classify]
    C -- gather --> E[Gather Evidence]
    C -- analyse --> F[Analyse]
    C -- fix --> G[Propose Fix]
    C -- done --> H([Report])
    D & E & F & G --> C

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#c48a1a,stroke:#fff,color:#fff
    style D fill:#4a7ab5,stroke:#fff,color:#fff
    style E fill:#4a7ab5,stroke:#fff,color:#fff
    style F fill:#4a7ab5,stroke:#fff,color:#fff
    style G fill:#4a7ab5,stroke:#fff,color:#fff
    style H fill:#666666,stroke:#fff,color:#fff
```

> Same five steps as fixed-pipeline but routed dynamically by LangGraph — the agent decides the order.

## Status

`TODO` — implement `agent.py`
