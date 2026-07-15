"""Tools — tool registry, function + schema definitions (CH05).

A tool is a function with a JSON schema that the model can invoke.
The harness decides *how* to run it; the model decides *what* to call.

Design
------
- ``Tool`` dataclass: name, description, parameters (JSON schema), fn, requires_approval
- ``ToolRegistry``: stores tools, provides OpenAI-compatible specs, dispatches calls
- Built-in tools: calculator (safe), read_file (approval), write_file (approval)
"""

import os
import math
from dataclasses import dataclass, field
from typing import Any, Callable

from harness.sandbox import Sandbox


# ---------------------------------------------------------------------------
# Tool definition
# ---------------------------------------------------------------------------

@dataclass
class Tool:
    """A single tool the model can invoke.

    Attributes
    ----------
    name : str
        Unique tool name (used by the model to call it).
    description : str
        Description of what the tool does (shown to the model).
    parameters : dict
        JSON Schema dict describing the tool's parameters.
    fn : Callable
        The Python function that implements the tool.
        Receives keyword arguments matching the schema.
    requires_approval : bool
        Whether the tool requires human approval before execution.
    needs_workspace : bool
        Whether the tool needs the ``workspace`` path injected by the
        harness.  File tools (read_file, write_file) set this to True.
    """

    name: str
    description: str
    parameters: dict
    fn: Callable[..., str]
    requires_approval: bool = False
    needs_workspace: bool = False


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Registry of tools available to the agent.

    The registry provides:
    - Registration via ``register()``
    - OpenAI-compatible tool specs via ``specs()``
    - Execution via ``execute()``
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool.

        Parameters
        ----------
        tool : Tool
            The tool to register.

        Raises
        ------
        ValueError
            If a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Get a tool by name.

        Parameters
        ----------
        name : str
            The tool name.

        Returns
        -------
        Tool or None
            The tool, or ``None`` if not found.
        """
        return self._tools.get(name)

    def specs(self) -> list[dict]:
        """Return OpenAI-compatible tool specifications.

        These are passed to the model on every turn so it knows
        which tools are available.

        Returns
        -------
        list[dict]
            A list of tool spec dicts in OpenAI-compatible format.
        """
        result = []
        for tool in self._tools.values():
            result.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            })
        return result

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool by name with the given arguments.

        Parameters
        ----------
        name : str
            The tool name.
        arguments : dict
            Keyword arguments to pass to the tool function.

        Returns
        -------
        str
            The tool's output as a string.

        Raises
        ------
        ValueError
            If the tool is not found.
        """
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: unknown tool '{name}'."
        try:
            result = tool.fn(**arguments)
            return str(result)
        except Exception as exc:
            return f"Error executing '{name}': {exc}"

    def requires_approval(self, name: str) -> bool:
        """Check whether a tool requires human approval.

        Parameters
        ----------
        name : str
            The tool name.

        Returns
        -------
        bool
            ``True`` if the tool requires approval.
        """
        tool = self._tools.get(name)
        return tool.requires_approval if tool else False

    def needs_workspace(self, name: str) -> bool:
        """Check whether a tool needs the workspace path injected.

        Parameters
        ----------
        name : str
            The tool name.

        Returns
        -------
        bool
            ``True`` if the tool needs workspace injection.
        """
        tool = self._tools.get(name)
        return tool.needs_workspace if tool else False

    def names(self) -> list[str]:
        """Return the list of registered tool names."""
        return list(self._tools.keys())


# ---------------------------------------------------------------------------
# Built-in tools
# ---------------------------------------------------------------------------

