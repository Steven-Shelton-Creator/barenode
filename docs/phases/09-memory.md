# Phase 9 — Durable State / Memory

**Status:** 📝 Not Started

---

## Goal

Kill the agent and the whole conversation is gone. The harness needs to write sessions to disk so the agent survives restarts.

## Concepts

- **JSONL sessions:** One message per line in a `.jsonl` file. Load on startup, save after every turn.
- **`memory.py`:** New module handling save, load, and search.
- **Episodic search:** Plain keyword search across stored sessions (no embeddings) — borrowed from Hermes agent.

## Plan

1. Build `memory.py` — `save_session()`, `load_session()`, `search_sessions()`.
2. Agent loads session on startup (hardcoded name for now).
3. Agent saves session after every turn.
4. Keyword search tool for retrieving past session content.

## Files

| File | Purpose |
|------|---------|
| `src/harness/memory.py` | JSONL persistence, keyword search |
| `src/harness/agent.py` | Wire session load/save into send() |

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

- [ ] Session saves to JSONL after every turn
- [ ] Session loads on startup from disk
- [ ] Kill and restart — conversation resumes
- [ ] Keyword search across sessions returns relevant results
- [ ] Session file is human-readable JSONL

## Learnings

*(To be filled during implementation.)*