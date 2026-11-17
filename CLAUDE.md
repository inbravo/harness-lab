# harness-lab — Claude Instructions

## Always read first

- `README.md` — repo structure and learning path
- `_shared/` — shared utilities (do not duplicate logic from here)

## Naming convention

```
[s<N>]-[concept]-[framework]-[ollama]/
```

Where `framework` is one of: `hand-built`, `langgraph`, `crewai`, `mcp-python`, `dspy`, `custom`, `code`.

## Code rules

- Python only. No TypeScript.
- Hand-built examples must import nothing from LangChain, CrewAI, or similar — only `openai` (Ollama-compatible client), `sqlite3`, stdlib.
- All agents must respect `MAX_STEPS = 25` from `_shared/budget.py`.
- All agents must emit JSONL traces via `_shared/tracer.py` when `TRACE=1` env var is set.
- Synthetic incidents come from `_shared/incident_generator.py` — do not hardcode incidents in example files.

## Domain

The domain project is an **incident investigator** agent.
- Tools available: `search_logs`, `check_metrics`, `get_deploy_history`, `lookup_runbook`, `query_incident_db`, `draft_fix`
- Alert format: `"ALERT: <service> <symptom>. Last exit code <N>. Severity: <P1|P2|P3>."`
- Expected output format: `FINAL_ANSWER: <root cause>` + `EVIDENCE: <sources>` + `PROPOSED_FIX: <remediation>`

## Git

- Commit messages: imperative, present tense
- Never commit `.env`, `*.db`, `*.log`, `traces/`
