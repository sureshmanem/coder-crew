# Multi-Agent Coding System — Brainstorm

## Goal
A learning-focused proof of concept: a small team of AI agents that collaborates
to write, test, and review code for a fixed toy task. Primary purpose is to get
hands-on with:
- Multi-agent orchestration (**LangGraph**)
- **OpenRouter** as a unified LLM API gateway (for planner/reviewer roles)
- **RunPod** as a self-hosted GPU backend for an open-weight coding model
  (**Qwen2.5-Coder-32B**)

This is explicitly a "learn the stack" project, not a production system. Keep it
small, observable, and easy to iterate on.

---

## Use case

**Autonomous coding agent team.** Given a fixed toy task (e.g. "build a CLI
todo app in Python with tests"), a small crew of agents plans, writes code,
runs tests, and reviews/iterates until the task passes — without a human in
the loop for each step.

### Why a fixed toy task first
Validates the full pipeline (plan → code → test → review → fix loop) against
known-good acceptance criteria before generalizing to arbitrary user specs.
Once the loop is solid, swapping in "user-supplied spec" or "repo bug-fix
loop" mode later is a small change (Brainstorm section below has notes on
this evolution path).

### Candidate toy task (to finalize before build)
"Build a small Python CLI todo app: add/list/complete/delete tasks, JSON file
persistence, plus a pytest suite covering the core commands." Good because:
- Small enough to finish in a handful of agent turns
- Has an objective pass/fail signal (pytest exit code)
- Real enough to exercise planning, file writing, and iteration

---

## Agent roles

| Agent | Responsibility | Model |
|---|---|---|
| **Planner** | Breaks the task into an ordered implementation plan / file list | OpenRouter (frontier model, e.g. Claude or GPT-class) |
| **Coder** | Writes/edits code per the current plan step | RunPod-hosted Qwen2.5-Coder-32B |
| **Tester** | Runs the test suite (or writes it if missing), reports pass/fail + errors | Local tool execution (no LLM, or a small LLM to interpret failures) |
| **Reviewer** | Reads diffs + test output, decides "done" or sends feedback back to Coder | OpenRouter (frontier model) |

Rationale for the split: the **Coder** role is the one we specifically want
running on our own RunPod GPU (that's the "self-hosted open-weight model"
piece); **Planner/Reviewer** stay on OpenRouter so we get strong reasoning
without hosting a big general model ourselves. This also naturally exercises
"two different LLM backends in one LangGraph graph," which is a good learning
goal in itself.

---

## Orchestration: LangGraph

Proposed graph (state machine, not a fixed pipeline — allows loops):

```
        ┌──────────┐
        │ Planner  │
        └────┬─────┘
             │ plan
             ▼
        ┌──────────┐
   ┌───▶│  Coder   │
   │    └────┬─────┘
   │         │ code changes
   │         ▼
   │    ┌──────────┐
   │    │  Tester   │
   │    └────┬─────┘
   │         │ results
   │         ▼
   │    ┌──────────┐
   │    │ Reviewer  │
   │    └────┬─────┘
   │    fail │  │ pass
   └─────────┘  ▼
              done
```

State object carries: task spec, plan, current file tree/diffs, last test
output, review feedback, iteration count (with a max-iteration cutoff to
avoid infinite loops — important for a POC).

---

## Model backends

### OpenRouter (Planner, Reviewer)
- Single API key, pick any hosted frontier model per role (can start with
  the same model for both, tune later).
- Straightforward REST/OpenAI-compatible client — minimal setup.
- Pay-per-token, no infra to manage.

### RunPod (Coder — Qwen2.5-Coder-32B)
- Spin up a GPU pod (single 48GB-class GPU, e.g. A6000/L40S) running an
  OpenAI-compatible inference server (vLLM or text-generation-inference)
  serving Qwen2.5-Coder-32B-Instruct.
- Expose it via RunPod's proxy URL as an OpenAI-compatible endpoint so the
  Coder agent calls it exactly like any other chat completion API.
- **Cost note for POC:** use RunPod's on-demand pod (not serverless) for
  simplicity while iterating, but remember to **stop the pod when not
  actively testing** — GPU time is billed while running. Serverless RunPod
  endpoints (scale-to-zero) are a natural next step once the flow is stable,
  to avoid idle GPU cost.
- Quantized weights (AWQ/GPTQ) likely needed to fit 32B comfortably and keep
  pod cost down — worth confirming GPU size vs. quantization tradeoff before
  provisioning.

---

## Tech stack summary
- **Language:** Python
- **Orchestration:** LangGraph
- **LLM access:** `langchain-openai` (or raw `openai` client) pointed at two
  base URLs — OpenRouter for Planner/Reviewer, RunPod pod endpoint for Coder
- **Sandboxing:** run generated code/tests in a subprocess or lightweight
  container, not directly on the host, even for a POC
- **Secrets:** `OPENROUTER_API_KEY`, `RUNPOD_API_KEY` / pod endpoint URL via
  `.env` (never committed)

---

## Decisions (resolved)
1. **Toy task:** confirmed — CLI todo app (add/list/complete/delete tasks,
   JSON file persistence, pytest suite covering core commands).
2. **OpenRouter model:** use the **same model** for both Planner and Reviewer
   roles initially (simplifies setup/cost tracking; can split later if the
   Reviewer needs a different strength profile).
3. **Quantization:** as proposed — AWQ/GPTQ-quantized Qwen2.5-Coder-32B to
   fit a single 48GB-class GPU affordably on RunPod.
4. **Max iterations:** cap the Coder↔Tester↔Reviewer loop at **3** attempts;
   if still failing after 3, stop and surface the failure instead of looping
   forever.
5. **Logging/tracing:** turn on tracing (LangSmith or equivalent
   LangGraph-native tracing) from the start so each run is inspectable —
   useful given this is a learning-focused POC.

## Evolution path (not part of this POC, just noted for later)
- Swap fixed toy task → user-supplied spec per run
- Swap fixed toy task → real repo bug-fix loop (reproduce failing test, fix,
  verify) — closer to a real coding-agent product
- Move RunPod from on-demand pod to serverless endpoint for cost efficiency
