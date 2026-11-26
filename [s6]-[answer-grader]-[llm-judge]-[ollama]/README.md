# S6 — Answer Grader (LLM judge, Ollama)

Uses `qwen2.5:3b` as a cheap local LLM judge to grade final answer quality:

| Criterion | Prompt asks | Score |
|---|---|---|
| Root cause correct | Does the answer identify the root cause from ground truth? | 0–1 |
| Fix plausible | Is the proposed fix a sensible remediation? | 0–1 |
| Evidence cited | Does the answer mention which tools/evidence were used? | 0–1 |

Composite score = mean of three criteria. Pass threshold: ≥ 0.67.


## Step Diagram

```mermaid
flowchart LR
    A([P1 Alert]) --> B[Full agent stack
llama3.1:8b]
    B --> C[Final answer]
    C --> D[LLM Judge
qwen2.5:3b]
    D --> E{Criteria}
    E --> F[Root cause cited?]
    E --> G[Fix actionable?]
    E --> H[Hallucination free?]
    F & G & H --> I([Quality score 0-1])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#666666,stroke:#fff,color:#fff
    style D fill:#b54a4a,stroke:#fff,color:#fff
    style E fill:#c48a1a,stroke:#fff,color:#fff
    style F fill:#b54a4a,stroke:#fff,color:#fff
    style G fill:#b54a4a,stroke:#fff,color:#fff
    style H fill:#b54a4a,stroke:#fff,color:#fff
    style I fill:#666666,stroke:#fff,color:#fff
```

> qwen2.5:3b judges llama3.1:8b output on three criteria — cheaper judge, full agent under test.

## Status

`TODO` — implement `answer_grader_llm.py`
