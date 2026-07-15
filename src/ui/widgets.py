"""Widgets — TUI components (CH14).

Two-pane terminal UI:
  - Left: Conversation pane — scrollable history of user/assistant messages
  - Right: Trace stream pane — live spans from the most recent turn
  - Approval modal — unified diff for file writes

Only this package imports ``textual`` — the rest of barenode stays
framework-agnostic.
"""

import os
import json
import difflib
import textwrap
from datetime import datetime
from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Header, Footer, RichLog
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.reactive import reactive
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.console import RenderableType


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

MAX_MESSAGE_LENGTH = 2000


def _truncate(text: str, max_len: int = MAX_MESSAGE_LENGTH) -> str:
    """Truncate text to max_len with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def _format_timestamp() -> str:
    """Return a formatted timestamp string."""
    return datetime.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Conversation pane
# ---------------------------------------------------------------------------

class ConversationPane(Widget):
    """Left pane — scrollable conversation history."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._messages: list[dict] = []

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, wrap=True)

    def on_mount(self) -> None:
        self._log = self.query_one(RichLog)
        self._log.write(Panel("[bold blue]Conversation[/]", border_style="blue"))

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation display.

        Parameters
        ----------
        role : str
            One of ``"user"``, ``"assistant"``, ``"system"``, ``"tool"``.
        content : str
            The message content.
        """
        if not content:
            return

        timestamp = _format_timestamp()

        if role == "user":
            style = "bold green"
            prefix = "You"
        elif role == "assistant":
            style = "bold cyan"
            prefix = "Bot"
        elif role == "system":
            style = "bold yellow"
            prefix = "System"
        elif role == "tool":
            style = "bold magenta"
            prefix = "Tool"
        else:
            style = "bold white"
            prefix = role.capitalize()

        display = _truncate(content)
        self._log.write(
            Text(f"[{timestamp}] {prefix}: ", style=style)
            + Text(display, style="white")
        )

    def clear(self) -> None:
        """Clear all messages."""
        self._log.clear()
        self._log.write(Panel("[bold blue]Conversation[/]", border_style="blue"))


# ---------------------------------------------------------------------------
# Trace stream pane
# ---------------------------------------------------------------------------

class TraceStreamPane(Widget):
    """Right pane — live trace stream from the last turn."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._spans: list[dict] = []

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, wrap=True)

    def on_mount(self) -> None:
        self._log = self.query_one(RichLog)
        self._log.write(Panel("[bold cyan]Live Trace[/]", border_style="cyan"))

    def display_trace(self, spans: list[dict]) -> None:
        """Display a trace from the agent's tracer.

        Parameters
        ----------
        spans : list of dict
            Serialized span data from the tracer.
        """
        if not spans:
            return

        self._log.write("\n" + "─" * 20)

        total_tokens = 0
        total_cost = 0.0

        for span in spans:
            attrs = span.get("attributes", {})
            kind = span.get("kind", "")
            name = span.get("name", "")
            duration = span.get("duration", 0.0)

            if "genai.operation" in kind or "llm" in name.lower():
                tokens = attrs.get("total_tokens", 0)
                cost = attrs.get("cost", 0.0)
                model = attrs.get("model", "?")
                total_tokens += tokens
                total_cost += cost
                self._log.write(
                    Text(f"  LLM  ", style="bold blue")
                    + Text(f"model={model} tokens={tokens} cost=${cost:.6f} ({duration:.2f}s)", style="white")
                )

            elif "genai.tool_call" in kind or "tool" in name.lower():
                tool = attrs.get("tool", "?")
                args = attrs.get("arguments", "")
                result = attrs.get("result", "")
                result_preview = result[:80].replace("\n", " ")
                self._log.write(
                    Text(f"  Tool ", style="bold magenta")
                    + Text(f"{tool}({args}) → {result_preview} ({duration:.2f}s)", style="white")
                )

            elif "chain" in kind.lower():
                self._log.write(
                    Text(f"  Step ", style="bold yellow")
                    + Text(f"{name} ({duration:.2f}s)", style="white")
                )

        self._log.write(
            Text(f"  ─── Total: tokens={total_tokens} cost=${total_cost:.6f}", style="bold")
        )

    def clear(self) -> None:
        """Clear the trace stream."""
        self._log.clear()
        self._log.write(Panel("[bold cyan]Live Trace[/]", border_style="cyan"))


# ---------------------------------------------------------------------------
# Approval modal — unified diff for file writes
# ---------------------------------------------------------------------------

class ApprovalModal(ModalScreen):
    """Modal screen that shows a unified diff and asks for approval.

    The modal displays the proposed file change as a unified diff and
    provides Approve/Deny buttons.
    """

    def __init__(self, tool_name: str, summary: str, path: str | None = None,
                 content: str | None = None, existing: str | None = None):
        super().__init__()
        self.tool_name = tool_name
        self.summary = summary
        self.path = path
        self.content = content
        self.existing = existing

    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold yellow]Approval Required[/]", id="title"),
            Static(f"Tool: {self.tool_name}", id="tool-name"),
            Static(self.summary, id="summary"),
            Static(self._build_diff(), id="diff"),
            Horizontal(
                Static("[bold green]Press Y to approve[/]", id="approve-hint"),
                Static("[bold red]Press N to deny[/]", id="deny-hint"),
                id="buttons",
            ),
            id="modal",
        )

    def _build_diff(self) -> str:
        """Build a unified diff string for the proposed change."""
        if not self.path or self.content is None:
            return self.summary

        old_lines = (self.existing or "").splitlines(keepends=True)
        new_lines = self.content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{self.path}",
            tofile=f"b/{self.path}",
        )
        diff_text = "".join(diff)
        if not diff_text:
            return f"[new file] {self.path}\n{self.content[:200]}"
        return diff_text

    def key_y(self) -> None:
        """Approve — close modal with True result."""
        self.dismiss(True)

    def key_n(self) -> None:
        """Deny — close modal with False result."""
        self.dismiss(False)

    def key_escape(self) -> None:
        """Escape — treat as deny."""
        self.dismiss(False)


# ---------------------------------------------------------------------------
# Main app layout
# ---------------------------------------------------------------------------

class BarenodeAppLayout(Widget):
    """Root layout for the barenode TUI."""

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="left-pane"):
                yield ConversationPane(id="conversation")
            with Vertical(id="right-pane"):
                yield TraceStreamPane(id="trace-stream")

    def on_mount(self) -> None:
        self.conversation = self.query_one("#conversation", ConversationPane)
        self.trace_stream = self.query_one("#trace-stream", TraceStreamPane)