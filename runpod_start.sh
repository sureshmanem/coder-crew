#!/usr/bin/env bash
# Start command for the RunPod pod's vLLM OpenAI-compatible server, serving
# the Coder agent's model (Qwen2.5-Coder-32B, AWQ-quantized).
#
# Set this as the pod's Docker start command, or run it inside the pod's
# terminal after connecting.
#
# Expects RUNPOD_SERVER_API_KEY to be set as a pod environment variable
# (any string you choose) — this becomes the value coder-crew's .env uses
# as RUNPOD_API_KEY.
set -euo pipefail

if [ -z "${RUNPOD_SERVER_API_KEY:-}" ]; then
  echo "ERROR: RUNPOD_SERVER_API_KEY is not set. Set it as a pod env var." >&2
  exit 1
fi

python3 -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-32B-Instruct-AWQ \
  --quantization awq \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --host 0.0.0.0 \
  --port 8000 \
  --api-key "$RUNPOD_SERVER_API_KEY"
