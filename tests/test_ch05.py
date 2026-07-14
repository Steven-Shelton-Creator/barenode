"""Tests for CH05 — Tools.

Tests the tool registry, built-in tools, approval gate, and the
agent's tool loop integration.
"""

import os
import json
import tempfile

import pytest

from harness.tools import Tool, ToolRegistry, default_registry
from harness.approval import prompt_approval
from harness.agent import Agent
from model.provider import fake_set_next_tool_calls


# =========================================================================
# Tool dataclass
# =========================================================================


def test_tool_dataclass() -> None:
    """Tool can be created with all required fields."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters={"type": "object", "properties": {}},
        fn=lambda: "result",
    )
    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert tool.requires_approval is False


def test_tool_default_approval() -> None:
    """requires_approval defaults to False."""
    tool = Tool(
        name="safe_tool",
        description="Safe tool",
        parameters={"type": "object", "properties": {}},
        fn=lambda: "ok",
    )
    assert tool.requires_approval is False


def test_tool_with_approval() -> None:
    """requires_approval can be set to True."""
    tool = Tool(
        name="dangerous_tool",
        description="Dangerous tool",
        parameters={"type": "object", "properties": {}},
        fn=lambda: "ok",
        requires_approval=True,
    )
    assert tool.requires_approval is True


# =========================================================================
# ToolRegistry
# =========================================================================


def test_registry_register_and_get() -> None:
    """Register a tool and retrieve it by name."""
    registry = ToolRegistry()
    tool = Tool(
        name="greet",
        description="Say hello",
        parameters={"type": "object", "properties": {}},
        fn=lambda: "hello",
    )
    registry.register(tool)
    assert registry.get("greet") is tool
    assert registry.get("nonexistent") is None


def test_registry_duplicate_name() -> None:
    """Registering a duplicate tool name raises ValueError."""
    registry = ToolRegistry()
    tool = Tool(
        name="dup", description="", parameters={"type": "object", "properties": {}},
        fn=lambda: "",
    )
    registry.register(tool)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(tool)


def test_registry_specs_format() -> None:
    """specs() returns OpenAI-compatible tool definitions."""
    registry = ToolRegistry()
    tool = Tool(
        name="greet",
        description="Say hello to someone",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The name to greet"},
            },
            "required": ["name"],
        },
        fn=lambda name: f"Hello, {name}!",
    )
    registry.register(tool)

    specs = registry.specs()
    assert len(specs) == 1
    assert specs[0]["type"] == "function"
    assert specs[0]["function"]["name"] == "greet"
    assert specs[0]["function"]["description"] == "Say hello to someone"
    assert "parameters" in specs[0]["function"]


def test_registry_execute() -> None:
    """execute() runs the tool function and returns the result."""
    registry = ToolRegistry()
    tool = Tool(
        name="greet",
        description="Greet someone",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        },
        fn=lambda name: f"Hi, {name}!",
    )
    registry.register(tool)

    result = registry.execute("greet", {"name": "Alice"})
    assert result == "Hi, Alice!"


def test_registry_execute_unknown() -> None:
    """execute() returns an error message for unknown tools."""
    registry = ToolRegistry()
    result = registry.execute("ghost", {})
    assert "unknown tool" in result.lower()


def test_registry_requires_approval() -> None:
    """requires_approval() checks the tool's flag."""
    registry = ToolRegistry()
    safe = Tool(
        name="safe", description="", parameters={"type": "object", "properties": {}},
        fn=lambda: "",
    )
    risky = Tool(
        name="risky", description="", parameters={"type": "object", "properties": {}},
        fn=lambda: "", requires_approval=True,
    )
    registry.register(safe)
    registry.register(risky)

    assert registry.requires_approval("safe") is False
    assert registry.requires_approval("risky") is True
    assert registry.requires_approval("ghost") is False


def test_registry_names() -> None:
    """names() returns all registered tool names."""
    registry = ToolRegistry()
    registry.register(Tool(name="a", description="", parameters={"type": "object", "properties": {}}, fn=lambda: ""))
    registry.register(Tool(name="b", description="", parameters={"type": "object", "properties": {}}, fn=lambda: ""))
    assert set(registry.names()) == {"a", "b"}


def test_registry_execute_error_handling() -> None:
    """execute() catches exceptions from tool functions."""
    registry = ToolRegistry()

    def _broken(**kwargs):
        raise RuntimeError("something broke")

    registry.register(Tool(
        name="broken", description="", parameters={"type": "object", "properties": {}},
        fn=_broken,
    ))

    result = registry.execute("broken", {})
    assert "Error" in result
    assert "broken" in result.lower()
    assert "something broke" in result


