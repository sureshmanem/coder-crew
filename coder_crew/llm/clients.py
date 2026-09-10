"""LLM client factories for the two backends used in coder-crew:

- OpenRouter: OpenAI-compatible API, used by the Planner and Reviewer agents.
- RunPod: OpenAI-compatible endpoint (vLLM/TGI serving Qwen2.5-Coder-32B),
  used by the Coder agent.

Both are wired through `langchain_openai.ChatOpenAI` since both backends
expose OpenAI-compatible chat completion APIs — only base_url/api_key/model
differ.
"""
from langchain_openai import ChatOpenAI

from coder_crew import config


def get_openrouter_llm(temperature: float = 0.2) -> ChatOpenAI:
    """LLM client for Planner/Reviewer agents, routed through OpenRouter."""
    config.require(config.OPENROUTER_API_KEY, "OPENROUTER_API_KEY")
    return ChatOpenAI(
        model=config.OPENROUTER_MODEL,
        api_key=config.OPENROUTER_API_KEY,
        base_url=config.OPENROUTER_BASE_URL,
        temperature=temperature,
    )


def get_runpod_llm(temperature: float = 0.2) -> ChatOpenAI:
    """LLM client for the Coder agent, routed to a self-hosted RunPod pod."""
    config.require(config.RUNPOD_ENDPOINT_URL, "RUNPOD_ENDPOINT_URL")
    config.require(config.RUNPOD_API_KEY, "RUNPOD_API_KEY")
    return ChatOpenAI(
        model=config.RUNPOD_MODEL,
        api_key=config.RUNPOD_API_KEY,
        base_url=config.RUNPOD_ENDPOINT_URL,
        temperature=temperature,
    )
