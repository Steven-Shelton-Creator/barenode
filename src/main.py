"""barenode — CLI entry points.

Usage
-----
    uv run agent          # interactive REPL
    uv run demo           # scripted demo
"""

import os
import sys

from harness.agent import Agent


def repl() -> None:
    """Interactive REPL — ``uv run agent``."""
    model = os.environ.get("BARENODE_MODEL", "ollama/qwen2.5:8b")
    agent = Agent(model=model)

    print(f"barenode [{model}]")
    print("Type /quit to exit.")

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
            response = agent.send(msg)
            print(response)
        except Exception as exc:
            print(f"[error] {exc}")


def demo() -> None:
    """Scripted demo — ``uv run demo``."""
    print("barenode demo — CH02")
    print("=" * 40)

    model = os.environ.get("BARENODE_MODEL", "fake/echo")
    agent = Agent(model=model)

    messages = [
        "Hello! What is your name?",
        "My name is Gemma.",
        "What is my name?",
    ]

    for i, msg in enumerate(messages):
        print(f"\n> {msg}")
        try:
            print(agent.send(msg))
        except Exception as exc:
            print(f"[error] {exc}")

    print("\n" + "=" * 40)
    print(f"History now contains {len(agent.messages)} messages.")
    print("The harness replays the full conversation on every call.")
    print("With a real model, the agent would 'remember' your name.")


if __name__ == "__main__":
    repl()