# =========================================================================
# Calculator tool
# =========================================================================


def test_calculator_basic() -> None:
    """Calculator evaluates simple arithmetic."""
    registry = default_registry()
    result = registry.execute("calculator", {"expression": "2 + 2"})
    assert result == "4"


def test_calculator_complex() -> None:
    """Calculator handles complex expressions."""
    registry = default_registry()
    result = registry.execute("calculator", {"expression": "256 * 8"})
    assert result == "2048"


def test_calculator_sqrt() -> None:
    """Calculator supports math functions."""
    registry = default_registry()
    result = registry.execute("calculator", {"expression": "sqrt(16)"})
    assert result == "4.0"


def test_calculator_pi() -> None:
    """Calculator has access to math constants."""
    registry = default_registry()
    result = registry.execute("calculator", {"expression": "pi"})
    assert float(result) == pytest.approx(3.14159, rel=1e-4)


def test_calculator_safe_no_builtins() -> None:
    """Calculator doesn't have access to dangerous builtins."""
    registry = default_registry()
    result = registry.execute("calculator", {"expression": "__import__('os')"})
    assert "Error" in result


def test_calculator_invalid_expression() -> None:
    """Calculator gracefully handles invalid expressions."""
    registry = default_registry()
    result = registry.execute("calculator", {"expression": "not math"})
    assert "Error" in result


# =========================================================================
# Read file tool
# =========================================================================


def test_read_file(tmp_path) -> None:
    """read_file reads a file from the workspace."""
    notes = tmp_path / "notes.txt"
    notes.write_text("Hello, world!")

    registry = default_registry()
    result = registry.execute("read_file", {"path": "notes.txt", "workspace": str(tmp_path)})
    assert result == "Hello, world!"


def test_read_file_outside_workspace(tmp_path) -> None:
    """read_file rejects paths outside the workspace."""
    registry = default_registry()
    result = registry.execute("read_file", {"path": "../etc/passwd", "workspace": str(tmp_path)})
    assert "outside the workspace" in result.lower()


def test_read_file_missing(tmp_path) -> None:
    """read_file reports missing files gracefully."""
    registry = default_registry()
    result = registry.execute("read_file", {"path": "nope.txt", "workspace": str(tmp_path)})
    assert "not found" in result.lower()


# =========================================================================
# Write file tool
# =========================================================================


def test_write_file(tmp_path) -> None:
    """write_file writes content to a file in the workspace."""
    registry = default_registry()
    result = registry.execute("write_file", {
        "path": "output.txt",
        "content": "Hello, world!",
        "workspace": str(tmp_path),
    })
    assert "File written" in result
    assert (tmp_path / "output.txt").read_text() == "Hello, world!"


def test_write_file_outside_workspace(tmp_path) -> None:
    """write_file rejects paths outside the workspace."""
    registry = default_registry()
    result = registry.execute("write_file", {
        "path": "../escape.txt",
        "content": "oops",
        "workspace": str(tmp_path),
    })
    assert "outside the workspace" in result.lower()
    # The file should NOT exist
    assert not (tmp_path.parent / "escape.txt").exists()


def test_write_file_creates_dirs(tmp_path) -> None:
    """write_file creates parent directories automatically."""
    registry = default_registry()
    result = registry.execute("write_file", {
        "path": "sub/deep/file.txt",
        "content": "deep content",
        "workspace": str(tmp_path),
    })
    assert "File written" in result
    assert (tmp_path / "sub" / "deep" / "file.txt").read_text() == "deep content"


# =========================================================================
# Default registry
# =========================================================================


def test_default_registry_has_three_tools() -> None:
    """default_registry() has calculator, read_file, write_file."""
    registry = default_registry()
    names = registry.names()
    assert "calculator" in names
    assert "read_file" in names
    assert "write_file" in names


def test_write_file_requires_approval() -> None:
    """write_file requires approval."""
    registry = default_registry()
    assert registry.requires_approval("write_file") is True


def test_calculator_does_not_require_approval() -> None:
    """calculator does not require approval."""
    registry = default_registry()
    assert registry.requires_approval("calculator") is False


# =========================================================================
# Agent tool loop integration
# =========================================================================


def test_agent_without_tool_calls_returns_text() -> None:
    """When the model returns text, send() returns it directly."""
    agent = Agent(model="fake/echo")
    reply = agent.send("Hello!")
    assert reply.startswith("Echo")
    assert "Hello!" in reply


