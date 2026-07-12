"""Agent — the harness core.

At CH01, the agent is deliberately minimal: a single send() call that
passes a message to the model and returns the response.  No history,
no tools, no context management — those come in later chapters.

The agent is stateless.  Every call is independent.
"""

from model.provider import chat


class Agent:
    """A bare-bones coding agent.

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

    def send(self, message: str) -> str:
        """Send a single message and return the model's reply.

        This is a *stateless* call — the model has no memory of
        previous messages.  History is added in CH02.
        """
        return chat(self.model, message)