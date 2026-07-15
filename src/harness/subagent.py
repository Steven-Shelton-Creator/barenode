"""Subagents — fresh agent per subtask, delegate + fan_out (CH11).

Every step in a plan shares a single context window.  A big job might
pollute it with many tool calls and dead ends.  Subagents give each
subtask its own clean context.

Design
------
- ``run_subagent()`` — builds a fresh ``Agent``, sends one message,
  returns just the text reply.  The subtask's entire transcript is
  discarded after execution — only the final answer survives.
- ``delegate`` tool — single subtask, returns the answer.
- ``fan_out`` tool — batch of subtasks, runs in parallel via
  ``ThreadPoolExecutor``, returns answers in order.
- Context isolation is a feature: one subtask never sees another's
  reasoning or the parent's history.
"""

import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from harness.agent import Agent


# ---------------------------------------------------------------------------
# Internal counter for unique subagent session names
# ---------------------------------------------------------------------------

_subagent_counter = 0
_counter_lock = threading.Lock()


def _next_session_name() -> str:
    """Return a unique session name for a subagent."""
    global _subagent_counter
    with _counter_lock:
        _subagent_counter += 1
        return f"subagent_{_subagent_counter}"


# ---------------------------------------------------------------------------
# Subagent runner
# ---------------------------------------------------------------------------

def run_subagent(
    message: str,
    model: str | None = None,
    workspace: str | None = None,
) -> str:
    """Run a single subtask in a fresh agent and return the text reply.

    The subagent has its own clean context (empty message list) and its
    own unique session name to avoid file collisions.  After execution,
    only the text reply is returned — the subtask's transcript is
    discarded.

    Parameters
    ----------
    message : str
        The task to give to the subagent.
    model : str or None
        Model spec for the subagent.  Defaults to the ``BARENODE_MODEL``
        env var (same pattern as the parent agent).
    workspace : str or None
        Workspace directory.  Defaults to current working directory.

    Returns
    -------
    str
        The subagent's text reply.
    """
    agent = Agent(
        model=model,
        workspace=workspace,
        session_name=_next_session_name(),
    )
    return agent.send(message)


# ---------------------------------------------------------------------------
# Delegate tool — single subtask
# ---------------------------------------------------------------------------

def delegate(task: str) -> str:
    """Delegate a single subtask to a fresh agent.

    Parameters
    ----------
    task : str
        The task description for the subagent.

    Returns
    -------
    str
        The subagent's response.
    """
    try:
        result = run_subagent(task)
        return f"[Subagent result]\n{result}"
    except Exception as exc:
        return f"[Subagent error] {exc}"


# ---------------------------------------------------------------------------
# Fan-out tool — parallel subtasks
# ---------------------------------------------------------------------------

def fan_out(tasks: list[str]) -> str:
    """Delegate multiple subtasks to fresh agents in parallel.

    Each subtask runs in its own agent with isolated context.  Results
    are returned in the same order as the input tasks.  If a subtask
    fails, its error is included in place of the result — other
    subtasks are unaffected.

    Parameters
    ----------
    tasks : list of str
        A list of task descriptions, one per subagent.

    Returns
    -------
    str
        A formatted string listing each subtask's result in order.
    """
    if not tasks:
        return "No tasks provided."

    model = os.environ.get("BARENODE_MODEL")
    workspace = os.getcwd()

    results: dict[int, str] = {}

    def _run_one(index: int, task: str) -> tuple[int, str]:
        try:
            agent = Agent(
                model=model,
                workspace=workspace,
                session_name=_next_session_name(),
            )
            reply = agent.send(task)
            return index, f"  Subagent {index + 1}: {reply}"
        except Exception as exc:
            return index, f"  Subagent {index + 1}: [error] {exc}"

    with ThreadPoolExecutor(max_workers=min(len(tasks), 10)) as pool:
        futures = [pool.submit(_run_one, i, t) for i, t in enumerate(tasks)]
        for future in as_completed(futures):
            idx, line = future.result()
            results[idx] = line

    # Build ordered output
    lines = ["[Fan-out results]"]
    for i in range(len(tasks)):
        lines.append(results.get(i, f"  Subagent {i + 1}: [error] no result"))
    return "\n".join(lines)