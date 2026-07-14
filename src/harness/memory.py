"""Memory — JSONL session persistence, keyword search (CH09).

The harness writes each session to disk as a JSONL file (one message
per line).  Sessions survive process restarts — kill and resume.

Episodic search uses plain keyword matching across stored sessions.
No embeddings, no vector database — just human-readable JSONL files.
"""

import json
import os
import glob
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default directory for session files
DEFAULT_SESSION_DIR = os.path.join(os.getcwd(), "logs")


# ---------------------------------------------------------------------------
# Session file helpers
# ---------------------------------------------------------------------------

def _session_path(session_name: str, session_dir: str | None = None) -> str:
    """Return the full path to a session JSONL file."""
    if session_dir is None:
        session_dir = DEFAULT_SESSION_DIR
    os.makedirs(session_dir, exist_ok=True)
    return os.path.join(session_dir, f"{session_name}.jsonl")


def _message_to_line(msg: dict) -> str:
    """Serialize a single message dict to a JSONL line (with a timestamp)."""
    lined = dict(msg)
    if "timestamp" not in lined:
        lined["timestamp"] = datetime.now(timezone.utc).isoformat()
    return json.dumps(lined, ensure_ascii=False)


def _line_to_message(line: str) -> dict | None:
    """Deserialize a single JSONL line to a message dict."""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_session(session_name: str, messages: list[dict], session_dir: str | None = None) -> str:
    """Save messages to a session file.

    Writes one JSON line per message.  Appends if the file already
    exists (does not overwrite — call ``clear_session()`` first if
    you want a fresh start).

    Parameters
    ----------
    session_name : str
        Name of the session (used as the filename stem).
    messages : list[dict]
        List of message dicts to persist.
    session_dir : str or None
        Directory for session files.  Defaults to ``logs/``.

    Returns
    -------
    str
        Path to the saved session file.
    """
    path = _session_path(session_name, session_dir)
    with open(path, "w", encoding="utf-8") as f:
        for msg in messages:
            f.write(_message_to_line(msg) + "\n")
    return path


def load_session(session_name: str, session_dir: str | None = None) -> list[dict]:
    """Load messages from a session file.

    Parameters
    ----------
    session_name : str
        Name of the session.
    session_dir : str or None
        Directory for session files.  Defaults to ``logs/``.

    Returns
    -------
    list[dict]
        List of message dicts.  Empty list if the file doesn't exist.
    """
    path = _session_path(session_name, session_dir)
    if not os.path.isfile(path):
        return []

    messages: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            msg = _line_to_message(line)
            if msg is not None:
                messages.append(msg)
    return messages


def clear_session(session_name: str, session_dir: str | None = None) -> None:
    """Delete a session file.

    Parameters
    ----------
    session_name : str
        Name of the session.
    session_dir : str or None
        Directory for session files.
    """
    path = _session_path(session_name, session_dir)
    if os.path.isfile(path):
        os.remove(path)


def list_sessions(session_dir: str | None = None) -> list[str]:
    """List all available session names.

    Parameters
    ----------
    session_dir : str or None
        Directory for session files.  Defaults to ``logs/``.

    Returns
    -------
    list[str]
        Sorted list of session names (without the ``.jsonl`` extension).
    """
    if session_dir is None:
        session_dir = DEFAULT_SESSION_DIR
    if not os.path.isdir(session_dir):
        return []

    sessions = []
    for fname in sorted(glob.glob(os.path.join(session_dir, "*.jsonl"))):
        name, _ = os.path.splitext(os.path.basename(fname))
        sessions.append(name)
    return sessions


# ---------------------------------------------------------------------------
# Keyword search
# ---------------------------------------------------------------------------

def search_sessions(
    query: str,
    session_dir: str | None = None,
    max_results: int = 5,
) -> list[dict]:
    """Search all session files for a keyword.

    Performs a simple case-insensitive substring match on message
    content.  Returns matching messages grouped by session.

    Parameters
    ----------
    query : str
        The keyword or phrase to search for.
    session_dir : str or None
        Directory for session files.  Defaults to ``logs/``.
    max_results : int
        Maximum number of matching messages to return.

    Returns
    -------
    list[dict]
        A list of matching message dicts, each augmented with a
        ``_session`` key indicating which session it came from.
        Ordered by timestamp descending (newest first).
    """
    if session_dir is None:
        session_dir = DEFAULT_SESSION_DIR
    if not os.path.isdir(session_dir):
        return []

    query_lower = query.lower()
    results: list[dict] = []

    for session_name in list_sessions(session_dir):
        messages = load_session(session_name, session_dir)
        for msg in messages:
            content = msg.get("content", "") or ""
            if query_lower in content.lower():
                hit = dict(msg)
                hit["_session"] = session_name
                results.append(hit)

    # Sort by timestamp descending (newest first)
    results.sort(
        key=lambda m: m.get("timestamp", ""),
        reverse=True,
    )

    return results[:max_results]