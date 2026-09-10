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
1. Provision the Coder agent's backend: see [RUNPOD_SETUP.md](./RUNPOD_SETUP.md)
   to stand up a RunPod GPU pod serving Qwen2.5-Coder-32B via vLLM.
2. Copy `.env.example` to `.env` and fill in `OPENROUTER_API_KEY` plus the
   `RUNPOD_*` values from step 1.
3. `pip install -r requirements.txt`
4. `python main.py`
