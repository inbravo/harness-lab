# S4 — Semantic Memory (ChromaDB, Ollama)

Same SQLite episodic memory as `[s4]-[episodic-memory]` but retrieval uses
ChromaDB + `nomic-embed-text` (Ollama) instead of keyword match.

Runs the same 30-incident replay and compares retrieval quality:
keyword recall vs. embedding recall vs. no memory baseline.


## Step Diagram

```mermaid
flowchart LR
    A([P1 Alert]) --> B[ReAct Agent]
    B --> C[nomic-embed-text
Ollama]
    C --> D[(ChromaDB
vector store)]
    D --> E{Similarity
threshold?}
    E -- hit --> F[Retrieve past fix
from SQLite]
    E -- miss --> G[Run investigation]
    F & G --> H([Report])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#2e8b6e,stroke:#fff,color:#fff
    style D fill:#7a5ba8,stroke:#fff,color:#fff
    style E fill:#c48a1a,stroke:#fff,color:#fff
    style F fill:#7a5ba8,stroke:#fff,color:#fff
    style G fill:#4a7ab5,stroke:#fff,color:#fff
    style H fill:#666666,stroke:#fff,color:#fff
```

> ChromaDB + nomic-embed-text replaces keyword match — retrieval is now semantic similarity.

## Status

`TODO` — implement `agent.py` and `semantic_store.py`
