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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chat(model_spec: str, messages: list[dict]) -> str:
    """Send a conversation to the model and return the text response.

    Parameters
    ----------
    model_spec : str
        Format ``provider/model_name``, e.g. ``ollama/qwen2.5:8b``.
    messages : list[dict]
        Conversation history as a list of ``{"role": ..., "content": ...}``
        dicts.  The last message should be the user's turn.

    Returns
    -------
    str
        The model's text response.
    """
    provider, model = _parse_spec(model_spec)

    if provider == "ollama":
        return _call_ollama(model, messages)
    if provider == "openrouter":
        return _call_openrouter(model, messages)
    if provider == "lstudio":
        return _call_lstudio(model, messages)
    if provider == "fake":
        return _call_fake(model, messages)

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


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

def _call_ollama(model: str, messages: list[dict]) -> str:
    """Call Ollama's chat completion endpoint."""
    url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    data = _post_json(url, headers, payload)
    return data["message"]["content"]


def _call_openrouter(model: str, messages: list[dict]) -> str:
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
    data = _post_json(url, headers, payload)
    return data["choices"][0]["message"]["content"]


def _call_lstudio(model: str, messages: list[dict]) -> str:
    """Call LM Studio's local OpenAI-compatible endpoint."""
    base = os.environ.get("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    url = f"{base.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
    }
    data = _post_json(url, headers, payload)
    return data["choices"][0]["message"]["content"]


def _call_fake(model: str, messages: list[dict]) -> str:
    """Fake provider — echoes the last user message back for testing."""
    # Find the last user message in the conversation
    last_user = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        "(no user message)"
    )
    return f"Echo ({model}): {last_user}"