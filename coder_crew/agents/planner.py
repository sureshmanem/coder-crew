"""Planner agent: breaks the toy task into an ordered implementation plan.

Runs on OpenRouter (see Brainstorm.md rationale: frontier reasoning model,
not the self-hosted coder model).
"""
from langchain_core.messages import HumanMessage, SystemMessage

from coder_crew.llm.clients import get_openrouter_llm
from coder_crew.state import CrewState

SYSTEM_PROMPT = """\
You are the Planner in a multi-agent coding team. Given a task spec, produce
a short, ordered implementation plan (numbered steps) that a Coder agent will
follow to write the code. Be concrete about file names and what each file
must contain. Do not write code yourself — only the plan.
"""


def planner_node(state: CrewState) -> CrewState:
    llm = get_openrouter_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Task:\n{state['task']}"),
    ]
    response = llm.invoke(messages)
    return {**state, "plan": response.content, "iteration": 0}
