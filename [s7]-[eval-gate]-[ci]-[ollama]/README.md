# S7 — Eval Gate in CI (GitHub Actions, Ollama)

GitHub Actions workflow that runs the 30-incident replay suite on every PR.
Fails the PR if quality regresses:

| Check | Threshold |
|---|---|
| Trajectory pass rate | < 75% fails |
| Tool selection pass rate | < 85% fails |
| Any category drop > 10% vs. baseline | fails |

Requires a self-hosted runner with Ollama installed, or a container with Ollama sidecar.


## Step Diagram

```mermaid
flowchart LR
    A([PR opened]) --> B[GitHub Actions]
    B --> C[Start Ollama
llama3.1:8b]
    C --> D[30-incident
replay suite]
    D --> E{Quality >= baseline?}
    E -- Yes --> F([PR passes])
    E -- No --> G([PR blocked])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#c48a1a,stroke:#fff,color:#fff
    style C fill:#2e8b6e,stroke:#fff,color:#fff
    style D fill:#b54a4a,stroke:#fff,color:#fff
    style E fill:#c48a1a,stroke:#fff,color:#fff
    style F fill:#666666,stroke:#fff,color:#fff
    style G fill:#b54a4a,stroke:#fff,color:#fff
```

> GitHub Actions runs the replay suite on every PR — fails the merge if quality regresses.

## Files

- `.github/workflows/eval_gate.yml` — workflow definition
- `run_eval_gate.py` — entry point, writes `eval_results.json`
- `check_thresholds.py` — reads `eval_results.json`, exits non-zero on regression

## Status

`TODO` — implement workflow and scripts
