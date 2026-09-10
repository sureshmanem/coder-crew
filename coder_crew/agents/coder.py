"""Coder agent: writes/edits code per the current plan (and prior review
feedback, if this is a retry).

Runs on RunPod, serving the self-hosted Qwen2.5-Coder-32B model — this is the
piece of the POC specifically meant to exercise a self-hosted open-weight
model (see Brainstorm.md).
"""
from langchain_core.messages import HumanMessage, SystemMessage

from coder_crew.agents.parsing import parse_files
from coder_crew.llm.clients import get_runpod_llm
from coder_crew.state import CrewState

SYSTEM_PROMPT = """\
You are the Coder in a multi-agent coding team. Given a task, an
implementation plan, and (optionally) reviewer feedback from a previous
attempt, write the complete code to satisfy the task.

Output ONLY file blocks in this exact format, one per file, no other text:

### FILE: relative/path.py
<full file content, no markdown code fences>
### END FILE

Always output complete file contents (not diffs), even on retries.
"""


def coder_node(state: CrewState) -> CrewState:
    llm = get_runpod_llm()

    prompt_parts = [f"Task:\n{state['task']}", f"Plan:\n{state['plan']}"]
    if state.get("review_feedback"):
        prompt_parts.append(
            "Previous attempt failed review. Feedback to address:\n"
            f"{state['review_feedback']}"
        )
        if state.get("files"):
            existing = "\n\n".join(
                f"### FILE: {path}\n{content}\n### END FILE"
                for path, content in state["files"].items()
            )
            prompt_parts.append(f"Previous file versions:\n{existing}")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="\n\n".join(prompt_parts)),
    ]
    response = llm.invoke(messages)
    files = parse_files(response.content)
    return {**state, "files": files}
