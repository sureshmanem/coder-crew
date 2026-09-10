# coder-crew

Proof-of-concept multi-agent coding system built with LangGraph. A
Planner/Reviewer pair on OpenRouter and a self-hosted Qwen2.5-Coder-32B on
RunPod collaborate to write, test, and iterate on code for a fixed toy task —
exploring multi-LLM-backend agent orchestration.

See [Brainstorm.md](./Brainstorm.md) for the full design discussion and
architecture.

## Status
🚧 Proof of concept / learning project — not production-ready.

## Stack
- Python + LangGraph for orchestration
- OpenRouter (Planner + Reviewer agents)
- RunPod-hosted Qwen2.5-Coder-32B (Coder agent)

## Setup
See `.env.example` for required environment variables. Setup and run
instructions will be added as the implementation progresses.
