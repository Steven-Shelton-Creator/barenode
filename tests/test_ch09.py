"""Tests for CH09 — Durable State / Memory (JSONL session persistence).

Tests the session save/load/clear/search functions, and the agent's
session load/save integration.
"""

import os
import json
import tempfile

import pytest

from harness.memory import (
    save_session,
    load_session,
    clear_session,
    list_sessions,
    search_sessions,
    DEFAULT_SESSION_DIR,
)
from harness.agent import Agent


# =========================================================================
# Session persistence
# =========================================================================


def test_save_and_load(tmp_path) -> None:
    """Save messages and load them back."""
    msgs = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi there"},
    ]
    path = save_session("test_save", msgs, session_dir=str(tmp_path))
    assert os.path.isfile(path)

    loaded = load_session("test_save", session_dir=str(tmp_path))
    assert len(loaded) == 2
    assert loaded[0]["content"] == "hello"
    assert loaded[1]["content"] == "hi there"


def test_load_nonexistent(tmp_path) -> None:
    """load_session returns empty list for missing file."""
    loaded = load_session("nonexistent", session_dir=str(tmp_path))
    assert loaded == []


def test_save_jsonl_format(tmp_path) -> None:
    """Saved file is valid JSONL (one JSON object per line)."""
    msgs = [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "second"},
    ]
    path = save_session("test_format", msgs, session_dir=str(tmp_path))

    with open(path) as f:
        lines = f.readlines()

    assert len(lines) == 2
    for line in lines:
        obj = json.loads(line)
        assert "role" in obj
        assert "content" in obj
        assert "timestamp" in obj


def test_save_overwrites(tmp_path) -> None:
    """save_session overwrites the file (does not append)."""
    save_session("test_overwrite", [{"role": "user", "content": "old"}], session_dir=str(tmp_path))
    save_session("test_overwrite", [{"role": "user", "content": "new"}], session_dir=str(tmp_path))

    loaded = load_session("test_overwrite", session_dir=str(tmp_path))
    assert len(loaded) == 1
    assert loaded[0]["content"] == "new"


def test_clear_session(tmp_path) -> None:
    """clear_session removes the session file."""
    save_session("test_clear", [{"role": "user", "content": "x"}], session_dir=str(tmp_path))
    clear_session("test_clear", session_dir=str(tmp_path))
    assert load_session("test_clear", session_dir=str(tmp_path)) == []


# =========================================================================
# List sessions
# =========================================================================


def test_list_sessions(tmp_path) -> None:
    """list_sessions returns all session names."""
    save_session("alpha", [{"role": "user", "content": "a"}], session_dir=str(tmp_path))
    save_session("beta", [{"role": "user", "content": "b"}], session_dir=str(tmp_path))

    sessions = list_sessions(session_dir=str(tmp_path))
    assert "alpha" in sessions
    assert "beta" in sessions


def test_list_sessions_empty(tmp_path) -> None:
    """list_sessions returns empty list for empty directory."""
    assert list_sessions(session_dir=str(tmp_path)) == []


def test_list_sessions_missing_dir(tmp_path) -> None:
    """list_sessions returns empty list for non-existent directory."""
    assert list_sessions(session_dir=str(tmp_path / "nope")) == []


# =========================================================================
# Keyword search
# =========================================================================


def test_search_sessions(tmp_path) -> None:
    """search_sessions finds matching messages."""
    save_session("s1", [
        {"role": "user", "content": "The secret code is 42."},
        {"role": "assistant", "content": "Got it."},
    ], session_dir=str(tmp_path))
    save_session("s2", [
        {"role": "user", "content": "What is the weather?"},
    ], session_dir=str(tmp_path))

    results = search_sessions("secret", session_dir=str(tmp_path))
    assert len(results) == 1
    assert results[0]["_session"] == "s1"
    assert "42" in results[0]["content"]


def test_search_sessions_no_match(tmp_path) -> None:
    """search_sessions returns empty list when no match."""
    save_session("s1", [{"role": "user", "content": "hello"}], session_dir=str(tmp_path))
    results = search_sessions("zzz_nonexistent_zzz", session_dir=str(tmp_path))
    assert results == []


def test_search_sessions_case_insensitive(tmp_path) -> None:
    """Search is case-insensitive."""
    save_session("s1", [{"role": "user", "content": "SECRET"}], session_dir=str(tmp_path))
    results = search_sessions("secret", session_dir=str(tmp_path))
    assert len(results) == 1


def test_search_sessions_max_results(tmp_path) -> None:
    """search_sessions respects max_results."""
    save_session("s1", [
        {"role": "user", "content": "secret one"},
        {"role": "user", "content": "secret two"},
        {"role": "user", "content": "secret three"},
    ], session_dir=str(tmp_path))

    results = search_sessions("secret", session_dir=str(tmp_path), max_results=2)
    assert len(results) <= 2


# =========================================================================
# Agent integration
# =========================================================================


def test_agent_loads_session_on_init(tmp_path) -> None:
    """Agent loads existing messages from disk on init."""
    # Save a session first
    save_session("test_agent_load", [
        {"role": "user", "content": "persisted message"},
    ], session_dir=str(tmp_path))

    agent = Agent(
        model="fake/echo",
        session_name="test_agent_load",
        session_dir=str(tmp_path),
    )
    assert len(agent.messages) == 1
    assert agent.messages[0]["content"] == "persisted message"


def test_agent_saves_after_send(tmp_path) -> None:
    """Agent saves messages after each send()."""
    agent = Agent(
        model="fake/echo",
        session_name="test_agent_save",
        session_dir=str(tmp_path),
    )
    agent.send("hello")

    loaded = load_session("test_agent_save", session_dir=str(tmp_path))
    assert len(loaded) >= 2  # user + assistant
    assert loaded[0]["content"] == "hello"


def test_agent_session_survives_restart(tmp_path) -> None:
    """Messages persist across agent restarts."""
    # First agent instance
    agent1 = Agent(
        model="fake/echo",
        session_name="test_restart",
        session_dir=str(tmp_path),
    )
    agent1.send("my name is TestBot")

    # Second agent instance (simulates restart)
    agent2 = Agent(
        model="fake/echo",
        session_name="test_restart",
        session_dir=str(tmp_path),
    )
    assert len(agent2.messages) >= 2
    assert any("TestBot" in m.get("content", "") for m in agent2.messages)


def test_agent_session_name_from_env(monkeypatch, tmp_path) -> None:
    """Session name can be set via BARENODE_SESSION env var."""
    monkeypatch.setenv("BARENODE_SESSION", "env_session")
    # The conftest.py sets BARENODE_SESSION for each test,
    # so we need to use a workspace-based session_dir to isolate
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    assert agent.session_name == "env_session"


# =========================================================================
# CH01–CH08 regression tests
# =========================================================================


def test_ch01_regression(tmp_path) -> None:
    """CH01 echo still works with persistence."""
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    reply = agent.send("hello")
    assert "hello" in reply


def test_ch05_tools_unchanged(tmp_path) -> None:
    """CH05 tools still work with persistence."""
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    assert "calculator" in agent.tools.names()


def test_ch06_compaction_still_works(tmp_path, monkeypatch) -> None:
    """CH06 compaction still works with persistence."""
    monkeypatch.setenv("BARENODE_CONTEXT_BUDGET", "10")
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    for i in range(10):
        agent.send(f"spam {i} " * 20)
    contents = [m.get("content", "") for m in agent.messages]
    assert any("compressed" in c for c in contents)


def test_ch08_bash_tool_available(tmp_path) -> None:
    """CH08 bash tool is still registered."""
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    assert "bash" in agent.tools.names()