# S1 — Fixed Pipeline (hand-built, Ollama)

Five-step deterministic pipeline: alert → classify → lookup runbook → draft response → log.
No branching. No tool calls. Each step is a single LLM prompt with a fixed template.

Pairs with `[s1]-[dynamic-agent]` for a side-by-side comparison of fixed vs. open-ended routing.

## Status

`TODO` — implement `pipeline.py`
