# Phase 9 — Durable State / Memory

**Status:** ✅ Complete (2026-07-14)

---

## Goal

Kill the agent and the whole conversation is gone. The harness needs to write sessions to disk so the agent survives restarts.

## Concepts

- **JSONL sessions:** One message per line in a `.jsonl` file. Load on startup, save after every turn.
- **`memory.py`:** New module handling save, load, and search.
- **Episodic search:** Plain keyword search across stored sessions (no embeddings) — borrowed from Hermes agent.

## Plan (completed)

1. ✅ Built `memory.py` — `save_session()`, `load_session()`, `clear_session()`, `list_sessions()`, `search_sessions()`
2. ✅ Agent loads session on init, saves after every `send()`
3. ✅ Session name from ``session_name`` param or ``BARENODE_SESSION`` env var
4. ✅ Keyword search across sessions — case-insensitive substring match

## Files

| File | Purpose |
|------|---------|
| `src/harness/memory.py` | JSONL persistence, keyword search, session management |
| `src/harness/agent.py` | Session load on init, save after every send() |
| `tests/test_ch09.py` | 20 tests — save/load, search, agent integration, regression |
| `tests/conftest.py` | Unique session name per test (isolation) |

## Demo

```
$ uv run agent
> The secret amount is 42.
Saved.

[Kill process. Restart.]

$ uv run agent
[Session loaded from disk]
> What was the secret amount?
42.
```

The fact outlived the process that held it.

## Acceptance Criteria

- [x] Session saves to JSONL after every turn
- [x] Session loads on startup from disk
- [x] Kill and restart — conversation resumes
- [x] Keyword search across sessions returns relevant results
- [x] Session file is human-readable JSONL

## Learnings

### Key Design Decisions
- **JSONL format.** One JSON object per line. Human-readable, append-friendly, greppable.
- **Full overwrite on save.** `save_session()` writes the entire message list on each call. This is safe for our scale (hundreds of messages, not millions).
- **Session name from param or env var.** `session_name` parameter takes priority, falls back to `BARENODE_SESSION` env var, then `"default"`.
- **Test isolation via conftest.** Each test gets a unique session name via `BARENODE_SESSION` env var so tests don't share state.

### Real Model Demo
```
Session 1: "My name is Gemma."
           "What is my name?"   → "Your name is Gemma."

Session 2 (restart): loaded 4 messages from disk
           "What was my name again?" → "Your name is Gemma."
```
The name "Gemma" survived the process restart.

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch09/barenode-ch09-01.png` | *(to annotate)* |
| 2 | `docs/research/images/ch09/barenode-ch09-02.png` | *(to annotate)* |