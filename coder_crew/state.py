"""Shared state object passed between LangGraph nodes."""
from typing import TypedDict


class CrewState(TypedDict, total=False):
    task: str  # the fixed toy task spec
    plan: str  # Planner's output: ordered implementation steps
    files: dict[str, str]  # path -> file contents, written by Coder
    test_output: str  # stdout/stderr from the Tester's pytest run
    tests_passed: bool
    review_feedback: str  # Reviewer's notes when tests fail or code is incomplete
    done: bool
    iteration: int
    max_iterations: int
