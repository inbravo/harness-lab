#!/usr/bin/env bash
# create-github-issues.sh — create dev + stress-test issues for every harness-lab example
#
# Prerequisites: gh auth login  (run once if not already authenticated)
# Usage:         bash create-github-issues.sh

set -euo pipefail

REPO="inbravo/harness-lab"
ASSIGNEE="inbravo"

echo "==> Creating labels..."
gh label create "enhancement" --repo "$REPO" --color "84b6eb" \
  --description "New feature or example implementation" 2>/dev/null || true
gh label create "stress-test" --repo "$REPO" --color "e4e669" \
  --description "Stress testing over all 30 incidents with budget and quality checks" 2>/dev/null || true

echo "==> Creating milestones..."
for STEP in "S1: Workflow vs Agent" "S2: Reason-Act-Observe Loop" \
            "S3: Tool Design and MCP" "S4: Memory" "S5: Multi-Agent" \
            "S6: Evals" "S7: Deployment Guardrails"; do
  gh api repos/"$REPO"/milestones --method POST \
    --field title="$STEP" 2>/dev/null || true
done

# Helper — creates one dev issue and one stress-test issue
# Args: step label (e.g. S1), example slug, one-line description, stress-test detail
issue_pair() {
  local STEP="$1" SLUG="$2" DESC="$3" STRESS="$4"
  local FOLDER="[$(echo "$SLUG" | cut -d- -f1)]-[$( echo "$SLUG" | cut -d- -f2-)]-[hand-built]-[ollama]"

  echo "--> [$STEP] $SLUG — dev"
  gh issue create \
    --repo      "$REPO" \
    --assignee  "$ASSIGNEE" \
    --label     "enhancement" \
    --title     "[$STEP] Implement: $SLUG" \
    --body      "$DESC

Folder: \`[$(echo "$SLUG" | sed 's/-.*//')]- ... \`
Follows harness-lab CLAUDE.md conventions: python-pptx, logging_config, box author block, Args/Returns docstrings."

  echo "--> [$STEP] $SLUG — stress-test"
  gh issue create \
    --repo      "$REPO" \
    --assignee  "$ASSIGNEE" \
    --label     "stress-test" \
    --title     "[$STEP] Stress test: $SLUG" \
    --body      "$STRESS

Folder: \`[$(echo "$SLUG" | sed 's/-.*//')]- ... \`
Run with: \`TRACE=1 python <entry>.py\` and validate BudgetEnforcer limits, grader scores, and no regressions across all 30 incidents."
}

echo ""
echo "==> S1 — Workflow vs Agent"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S1] Implement: fixed-pipeline" \
  --body "Five sequential LLM calls (classify → symptoms → runbook → draft → report) with no branching. Includes compare.py harness for S1 vs S2 side-by-side metrics.
Folder: \`[s1]-[fixed-pipeline]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S1] Stress test: fixed-pipeline" \
  --body "Run \`python compare.py --all\` over all 30 incidents. Assert: 5 LLM calls per incident, BudgetEnforcer never triggered, quality scores logged, elapsed < 30 s per incident.
Folder: \`[s1]-[fixed-pipeline]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S1] Implement: dynamic-agent" \
  --body "Same five investigation steps as fixed-pipeline but expressed as a LangGraph agent with open-ended routing — the LLM decides which step to run next.
Folder: \`[s1]-[dynamic-agent]-[langgraph]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S1] Stress test: dynamic-agent" \
  --body "Run over all 30 incidents. Validate routing decisions are consistent, no infinite loops, BudgetEnforcer cap never exceeded, quality score >= fixed-pipeline baseline.
Folder: \`[s1]-[dynamic-agent]-[langgraph]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S1] Implement: decomposition" \
  --body "Break a complex incident alert into sub-tasks and dispatch each to a specialist LLM call. Demonstrates task decomposition as a planning pattern before tool use.
Folder: \`[s1]-[decomposition]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S1] Stress test: decomposition" \
  --body "Run over all 30 incidents. Validate sub-task count is stable, final answer synthesises all sub-results, and total tokens stay within BudgetEnforcer cost cap.
Folder: \`[s1]-[decomposition]-[hand-built]-[ollama]\`"

echo ""
echo "==> S2 — Reason-Act-Observe Loop"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S2] Implement: react-loop" \
  --body "Bare ReAct loop — reason → act (search_logs / check_metrics) → observe — until FINAL_ANSWER. No framework. Integrates BudgetEnforcer and JSONL Tracer.
Folder: \`[s2]-[react-loop]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S2] Stress test: react-loop" \
  --body "Run over all 30 incidents. Assert: FINAL_ANSWER reached on every incident, avg steps <= 5, trajectory_grader pass rate >= 70%, no BudgetExceeded raised.
Folder: \`[s2]-[react-loop]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S2] Implement: failure-modes" \
  --body "Inject loop failure scenarios (tool timeout, hallucinated tool call, missing FINAL_ANSWER) and show how BudgetEnforcer and retry logic handle each.
Folder: \`[s2]-[failure-modes]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S2] Stress test: failure-modes" \
  --body "Run each failure mode against all 30 incidents. Validate that every injected failure produces a graceful error dict (not an unhandled exception) with a populated budget.summary.
Folder: \`[s2]-[failure-modes]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S2] Implement: loop-tracing" \
  --body "Instrument the ReAct loop with the JSONL Tracer (TRACE=1). Each span carries step index, tool name, args, result length, and duration_ms for post-run analysis.
Folder: \`[s2]-[loop-tracing]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S2] Stress test: loop-tracing" \
  --body "Run TRACE=1 over all 30 incidents. Assert JSONL file is written, every step has a valid span_id and duration_ms > 0, and trace file size stays under 1 MB.
Folder: \`[s2]-[loop-tracing]-[hand-built]-[ollama]\`"

echo ""
echo "==> S3 — Tool Design and MCP"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S3] Implement: tool-design" \
  --body "Hand-craft the five domain tools (search_logs, check_metrics, get_deploy_history, lookup_runbook, draft_fix) with proper OpenAI function-calling schemas and grader-compatible outputs.
Folder: \`[s3]-[tool-design]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S3] Stress test: tool-design" \
  --body "Run argument_grader against every tool schema with valid and invalid inputs. Assert 100% pass on valid calls and correct error dicts on invalid calls. No unhandled exceptions.
Folder: \`[s3]-[tool-design]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S3] Implement: mcp-server" \
  --body "Expose the five domain tools as an MCP server using the mcp-python SDK. Server must handle list_tools and call_tool requests over stdio transport.
Folder: \`[s3]-[mcp-server]-[mcp-python]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S3] Stress test: mcp-server" \
  --body "Send 100 concurrent call_tool requests to the MCP server. Validate all responses are valid JSON, latency p99 < 500 ms, and no server crashes or dropped connections.
Folder: \`[s3]-[mcp-server]-[mcp-python]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S3] Implement: mcp-client" \
  --body "Build a LangGraph agent that connects to the MCP server as its tool provider. The agent uses list_tools at startup and call_tool at each step — no hardcoded tool schemas.
Folder: \`[s3]-[mcp-client]-[langgraph]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S3] Stress test: mcp-client" \
  --body "Run over all 30 incidents with the MCP server live. Assert trajectory_grader pass rate >= 70%, no connection errors, and tool calls match the schemas advertised by list_tools.
Folder: \`[s3]-[mcp-client]-[langgraph]-[ollama]\`"

echo ""
echo "==> S4 — Memory"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S4] Implement: scratchpad" \
  --body "Add an in-context scratchpad (a growing text block in the system prompt) that accumulates observations across ReAct steps. Compare answer quality vs. the stateless S2 loop.
Folder: \`[s4]-[scratchpad]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S4] Stress test: scratchpad" \
  --body "Run over all 30 incidents. Measure scratchpad size growth per step and validate that quality score improves vs. S2 baseline while total prompt tokens stay within BudgetEnforcer cap.
Folder: \`[s4]-[scratchpad]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S4] Implement: episodic-memory" \
  --body "Store past incident investigations in SQLite. At the start of each run, retrieve the top-3 most similar past incidents and inject their root causes into the system prompt.
Folder: \`[s4]-[episodic-memory]-[sqlite]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S4] Stress test: episodic-memory" \
  --body "Pre-load 29 incidents, then run the 30th. Validate retrieval latency < 100 ms, the injected context is relevant (category match), and answer quality improves vs. no-memory baseline.
Folder: \`[s4]-[episodic-memory]-[sqlite]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S4] Implement: semantic-memory" \
  --body "Embed past incidents with nomic-embed-text and store in ChromaDB. Retrieve top-k similar incidents by cosine similarity to seed the agent's context.
Folder: \`[s4]-[semantic-memory]-[chromadb]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S4] Stress test: semantic-memory" \
  --body "Index all 30 incidents, then run retrieval for each. Assert top-1 retrieved incident matches expected category, p99 retrieval latency < 200 ms, and embedding store size < 10 MB.
Folder: \`[s4]-[semantic-memory]-[chromadb]-[ollama]\`"

echo ""
echo "==> S5 — Multi-Agent"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S5] Implement: orchestrator-worker" \
  --body "Build an orchestrator agent that breaks the incident into sub-tasks and dispatches each to a specialist worker agent (log-analyst, metrics-analyst, runbook-lookup) via LangGraph.
Folder: \`[s5]-[orchestrator-worker]-[langgraph]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S5] Stress test: orchestrator-worker" \
  --body "Run over all 30 incidents. Assert all worker agents complete, the orchestrator synthesises a final answer for every incident, and total elapsed time is within 2× the S2 baseline.
Folder: \`[s5]-[orchestrator-worker]-[langgraph]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S5] Implement: parallel-workers" \
  --body "Fan out log-search and metrics-check to two CrewAI workers running in parallel. Merge their observations before the final root-cause synthesis step.
Folder: \`[s5]-[parallel-workers]-[crewai]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S5] Stress test: parallel-workers" \
  --body "Run over all 30 incidents. Validate parallel execution reduces elapsed time vs. sequential baseline, both workers always return results, and merged output is coherent.
Folder: \`[s5]-[parallel-workers]-[crewai]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S5] Implement: worker-briefs" \
  --body "Hand-craft structured worker briefs (task + context + output schema) that the orchestrator fills before dispatching. Demonstrates prompt engineering for multi-agent coordination.
Folder: \`[s5]-[worker-briefs]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S5] Stress test: worker-briefs" \
  --body "Run over all 30 incidents. Assert worker brief JSON is valid and schema-complete for every dispatch, and the final synthesis uses all worker outputs (no silent drops).
Folder: \`[s5]-[worker-briefs]-[hand-built]-[ollama]\`"

echo ""
echo "==> S6 — Evals"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S6] Implement: tool-grader" \
  --body "Wire tool_selection_grader and argument_grader from _shared/grader.py into a standalone eval runner. Reports per-tool pass rates across all 30 incidents.
Folder: \`[s6]-[tool-grader]-[code]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S6] Stress test: tool-grader" \
  --body "Run the eval runner over all 30 incidents for S2 and S3 agents. Assert tool_selection pass rate >= 80% and argument_grader 100% pass on valid calls. Output a JSONL report.
Folder: \`[s6]-[tool-grader]-[code]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S6] Implement: answer-grader" \
  --body "Replace keyword-overlap answer_grader with an LLM-judge variant: qwen2.5:3b scores each agent answer against the ground-truth root cause on a 0–1 scale.
Folder: \`[s6]-[answer-grader]-[llm-judge]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S6] Stress test: answer-grader" \
  --body "Run LLM judge over all 30 incidents. Compare judge scores vs. keyword-overlap baseline. Assert Pearson correlation >= 0.7 and judge latency p99 < 10 s per answer.
Folder: \`[s6]-[answer-grader]-[llm-judge]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S6] Implement: replay-suite" \
  --body "Build a replay harness that re-runs saved JSONL traces against updated agent code. Diffs quality scores between baseline and new run to detect regressions.
Folder: \`[s6]-[replay-suite]-[custom]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S6] Stress test: replay-suite" \
  --body "Replay all 30 baseline traces. Assert zero regressions (score drop > 0.05) on any incident, replay completes in < 5 min total, and diff report is written to JSONL.
Folder: \`[s6]-[replay-suite]-[custom]-[ollama]\`"

echo ""
echo "==> S7 — Deployment Guardrails"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S7] Implement: budget-enforcer" \
  --body "Standalone example showing BudgetEnforcer in action: configure step, time, and cost caps; demonstrate BudgetExceeded raised at each limit; print budget.summary.
Folder: \`[s7]-[budget-enforcer]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S7] Stress test: budget-enforcer" \
  --body "Run BudgetEnforcer at aggressive caps (max_steps=3, max_seconds=5) over all 30 incidents. Assert BudgetExceeded is always raised before the cap is exceeded by more than 1 unit.
Folder: \`[s7]-[budget-enforcer]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S7] Implement: approval-gate" \
  --body "Add a human-in-the-loop pause before the agent executes a proposed fix. Gate reads from stdin in interactive mode and auto-approves in CI mode (env var HARNESS_AUTO_APPROVE=1).
Folder: \`[s7]-[approval-gate]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S7] Stress test: approval-gate" \
  --body "Run in HARNESS_AUTO_APPROVE=1 mode over all 30 incidents. Assert gate is reached for every incident, auto-approval is logged, and the agent continues after approval without error.
Folder: \`[s7]-[approval-gate]-[hand-built]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S7] Implement: tracing" \
  --body "Standalone tracing example: show Tracer producing a valid JSONL file for a full S2 run. Include a simple reader script that pretty-prints spans with timing and tool names.
Folder: \`[s7]-[tracing]-[jsonl]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S7] Stress test: tracing" \
  --body "Run TRACE=1 over all 30 incidents. Assert JSONL file has exactly one span per step, all duration_ms > 0, no duplicate span_ids, and file is parseable line-by-line.
Folder: \`[s7]-[tracing]-[jsonl]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "enhancement" \
  --title "[S7] Implement: eval-gate" \
  --body "CI eval gate: run the replay-suite as a pre-commit or pre-merge check. Fail the pipeline if any incident's trajectory_grader score drops below the stored baseline threshold.
Folder: \`[s7]-[eval-gate]-[ci]-[ollama]\`"

gh issue create --repo "$REPO" --assignee "$ASSIGNEE" --label "stress-test" \
  --title "[S7] Stress test: eval-gate" \
  --body "Inject a deliberate regression (lower quality answer for inc-001) and run the eval gate. Assert the gate fails fast (exits non-zero) and the failure report names the regressed incident.
Folder: \`[s7]-[eval-gate]-[ci]-[ollama]\`"

echo ""
echo "Done. 44 issues created in $REPO."
