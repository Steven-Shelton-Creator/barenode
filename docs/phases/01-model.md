# CH01 Implementation Plan — The Model

**Phase:** 1  
**Status:** 🔷 Ready for Decision  
**Date:** 2026-07-11

---

## What the Transcript Says

> *"An agent class with one `send` method. A single chat call with no message list at all. A small REPL so you can keep typing, but every turn is an independent call. The call goes through a seam: a free `chat` function over a provider."*

> *"If you want to have a fake provider to run the test. We just swap the provider in one line in one variable."*

---

## Decisions Needed

### Decision 1 — Which provider to support first?

| Option | Setup | Pros | Cons |
|--------|-------|------|------|
| **Ollama** | `ollama pull gemma2:2b` | Free, local, dead simple API | Requires Ollama install |
| **OpenRouter** | API key only | No local install, free tier | Needs internet + API key |
| **LM Studio** | Download + load model | Matches video exactly | Heavier setup |

**Recommendation:** Start with **Ollama** as default (easiest local setup), but write the provider seam to support all three from the start. Add a `FakeProvider` for tests.

### Decision 2 — How to configure the provider?

**Recommendation:** Single environment variable `BARENODE_MODEL` — format `provider/model`.

Examples:
```
BARENODE_MODEL=ollama/gemma2:2b
BARENODE_MODEL=openrouter/meta-llama/llama-3.1-8b
BARENODE_MODEL=fake/echo
```

### Decision 3 — REPL behavior?

**Recommendation:** Simple `input()` loop with `/quit` to exit. Print a clear prompt showing the model in use.

---

## Implementation Steps

### Step 1 — `src/model/provider.py`

The provider seam. One function, multiple backends.

```python
def chat(model_spec: str, message: str) -> str:
    provider, model = parse_model_spec(model_spec)
    if provider == "ollama":
        return _call_ollama(model, message)
    elif provider == "openrouter":
        return _call_openrouter(model, message)
    elif provider == "lstudio":
        return _call_lm_studio(model, message)
    elif provider == "fake":
        return f"Echo: {message}"
    else:
        raise ValueError(f"Unknown provider: {provider}")
```

### Step 2 — `src/harness/agent.py`

```python
class Agent:
    def __init__(self, model: str = "ollama/gemma2:2b"):
        self.model = model

    def send(self, message: str) -> str:
        return chat(self.model, message)    # No history — stateless
```

### Step 3 — `src/main.py` — REPL

```python
def repl():
    model = os.environ.get("BARENODE_MODEL", "ollama/gemma2:2b")
    agent = Agent(model=model)
    
    print(f"barenode [{model}]")
    while True:
        msg = input("> ").strip()
        if msg in ("/quit", "/exit"): break
        if msg.startswith("/"): ...  # future commands
        response = agent.send(msg)
        print(response)
```

### Step 4 — Tests

Add a test that uses the `fake` provider to verify the agent returns a response without hitting a real API.

---

## Files Changed

| File | Action | Purpose |
|------|--------|---------|
| `src/model/provider.py` | **Write** | Provider seam with ollama/openrouter/lstudio/fake backends |
| `src/harness/agent.py` | **Write** | Agent class with `send()` method |
| `src/main.py` | **Rewrite** | Real REPL loop |
| `tests/test_ch01.py` | **Create** | Tests using fake provider |
| `.env.example` | **Create** | Template for `BARENODE_MODEL` |

---

## Acceptance Criteria

- [ ] `BARENODE_MODEL=fake/echo uv run agent` starts REPL with fake provider
- [ ] Type a message → see echoed response
- [ ] Type another message → previous turn is **forgotten** (stateless)
- [ ] `BARENODE_MODEL=ollama/gemma2:2b uv run agent` works with a real model (if Ollama available)
- [ ] `/quit` exits cleanly
- [ ] Tests pass with fake provider, no real API needed

---

## What's NOT built (that comes in CH02)

- No history tracking
- No message list
- No memory between turns

---

## Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary provider | **Ollama** | Already installed with 8b models |
| Config format | `BARENODE_MODEL=provider/model` | Unambiguous, extensible |
| Default model | `ollama/qwen2.5:8b` | Lightweight, works on most hardware |
| Provider-agnostic | All providers built-in | User picks by env var, no code changes |
| REPL | `input()` loop, `/quit` to exit | Minimal, no dependencies |

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch01/barenode-ch01-01.png` | *(to annotate)* |
| 2 | `docs/research/images/ch01/barenode-ch01-02.png` | *(to annotate)* |