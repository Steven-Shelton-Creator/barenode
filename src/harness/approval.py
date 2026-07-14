"""Approval gate — human-in-the-loop for dangerous tool operations (CH05).

Some tools (e.g. write_file) require explicit human approval before
execution.  The approval gate prompts the user and waits for y/n input.

No approval → fails safe.  The tool is not executed.
"""

import sys


def prompt_approval(tool_name: str, summary: str) -> bool:
    """Prompt the user for approval to execute a tool.

    Parameters
    ----------
    tool_name : str
        Name of the tool requiring approval.
    summary : str
        A human-readable summary of what the tool will do.

    Returns
    -------
    bool
        ``True`` if the user approved, ``False`` otherwise.
    """
    print(f"\n[APPROVAL REQUIRED] {tool_name}: {summary}", file=sys.stderr)
    print("  Proceed? (y/n): ", end="", file=sys.stderr)

    try:
        raw = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        return False

    if raw in ("y", "yes"):
        print(f"  Approved.", file=sys.stderr)
        return True

    print(f"  Rejected.", file=sys.stderr)
    return False