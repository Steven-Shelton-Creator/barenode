"""Terminal UI — two-pane TUI (CH14).

The UI package is the only package that imports ``textual``.
The agent runs in a worker thread, and the UI consumes tracer
events for the live trace stream.

Usage
-----
    uv run tui
"""

import os
import sys
import asyncio
import threading
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, RichLog
from textual.reactive import reactive
from textual.binding import Binding
from textual.worker import WorkerState, get_current_worker
from textual import work
from rich.text import Text
from rich.panel import Panel

from harness.agent import Agent
from harness.tracer import Tracer, ConsoleSink, StoreSink, MultiSink, GenAISpanKind
from harness.approval import prompt_approval
from model.provider import fake_set_next_tool_calls

from ui.widgets import (
    ConversationPane,
    TraceStreamPane,
    ApprovalModal,
    BarenodeAppLayout,
)


# ---------------------------------------------------------------------------
# Agent runner — runs in a worker thread
# ---------------------------------------------------------------------------

class AgentRunner:
    """Runs the agent in a separate thread, capturing events for the UI.

    The runner intercepts the approval gate so dangerous operations
    show a modal instead of blocking on stdin.
    """

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.environ.get("BARENODE_MODEL", "ollama/gemma4:e4b")
        self.agent = Agent(model=self.model)
        self._approval_queue: list[dict] = []
        self._approval_event = threading.Event()
        self._approval_result = False

        # Replace the agent's single sink with a MultiSink that
        # keeps the ConsoleSink (stdout) and adds a StoreSink so
        # the TUI can read the trace after the agent clears it.
        self._store_sink = StoreSink()
        self.agent.sink = MultiSink([ConsoleSink(), self._store_sink])

    def send(self, message: str) -> str:
        """Send a message to the agent and return the reply.

        Parameters
        ----------
        message : str
            The user message.

        Returns
        -------
        str
            The agent's reply.
        """
        return self.agent.send(message)

    def get_conversation(self) -> list[dict]:
        """Return the agent's message history."""
        return list(self.agent.messages)

    def get_trace_spans(self) -> list[dict]:
        """Return the most recent trace from the store sink.

        The agent clears its tracer inside ``_flush_trace()``,
        so we read from the StoreSink which captured the data
        before it was lost.
        """
        return self._store_sink.get_trace()


# ---------------------------------------------------------------------------
# TUI App
# ---------------------------------------------------------------------------

class BarenodeApp(App):
    """Two-pane terminal UI for barenode.

    Left pane: conversation history.
    Right pane: live trace stream.
    Input bar: type messages at the bottom.
    """

    TITLE = "barenode"
    SUB_TITLE = "An agent built from scratch"

    CSS = """
    Screen {
        layout: vertical;
    }

    #main-layout {
        height: 1fr;
    }

    #left-pane {
        width: 50%;
        border: solid $primary;
        padding: 0 1;
    }

    #right-pane {
        width: 50%;
        border: solid $secondary;
        padding: 0 1;
    }

    #input-bar {
        dock: bottom;
        height: 3;
        padding: 0 1;
    }

    Input {
        width: 100%;
    }

    #conversation {
        height: 100%;
    }

    #trace-stream {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+l", "clear", "Clear", show=True),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.runner = AgentRunner()
        self._response_ready = threading.Event()

    def compose(self) -> ComposeResult:
        yield Header()
        yield BarenodeAppLayout()
        yield Input(id="input-bar", placeholder="Type a message...")
        yield Footer()

    def on_mount(self) -> None:
        self._input = self.query_one("#input-bar", Input)
        self._input.focus()
        self.conversation = self.query_one("#conversation", ConversationPane)
        self.trace_pane = self.query_one("#trace-stream", TraceStreamPane)
        self.conversation.add_message("system", "barenode TUI ready. Type a message or /quit to exit.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission."""
        msg = event.value.strip()
        if not msg:
            return

        self._input.clear()
        self._input.disabled = True

        if msg in ("/quit", "/exit"):
            self.exit()
            return

        if msg.startswith("/clear"):
            self.action_clear()
            self._input.disabled = False
            self._input.focus()
            return

        # Display the user message
        self.conversation.add_message("user", msg)

        # Run the agent in a worker
        self.run_agent_worker(msg)

    @work(exclusive=True, thread=True)
    async def run_agent_worker(self, message: str) -> None:
        """Run the agent in a worker thread."""
        worker = get_current_worker()

        try:
            # Send message to agent
            reply = self.runner.send(message)

            # Update UI on the main thread
            if not worker.is_cancelled:
                self.call_from_thread(self._on_agent_reply, reply)

        except Exception as exc:
            if not worker.is_cancelled:
                self.call_from_thread(self._on_agent_error, str(exc))

    def _on_agent_reply(self, reply: str) -> None:
        """Called on the main thread when the agent responds."""
        self.conversation.add_message("assistant", reply)

        # Update trace
        spans = self.runner.get_trace_spans()
        self.trace_pane.display_trace(spans)

        self._input.disabled = False
        self._input.focus()

    def _on_agent_error(self, error: str) -> None:
        """Called on the main thread when the agent errors."""
        self.conversation.add_message("system", f"[error] {error}")
        self._input.disabled = False
        self._input.focus()

    def action_clear(self) -> None:
        """Clear both panes."""
        self.conversation.clear()
        self.trace_pane.clear()
        self.runner.agent.tracer.clear()
        self.runner._store_sink.clear()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> None:
    """Launch the TUI."""
    app = BarenodeApp()
    app.run()


if __name__ == "__main__":
    run()