def test_agent_executes_single_tool_call(tmp_path) -> None:
    """When the model calls a tool, the agent executes the tool and stores the result."""
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

    agent.send("Calculate 2 + 2")
    # After the tool call, the agent executes it and stores the result in messages
    tool_contents = [m["content"] for m in agent.messages if m["role"] == "tool"]
    assert any("4" in c for c in tool_contents)


def test_agent_multiple_tool_calls(tmp_path) -> None:
    """Agent handles multiple tool calls in one response."""
    agent = Agent(model="fake/echo", workspace=str(tmp_path))

    fake_set_next_tool_calls([
        {
            "id": "call_01",
            "type": "function",
            "function": {
                "name": "calculator",
                "arguments": json.dumps({"expression": "2 + 2"}),
            },
        },
        {
            "id": "call_02",
            "type": "function",
            "function": {
                "name": "calculator",
                "arguments": json.dumps({"expression": "3 * 3"}),
            },
        },
    ])

    agent.send("Calculate two things")
    # Both tool calls execute and results are stored in messages
    tool_contents = [m["content"] for m in agent.messages if m["role"] == "tool"]
    assert any("4" in c for c in tool_contents)
    assert any("9" in c for c in tool_contents)
    assert len(tool_contents) == 2


def test_agent_tool_loop_completes_without_exceeding_cap(tmp_path) -> None:
    """Agent handles one tool call and returns the final text without hitting the cap."""
    agent = Agent(model="fake/echo", workspace=str(tmp_path))

    fake_set_next_tool_calls([
        {
            "id": "call_01",
            "type": "function",
            "function": {
                "name": "calculator",
                "arguments": json.dumps({"expression": "1 + 1"}),
            },
        }
    ])

    reply = agent.send("Keep calculating")
    # The tool call executes, result is stored, then the agent calls the model
    # again which echoes back
    tool_contents = [m["content"] for m in agent.messages if m["role"] == "tool"]
    assert any("2" in c for c in tool_contents)
    # The final reply should be from the second model call (echo)
    assert isinstance(reply, str)
    assert len(reply) > 0


def test_agent_tool_result_stored_in_messages(tmp_path) -> None:
    """Tool results are stored in self.messages as 'tool' role messages."""
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
    # The messages should include: user, assistant (tool_calls), tool (result), assistant (text)
    roles = [m["role"] for m in agent.messages]
    assert "tool" in roles


def test_agent_with_unknown_tool(tmp_path) -> None:
    """Unknown tool calls produce an error message in the messages."""
    agent = Agent(model="fake/echo", workspace=str(tmp_path))

    fake_set_next_tool_calls([
        {
            "id": "call_01",
            "type": "function",
            "function": {
                "name": "nonexistent_tool",
                "arguments": "{}",
            },
        }
    ])

    reply = agent.send("Use mystery tool")
    # The error message should be in the tool result messages
    tool_contents = [m["content"] for m in agent.messages if m["role"] == "tool"]
    assert any("unknown tool" in c.lower() or "nonexistent" in c.lower() for c in tool_contents)


# =========================================================================
# Approval gate integration
# =========================================================================


def test_write_file_requires_approval_in_registry() -> None:
    """write_file is flagged as requiring approval."""
    registry = default_registry()
    assert registry.requires_approval("write_file") is True


def test_calculator_no_approval_needed() -> None:
    """calculator does not require approval."""
    registry = default_registry()
    assert registry.requires_approval("calculator") is False


# =========================================================================
# CH01–CH04 regression tests
# =========================================================================


def test_ch01_regression() -> None:
    """CH01 stateless echo still works."""
    from harness.agent import Agent
    agent = Agent(model="fake/echo")
    reply = agent.send("hello")
    assert "hello" in reply


def test_ch02_regression() -> None:
    """CH02 history still grows correctly."""
    agent = Agent(model="fake/echo")
    agent.send("first")
    agent.send("second")
    assert len(agent.messages) == 4


def test_ch03_regression(tmp_path) -> None:
    """CH03 instructions still work with tools wired in."""
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("You are a test agent.")

    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("Who are you?")
    assert reply.startswith("Echo")


def test_ch04_regression(tmp_path) -> None:
    """CH04 @file references still work with tools wired in."""
    notes = tmp_path / "data.txt"
    notes.write_text("secret data")

    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("Read @data.txt")
    assert "secret data" in reply