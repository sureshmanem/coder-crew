"""The fixed toy task for this POC (see Brainstorm.md)."""

TOY_TASK = """\
Build a small Python CLI todo app with these requirements:

- A single-file CLI (todo.py) using argparse, with subcommands:
    - add <text>        : add a new task
    - list              : list all tasks with their id and status
    - complete <id>     : mark a task complete
    - delete <id>       : delete a task
- Tasks persist to a JSON file (tasks.json) in the same directory.
- Include a pytest test suite (test_todo.py) covering add/list/complete/delete,
  using a temporary file for persistence so tests don't clobber real data.
- No external dependencies beyond the Python standard library and pytest.
"""