def _calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Uses only Python's ``math`` module and basic arithmetic operators.
    No arbitrary code execution.

    Parameters
    ----------
    expression : str
        The mathematical expression to evaluate (e.g. ``"256 * 8"``).

    Returns
    -------
    str
        The result of the expression.
    """
    # Build a safe evaluation environment
    allowed_names = {
        "abs": abs, "round": round, "int": int, "float": float,
        "min": min, "max": max, "sum": sum,
        "pi": math.pi, "e": math.e,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "floor": math.floor, "ceil": math.ceil,
        "pow": pow,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as exc:
        return f"Error: {exc}"


_CALCULATOR_TOOL = Tool(
    name="calculator",
    description="Evaluate a mathematical expression. Supports +, -, *, /, **, sqrt, sin, cos, etc.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate (e.g. '256 * 8').",
            },
        },
        "required": ["expression"],
    },
    fn=_calculator,
    requires_approval=False,
    needs_workspace=False,
)


def _read_file(path: str, workspace: str) -> str:
    """Read a file from the workspace directory.

    Parameters
    ----------
    path : str
        Relative path to the file within the workspace.
    workspace : str
        The workspace directory (injected by the harness).

    Returns
    -------
    str
        The file contents.
    """
    full_path = os.path.abspath(os.path.join(workspace, path))

    # Security: file must be inside workspace
    if not full_path.startswith(os.path.abspath(workspace) + os.sep):
        return f"Error: path '{path}' is outside the workspace."

    if not os.path.isfile(full_path):
        return f"Error: file '{path}' not found."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as exc:
        return f"Error reading '{path}': {exc}"


_READ_FILE_TOOL = Tool(
    name="read_file",
    description="Read the contents of a file from the workspace. The path must be relative to the workspace.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the file within the workspace.",
            },
        },
        "required": ["path"],
    },
    fn=_read_file,
    requires_approval=False,
    needs_workspace=True,
)


def _write_file(path: str, content: str, workspace: str) -> str:
    """Write content to a file in the workspace directory.

    Parameters
    ----------
    path : str
        Relative path to the file within the workspace.
    content : str
        The content to write.
    workspace : str
        The workspace directory (injected by the harness).

    Returns
    -------
    str
        Confirmation message.
    """
    full_path = os.path.abspath(os.path.join(workspace, path))

    # Security: file must be inside workspace
    if not full_path.startswith(os.path.abspath(workspace) + os.sep):
        return f"Error: path '{path}' is outside the workspace."

    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File written: {path}"
    except OSError as exc:
        return f"Error writing '{path}': {exc}"


_WRITE_FILE_TOOL = Tool(
    name="write_file",
    description="Write content to a file in the workspace. Creates parent directories if needed.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the file within the workspace.",
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file.",
            },
        },
        "required": ["path", "content"],
    },
    fn=_write_file,
    requires_approval=True,
    needs_workspace=True,
)


# ---------------------------------------------------------------------------
# Bash tool (runs through sandbox)
# ---------------------------------------------------------------------------


def _bash(command: str, workspace: str) -> str:
    """Run a shell command through the sandbox.

    Parameters
    ----------
    command : str
        The shell command to execute.
    workspace : str
        The workspace directory (injected by the harness).

    Returns
    -------
    str
        The command output (stdout + stderr).
    """
    sandbox = Sandbox(workspace=workspace)
    result = sandbox.run(command)

    output = result.stdout
    if result.stderr:
        output += f"\n[stderr]\n{result.stderr}"
    if result.exit_code != 0:
        output += f"\n[exit code: {result.exit_code}]"

    output += f"\n[sandbox: {result.method}, {result.duration:.2f}s]"
    return output.strip()


_BASH_TOOL = Tool(
    name="bash",
    description="Run a shell command. The command runs inside an isolated sandbox (Docker if available, local subprocess otherwise).",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute (e.g. 'ls -la').",
            },
        },
        "required": ["command"],
    },
    fn=_bash,
    requires_approval=True,
    needs_workspace=True,
)


# ---------------------------------------------------------------------------
# Default registry
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Delegate tool (CH11 — single subtask)
# ---------------------------------------------------------------------------


def _run_delegate(task: str) -> str:
    """Lazy-import wrapper for delegate to avoid circular imports."""
    from harness.subagent import delegate as _delegate
    return _delegate(task)


_DELEGATE_TOOL = Tool(
    name="delegate",
    description="Delegate a single subtask to a fresh agent with its own clean context. "
                "Use this when a task is self-contained and would pollute the main context. "
                "The subagent will run independently and return its answer.",
    parameters={
        "type": "object",
        "properties": {
            "task": {
                "type": "string",
                "description": "The task description to delegate to the subagent.",
            },
        },
        "required": ["task"],
    },
    fn=_run_delegate,
    requires_approval=True,
    needs_workspace=False,
)


# ---------------------------------------------------------------------------
# Fan-out tool (CH11 — parallel subtasks)
# ---------------------------------------------------------------------------


def _run_fan_out(tasks: list[str]) -> str:
    """Lazy-import wrapper for fan_out to avoid circular imports."""
    from harness.subagent import fan_out as _fan_out
    return _fan_out(tasks)


_FAN_OUT_TOOL = Tool(
    name="fan_out",
    description="Delegate multiple subtasks to fresh agents running in parallel. "
                "Each subtask gets its own isolated context. "
                "Provide a list of task descriptions, and results are returned in order.",
    parameters={
        "type": "object",
        "properties": {
            "tasks": {
                "type": "array",
                "items": {"type": "string"},
                "description": "A list of task descriptions, one per subagent.",
            },
        },
        "required": ["tasks"],
    },
    fn=_run_fan_out,
    requires_approval=True,
    needs_workspace=False,
)


# ---------------------------------------------------------------------------
# Default registry
# ---------------------------------------------------------------------------

def default_registry() -> ToolRegistry:
    """Create a ToolRegistry with all built-in tools.

    Returns
    -------
    ToolRegistry
        A registry pre-populated with calculator, read_file, write_file,
        bash, delegate, and fan_out.
    """
    registry = ToolRegistry()
    registry.register(_CALCULATOR_TOOL)
    registry.register(_READ_FILE_TOOL)
    registry.register(_WRITE_FILE_TOOL)
    registry.register(_BASH_TOOL)
    registry.register(_DELEGATE_TOOL)
    registry.register(_FAN_OUT_TOOL)
    return registry