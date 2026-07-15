"""Tests for CH12 — Self-Verification.

Tests the verification gate: detecting code file writes, parsing test
commands from AGENTS.md, checking test results, and the agent integration.
"""

import os
import pytest

from harness.verify import (
    CODE_EXTENSIONS,
    parse_test_command,
    _get_tool_call_path,
    was_code_file_written,
    check_test_result,
    build_verification_prompt,
)
from harness.agent import Agent
from model.provider import fake_set_next_tool_calls, fake_set_next_tool_result


# =========================================================================
# CODE_EXTENSIONS
# =========================================================================


def test_code_extensions_contains_py() -> None:
    """CODE_EXTENSIONS includes .py files."""
    assert ".py" in CODE_EXTENSIONS


def test_code_extensions_contains_md() -> None:
    """CODE_EXTENSIONS includes documentation files."""
    assert ".md" in CODE_EXTENSIONS


def test_code_extensions_contains_js() -> None:
    """CODE_EXTENSIONS includes JavaScript files."""
    assert ".js" in CODE_EXTENSIONS


def test_code_extensions_does_not_contain_txt() -> None:
    """CODE_EXTENSIONS does not include plain text."""
    assert ".txt" not in CODE_EXTENSIONS


# =========================================================================
# parse_test_command
# =========================================================================


def test_parse_test_command_found(tmp_path) -> None:
    """parse_test_command extracts the command from AGENTS.md."""
    agents_md = """# Agent

## Behavior

Be helpful.

## Testing

Run the automated test suite:

```bash
uv run pytest tests/ -v
```
"""
    agents_path = tmp_path / "AGENTS.md"
    agents_path.write_text(agents_md)

    cmd = parse_test_command(str(tmp_path))
    assert cmd == "uv run pytest tests/ -v"


def test_parse_test_command_no_section(tmp_path) -> None:
    """parse_test_command returns None when no Testing section exists."""
    agents_md = "# Agent\n\nBe helpful.\n"
    agents_path = tmp_path / "AGENTS.md"
    agents_path.write_text(agents_md)

    cmd = parse_test_command(str(tmp_path))
    assert cmd is None


def test_parse_test_command_no_file(tmp_path) -> None:
    """parse_test_command returns None when AGENTS.md doesn't exist."""
    cmd = parse_test_command(str(tmp_path))
    assert cmd is None


def test_parse_test_command_empty_command(tmp_path) -> None:
    """parse_test_command returns None when the code block is empty."""
    agents_md = """## Testing

```bash
```
"""
    agents_path = tmp_path / "AGENTS.md"
    agents_path.write_text(agents_md)

    cmd = parse_test_command(str(tmp_path))
    assert cmd is None


# =========================================================================
# _get_tool_call_path
# =========================================================================


def test_get_tool_call_path_from_string_args() -> None:
    """Extract path from string JSON arguments."""
    tc = {"function": {"name": "write_file", "arguments": '{"path": "src/main.py"}'}}
    assert _get_tool_call_path(tc) == "src/main.py"


def test_get_tool_call_path_from_dict_args() -> None:
    """Extract path from dict arguments."""
    tc = {"function": {"name": "write_file", "arguments": {"path": "test.py"}}}
    assert _get_tool_call_path(tc) == "test.py"


def test_get_tool_call_path_no_path() -> None:
    """Return None when no path argument."""
    tc = {"function": {"name": "calculator", "arguments": '{"expression": "2+2"}'}}
    assert _get_tool_call_path(tc) is None


def test_get_tool_call_path_invalid_json() -> None:
    """Return None when arguments is not valid JSON."""
    tc = {"function": {"name": "write_file", "arguments": "not-json"}}
    assert _get_tool_call_path(tc) is None


# =========================================================================
# was_code_file_written
# =========================================================================


def test_was_code_file_written_py_file() -> None:
    """Detect a .py file written via write_file."""
    tool_calls = [
        {"function": {"name": "write_file", "arguments": '{"path": "src/main.py", "content": "print(1)"}'}},
    ]
    assert was_code_file_written(tool_calls) is True


def test_was_code_file_written_txt_file() -> None:
    """Ignore .txt files."""
    tool_calls = [
        {"function": {"name": "write_file", "arguments": '{"path": "notes.txt", "content": "hello"}'}},
    ]
    assert was_code_file_written(tool_calls) is False


