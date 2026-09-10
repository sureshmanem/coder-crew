"""Entrypoint: run the coder-crew POC against the fixed toy task.

Usage:
    python main.py

Requires OPENROUTER_API_KEY, RUNPOD_API_KEY, RUNPOD_ENDPOINT_URL set in
.env (see .env.example). LangSmith tracing is picked up automatically from
LANGCHAIN_TRACING_V2 / LANGCHAIN_API_KEY if set.
"""
from coder_crew import config
from coder_crew.graph import build_graph
from coder_crew.task import TOY_TASK


def main() -> None:
    graph = build_graph()

    initial_state = {
        "task": TOY_TASK,
        "max_iterations": config.MAX_ITERATIONS,
        "iteration": 0,
        "done": False,
    }

    print("Running coder-crew on the toy task...\n")
    final_state = graph.invoke(initial_state)

    print("\n=== Plan ===")
    print(final_state.get("plan"))

    print("\n=== Files ===")
    for path in final_state.get("files", {}):
        print(f"- {path}")

    print(f"\n=== Iterations used: {final_state.get('iteration')} ===")
    print(f"=== Tests passed: {final_state.get('tests_passed')} ===")

    if not final_state.get("tests_passed"):
        print("\n=== Last review feedback ===")
        print(final_state.get("review_feedback"))

    print(f"\nWorkspace: {config.WORKSPACE_DIR}/")


if __name__ == "__main__":
    main()
