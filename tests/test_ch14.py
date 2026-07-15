"""Tests for CH14 — Terminal UI.

Tests the widgets, app structure, and integration.
Note: Full TUI testing would require a terminal emulator.
These tests verify the components can be imported and constructed.
"""

import pytest
from unittest.mock import MagicMock, patch

from ui.widgets import (
    ConversationPane,
    TraceStreamPane,
    ApprovalModal,
    BarenodeAppLayout,
    _truncate,
    _format_timestamp,
)
from ui.app import AgentRunner, BarenodeApp


# =========================================================================
# Utility functions
# =========================================================================


def test_truncate_short() -> None:
    """Short text is not truncated."""
    assert _truncate("hello") == "hello"


def test_truncate_long() -> None:
    """Long text is truncated with ellipsis."""
    long = "x" * 3000
    result = _truncate(long, max_len=100)
    assert len(result) == 103  # 100 + "..."
    assert result.endswith("...")


def test_truncate_exact() -> None:
    """Text at exactly max_len is not truncated."""
    exact = "x" * 100
    result = _truncate(exact, max_len=100)
    assert len(result) == 100
    assert result == exact


def test_format_timestamp() -> None:
    """Timestamp returns a formatted string."""
    ts = _format_timestamp()
    assert len(ts) == 8  # HH:MM:SS
    assert ":" in ts


# =========================================================================
# AgentRunner
# =========================================================================


def test_agent_runner_creates_agent() -> None:
    """AgentRunner creates an Agent instance."""
    runner = AgentRunner(model="fake/echo")
    assert runner.agent is not None
    assert runner.agent.model == "fake/echo"


def test_agent_runner_send(tmp_path, monkeypatch) -> None:
    """AgentRunner.send() returns a reply."""
    monkeypatch.setattr("harness.agent.prompt_approval", lambda *a, **kw: True)
    runner = AgentRunner(model="fake/echo")
    runner.agent.session_dir = str(tmp_path)
    reply = runner.send("hello")
    assert reply is not None
    assert "hello" in reply


def test_agent_runner_get_conversation(tmp_path, monkeypatch) -> None:
    """AgentRunner returns the conversation history."""
    monkeypatch.setattr("harness.agent.prompt_approval", lambda *a, **kw: True)
    runner = AgentRunner(model="fake/echo")
    runner.agent.session_dir = str(tmp_path)
    runner.send("first")
    runner.send("second")
    conv = runner.get_conversation()
    assert len(conv) >= 4  # 2 user + 2 assistant messages


def test_agent_runner_get_trace_spans(tmp_path, monkeypatch) -> None:
    """AgentRunner returns serialized trace spans."""
    monkeypatch.setattr("harness.agent.prompt_approval", lambda *a, **kw: True)
    runner = AgentRunner(model="fake/echo")
    runner.agent.session_dir = str(tmp_path)
    runner.send("hello")
    spans = runner.get_trace_spans()
    # The trace is flushed after send(), so spans may be empty
    # But at minimum it should return a list
    assert isinstance(spans, list)


# =========================================================================
# UI Component construction
# =========================================================================


def test_conversation_pane_can_be_constructed() -> None:
    """ConversationPane can be instantiated."""
    pane = ConversationPane()
    assert pane is not None


def test_trace_stream_pane_can_be_constructed() -> None:
    """TraceStreamPane can be instantiated."""
    pane = TraceStreamPane()
    assert pane is not None


def test_approval_modal_can_be_constructed() -> None:
    """ApprovalModal can be instantiated."""
    modal = ApprovalModal(tool_name="write_file", summary="write test.py")
    assert modal is not None
    assert modal.tool_name == "write_file"


def test_approval_modal_with_diff() -> None:
    """ApprovalModal builds a diff when content is provided."""
    modal = ApprovalModal(
        tool_name="write_file",
        summary="write test.py",
        path="test.py",
        content="print('hello')",
        existing="",
    )
    diff = modal._build_diff()
    assert "test.py" in diff
    assert "hello" in diff


def test_barenode_app_layout_can_be_constructed() -> None:
    """BarenodeAppLayout can be instantiated."""
    layout = BarenodeAppLayout()
    assert layout is not None


# =========================================================================
# BarenodeApp
# =========================================================================


def test_barenode_app_instantiation() -> None:
    """BarenodeApp can be instantiated."""
    app = BarenodeApp()
    assert app is not None
    assert app.runner is not None


# =========================================================================
# Regression tests
# =========================================================================


def test_ch01_regression(tmp_path, monkeypatch) -> None:
    """CH01 echo still works through the runner."""
    monkeypatch.setattr("harness.agent.prompt_approval", lambda *a, **kw: True)
    runner = AgentRunner(model="fake/echo")
    runner.agent.session_dir = str(tmp_path)
    reply = runner.send("hello")
    assert "hello" in reply


def test_ch05_tools_unchanged(tmp_path, monkeypatch) -> None:
    """CH05 tools still work through the runner."""
    monkeypatch.setattr("harness.agent.prompt_approval", lambda *a, **kw: True)
    runner = AgentRunner(model="fake/echo")
    runner.agent.session_dir = str(tmp_path)
    assert "calculator" in runner.agent.tools.names()


def test_ch13_tracer_unchanged(tmp_path, monkeypatch) -> None:
    """CH13 tracer still works through the runner."""
    monkeypatch.setattr("harness.agent.prompt_approval", lambda *a, **kw: True)
    runner = AgentRunner(model="fake/echo")
    runner.agent.session_dir = str(tmp_path)
    runner.send("hello")
    assert hasattr(runner.agent, "tracer")