"""Context delivery — @file reference injection (CH04).

Before the model call, the harness scans the user's message for
``@path`` references, reads the corresponding files from the
workspace directory, and injects their contents inline.

Design
------
- Reference symbol: ``@`` followed by a file path.
- Files are resolved relative to the workspace directory.
- Multiple ``@`` references in one message are all resolved.
- Missing files are left as-is (graceful fallback — the model
  can ask the user for the correct path).
- Files outside the workspace are **not** read (security boundary).
"""

import os
import re

# Pattern: @ followed by a path (word chars, dots, slashes, hyphens)
# The path is matched greedily; trailing punctuation (.,!?;:) is stripped
# in _replace_match to avoid capturing sentence-ending dots as part of
# the file path.
_AT_REF_PATTERN = re.compile(r"@([\w.\-/]+)")


def deliver(message: str, workspace: str | None = None) -> str:
    """Scan *message* for ``@path`` references and inject file contents.

    Each ``@path`` is replaced with the contents of the file found at
    ``workspace/path``.  If the file does not exist or is outside the
    workspace, the reference is left unchanged.

    Parameters
    ----------
    message : str
        The user's raw message, possibly containing ``@path`` references.
    workspace : str or None
        The workspace directory to resolve paths against.  Defaults to
        the current working directory.

    Returns
    -------
    str
        The message with ``@path`` references replaced by file contents.
    """
    if workspace is None:
        workspace = os.getcwd()

    workspace = os.path.abspath(workspace)

    def _replace_match(match: re.Match) -> str:
        """Replace a single @path match with the file content."""
        ref = match.group(1).rstrip(".,!?;:")  # strip trailing sentence punctuation
        full_path = os.path.abspath(os.path.join(workspace, ref))

        # Security: file must be inside workspace
        if not full_path.startswith(workspace + os.sep):
            return match.group(0)  # leave @ref unchanged

        if not os.path.isfile(full_path):
            return match.group(0)  # leave @ref unchanged

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except (OSError, UnicodeDecodeError):
            return match.group(0)  # leave @ref unchanged

        if not content:
            return match.group(0)  # leave @ref unchanged

        return f"\n--- {ref} ---\n{content}\n--- end {ref} ---\n"

    return _AT_REF_PATTERN.sub(_replace_match, message)
