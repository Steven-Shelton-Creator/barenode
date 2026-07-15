"""Events — OpenTelemetry GenAI semantic event conventions (CH13).

Provides standardized event names and structures for observability.
Follows the OpenTelemetry GenAI semantic conventions where applicable.

Design
------
- ``GenAISpanKind`` — enum for span types (LLM, TOOL, CHAIN, RETRIEVER)
- ``SpanEvent`` — dataclass for events within a span
- Event builders: ``llm_call_event()``, ``tool_call_event()``, ``completion_event()``
"""

import time
from enum import Enum
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Span kinds
# ---------------------------------------------------------------------------

class GenAISpanKind(str, Enum):
    """OpenTelemetry GenAI span kind identifiers.

    Attributes
    ----------
    LLM : str
        A large language model call.
    TOOL : str
        A tool or function invocation.
    CHAIN : str
        A sequence of operations (e.g. agent loop iteration).
    RETRIEVER : str
        A retrieval operation (e.g. memory search).
    """

    LLM = "genai.operation"
    TOOL = "genai.tool_call"
    CHAIN = "genai.chain"
    RETRIEVER = "genai.retriever"


# ---------------------------------------------------------------------------
# Event data
# ---------------------------------------------------------------------------

@dataclass
class SpanEvent:
    """A single event within a span.

    Attributes
    ----------
    name : str
        Event name (e.g. ``"genai.usage"``).
    attributes : dict
        Key-value pairs describing the event.
    timestamp : float
        Unix timestamp when the event occurred.
    """

    name: str
    attributes: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Event builders
# ---------------------------------------------------------------------------

def make_event(name: str, **attributes: object) -> SpanEvent:
    """Create a SpanEvent with the given name and attributes.

    Parameters
    ----------
    name : str
        Event name.
    **attributes : object
        Key-value pairs for the event.

    Returns
    -------
    SpanEvent
    """
    return SpanEvent(name=name, attributes=dict(attributes))


def llm_call_event(
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost: float = 0.0,
    **extra: object,
) -> SpanEvent:
    """Create an event for an LLM call.

    Parameters
    ----------
    model : str
        The model spec that was called.
    input_tokens : int
        Number of input tokens.
    output_tokens : int
        Number of output tokens.
    cost : float
        Estimated cost in USD.
    **extra : object
        Additional attributes.

    Returns
    -------
    SpanEvent
    """
    return make_event(
        "genai.usage",
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        cost=cost,
        **extra,
    )


def tool_call_event(
    tool_name: str,
    arguments: str = "",
    result: str = "",
    duration: float = 0.0,
    **extra: object,
) -> SpanEvent:
    """Create an event for a tool call.

    Parameters
    ----------
    tool_name : str
        Name of the tool that was called.
    arguments : str
        String representation of the arguments.
    result : str
        Truncated result string.
    duration : float
        Execution duration in seconds.
    **extra : object
        Additional attributes.

    Returns
    -------
    SpanEvent
    """
    return make_event(
        "genai.tool_call",
        tool=tool_name,
        arguments=arguments,
        result=result[:200] if result else "",
        duration_seconds=duration,
        **extra,
    )


def completion_event(
    content: str = "",
    finish_reason: str = "stop",
    **extra: object,
) -> SpanEvent:
    """Create an event for a model completion.

    Parameters
    ----------
    content : str
        The completion text (truncated).
    finish_reason : str
        Why the model stopped (e.g. ``"stop"``, ``"tool_calls"``).
    **extra : object
        Additional attributes.

    Returns
    -------
    SpanEvent
    """
    return make_event(
        "genai.completion",
        content=content[:200] if content else "",
        finish_reason=finish_reason,
        **extra,
    )