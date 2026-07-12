"""Agent — the harness core.

At CH01, the agent is deliberately minimal: a single send() call that
passes a message to the model and returns the response.  No history,
no tools, no context management — those come in later chapters.

The agent is stateless.  Every call is independent.
"""

from model.provider import chat


class Agent:
    """A coding agent with conversation memory.

    Keeps a ``self.messages`` list that grows with every turn and is
    replayed on every call so the model appears to "remember" the
    conversation.

    Parameters
    ----------
    model : str
        Model spec in ``provider/model`` format (default from env var
        ``BARENODE_MODEL`` or ``ollama/qwen2.5:8b``).
    """

    def __init__(self, model: str | None = None) -> None:
        import os
        self.model = model or os.environ.get(
            "BARENODE_MODEL", "ollama/qwen2.5:8b"
        )
        self.messages: list[dict] = []

    def send(self, message: str) -> str:
        """Append a user message to the conversation and return the model's reply.

        The full message history is sent with every call so the model
        has context from previous turns.
        """
        self.messages.append({"role": "user", "content": message})
        reply = chat(self.model, self.messages)
        self.messages.append({"role": "assistant", "content": reply})
        return reply