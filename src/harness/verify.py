"""Self-verification gate (CH12).

After the agent writes a code file, the harness arms a verification gate.
The agent must run the test suite (via bash tool), and the harness checks
the result for exit code 0 before accepting "done."

Design
------
- ``CODE_EXTENSIONS`` — set of file extensions considered "code"
- ``parse_test_command()`` — reads the ``[testing]`` section from AGENTS.md
- ``was_code_file_written()`` — inspects tool calls for write_file with code paths
- ``check_test_result()`` — parses a bash tool result string for exit code indicators
- ``build_verification_prompt()`` — message to ask the agent to run tests
"""

import os
import json
import re


# ---------------------------------------------------------------------------
# Code file extensions — triggers verification when written
# ---------------------------------------------------------------------------

CODE_EXTENSIONS = {
    ".py", ".pyw",
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
    ".java", ".clj", ".cljs", ".ex", ".exs", ".erl", ".hs",
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".hh", ".hxx",
    ".css", ".scss", ".less", ".html", ".htm", ".xhtml",
    ".json", ".yaml", ".yml", ".toml", ".xml",
    ".sh", ".bash", ".zsh", ".fish",
    ".lua", ".r", ".m", ".mm", ".pl", ".pm", ".t",
    ".sql", ".graphql", ".proto",
    ".md", ".rst", ".tex",
    ".cfg", ".ini", ".conf",
    ".dockerfile", ".Dockerfile",
    ".env.example",
}


# ---------------------------------------------------------------------------
# Test command parsing
# ---------------------------------------------------------------------------

def parse_test_command(workspace: str | None = None) -> str | None:
    """Read the ``[testing]`` section from AGENTS.md and return the test command.

    Looks for a section header ``## Testing`` followed by a code block
    containing a bash command.  Returns the first such command found,
    or ``None`` if no testing section exists.

    Parameters
    ----------
    workspace : str or None
        Path to the workspace directory.  Defaults to current working directory.

    Returns
    -------
    str or None
        The test command (e.g. ``"uv run pytest tests/ -v"``), or ``None``.
    """
    if workspace is None:
        workspace = os.getcwd()

    agents_path = os.path.join(workspace, "AGENTS.md")
    if not os.path.isfile(agents_path):
        return None

    try:
        with open(agents_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return None

    # Look for a "## Testing" section followed by a bash code block
    match = re.search(
        r"##\s+Testing\s*\n.*?```(?:bash)?\s*\n(.*?)```",
        content,
        re.DOTALL,
    )
    if match:
        command = match.group(1).strip()
        return command if command else None

    return None


# ---------------------------------------------------------------------------
# Code file detection
# ---------------------------------------------------------------------------

def _get_tool_call_path(tc: dict) -> str | None:
    """Extract the ``path`` argument from a tool call dict, if present."""
    raw_args = tc.get("function", {}).get("arguments", "{}")
    if isinstance(raw_args, str):
        try:
            args = json.loads(raw_args)
        except (json.JSONDecodeError, TypeError):
            return None
    else:
        args = raw_args
    return args.get("path") if isinstance(args, dict) else None


def was_code_file_written(tool_calls: list[dict]) -> bool:
    """Check whether any tool call in the list wrote a code file.

    A code file is any file with an extension in ``CODE_EXTENSIONS``
    that was written via the ``write_file`` tool.

    Parameters
    ----------
    tool_calls : list of dict
        A list of tool call dicts in OpenAI-compatible format
        (``{"function": {"name": ..., "arguments": ...}}``).

    Returns
    -------
    bool
        ``True`` if at least one code file was written.
    """
    for tc in tool_calls:
        func = tc.get("function", {})
        name = func.get("name", "")
        if name != "write_file":
            continue

        path = _get_tool_call_path(tc)
        if path is None:
            continue

        _, ext = os.path.splitext(path)
        if ext in CODE_EXTENSIONS:
            return True

    return False


# ---------------------------------------------------------------------------
# Test result checking
# ---------------------------------------------------------------------------

def check_test_result(result_str: str) -> bool:
    """Check whether a bash tool result indicates a passing test suite.

    The bash tool appends ``[exit code: N]`` when the exit code is non-zero.
    If the string does *not* contain ``[exit code:``, the test passed (exit 0).

    Parameters
    ----------
    result_str : str
        The output string from the bash tool (or any tool result).

    Returns
    -------
    bool
        ``True`` if the result suggests a passing test run.
    """
    if "[exit code:" not in result_str:
        return True

    match = re.search(r"\[exit code: (\d+)\]", result_str)
    if match:
        return int(match.group(1)) == 0

    return False


# ---------------------------------------------------------------------------
# Verification prompt builder
# ---------------------------------------------------------------------------

def build_verification_prompt(test_command: str) -> str:
    """Build a user message asking the agent to run the test suite.

    Parameters
    ----------
    test_command : str
        The test command to run (e.g. ``"uv run pytest tests/ -v"``).

    Returns
    -------
    str
        A message to inject into the conversation.
    """
    return (
        f"[Verification required] Code files were changed. "
        f"Please run the test suite to verify your changes:\n\n"
        f"```bash\n{test_command}\n```\n\n"
        f"If tests fail, fix the issues and re-run until all tests pass."
    )