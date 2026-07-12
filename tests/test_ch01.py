"""Tests for CH01 — the bare model call."""

from harness.agent import Agent


def test_agent_echoes_with_fake_provider() -> None:
    """Fake provider should echo the message back."""
    agent = Agent(model="fake/echo")
    response = agent.send("hello")
    assert "hello" in response
    assert "Echo" in response


def test_agent_is_stateless() -> None:
    """Each call is independent — no memory of previous turns."""
    agent = Agent(model="fake/echo")
    agent.send("remember that my name is Gemma")
    response = agent.send("what is my name?")
    # Fake provider doesn't carry state, so it won't know
    assert "Gemma" not in response


def test_agent_default_model() -> None:
    """Agent should use the default model when none is given."""
    agent = Agent()
    assert agent.model is not None
    assert "/" in agent.model  # must be provider/model format


def test_invalid_model_spec() -> None:
    """Bad model spec should raise a clear error."""
    import pytest
    from model.provider import chat

    with pytest.raises(ValueError, match="Invalid model spec"):
        chat("bad-spec", [{"role": "user", "content": "hello"}])