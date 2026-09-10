"""Tester agent: writes the Coder's files to a sandbox workspace and runs
pytest against them. Pure tool execution, no LLM involved.
"""
import subprocess
from pathlib import Path

from coder_crew import config
from coder_crew.state import CrewState


def _write_files(workspace: Path, files: dict[str, str]) -> None:
    for rel_path, content in files.items():
        target = workspace / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


def tester_node(state: CrewState) -> CrewState:
    workspace = Path(config.WORKSPACE_DIR)
    workspace.mkdir(parents=True, exist_ok=True)

    files = state.get("files", {})
    if not files:
        return {
            **state,
            "test_output": "No files were produced by the Coder agent.",
            "tests_passed": False,
        }

    _write_files(workspace, files)

    result = subprocess.run(
        ["pytest", "-v"],
        cwd=str(workspace),
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = result.stdout + "\n" + result.stderr
    return {
        **state,
        "test_output": output,
        "tests_passed": result.returncode == 0,
    }
