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
| S1 | Workflow vs. Agent | [fixed-pipeline]([s1]-[fixed-pipeline]-[hand-built]-[ollama]/) · [dynamic-agent]([s1]-[dynamic-agent]-[langgraph]-[ollama]/) · [decomposition]([s1]-[decomposition]-[hand-built]-[ollama]/) |
| S2 | Reason-Act-Observe loop | [react-loop]([s2]-[react-loop]-[hand-built]-[ollama]/) · [failure-modes]([s2]-[failure-modes]-[hand-built]-[ollama]/) · [loop-tracing]([s2]-[loop-tracing]-[hand-built]-[ollama]/) |
| S3 | Tool design + MCP | [tool-design]([s3]-[tool-design]-[hand-built]-[ollama]/) · [mcp-server]([s3]-[mcp-server]-[mcp-python]-[ollama]/) · [mcp-client]([s3]-[mcp-client]-[langgraph]-[ollama]/) |
| S4 | Memory | [scratchpad]([s4]-[scratchpad]-[hand-built]-[ollama]/) · [episodic-memory]([s4]-[episodic-memory]-[sqlite]-[ollama]/) · [semantic-memory]([s4]-[semantic-memory]-[chromadb]-[ollama]/) |
| S5 | Multi-agent | [orchestrator-worker]([s5]-[orchestrator-worker]-[langgraph]-[ollama]/) · [parallel-workers]([s5]-[parallel-workers]-[crewai]-[ollama]/) · [worker-briefs]([s5]-[worker-briefs]-[hand-built]-[ollama]/) |
| S6 | Evals | [tool-grader]([s6]-[tool-grader]-[code]-[ollama]/) · [answer-grader]([s6]-[answer-grader]-[llm-judge]-[ollama]/) · [replay-suite]([s6]-[replay-suite]-[custom]-[ollama]/) |
| S7 | Deployment guardrails | [budget-enforcer]([s7]-[budget-enforcer]-[hand-built]-[ollama]/) · [approval-gate]([s7]-[approval-gate]-[hand-built]-[ollama]/) · [tracing]([s7]-[tracing]-[jsonl]-[ollama]/) · [eval-gate]([s7]-[eval-gate]-[ci]-[ollama]/) |

---

## Environment setup

**Prerequisites:** Python 3.11+, [Ollama](https://ollama.com) running locally.

```bash
# 1. Clone
git clone https://github.com/inbravo/harness-lab.git
cd harness-lab

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull Ollama models
ollama pull llama3.1:8b            # main agent (tool-call support required)
ollama pull qwen2.5:3b             # LLM judge (S6)
ollama pull nomic-embed-text       # embeddings (S4)

# 5. Run the first working example
python "[s1]-[fixed-pipeline]-[hand-built]-[ollama]/pipeline.py"
```

> **Note:** activate the venv (`source .venv/bin/activate`) at the start of every session.
> Deactivate with `deactivate` when done.

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
