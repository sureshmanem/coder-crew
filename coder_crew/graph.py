"""LangGraph wiring for the coder-crew POC.

Graph shape (see Brainstorm.md):

    Planner -> Coder -> Tester -> Reviewer -> (loop back to Coder, or end)
"""
from langgraph.graph import END, StateGraph

from coder_crew.agents.coder import coder_node
from coder_crew.agents.planner import planner_node
from coder_crew.agents.reviewer import reviewer_node
from coder_crew.agents.tester import tester_node
from coder_crew.state import CrewState


def _route_after_review(state: CrewState) -> str:
    return END if state.get("done") else "coder"


def build_graph():
    graph = StateGraph(CrewState)

    graph.add_node("planner", planner_node)
    graph.add_node("coder", coder_node)
    graph.add_node("tester", tester_node)
    graph.add_node("reviewer", reviewer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "tester")
    graph.add_edge("tester", "reviewer")
    graph.add_conditional_edges(
        "reviewer", _route_after_review, {"coder": "coder", END: END}
    )

    return graph.compile()
