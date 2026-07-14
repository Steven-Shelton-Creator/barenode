"""Provider abstraction — the model seam.

One chat() function, multiple backends. Swap the provider by changing
the BARENODE_MODEL environment variable (format: provider/model).

Supported providers:
  - ollama    — local via Ollama daemon
  - openrouter — hosted via OpenRouter API
  - lstudio   — local via LM Studio
  - fake      — echo backend for testing
"""

import os
import json
import urllib.request
import urllib.error
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Model response type
# ---------------------------------------------------------------------------

@dataclass
class ModelResponse:
    """Structured response from a model call.

    Attributes
    ----------
    content : str or None
        The text content of the response.  ``None`` if the response
        contains only tool calls.
    tool_calls : list[dict] or None
        A list of tool call dicts in OpenAI-compatible format:
        ``{"id": ..., "type": "function", "function": {"name": ..., "arguments": ...}}``
        ``None`` if the response contains only text.
    """

    content: str | None = None
    tool_calls: list[dict] | None = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chat(model_spec: str, messages: list[dict], tools: list[dict] | None = None) -> ModelResponse:
    """Send a conversation to the model and return the structured response.

    Parameters
    ----------
    model_spec : str
        Format ``provider/model_name``, e.g. ``ollama/qwen2.5:8b``.
    messages : list[dict]
        Conversation history as a list of ``{"role": ..., "content": ...}``
        dicts.  The last message should be the user's turn.
    tools : list[dict] or None
        Optional OpenAI-compatible tool specs to advertise to the model.

    Returns
    -------
    ModelResponse
        The model's response, with ``content`` for text replies and/or
        ``tool_calls`` for tool invocations.
    """
    provider, model = _parse_spec(model_spec)

    if provider == "ollama":
        return _call_ollama(model, messages, tools)
    if provider == "openrouter":
        return _call_openrouter(model, messages, tools)
    if provider == "lstudio":
        return _call_lstudio(model, messages, tools)
    if provider == "fake":
        return _call_fake(model, messages, tools)

    raise ValueError(f"Unknown provider '{provider}'. "
                     f"Expected one of: ollama, openrouter, lstudio, fake")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_spec(spec: str) -> tuple[str, str]:
    """Split ``provider/model`` into (provider, model)."""
    parts = spec.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Invalid model spec '{spec}'. "
                         f"Expected format: provider/model_name")
    return parts[0], parts[1]


def _post_json(url: str, headers: dict, payload: dict) -> dict:
    """POST a JSON payload and return the parsed JSON response."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Connection failed to {url}: {exc.reason}") from exc


def _extract_tool_calls(message: dict) -> list[dict] | None:
    """Extract tool_calls from a response message dict, if present."""
    raw = message.get("tool_calls")
    if not raw:
        return None
    return raw


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

def _call_ollama(model: str, messages: list[dict], tools: list[dict] | None = None) -> ModelResponse:
    """Call Ollama's chat completion endpoint."""
    url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools

    data = _post_json(url, headers, payload)
    msg = data["message"]
    return ModelResponse(
        content=msg.get("content"),
        tool_calls=_extract_tool_calls(msg),
    )


def _call_openrouter(model: str, messages: list[dict], tools: list[dict] | None = None) -> ModelResponse:
    """Call the OpenRouter chat completions endpoint."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools

    data = _post_json(url, headers, payload)
    msg = data["choices"][0]["message"]
    return ModelResponse(
        content=msg.get("content"),
        tool_calls=_extract_tool_calls(msg),
    )


def _call_lstudio(model: str, messages: list[dict], tools: list[dict] | None = None) -> ModelResponse:
    """Call LM Studio's local OpenAI-compatible endpoint."""
    base = os.environ.get("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    url = f"{base.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
    }
    if tools:
        payload["tools"] = payload

    data = _post_json(url, headers, payload)
    msg = data["choices"][0]["message"]
    return ModelResponse(
        content=msg.get("content"),
        tool_calls=_extract_tool_calls(msg),
    )


# ---------------------------------------------------------------------------
# Fake provider (for testing)
# ---------------------------------------------------------------------------

# Control how the fake provider behaves in tests.
# The agent can set this to simulate tool calls.
_FAKE_NEXT_TOOL_CALLS: list[dict] | None = None
_FAKE_NEXT_TOOL_RESULT: str | None = None


def fake_set_next_tool_calls(tool_calls: list[dict] | None) -> None:
    """Set the tool_calls the fake provider will return on the next call."""
    global _FAKE_NEXT_TOOL_CALLS
    _FAKE_NEXT_TOOL_CALLS = tool_calls


def fake_set_next_tool_result(result: str | None) -> None:
    """Set the tool result text the fake provider will include alongside tool_calls."""
    global _FAKE_NEXT_TOOL_RESULT
    _FAKE_NEXT_TOOL_RESULT = result


def _call_fake(model: str, messages: list[dict], tools: list[dict] | None = None) -> ModelResponse:
    """Fake provider — echoes the last user message, or simulates tool calls."""
    global _FAKE_NEXT_TOOL_CALLS, _FAKE_NEXT_TOOL_RESULT

    # If a test has queued tool calls, return them
    if _FAKE_NEXT_TOOL_CALLS is not None:
        tc = _FAKE_NEXT_TOOL_CALLS
        content = _FAKE_NEXT_TOOL_RESULT
        _FAKE_NEXT_TOOL_CALLS = None
        _FAKE_NEXT_TOOL_RESULT = None
        return ModelResponse(content=content, tool_calls=tc)

    # Otherwise echo the last user message
    last_user = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        "(no user message)"
    )
    return ModelResponse(content=f"Echo ({model}): {last_user}")