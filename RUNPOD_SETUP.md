# RunPod Setup Guide — Qwen2.5-Coder-32B (Coder agent backend)

This sets up the self-hosted model the **Coder** agent calls (see
`Brainstorm.md`). We run vLLM's OpenAI-compatible server on a RunPod GPU pod,
serving an AWQ-quantized Qwen2.5-Coder-32B-Instruct so it fits comfortably
on a single 48GB-class GPU.

---

## 1. Choose a pod

In the RunPod console → **Pods** → **Deploy**:

- **Template:** search "vLLM" and pick the official `runpod/worker-vllm` or
  a plain `vllm/vllm-openai` image. Either works; steps below assume the
  generic `vllm/vllm-openai` Docker image so you have full control over
  flags.
- **GPU:** 1x **A6000 (48GB)** or **L40S (48GB)** — enough for a 32B model
  in AWQ 4-bit. (An A100 80GB also works and gives headroom, at higher cost.)
- **Container disk:** at least 60GB (model weights ~20GB in AWQ, plus vLLM
  image).
- **Expose HTTP port:** `8000` (vLLM's default OpenAI-server port). RunPod
  will give you a public proxy URL for it, e.g.
  `https://<pod-id>-8000.proxy.runpod.net`.
- **Pod type:** use an **On-Demand** pod for this POC (not serverless) —
  simpler to iterate on. Remember to **stop it when not testing**; you're
  billed while it runs. Serverless is a good next step once the pipeline is
  working (see Brainstorm.md evolution path).

## 2. Container start command

Set this as the pod's **Docker command / start command** (or run it manually
in a terminal session once the pod is up):

```bash
python3 -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-32B-Instruct-AWQ \
  --quantization awq \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --host 0.0.0.0 \
  --port 8000 \
  --api-key "$RUNPOD_SERVER_API_KEY"
```

Notes:
- `--api-key` makes vLLM require a bearer token on requests — set
  `RUNPOD_SERVER_API_KEY` as a pod environment variable (any string you
  choose) so the endpoint isn't wide open on the public proxy URL. This is
  the value you'll put in `coder-crew`'s `.env` as `RUNPOD_API_KEY`.
- `--max-model-len 8192` keeps KV-cache memory reasonable for a POC; raise
  it if the Coder agent's file outputs get truncated on larger tasks.
- First boot will take a few minutes while vLLM downloads the model weights
  from Hugging Face — watch the pod logs for `Uvicorn running on
  http://0.0.0.0:8000` before hitting the endpoint.

A ready-to-paste version of this is in `runpod_start.sh` in this repo.

## 3. Get your endpoint URL

From the RunPod console, open the pod → **Connect** → **HTTP Service [Port
8000]**. That URL is your `RUNPOD_ENDPOINT_URL`. vLLM's OpenAI server serves
chat completions at `<that-url>/v1/chat/completions`, but LangChain's
`ChatOpenAI` client only needs the base (it appends `/v1/...` itself), so:

```
RUNPOD_ENDPOINT_URL=https://<pod-id>-8000.proxy.runpod.net/v1
```

## 4. Update coder-crew's .env

```bash
RUNPOD_API_KEY=<the RUNPOD_SERVER_API_KEY you set on the pod>
RUNPOD_ENDPOINT_URL=https://<pod-id>-8000.proxy.runpod.net/v1
RUNPOD_MODEL=Qwen/Qwen2.5-Coder-32B-Instruct-AWQ
```

## 5. Smoke-test the endpoint

Before running the full crew, confirm the pod answers:

```bash
curl "$RUNPOD_ENDPOINT_URL/chat/completions" \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-Coder-32B-Instruct-AWQ",
    "messages": [{"role": "user", "content": "Write a Python hello world."}]
  }'
```

You should get back a normal OpenAI-style chat completion JSON response. A
`check_runpod.sh` script wrapping this same check is included in the repo.

## 6. Run coder-crew

```bash
pip install -r requirements.txt
python main.py
```

## 7. Shut down when done

Stop (or terminate) the pod from the RunPod console to stop billing. Stopped
pods keep their container disk (and downloaded weights) so a restart is
faster than a fresh deploy; terminated pods free the disk too and require a
full re-download next time.

## Cost/quantization notes
- AWQ 4-bit keeps the 32B model's weights around ~20GB, comfortably fitting
  a 48GB GPU with room for KV cache at `--max-model-len 8192`.
- If you hit out-of-memory errors, lower `--gpu-memory-utilization` or
  `--max-model-len`, or move up to an 80GB GPU.
- If you'd rather not quantize, Qwen2.5-Coder-32B-Instruct (full precision)
  needs ~65GB+ and requires an 80GB-class GPU (A100/H100) — pricier for a
  learning POC, so AWQ is the recommended default here.
