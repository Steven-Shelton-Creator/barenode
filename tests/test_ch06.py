"""Tests for CH06 — Context Management (compaction + clamping).

Tests the token estimator, clamp function, compact function, and
agent integration.
"""

import os
import json
import tempfile

import pytest

from harness.limits import (
    estimate_tokens,
    estimate_messages_tokens,
    is_budget_exceeded,
    MAX_CONTEXT_TOKENS,
    MAX_ITEM_CHARS,
)
from harness.compaction import clamp_content, compact
from harness.agent import Agent
from model.provider import fake_set_next_tool_calls


# =========================================================================
# Token estimation
# =========================================================================


def test_estimate_tokens_short_text() -> None:
    """Short text returns a small token estimate."""
    assert estimate_tokens("hello") == 1  # 4 chars -> 1 token


def test_estimate_tokens_empty() -> None:
    """Empty string returns 0 tokens."""
    assert estimate_tokens("") == 0


def test_estimate_tokens_long_text() -> None:
    """Longer text returns proportionally more tokens."""
    text = "hello world " * 100  # 1200 chars
    assert estimate_tokens(text) == 300  # 1200 // 4


def test_estimate_messages_tokens_empty() -> None:
    """Empty message list returns 0."""
    assert estimate_messages_tokens([]) == 0


def test_estimate_messages_tokens_single() -> None:
    """Single message estimates content + overhead."""
    msgs = [{"role": "user", "content": "hello"}]
    count = estimate_messages_tokens(msgs)
    assert count > 0
    assert count == estimate_tokens("hello") + 4  # content + overhead


def test_estimate_messages_tokens_includes_tool_calls() -> None:
    """Messages with tool_calls include function name/args in estimate."""
    msgs = [{
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": "call_01",
            "type": "function",
            "function": {"name": "calculator", "arguments": '{"expression": "2+2"}'},
        }],
    }]
    count = estimate_messages_tokens(msgs)
    # Should include content (None -> 0), tool call overhead, and structural overhead
    assert count >= 4  # at minimum structural overhead


def test_estimate_messages_tokens_overhead() -> None:
    """Each message has structural overhead in the estimate."""
    one = estimate_messages_tokens([{"role": "user", "content": "a"}])
    two = estimate_messages_tokens([{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}])
    # Two messages should be roughly double one (content + overhead x2)
    assert two > one


def test_is_budget_exceeded_under() -> None:
    """Messages under budget return False."""
    msgs = [{"role": "user", "content": "hi"}]
    assert is_budget_exceeded(msgs, budget=1000) is False


def test_is_budget_exceeded_over() -> None:
    """Messages over budget return True."""
    # Create a message large enough to exceed a tiny budget
    msgs = [{"role": "user", "content": "x" * 1000}]
    assert is_budget_exceeded(msgs, budget=10) is True


# =========================================================================
# Clamp
# =========================================================================


def test_clamp_short_content_unchanged() -> None:
    """Content under max_chars is not modified."""
    msgs = [{"role": "user", "content": "short"}]
    result = clamp_content(msgs, max_chars=100)
    assert result[0]["content"] == "short"


def test_clamp_long_content_truncated() -> None:
    """Content over max_chars is truncated with a note."""
    long_text = "x" * 1000
    msgs = [{"role": "user", "content": long_text}]
    result = clamp_content(msgs, max_chars=100)
    assert len(result[0]["content"]) < len(long_text)
    assert "truncated" in result[0]["content"]


def test_clamp_does_not_mutate_original() -> None:
    """clamp_content returns a new list, does not mutate."""
    msgs = [{"role": "user", "content": "x" * 500}]
    original_len = len(msgs[0]["content"])
    result = clamp_content(msgs, max_chars=100)
    assert len(msgs[0]["content"]) == original_len  # original unchanged
    assert result[0]["content"] != msgs[0]["content"]  # copy was clamped


def test_clamp_multiple_messages() -> None:
    """Multiple long messages are all clamped."""
    msgs = [
        {"role": "user", "content": "x" * 200},
        {"role": "assistant", "content": "y" * 200},
    ]
    result = clamp_content(msgs, max_chars=50)
    for msg in result:
        assert "truncated" in msg["content"]


# =========================================================================
# Compact
# =========================================================================


def test_compact_below_budget_unchanged() -> None:
    """Messages under budget are returned unchanged (after clamp)."""
    msgs = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    result = compact(msgs, budget=1000)
    assert len(result) == len(msgs)
    assert result[0]["content"] == "hi"


def test_compact_over_budget_compresses_middle() -> None:
    """Messages over budget have their middle compressed."""
    # Build a conversation that exceeds a small budget
    msgs = []
    for i in range(10):
        msgs.append({"role": "user", "content": f"message {i} " * 50})
        msgs.append({"role": "assistant", "content": f"response {i} " * 50})

    result = compact(msgs, budget=500, head_turns=1, tail_turns=2)
    # The result should have fewer messages than the original
    assert len(result) < len(msgs)
    # The summary note should be present
    contents = [m.get("content", "") for m in result]
    assert any("compressed" in c for c in contents)


