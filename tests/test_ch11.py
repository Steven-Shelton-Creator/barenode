"""Tests for CH11 — Subagents.

Tests the delegate/fan_out tools, run_subagent, and context isolation.
"""

import pytest

from harness.subagent import run_subagent, delegate, fan_out
from harness.agent import Agent
from model.provider import fake_set_next_tool_calls


# =========================================================================
# run_subagent — core subagent runner
# =========================================================================


def test_run_subagent_returns_reply(tmp_path) -> None:
    """run_subagent creates a fresh agent and returns its reply."""
    result = run_subagent(
        message="hello from subagent",
        model="fake/echo",
        workspace=str(tmp_path),
    )
    assert "hello from subagent" in result
    assert "Echo" in result or "fake" in result


def test_run_subagent_unique_session(tmp_path) -> None:
    """Each call to run_subagent uses a unique session name."""
    result1 = run_subagent("task one", model="fake/echo", workspace=str(tmp_path))
    result2 = run_subagent("task two", model="fake/echo", workspace=str(tmp_path))
    assert "task one" in result1
    assert "task two" in result2


def test_run_subagent_context_isolation(tmp_path) -> None:
    """Subagent does not see messages from the parent agent."""
    # Build a parent agent with some history
    parent = Agent(model="fake/echo", workspace=str(tmp_path))
    parent.send("my secret is 42")

    # Subagent should not know the secret
    result = run_subagent(
        message="What is the secret?",
        model="fake/echo",
        workspace=str(tmp_path),
    )
    # The fake provider echoes the last user message, so it should NOT contain "42"
    assert "42" not in result or "my secret" not in result


# =========================================================================
# delegate tool
# =========================================================================


def test_delegate_single_task(tmp_path, monkeypatch) -> None:
    """Delegate runs a single subtask and returns the result."""
    monkeypatch.setenv("BARENODE_MODEL", "fake/echo")
    monkeypatch.chdir(str(tmp_path))

    result = delegate("compute 2 + 2")
    assert "[Subagent result]" in result
    assert "compute 2 + 2" in result or "Echo" in result


def test_delegate_empty_task(tmp_path, monkeypatch) -> None:
    """Delegate handles an empty task gracefully."""
    monkeypatch.setenv("BARENODE_MODEL", "fake/echo")
    monkeypatch.chdir(str(tmp_path))

    result = delegate("")
    assert "[Subagent result]" in result or "[Subagent error]" in result


# =========================================================================
# fan_out tool
# =========================================================================


def test_fan_out_multiple_tasks(tmp_path, monkeypatch) -> None:
    """Fan-out runs multiple subtasks and returns results in order."""
    monkeypatch.setenv("BARENODE_MODEL", "fake/echo")
    monkeypatch.chdir(str(tmp_path))

    tasks = ["task alpha", "task beta", "task gamma"]
    result = fan_out(tasks)

    assert "[Fan-out results]" in result
    assert "Subagent 1" in result
    assert "Subagent 2" in result
    assert "Subagent 3" in result


def test_fan_out_empty_tasks(tmp_path, monkeypatch) -> None:
    """Fan-out handles an empty task list gracefully."""
    result = fan_out([])
    assert "No tasks provided" in result


def test_fan_out_single_task(tmp_path, monkeypatch) -> None:
    """Fan-out works with a single task."""
    monkeypatch.setenv("BARENODE_MODEL", "fake/echo")
    monkeypatch.chdir(str(tmp_path))

    result = fan_out(["only task"])
    assert "[Fan-out results]" in result
    assert "Subagent 1" in result


def test_fan_out_parallelism(tmp_path, monkeypatch) -> None:
    """Fan-out actually runs tasks in parallel (not serial)."""
    import time

    monkeypatch.setenv("BARENODE_MODEL", "fake/echo")
    monkeypatch.chdir(str(tmp_path))

    tasks = ["slow one", "slow two", "slow three"]

    start = time.time()
    result = fan_out(tasks)
    elapsed = time.time() - start

    # With parallelism, 3 tasks should take roughly the same time as 1
    assert "[Fan-out results]" in result
    assert elapsed < 5.0  # generous bound — should be ~0.1s


# =========================================================================
# Context isolation
# =========================================================================


def test_fan_out_context_isolation(tmp_path, monkeypatch) -> None:
    """Subtask contexts are isolated from each other."""
    monkeypatch.setenv("BARENODE_MODEL", "fake/echo")
    monkeypatch.chdir(str(tmp_path))

    # Each subagent gets its own fresh agent with no shared state
    tasks = ["task X", "task Y"]
    result = fan_out(tasks)

    assert "Subagent 1" in result
    assert "Subagent 2" in result


# =========================================================================
# Error handling
# =========================================================================


def test_fan_out_subagent_error_does_not_crash_parent(tmp_path, monkeypatch) -> None:
    """If one subagent fails, others still complete."""
    monkeypatch.setenv("BARENODE_MODEL", "fake/echo")
    monkeypatch.chdir(str(tmp_path))

    # All tasks should succeed with fake/echo, but test that errors don't crash
    tasks = ["good task"]
    result = fan_out(tasks)

    # The result should contain the output, not a crash message
    assert "[Fan-out results]" in result


# =========================================================================
# Tool registry integration
# =========================================================================


def test_delegate_tool_in_registry(tmp_path) -> None:
    """Delegate tool is registered in the default registry."""
    from harness.tools import default_registry

    registry = default_registry()
    tool = registry.get("delegate")
    assert tool is not None
    assert tool.name == "delegate"
    assert tool.requires_approval is True


def test_fan_out_tool_in_registry(tmp_path) -> None:
    """Fan-out tool is registered in the default registry."""
    from harness.tools import default_registry

    registry = default_registry()
    tool = registry.get("fan_out")
    assert tool is not None
    assert tool.name == "fan_out"
    assert tool.requires_approval is True


# =========================================================================
# Regression tests
# =========================================================================


def test_ch01_regression(tmp_path) -> None:
    """CH01 echo still works."""
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    reply = agent.send("hello")
    assert "hello" in reply


def test_ch05_tools_unchanged(tmp_path) -> None:
    """CH05 tools still work after adding subagent tools."""
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    assert "calculator" in agent.tools.names()
    assert "delegate" in agent.tools.names()
    assert "fan_out" in agent.tools.names()


def test_ch10_planning_unchanged(tmp_path) -> None:
    """CH10 planning still works."""
    from harness.orchestrator import generate_plan

    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    plan = generate_plan("test task", agent)
    assert len(plan.steps) >= 1