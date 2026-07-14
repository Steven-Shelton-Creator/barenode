"""Tests for CH08 — Sandbox (Docker isolation + local fallback).

Tests the Sandbox class, bash tool integration, and workspace fencing.
"""

import os
import tempfile

import pytest

from harness.sandbox import Sandbox, SandboxResult


# =========================================================================
# Sandbox — basic execution
# =========================================================================


def test_sandbox_runs_echo() -> None:
    """Sandbox can run a simple echo command."""
    sandbox = Sandbox()
    result = sandbox.run('echo "hello sandbox"')
    assert "hello sandbox" in result.stdout
    assert result.exit_code == 0


def test_sandbox_works_with_cwd(tmp_path) -> None:
    """Sandbox runs commands relative to the workspace."""
    (tmp_path / "test.txt").write_text("sandbox content")
    sandbox = Sandbox(workspace=str(tmp_path))
    result = sandbox.run("cat test.txt")
    assert "sandbox content" in result.stdout


def test_sandbox_exit_code() -> None:
    """Sandbox returns non-zero exit codes for failing commands."""
    sandbox = Sandbox()
    result = sandbox.run("exit 42")
    assert result.exit_code != 0


def test_sandbox_returns_stderr() -> None:
    """Sandbox captures stderr output."""
    sandbox = Sandbox()
    result = sandbox.run("echo 'error msg' >&2")
    assert "error msg" in result.stderr


def test_sandbox_duration_is_positive() -> None:
    """Sandbox result includes a positive duration."""
    sandbox = Sandbox()
    result = sandbox.run("echo fast")
    assert result.duration > 0


# =========================================================================
# Sandbox — Docker-specific behavior
# =========================================================================


def test_sandbox_docker_method() -> None:
    """When Docker is available, the sandbox uses Docker."""
    sandbox = Sandbox()
    if sandbox.check():
        result = sandbox.run("echo docker test")
        assert result.method == "docker"
    else:
        pytest.skip("Docker not available")


def test_sandbox_docker_no_network() -> None:
    """Docker sandbox has no network access."""
    sandbox = Sandbox()
    if not sandbox.check():
        pytest.skip("Docker not available")
    result = sandbox.run("ping -c 1 8.8.8.8 2>&1 || true")
    # Should fail — no network
    assert "unreachable" in result.stdout.lower()


def test_sandbox_docker_read_only_rootfs() -> None:
    """Docker sandbox root filesystem is read-only."""
    sandbox = Sandbox()
    if not sandbox.check():
        pytest.skip("Docker not available")
    result = sandbox.run("touch /test-rootfs-write 2>&1 || true")
    # Should fail — read-only filesystem
    assert "read-only" in result.stdout.lower()


# =========================================================================
# Sandbox — workspace fencing (read_file already fenced since CH05)
# =========================================================================


def test_sandbox_cannot_escape_workspace(tmp_path) -> None:
    """Sandbox cannot access files outside the mounted workspace."""
    # Create a file outside the workspace
    outside = tmp_path.parent / "secret.txt"
    outside.write_text("should not be readable")

    sandbox = Sandbox(workspace=str(tmp_path))
    result = sandbox.run(f"cat {outside} 2>&1 || true")
    # The sandbox cannot see the file — either error or empty
    assert "should not be readable" not in result.stdout


# =========================================================================
# Bash tool integration
# =========================================================================


def test_bash_tool_in_default_registry() -> None:
    """bash tool is registered by default."""
    from harness.tools import default_registry
    registry = default_registry()
    assert "bash" in registry.names()


def test_bash_tool_requires_approval() -> None:
    """bash tool requires approval."""
    from harness.tools import default_registry
    registry = default_registry()
    assert registry.requires_approval("bash") is True


def test_bash_tool_runs_through_sandbox(tmp_path) -> None:
    """bash tool executes a command through the sandbox."""
    from harness.tools import default_registry
    registry = default_registry()
    result = registry.execute("bash", {"command": "echo hello from bash", "workspace": str(tmp_path)})
    assert "hello from bash" in result
    assert "sandbox" in result


# =========================================================================
# Agent integration
# =========================================================================


def test_agent_can_use_bash_tool(tmp_path, monkeypatch) -> None:
    """Agent can invoke the bash tool when the model calls for it."""
    from harness.agent import Agent
    from model.provider import fake_set_next_tool_calls
    import json

    # Auto-approve the approval gate for this test
    # Patch where it's imported (harness.agent), not where it's defined (harness.approval)
    monkeypatch.setattr("harness.agent.prompt_approval", lambda tool, summary: True)

    agent = Agent(model="fake/echo", workspace=str(tmp_path))

    fake_set_next_tool_calls([
        {
            "id": "call_bash",
            "type": "function",
            "function": {
                "name": "bash",
                "arguments": json.dumps({"command": "echo sandbox test"}),
            },
        }
    ])

    reply = agent.send("Run echo")
    # The tool result should be in the messages
    tool_contents = [m["content"] for m in agent.messages if m["role"] == "tool"]
    assert any("sandbox" in c.lower() for c in tool_contents)


# =========================================================================
# CH01–CH07 regression tests
# =========================================================================


def test_ch01_regression() -> None:
    """CH01 echo still works."""
    from harness.agent import Agent
    agent = Agent(model="fake/echo")
    reply = agent.send("hello")
    assert "hello" in reply


def test_ch05_tools_unchanged(tmp_path) -> None:
    """Existing tools still work with bash tool added."""
    from harness.tools import default_registry
    registry = default_registry()
    assert registry.execute("calculator", {"expression": "2+2"}) == "4"
    assert registry.requires_approval("write_file") is True
    assert registry.requires_approval("calculator") is False