def test_compact_preserves_head(tmp_path) -> None:
    """Head turns survive compaction."""
    msgs = [
        {"role": "user", "content": "HEAD_MARKER"},
        {"role": "assistant", "content": "head response"},
        {"role": "user", "content": "middle 1"},
        {"role": "assistant", "content": "mid response 1"},
        {"role": "user", "content": "middle 2"},
        {"role": "assistant", "content": "mid response 2"},
        {"role": "user", "content": "tail 1"},
        {"role": "assistant", "content": "tail response 1"},
    ]
    result = compact(msgs, budget=10, head_turns=1, tail_turns=1)
    # Head should survive
    contents = [m.get("content", "") for m in result]
    assert "HEAD_MARKER" in contents


def test_compact_preserves_tail(tmp_path) -> None:
    """Tail turns survive compaction."""
    msgs = [
        {"role": "user", "content": "head"},
        {"role": "assistant", "content": "head response"},
        {"role": "user", "content": "middle"},
        {"role": "assistant", "content": "mid response"},
        {"role": "user", "content": "TAIL_MARKER"},
        {"role": "assistant", "content": "tail response"},
    ]
    result = compact(msgs, budget=10, head_turns=1, tail_turns=1)
    contents = [m.get("content", "") for m in result]
    assert "TAIL_MARKER" in contents


def test_compact_few_turns_no_compression() -> None:
    """Fewer turns than head+tail results in no compression."""
    msgs = [
        {"role": "user", "content": "one"},
        {"role": "assistant", "content": "one response"},
    ]
    result = compact(msgs, budget=10, head_turns=2, tail_turns=2)
    # Not enough turns to have a middle, so unchanged
    assert len(result) == len(msgs)


def test_compact_empty_messages() -> None:
    """Empty message list returns empty list."""
    assert compact([]) == []


def test_compact_does_not_mutate_original() -> None:
    """compact returns a new list, does not mutate."""
    msgs = [{"role": "user", "content": "x" * 500}] * 10
    original_len = len(msgs)
    _ = compact(msgs, budget=100)
    assert len(msgs) == original_len  # unchanged


# =========================================================================
# Agent integration
# =========================================================================


def test_agent_send_does_not_break_with_compaction(tmp_path) -> None:
    """Agent.send() works with compaction wired in."""
    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("hello")
    assert reply.startswith("Echo")
    assert "hello" in reply


def test_agent_compaction_fires_when_over_budget(tmp_path, monkeypatch) -> None:
    """When the context budget is tiny, compaction fires."""
    monkeypatch.setenv("BARENODE_CONTEXT_BUDGET", "10")
    agent = Agent(model="fake/echo", workspace=str(tmp_path))

    # Build up a long history
    for i in range(20):
        agent.send(f"message {i} " * 50)

    # Compaction should have fired — look for the compressed note
    contents = [m.get("content", "") for m in agent.messages]
    assert any("compressed" in c for c in contents)


def test_agent_compaction_preserves_recent_context(tmp_path, monkeypatch) -> None:
    """After compaction, the agent still remembers the most recent context."""
    monkeypatch.setenv("BARENODE_CONTEXT_BUDGET", "10")
    agent = Agent(model="fake/echo", workspace=str(tmp_path))

    # Add many turns to trigger compaction
    for i in range(15):
        agent.send(f"spam {i}")

    # The last user message should survive in the tail
    last_user = next(
        (m["content"] for m in reversed(agent.messages) if m["role"] == "user"),
        ""
    )
    assert "spam 14" in last_user or "spam 14" in str(agent.messages)


def test_agent_tool_loop_still_works_after_compaction(tmp_path) -> None:
    """Tool loop functions correctly when compaction is wired in."""
    agent = Agent(model="fake/echo", workspace=str(tmp_path))

    fake_set_next_tool_calls([
        {
            "id": "call_01",
            "type": "function",
            "function": {
                "name": "calculator",
                "arguments": json.dumps({"expression": "2 + 2"}),
            },
        }
    ])

    agent.send("Calculate")
    tool_contents = [m["content"] for m in agent.messages if m["role"] == "tool"]
    assert any("4" in c for c in tool_contents)


# =========================================================================
# CH01–CH05 regression tests
# =========================================================================


def test_ch01_regression() -> None:
    """CH01 stateless echo still works."""
    agent = Agent(model="fake/echo")
    reply = agent.send("hello")
    assert "hello" in reply


def test_ch02_regression() -> None:
    """CH02 history still grows."""
    agent = Agent(model="fake/echo")
    agent.send("first")
    agent.send("second")
    assert len(agent.messages) >= 4


def test_ch03_regression(tmp_path) -> None:
    """CH03 instructions still work."""
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("You are a test agent.")
    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("Who are you?")
    assert reply.startswith("Echo")


def test_ch04_regression(tmp_path) -> None:
    """CH04 @file references still work."""
    notes = tmp_path / "data.txt"
    notes.write_text("secret data")
    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("Read @data.txt")
    assert "secret data" in reply


def test_ch05_regression(tmp_path) -> None:
    """CH05 tool registry still works with compaction wired in."""
    registry_names = ["calculator", "read_file", "write_file"]
    for name in registry_names:
        agent = Agent(model="fake/echo", workspace=str(tmp_path))
        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("You are a test agent.")
        assert name in agent.tools.names()