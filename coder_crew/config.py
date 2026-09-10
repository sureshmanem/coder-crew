"""Environment/config loading for coder-crew."""
import os

from dotenv import load_dotenv

load_dotenv()

# OpenRouter — used by Planner and Reviewer agents
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")

# RunPod — used by the Coder agent (self-hosted Qwen2.5-Coder-32B)
RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY", "")
RUNPOD_ENDPOINT_URL = os.environ.get("RUNPOD_ENDPOINT_URL", "")
RUNPOD_MODEL = os.environ.get("RUNPOD_MODEL", "Qwen/Qwen2.5-Coder-32B-Instruct")

# Loop control
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "3"))

# Where the Coder agent writes files and the Tester agent runs pytest
WORKSPACE_DIR = os.environ.get("WORKSPACE_DIR", "sandbox_workspace")


def require(value: str, name: str) -> str:
    if not value:
        raise RuntimeError(
            f"Missing required config '{name}'. Set it in your .env file "
            f"(see .env.example)."
        )
    return value
