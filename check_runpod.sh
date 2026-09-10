#!/usr/bin/env bash
# Smoke-test a running RunPod vLLM endpoint before pointing coder-crew at it.
#
# Usage:
#   RUNPOD_ENDPOINT_URL=https://<pod-id>-8000.proxy.runpod.net/v1 \
#   RUNPOD_API_KEY=<your key> \
#   ./check_runpod.sh
set -euo pipefail

: "${RUNPOD_ENDPOINT_URL:?Set RUNPOD_ENDPOINT_URL}"
: "${RUNPOD_API_KEY:?Set RUNPOD_API_KEY}"

MODEL="${RUNPOD_MODEL:-Qwen/Qwen2.5-Coder-32B-Instruct-AWQ}"

curl -sS "${RUNPOD_ENDPOINT_URL}/chat/completions" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${MODEL}\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Write a Python hello world.\"}]
  }" | python3 -m json.tool
