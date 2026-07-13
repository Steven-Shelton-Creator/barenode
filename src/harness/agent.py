"""Agent — the harness core.

The agent keeps a ``self.messages`` list that grows with every turn.
Instructions (system prompt + AGENTS.md) are prepended before each
call but are **not** stored in ``self.messages`` — they're rebuilt
fresh on every turn.
"""

import os

from model.provider import chat
from harness.instructions import build_system_message


class Agent:
    """A coding agent with conversation memory and instructions.

    Parameters
    ----------
    model : str
        Model spec in ``provider/model`` format (default from env var
        ``BARENODE_MODEL`` or ``ollama/gemma4:e4b``).
    workspace : str or None
        Workspace directory for file operations and AGENTS.md lookup.
        Defaults to current working directory.
    """

    def __init__(
        self,
        model: str | None = None,
        workspace: str | None = None,
    ) -> None:
        self.model = model or os.environ.get(
            "BARENODE_MODEL", "ollama/gemma4:e4b"
        )
        self.workspace = workspace or os.getcwd()
        self.messages: list[dict] = []

    def send(self, message: str) -> str:
        """Append a user message and return the model's reply.

        The full message history plus the system instruction message
        is sent with every call.  The instruction message is rebuilt
        fresh each time and is **not** appended to ``self.messages``.
        """
        self.messages.append({"role": "user", "content": message})

        # Build the messages to send: system prompt + conversation
        sys_msg = build_system_message(self.workspace)
        messages_to_send = (
            [sys_msg] + self.messages if sys_msg else self.messages
        )

        reply = chat(self.model, messages_to_send)
        self.messages.append({"role": "assistant", "content": reply})
        return reply