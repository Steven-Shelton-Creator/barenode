"""Agent — the harness core.

The agent keeps a ``self.messages`` list that grows with every turn.
Instructions (system prompt + AGENTS.md) are prepended before each
call but are **not** stored in ``self.messages`` — they're rebuilt
fresh on every turn.

Tools (CH05) are registered in a ToolRegistry.  When the model
responds with tool calls, the harness executes them and feeds the
results back to the model.  The tool loop is capped at 6 iterations.
"""

import os
import json

from model.provider import chat
from harness.instructions import build_system_message
from harness.context import deliver
from harness.tools import default_registry, ToolRegistry
from harness.approval import prompt_approval
from harness.compaction import compact
from harness.limits import MAX_CONTEXT_TOKENS
from harness.memory import save_session, load_session

# Maximum number of tool call iterations before the agent stops
_MAX_TOOL_ITERATIONS = 6


class Agent:
    """A coding agent with conversation memory, instructions, and tools.

    Parameters
    ----------
    model : str
        Model spec in ``provider/model`` format (default from env var
        ``BARENODE_MODEL`` or ``ollama/gemma4:e4b``).
    workspace : str or None
        Workspace directory for file operations and AGENTS.md lookup.
        Defaults to current working directory.
    tools : ToolRegistry or None
        Tool registry for the agent.  Defaults to the built-in tools
        (calculator, read_file, write_file).
    """

    def __init__(
        self,
        model: str | None = None,
        workspace: str | None = None,
        tools: ToolRegistry | None = None,
        session_name: str | None = None,
        session_dir: str | None = None,
    ) -> None:
        self.model = model or os.environ.get(
            "BARENODE_MODEL", "ollama/gemma4:e4b"
        )
        self.workspace = workspace or os.getcwd()
        self.tools = tools or default_registry()
        self._context_budget = int(os.environ.get("BARENODE_CONTEXT_BUDGET", str(MAX_CONTEXT_TOKENS)))

        # Session persistence (CH09)
        self.session_name = session_name or os.environ.get("BARENODE_SESSION", "default")
        self.session_dir = session_dir or os.environ.get("BARENODE_SESSION_DIR")
        self.messages: list[dict] = load_session(self.session_name, self.session_dir)

    def send(self, message: str) -> str:
        """Append a user message and return the model's final text reply.

        The message is scanned for ``@path`` references (CH04 — context
        delivery).  If the model responds with tool calls, the harness
        executes them (with approval gates for dangerous tools) and
        feeds the results back to the model.  The tool loop is capped
        at ``_MAX_TOOL_ITERATIONS`` (6).

        Parameters
        ----------
        message : str
            The user's message, possibly containing ``@path`` references.

        Returns
        -------
        str
            The model's final text response after all tool calls.
        """
        # Resolve @file references and store user message
        resolved = deliver(message, self.workspace)
        self.messages.append({"role": "user", "content": resolved})

        # Compact self.messages if budget exceeded (CH06)
        self.messages = compact(self.messages, budget=self._context_budget)

        # Build tool specs to advertise to the model
        tool_specs = self.tools.specs()

        # Tool loop — capped iterations
        for iteration in range(_MAX_TOOL_ITERATIONS):
            # Build system message fresh each turn
            sys_msg = build_system_message(self.workspace)
            messages_to_send = (
                [sys_msg] + self.messages if sys_msg else self.messages
            )

            # Call the model
            response = chat(self.model, messages_to_send, tools=tool_specs)

            # Handle tool calls
            if response.tool_calls:
                # Store the assistant message with tool_calls
                assistant_msg = {"role": "assistant", "content": response.content}
                # OpenAI-compatible: tool_calls lives at the top level of the message
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.get("id", f"call_{iteration}_{i}"),
                        "type": "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"],
                        },
                    }
                    for i, tc in enumerate(response.tool_calls)
                ]
                self.messages.append(assistant_msg)

                # Execute each tool call
                for tc in assistant_msg["tool_calls"]:
                    tool_name = tc["function"]["name"]
                    raw_args = tc["function"]["arguments"]

                    # Parse arguments (may be JSON string or dict)
                    if isinstance(raw_args, str):
                        try:
                            args = json.loads(raw_args)
                        except json.JSONDecodeError:
                            args = {}
                    else:
                        args = raw_args

                    # Inject workspace only for tools that need it
                    if self.tools.needs_workspace(tool_name) and "workspace" not in args:
                        args["workspace"] = self.workspace

                    # Check approval gate
                    if self.tools.requires_approval(tool_name):
                        summary = f"{tool_name}({', '.join(f'{k}={v}' for k, v in args.items() if k != 'workspace')})"
                        if not prompt_approval(tool_name, summary):
                            result = f"Approval rejected: {tool_name} was not executed."
                            self.messages.append({
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "content": result,
                            })
                            continue

                    # Execute the tool
                    result = self.tools.execute(tool_name, args)

                    # Store the tool result
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    })

                # Continue loop — the model will see the tool results
                continue

            # No tool calls — text response
            if response.content:
                self.messages.append({"role": "assistant", "content": response.content})
                self._save()
                return response.content

            # Edge case: empty response
            self.messages.append({"role": "assistant", "content": ""})
            self._save()
            return ""

        # Exceeded max iterations
        msg = f"[Agent] Tool loop exceeded {_MAX_TOOL_ITERATIONS} iterations. Stopping."
        self.messages.append({"role": "assistant", "content": msg})
        self._save()
        return msg

    def _save(self) -> None:
        """Persist current messages to disk (CH09)."""
        save_session(self.session_name, self.messages, self.session_dir)