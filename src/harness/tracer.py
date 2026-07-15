"""Tracer — observability spans, sinks, instrumentation (CH13).

The tracer records every step of an agent turn as spans.  Spans
capture model calls, tool calls, and their timing/attributes/events.
After each turn, the trace is flushed to all registered sinks.

Design
------
- ``Span`` — a single traced operation (name, timing, attributes, events)
- ``Tracer`` — span lifecycle manager with context manager support
- ``ConsoleSink`` — prints formatted trace to stdout
- ``JsonlSink`` — writes trace to a JSONL file
- ``MultiSink`` — dispatches to multiple sinks
"""

import os
import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from harness.events import SpanEvent, GenAISpanKind


# ---------------------------------------------------------------------------
# Span
# ---------------------------------------------------------------------------

@dataclass
class Span:
    """A single traced operation.

    Attributes
    ----------
    name : str
        Human-readable name (e.g. ``"model_call"``, ``"tool:calculator"``).
    kind : GenAISpanKind
        The type of span.
    start_time : float
        Unix timestamp when the span started.
    end_time : float or None
        Unix timestamp when the span ended (``None`` while running).
    attributes : dict
        Key-value metadata about the span.
    events : list of SpanEvent
        Events that occurred within the span.
    span_id : str
        Unique identifier for this span.
    parent_id : str or None
        Span ID of the parent span, if any.
    """

    name: str
    kind: GenAISpanKind = GenAISpanKind.CHAIN
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    attributes: dict = field(default_factory=dict)
    events: list[SpanEvent] = field(default_factory=list)
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_id: str | None = None

    @property
    def duration(self) -> float:
        """Return the span duration in seconds (or 0 if still running)."""
        if self.end_time is not None:
            return self.end_time - self.start_time
        return 0.0


# ---------------------------------------------------------------------------
# Tracer
# ---------------------------------------------------------------------------

class Tracer:
    """Records spans for a single agent turn.

    Usage
    -----
    .. code-block:: python

        tracer = Tracer()
        with tracer.span("model_call", kind=GenAISpanKind.LLM) as span_id:
            # do work
            tracer.add_event(span_id, my_event)
        trace = tracer.get_trace()
    """

    def __init__(self) -> None:
        self._completed: list[Span] = []
        self._active: dict[str, Span] = {}

    def start_span(
        self,
        name: str,
        kind: GenAISpanKind = GenAISpanKind.CHAIN,
        attributes: dict | None = None,
        parent_id: str | None = None,
    ) -> str:
        """Start a new span and return its ID.

        Parameters
        ----------
        name : str
            Span name.
        kind : GenAISpanKind
            Span kind.
        attributes : dict or None
            Initial attributes.
        parent_id : str or None
            Parent span ID for nesting.

        Returns
        -------
        str
            The new span's ID.
        """
        span = Span(
            name=name,
            kind=kind,
            attributes=attributes or {},
            parent_id=parent_id,
        )
        self._active[span.span_id] = span
        return span.span_id

    def end_span(
        self,
        span_id: str,
        attributes: dict | None = None,
    ) -> None:
        """End a span and move it to the completed list.

        Parameters
        ----------
        span_id : str
            The span ID to end.
        attributes : dict or None
            Additional attributes to merge.
        """
        span = self._active.pop(span_id, None)
        if span is None:
            return
        span.end_time = time.time()
        if attributes:
            span.attributes.update(attributes)
        self._completed.append(span)

    def add_event(self, span_id: str, event: SpanEvent) -> None:
        """Add an event to an active span.

        Parameters
        ----------
        span_id : str
            The target span ID.
        event : SpanEvent
            The event to add.
        """
        span = self._active.get(span_id)
        if span is not None:
            span.events.append(event)

    @contextmanager
    def span(
        self,
        name: str,
        kind: GenAISpanKind = GenAISpanKind.CHAIN,
        attributes: dict | None = None,
    ):
        """Context manager that starts and ends a span.

        Yields the span ID.  The span is ended when the context exits.

        Parameters
        ----------
        name : str
            Span name.
        kind : GenAISpanKind
            Span kind.
        attributes : dict or None
            Initial attributes.
        """
        span_id = self.start_span(name, kind=kind, attributes=attributes)
        try:
            yield span_id
        finally:
            self.end_span(span_id)

    def get_trace(self) -> list[Span]:
        """Return all completed spans.

        Returns
        -------
        list of Span
            Completed spans in the order they were ended.
        """
        return list(self._completed)

    def clear(self) -> None:
        """Clear all completed and active spans."""
        self._completed.clear()
        self._active.clear()

    @property
    def total_cost(self) -> float:
        """Sum of ``cost`` attributes across all spans."""
        return sum(
            s.attributes.get("cost", 0.0)
            for s in self._completed
        )

    @property
    def total_tokens(self) -> int:
        """Sum of ``total_tokens`` attributes across all LLM spans."""
        return sum(
            s.attributes.get("total_tokens", 0)
            for s in self._completed
            if s.kind == GenAISpanKind.LLM
        )


