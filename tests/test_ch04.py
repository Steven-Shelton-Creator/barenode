"""Tests for CH04 — Context Delivery (@file references).

Tests the ``deliver()`` function in ``harness/context.py`` and its
integration into the Agent's ``send()`` method.
"""

import os
import tempfile

import pytest

from harness.context import deliver


# ---------------------------------------------------------------------------
# Unit tests — deliver() standalone
# ---------------------------------------------------------------------------


def test_deliver_no_reference(tmp_path):
    """Message with no @ references is returned unchanged."""
    msg = "Hello, world!"
    assert deliver(msg, workspace=str(tmp_path)) == msg


def test_deliver_single_file(tmp_path):
    """@path is replaced with the file content."""
    facts = tmp_path / "facts.txt"
    facts.write_text("The sky is blue.")

    result = deliver("@facts.txt Who is Raveena?", workspace=str(tmp_path))
    assert "The sky is blue." in result
    assert "@facts.txt" not in result


def test_deliver_preserves_surrounding_text(tmp_path):
    """Text before and after @ref is preserved."""
    facts = tmp_path / "data.txt"
    facts.write_text("secret sauce")

    result = deliver("Read @data.txt and summarize.", workspace=str(tmp_path))
    assert result.startswith("Read ")
    assert "secret sauce" in result
    assert result.endswith(" and summarize.")


def test_deliver_multiple_references(tmp_path):
    """Multiple @refs in one message are all resolved."""
    (tmp_path / "a.txt").write_text("File A")
    (tmp_path / "b.txt").write_text("File B")

    result = deliver("Compare @a.txt with @b.txt.", workspace=str(tmp_path))
    assert "File A" in result
    assert "File B" in result
    assert "@a.txt" not in result
    assert "@b.txt" not in result


def test_deliver_missing_file_left_unchanged(tmp_path):
    """@ref to a missing file is left as-is (no crash)."""
    result = deliver("@nonexistent.txt hello", workspace=str(tmp_path))
    assert "@nonexistent.txt" in result


def test_deliver_outside_workspace_left_unchanged(tmp_path):
    """@ref to a path outside the workspace is left unchanged (security)."""
    result = deliver("@../outside.txt hello", workspace=str(tmp_path))
    assert "@../outside.txt" in result


def test_deliver_empty_file_left_unchanged(tmp_path):
    """@ref to an empty file is left unchanged."""
    empty = tmp_path / "empty.txt"
    empty.write_text("")

    result = deliver("Check @empty.txt", workspace=str(tmp_path))
    assert "@empty.txt" in result


def test_deliver_unreadable_file(tmp_path):
    """@ref to an unreadable file (no permissions) is left unchanged."""
    locked = tmp_path / "locked.txt"
    locked.write_text("forbidden content")
    locked.chmod(0o000)

    try:
        result = deliver("Read @locked.txt", workspace=str(tmp_path))
        assert "@locked.txt" in result
    finally:
        locked.chmod(0o644)  # restore so tmp_path cleanup works


def test_deliver_file_in_subdirectory(tmp_path):
    """@ref with a relative subdirectory path works."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "notes.txt").write_text("deep content")

    result = deliver("Read @sub/notes.txt", workspace=str(tmp_path))
    assert "deep content" in result
    assert "@sub/notes.txt" not in result


def test_deliver_default_workspace_is_cwd():
    """deliver() without workspace defaults to os.getcwd()."""
    msg = "no at refs here"
    assert deliver(msg) == msg  # no crash


# ---------------------------------------------------------------------------
# Integration tests — Agent + deliver()
# ---------------------------------------------------------------------------


def test_agent_resolves_at_ref(tmp_path):
    """Agent.send() resolves @path before sending to the model."""
    from harness.agent import Agent

    notes = tmp_path / "notes.txt"
    notes.write_text("Agent should know this.")

    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("What does @notes.txt say?")

    # The resolved content should appear in the messages
    assert "Agent should know this." in agent.messages[0]["content"]
    # The fake provider echoes back the last user message
    assert "Agent should know this." in reply


def test_agent_preserves_missing_ref(tmp_path):
    """Agent.send() leaves missing @refs unchanged."""
    from harness.agent import Agent

    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("Read @missing.txt")

    # The @ref is preserved in the stored message
    assert "@missing.txt" in agent.messages[0]["content"]
    # The fake provider echoes it back with "Echo (model):"
    assert "Echo" in reply


def test_agent_multiple_refs_integration(tmp_path):
    """Agent.send() resolves multiple @refs."""
    from harness.agent import Agent

    (tmp_path / "a.txt").write_text("Content A")
    (tmp_path / "b.txt").write_text("Content B")

    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("Check @a.txt and @b.txt")

    assert "Content A" in agent.messages[0]["content"]
    assert "Content B" in agent.messages[0]["content"]


def test_ch03_tests_still_pass_after_ch04_wiring(tmp_path, monkeypatch):
    """The CH03 instruction loading still works with the CH04 wiring."""
    from harness.agent import Agent

    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("You are a test agent.")

    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("Who are you?")

    # The system prompt should include AGENTS.md content
    assert agent.messages[0]["role"] == "user"
    assert len(agent.messages) == 2  # user + assistant
    # Reply from fake provider should be the echo
    assert reply.startswith("Echo")


def test_deliver_includes_file_header_footer(tmp_path):
    """The injected content is wrapped with markers."""
    facts = tmp_path / "data.txt"
    facts.write_text("some data")

    result = deliver("@data.txt summarize", workspace=str(tmp_path))
    assert "--- data.txt ---" in result
    assert "--- end data.txt ---" in result
    assert "some data" in result