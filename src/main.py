"""barenode — CLI entry points.

Usage
-----
    uv run agent          # interactive REPL
    uv run demo           # scripted demo
    uv run plan           # planning demo
"""

import os
import sys

from harness.agent import Agent
from harness.orchestrator import generate_plan, format_plan, execute_plan


_APPROVE_STEP = None  # set to a function to gate approvals


def _approve_step(step) -> bool:
    """Prompt the user for step approval."""
    print(f"\n[APPROVAL] Step {step.number}: {step.description}", file=sys.stderr)
    print("  Execute this step? (y/n): ", end="", file=sys.stderr)
    try:
        raw = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        return False
    return raw in ("y", "yes")


def repl() -> None:
    """Interactive REPL — ``uv run agent``."""
    model = os.environ.get("BARENODE_MODEL", "ollama/gemma4:e4b")
    agent = Agent(model=model)
    print("Type /quit to exit.  Type /plan <task> to plan and execute.")

    while True:
        try:
            raw = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        msg = raw.strip()
        if not msg:
            continue
        if msg in ("/quit", "/exit"):
            break

        try:
            if msg.startswith("/plan "):
                task = msg[6:].strip()
                if not task:
                    print("Usage: /plan <task description>")
                    continue
                print(f"\nGenerating plan for: {task}")
                plan = generate_plan(task, agent)
                print()
                print(format_plan(plan))
                print()
                result = execute_plan(plan, agent, approve_step=_approve_step)
                print(result)
            else:
                response = agent.send(msg)
                print(response)
        except Exception as exc:
            print(f"[error] {exc}")


def demo() -> None:
    """Scripted demo — ``uv run demo``."""
    print("barenode demo — CH10 (Planning)")
    print("=" * 40)

    model = os.environ.get("BARENODE_MODEL", "fake/echo")
    agent = Agent(model=model)

    # Demo: /plan
    task = "Calculate 256 * 8, then add 100"
    print(f"\n> /plan {task}")
    plan = generate_plan(task, agent)
    print()
    print(format_plan(plan))
    print()
    result = execute_plan(plan, agent, approve_step=None)
    print(result)

    print("\n" + "=" * 40)
    print("Plan executed.")


if __name__ == "__main__":
    repl()