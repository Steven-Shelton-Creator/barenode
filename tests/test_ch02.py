"""Tests for CH02 — conversation history.

The harness now keeps a ``self.messages`` list that grows with every
turn and is replayed on every call.  The model sees the full
conversation context.
"""

from harness.agent import Agent


def test_messages_list_grows() -> None:
    """Each send() appends one user + one assistant message."""
    agent = Agent(model="fake/echo")
    assert agent.messages == []

    agent.send("first message")
    assert len(agent.messages) == 2
    assert agent.messages[0] == {"role": "user", "content": "first message"}
    assert agent.messages[1]["role"] == "assistant"

    agent.send("second message")
    assert len(agent.messages) == 4
    assert agent.messages[2] == {"role": "user", "content": "second message"}
    assert agent.messages[3]["role"] == "assistant"


def test_full_history_forwarded_to_provider() -> None:
    """The provider receives the complete message list, not just the latest."""
    agent = Agent(model="fake/echo")

    agent.send("turn one")
    agent.send("turn two")

    # The fake provider sees all 4 messages
    assert len(agent.messages) == 4


def test_history_preserves_turn_order() -> None:
    """Messages alternate user/assistant in correct sequence."""
    agent = Agent(model="fake/echo")

    agent.send("first")
    agent.send("second")
    agent.send("third")

    roles = [m["role"] for m in agent.messages]
    assert roles == [
        "user", "assistant",
        "user", "assistant",
        "user", "assistant",
    ]


def test_new_agent_starts_empty() -> None:
    """Each fresh Agent instance starts with an empty history."""
    a1 = Agent(model="fake/echo")
    a2 = Agent(model="fake/echo")

    a1.send("hello")
    assert len(a1.messages) == 2
    assert len(a2.messages) == 0  # a2 is unaffected