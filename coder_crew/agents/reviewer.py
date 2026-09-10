"""Reviewer agent: reads test output and decides pass/fail; on failure,
writes concrete feedback for the Coder's next attempt.

Runs on OpenRouter (same model as Planner, per Brainstorm.md decision).
"""
from langchain_core.messages import HumanMessage, SystemMessage

from coder_crew.llm.clients import get_openrouter_llm
from coder_crew.state import CrewState

SYSTEM_PROMPT = """\
You are the Reviewer in a multi-agent coding team. You are given the task,
the plan, and pytest output from the latest attempt.

If tests_passed is True, respond with exactly: APPROVED

Otherwise, respond with concrete, actionable feedback for the Coder to fix
the failures — reference specific test names/errors from the output. Do not
restate the whole plan; focus only on what needs to change.
"""


def reviewer_node(state: CrewState) -> CrewState:
    iteration = state.get("iteration", 0) + 1
    max_iterations = state.get("max_iterations", 3)

    if state.get("tests_passed"):
        return {**state, "done": True, "iteration": iteration}

    if iteration >= max_iterations:
        return {
            **state,
            "done": True,
            "iteration": iteration,
            "review_feedback": (
                f"Max iterations ({max_iterations}) reached without passing "
                "tests. Stopping."
            ),
        }

    llm = get_openrouter_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Task:\n{state['task']}\n\n"
                f"Plan:\n{state['plan']}\n\n"
                f"Test output:\n{state.get('test_output', '')}"
            )
        ),
    ]
    response = llm.invoke(messages)
    return {
        **state,
        "done": False,
        "iteration": iteration,
        "review_feedback": response.content,
    }
