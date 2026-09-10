"""Shared helper for parsing multi-file code output from the Coder LLM.

We ask the Coder to emit files in a simple, unambiguous block format rather
than relying on markdown-fenced-code heuristics:

### FILE: <relative/path.py>
<file content, verbatim, no code fences>
### END FILE
"""
import re

FILE_BLOCK_RE = re.compile(
    r"### FILE: (?P<path>\S+)\n(?P<content>.*?)\n### END FILE",
    re.DOTALL,
)


def parse_files(text: str) -> dict[str, str]:
    files = {}
    for match in FILE_BLOCK_RE.finditer(text):
        files[match.group("path").strip()] = match.group("content")
    return files
