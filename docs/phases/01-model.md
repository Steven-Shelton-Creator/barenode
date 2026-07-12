# Phase 1 — The Model

**Status:** 📝 Not Started

---

## Goal

Build the bare minimum agent: a stateless chat call with a REPL so you can type messages and get responses — but every turn is an independent call with no memory.

## Concepts

- **Model is stateless:** One request in, one answer out. Nothing is carried between calls.
- **Provider seam:** The model sits behind a `chat()` function that abstracts the provider (LM Studio, Ollama, OpenRouter).
- **REPL:** A simple read-eval-print loop so the user can interact.

## Plan

1. Implement a provider abstraction in `src/model/provider.py` — a `chat()` function that calls an OpenAI-compatible API.
2. Build the `Agent` class in `src/harness/agent.py` with a single `send()` method that calls the provider.
3. Wire up the REPL in `src/main.py` — `uv run agent` drops you into an interactive loop.

## Files

| File | Purpose |
|------|---------|
| `src/model/provider.py` | Provider abstraction (chat seam) |
| `src/harness/agent.py` | Agent class with `send()` method |
| `src/main.py` | REPL entry point |

## Demo

```
$ uv run agent
> My name is Gemma.
Hi Gemma! How can I help you?
> What is my name?
I don't know — you told me in a previous turn but I can't remember. Each call is stateless.
```

The model **forgets** between turns. That's the point — it shows why history (Phase 2) is needed.

## Acceptance Criteria

- [ ] `uv run agent` starts a REPL
- [ ] Agent responds to user messages
- [ ] Agent does NOT remember previous turns
- [ ] Provider can be swapped in one line (config or env var)

## Learnings

*(To be filled during implementation.)*