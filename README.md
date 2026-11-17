# harness-lab

Runtime infrastructure for agentic systems — built progressively as a single project.

**Domain project:** incident investigator agent. Each step adds one piece of infrastructure until the agent can receive a P1 alert, gather evidence from logs and metrics, and return a cited root-cause report with a proposed fix and human approval gate.

**Philosophy:** build the primitives first, then adopt frameworks. Every pattern is implemented in Python against a local Ollama endpoint before a framework version appears.

**Companion repos:**
- [agent-bench](https://github.com/inbravo/agent-bench) — pattern benchmarks with CPCD metric
- [context-lab](https://github.com/inbravo/context-lab) — context engineering: contracts, ontologies, semantic layers

---

## Learning path

Follows the [KDNuggets Agentic System Design roadmap](https://www.kdnuggets.com/agentic-system-design-a-self-study-roadmap) (Bala Priya, 2026-11-16).

| Step | Concept | Examples |
|---|---|---|
| S1 | Workflow vs. Agent | fixed-pipeline · dynamic-agent · decomposition |
| S2 | Reason-Act-Observe loop | react-loop · failure-modes · loop-tracing |
| S3 | Tool design + MCP | tool-design · mcp-server · mcp-client |
| S4 | Memory | scratchpad · episodic-memory · semantic-memory |
| S5 | Multi-agent | orchestrator-worker · parallel-workers · worker-briefs |
| S6 | Evals | tool-grader · answer-grader · replay-suite |
| S7 | Deployment guardrails | budget-enforcer · approval-gate · tracing · eval-gate |

---

## Quick start

```bash
# Prerequisites
ollama pull llama3.1:8b
ollama pull qwen2.5:3b          # LLM judge (S6)
ollama pull nomic-embed-text    # embeddings (S4)

pip install -r requirements.txt

# Run the first working example
python "[s2]-[react-loop]-[hand-built]-[ollama]/agent.py"
```

---

## Folder naming

```
[s<N>]-[concept]-[framework]-[ollama]/
```

`s<N>` = roadmap step. `framework` = `hand-built` | `langgraph` | `crewai` | `mcp-python` | `dspy` | `custom` | `code`.

---

## Shared utilities

```
_shared/
├── ollama_client.py       # get_llm() factory (OpenAI-compatible)
├── incident_generator.py  # 30 synthetic incidents, deterministic seed
├── tracer.py              # JSONL tracer, span model
├── grader.py              # tool / argument / answer / trajectory graders
└── budget.py              # BudgetEnforcer context manager
```

---

## Ollama models

| Model | Used for |
|---|---|
| `llama3.1:8b` | Main agent (tool-call support required) |
| `qwen2.5:3b` | LLM judge in S6 (cheaper) |
| `nomic-embed-text` | Embeddings in S4 semantic memory |
