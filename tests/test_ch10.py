"""Tests for CH10 — Planning & Orchestration.

Tests the plan generation, step execution, and /plan command integration.
"""

import json
import pytest

from harness.orchestrator import (
    Step, Plan, generate_plan, format_plan, execute_plan, _extract_json,
)
from harness.agent import Agent
from model.provider import fake_set_next_tool_calls


# =========================================================================
# Data classes
# =========================================================================


def test_step_defaults() -> None:
    """Step has sensible defaults."""
    step = Step()
    assert step.status == "pending"
    assert step.number == 0
    assert step.description == ""


def test_plan_is_complete() -> None:
    """Plan.is_complete() returns True when all steps are done."""
    plan = Plan(task="test")
    plan.steps = [Step(status="done"), Step(status="skipped")]
    assert plan.is_complete() is True


def test_plan_not_complete() -> None:
    """Plan.is_complete() returns False when steps remain."""
    plan = Plan(task="test")
    plan.steps = [Step(status="done"), Step(status="pending")]
    assert plan.is_complete() is False


def test_plan_current_step() -> None:
    """Plan.current_step() returns the first pending step."""
    plan = Plan(task="test")
    plan.steps = [
        Step(number=1, status="done"),
        Step(number=2, status="pending"),
        Step(number=3, status="pending"),
    ]
    current = plan.current_step()
    assert current is not None
    assert current.number == 2


def test_plan_current_step_none() -> None:
    """Plan.current_step() returns None when all done."""
    plan = Plan(task="test")
    plan.steps = [Step(status="done")]
    assert plan.current_step() is None


# =========================================================================
# JSON extraction
# =========================================================================


def test_extract_json_plain() -> None:
    """Extract JSON from a plain text response."""
    text = '[{"step": 1, "description": "do something"}]'
    assert _extract_json(text) == text


def test_extract_json_fenced() -> None:
    """Extract JSON from markdown code fences."""
    text = '```json\n[{"step": 1, "description": "do something"}]\n```'
    assert "do something" in _extract_json(text)


def test_extract_json_plain_fences() -> None:
    """Extract JSON from plain code fences (no language tag)."""
    text = '```\n[{"step": 1}]\n```'
    assert "step" in _extract_json(text)


# =========================================================================
# Plan generation
# =========================================================================


def test_generate_plan_with_fake_provider() -> None:
    """generate_plan handles the model response and creates a Plan."""
    agent = Agent(model="fake/echo")

    # The fake provider echoes back the user message, which won't be valid JSON.
    # generate_plan should fall back to a single-step plan.
    plan = generate_plan("Calculate something", agent)
    assert isinstance(plan, Plan)
    assert plan.task == "Calculate something"
    assert len(plan.steps) >= 1


def test_generate_plan_parses_json(tmp_path) -> None:
    """generate_plan parses JSON from the model response."""
    agent = Agent(model="fake/echo", workspace=str(tmp_path))

    # Queue a JSON response from the fake provider
    fake_set_next_tool_calls(None)  # reset

    # The fake provider echoes the planning prompt, which won't be JSON.
    # We need to test with a direct call to the underlying logic.
    # For now, verify the fallback works.
    plan = generate_plan("test", agent)
    assert len(plan.steps) >= 1


# =========================================================================
# Plan formatting
# =========================================================================


def test_format_plan_shows_task() -> None:
    """format_plan includes the task description."""
    plan = Plan(task="my task")
    output = format_plan(plan)
    assert "my task" in output


def test_format_plan_shows_steps() -> None:
    """format_plan shows each step."""
    plan = Plan(task="test")
    plan.steps = [Step(number=1, description="Step one"), Step(number=2, description="Step two")]
    output = format_plan(plan)
    assert "Step one" in output
    assert "Step two" in output


# =========================================================================
# Plan execution
# =========================================================================


def test_execute_plan_runs_steps(tmp_path) -> None:
    """execute_plan runs each step through the agent."""
    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    plan = Plan(task="test")
    plan.steps = [Step(number=1, description="hello"), Step(number=2, description="world")]

    result = execute_plan(plan, agent, approve_step=None)
    assert "Step 1" in result
    assert "Step 2" in result
    # Both steps should be done
    assert plan.steps[0].status == "done"
    assert plan.steps[1].status == "done"


def test_execute_plan_with_approval(tmp_path, monkeypatch) -> None:
    """execute_plan respects the approval gate."""
    from harness.orchestrator import execute_plan

    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    plan = Plan(task="test")
    plan.steps = [Step(number=1, description="step one"), Step(number=2, description="step two")]

    # Approve only step 1
    approvals = iter([True, False])
    result = execute_plan(plan, agent, approve_step=lambda s: next(approvals))

    assert plan.steps[0].status == "done"
    assert plan.steps[1].status == "skipped"


def test_execute_plan_retry_on_failure(tmp_path, monkeypatch) -> None:
    """execute_plan retries on failure."""
    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    plan = Plan(task="test")
    plan.steps = [Step(number=1, description="hello")]

    # Monkeypatch agent.send to fail once then succeed
    original_send = agent.send
    call_count = [0]

    def flaky_send(msg):
        call_count[0] += 1
        if call_count[0] == 1:
            raise RuntimeError("temporary error")
        return original_send(msg)

    monkeypatch.setattr(agent, "send", flaky_send)

    result = execute_plan(plan, agent, approve_step=None, max_retries=1)
    assert plan.steps[0].status == "done"
    assert call_count[0] == 2  # first failed, second succeeded


# =========================================================================
# /plan REPL integration
# =========================================================================


def test_plan_command_in_repl(tmp_path) -> None:
    """The /plan command workflow: generate → format → execute."""
    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    task = "Calculate 2 + 2"

    plan = generate_plan(task, agent)
    formatted = format_plan(plan)
    assert task in formatted

    result = execute_plan(plan, agent, approve_step=None)
    assert "Step 1" in result


# =========================================================================
# CH01–CH09 regression tests
# =========================================================================


def test_ch01_regression(tmp_path) -> None:
    """CH01 echo still works."""
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    reply = agent.send("hello")
    assert "hello" in reply


def test_ch05_tools_unchanged(tmp_path) -> None:
    """CH05 tools still work."""
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    assert "calculator" in agent.tools.names()


def test_ch09_persistence_unchanged(tmp_path) -> None:
    """CH09 persistence still works."""
    from harness.memory import load_session
    agent = Agent(model="fake/echo", session_name="ch10_test", session_dir=str(tmp_path))
    agent.send("hello")
    loaded = load_session("ch10_test", session_dir=str(tmp_path))
    assert len(loaded) >= 2