"""Self-verification gate (CH12).

Reads the [testing] section from agents.md and runs the configured command.
"""

import sys


def run() -> None:
    """Run the verification suite (uv run verify)."""
    print("barenode verify — test suite")
    print("(coming soon — CH12 adds the self-verification gate)")
    sys.exit(0)


if __name__ == "__main__":
    run()