def test_was_code_file_written_not_write_file() -> None:
    """Ignore non-write_file tool calls."""
    tool_calls = [
        {"function": {"name": "calculator", "arguments": '{"expression": "2+2"}'}},
    ]
    assert was_code_file_written(tool_calls) is False


def test_was_code_file_written_mixed() -> None:
    """Detect code file even when mixed with other tools."""
    tool_calls = [
        {"function": {"name": "calculator", "arguments": '{"expression": "2+2"}'}},
        {"function": {"name": "write_file", "arguments": '{"path": "test.py", "content": "x=1"}'}},
        {"function": {"name": "read_file", "arguments": '{"path": "README.md"}'}},
    ]
    assert was_code_file_written(tool_calls) is True


def test_was_code_file_written_empty_list() -> None:
    """Empty list returns False."""
    assert was_code_file_written([]) is False


# =========================================================================
# check_test_result
# =========================================================================


def test_check_test_result_pass() -> None:
    """Exit 0 — no [exit code:] marker means success."""
    result = "All tests passed!\n[sandbox: local, 0.50s]"
    assert check_test_result(result) is True


def test_check_test_result_fail() -> None:
    """Non-zero exit code is detected."""
    result = "FAILED test.py::test_something\n[exit code: 1]\n[sandbox: local, 0.30s]"
    assert check_test_result(result) is False


def test_check_test_result_no_sandbox_marker() -> None:
    """No sandbox marker at all — assume success."""
    result = "everything works"
    assert check_test_result(result) is True


# =========================================================================
# build_verification_prompt
# =========================================================================


def test_build_verification_prompt_contains_command() -> None:
    """Prompt includes the test command."""
    prompt = build_verification_prompt("uv run pytest")
    assert "uv run pytest" in prompt


def test_build_verification_prompt_contains_verification_label() -> None:
    """Prompt includes the [Verification required] label."""
    prompt = build_verification_prompt("uv run pytest")
    assert "[Verification required]" in prompt


# =========================================================================
# Agent integration — verification gate
# =========================================================================


def test_agent_starts_without_verification(tmp_path) -> None:
    """Agent has no verification state by default."""
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    assert agent._pending_verification is False
    assert agent._test_command is None


def test_agent_arms_verification_on_code_write(tmp_path, monkeypatch) -> None:
    """Agent arms verification after a write_file with a .py extension."""
    monkeypatch.setattr("harness.agent.prompt_approval", lambda *a, **kw: True)

    # Create AGENTS.md with a testing section so parse_test_command works
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("## Testing\n\n```bash\nuv run pytest tests/ -v\n```\n")

    agent = Agent(model="fake/echo", workspace=str(tmp_path), session_dir=str(tmp_path))

    # Simulate the model writing a .py file
    fake_set_next_tool_calls([
        {
            "id": "call_1",
            "type": "function",
            "function": {
                "name": "write_file",
                "arguments": '{"path": "test.py", "content": "x = 1"}',
            },
        },
    ])
    fake_set_next_tool_result("File written: test.py")

    # The fake provider will return the tool calls, then the agent will
    # execute them and check for code file writes
    agent.send("write a test file")

    # After the tool call, verification should have been armed
    # The agent may have injected the prompt already, so _verification_waiting
    # may be True (prompt injected, waiting for test result)
    assert agent._test_command is not None
    assert agent._pending_verification is True or agent._verification_waiting is True


def test_agent_skips_verification_for_non_code(tmp_path, monkeypatch) -> None:
    """Agent does not arm verification for non-code file writes."""
    monkeypatch.setattr("harness.agent.prompt_approval", lambda *a, **kw: True)
    agent = Agent(model="fake/echo", workspace=str(tmp_path), session_dir=str(tmp_path))

    fake_set_next_tool_calls([
        {
            "id": "call_1",
            "type": "function",
            "function": {
                "name": "write_file",
                "arguments": '{"path": "notes.txt", "content": "hello"}',
            },
        },
    ])
    fake_set_next_tool_result("File written: notes.txt")

    agent.send("write a note")

    # Verification should not be armed for .txt files
    assert agent._test_command is None or agent._pending_verification is False


# =========================================================================
# Regression tests
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


def test_ch11_subagents_unchanged(tmp_path) -> None:
    """CH11 subagent tools still work."""
    agent = Agent(model="fake/echo", session_dir=str(tmp_path))
    assert "delegate" in agent.tools.names()
    assert "fan_out" in agent.tools.names()