# ---------------------------------------------------------------------------
# Sinks
# ---------------------------------------------------------------------------

class Sink:
    """Abstract base for trace output destinations."""

    def write(self, trace: list[Span]) -> None:
        """Write a completed trace.

        Parameters
        ----------
        trace : list of Span
            The completed spans for one agent turn.
        """
        raise NotImplementedError


class ConsoleSink(Sink):
    """Formats and prints the trace to stdout.

    Output looks like::

        ── Trace ──
        LLM call        : tokens=142, cost=$0.00 (0.85s)
        Tool call       : calculator(256 * 8) → 2048 (0.01s)
        LLM call        : tokens=85, cost=$0.00 (0.60s)
        ───────────────
        Total           : tokens=227, cost=$0.00
    """

    def write(self, trace: list[Span]) -> None:
        if not trace:
            return

        lines: list[str] = []
        total_tokens = 0
        total_cost = 0.0

        for span in trace:
            attrs = span.attributes
            kind = span.kind

            if kind == GenAISpanKind.LLM:
                tokens = attrs.get("total_tokens", 0)
                cost = attrs.get("cost", 0.0)
                model = attrs.get("model", "?")
                lines.append(
                    f"  LLM call        : "
                    f"model={model}, tokens={tokens}, "
                    f"cost=${cost:.6f} ({span.duration:.2f}s)"
                )
                total_tokens += tokens
                total_cost += cost

            elif kind == GenAISpanKind.TOOL:
                tool = attrs.get("tool", "?")
                args = attrs.get("arguments", "")
                result = attrs.get("result", "")
                result_preview = result[:60].replace("\n", " ")
                lines.append(
                    f"  Tool call       : "
                    f"{tool}({args}) → {result_preview} ({span.duration:.2f}s)"
                )

            elif kind == GenAISpanKind.CHAIN:
                name = span.name
                lines.append(f"  Chain step      : {name} ({span.duration:.2f}s)")

        if lines:
            print("── Trace ──")
            for line in lines:
                print(line)
            print("───────────────")
            print(f"  Total           : tokens={total_tokens}, cost=${total_cost:.6f}")
            print()


class JsonlSink(Sink):
    """Writes trace data to a JSONL file.

    Each agent turn produces one JSON line with the full span data.
    """

    def __init__(self, path: str | None = None) -> None:
        if path is None:
            path = os.path.join(os.getcwd(), "logs", "traces.jsonl")
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def write(self, trace: list[Span]) -> None:
        if not trace:
            return

        # Serialize spans to JSON-compatible dicts
        spans_data = []
        for span in trace:
            spans_data.append({
                "name": span.name,
                "kind": span.kind.value,
                "duration": span.duration,
                "attributes": span.attributes,
                "events": [
                    {
                        "name": e.name,
                        "attributes": e.attributes,
                        "timestamp": e.timestamp,
                    }
                    for e in span.events
                ],
            })

        line = json.dumps({
            "timestamp": time.time(),
            "spans": spans_data,
        })

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line + "\n")


class MultiSink(Sink):
    """Fans out to multiple sinks.

    Parameters
    ----------
    sinks : list of Sink
        The sinks to dispatch to.
    """

    def __init__(self, sinks: list[Sink] | None = None) -> None:
        self.sinks = sinks or []

    def add(self, sink: Sink) -> None:
        """Register an additional sink."""
        self.sinks.append(sink)

    def write(self, trace: list[Span]) -> None:
        for sink in self.sinks:
            sink.write(trace)


class StoreSink(Sink):
    """Stores the last trace in memory for the TUI to read.

    The TUI reads the trace after each turn via ``get_trace()``,
    but the agent clears its tracer inside ``_flush_trace()``.
    This sink captures the trace data before it is lost.
    """

    def __init__(self) -> None:
        self._last_trace: list[dict] = []

    def write(self, trace: list[Span]) -> None:
        spans = []
        for span in trace:
            spans.append({
                "name": span.name,
                "kind": span.kind.value if hasattr(span.kind, "value") else str(span.kind),
                "duration": span.duration,
                "attributes": dict(span.attributes),
                "events": [
                    {"name": e.name, "attributes": dict(e.attributes)}
                    for e in span.events
                ],
            })
        self._last_trace = spans

    def get_trace(self) -> list[dict]:
        """Return the most recent trace as serialized dicts."""
        return list(self._last_trace)

    def clear(self) -> None:
        """Clear the stored trace."""
        self._last_trace = []