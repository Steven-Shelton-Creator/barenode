"""barenode — An AI agent built from scratch, one primitive at a time."""

import sys


def repl() -> None:
    """REPL entry point (uv run agent)."""
    print("barenode REPL — type /help for commands, /quit to exit")
    print("(coming soon — checkout CH01 for the first primitive)")
    sys.exit(0)


def demo() -> None:
    """Scripted demo entry point (uv run demo)."""
    print("barenode demo — scripted walkthrough")
    print("(coming soon — each chapter tag adds a demoable primitive)")
    sys.exit(0)


if __name__ == "__main__":
    repl()