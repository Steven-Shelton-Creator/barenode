"""Instructions — system prompt + AGENTS.md loader (CH03).

The harness prepends a system message on every turn that contains:
  1. A built-in system prompt describing the agent's role.
  2. Content auto-loaded from ``AGENTS.md`` in the workspace directory.

The system message is rebuilt fresh on every call — never stored in
``self.messages``.
"""

import os


def load_instructions(workspace: str | None = None) -> str:
    """Read ``AGENTS.md`` from the workspace and return its content.

    Parameters
    ----------
    workspace : str or None
        Path to the workspace directory.  If ``None``, uses the current
        working directory.

    Returns
    -------
    str
        Content of ``AGENTS.md``, or an empty string if the file does
        not exist or cannot be read.
    """
    if workspace is None:
        workspace = os.getcwd()

    path = os.path.join(workspace, "AGENTS.md")
    if not os.path.isfile(path):
        return ""

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except (OSError, UnicodeDecodeError):
        return ""


def make_system_prompt(agents_content: str) -> str:
    """Build the full system prompt string.

    Parameters
    ----------
    agents_content : str
        Content loaded from ``AGENTS.md`` (may be empty).

    Returns
    -------
    str
        The combined system prompt.
    """
    built_in = "You are barenode, a helpful coding assistant built from scratch."

    if agents_content:
        return f"{built_in}\n\n---\n\n{agents_content}"
    return built_in


def build_system_message(workspace: str | None = None) -> dict | None:
    """Build the system message dict for this turn.

    Returns ``None`` if no instructions are available (graceful
    fallback — the harness can skip the system message entirely).

    Parameters
    ----------
    workspace : str or None
        Path to the workspace directory.

    Returns
    -------
    dict or None
        A message dict ``{"role": "system", "content": ...}``, or
        ``None`` if there's no content.
    """
    agents_content = load_instructions(workspace)
    prompt = make_system_prompt(agents_content)
    if not prompt:
        return None
    return {"role": "system", "content": prompt}