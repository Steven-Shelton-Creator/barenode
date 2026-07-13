# Phase 3 — Instructions

**Phase:** 3
**Status:** ✅ Complete
**Date:** 2026-07-12

---

## Goal

Give the agent a standing personality and rules via a system prompt that's prepended on every turn, auto-loaded from an `AGENTS.md` file.

## Concepts

- **System prompt:** A message the harness prepends on every turn. Set once, it sticks.
- **`AGENTS.md` convention:** Same pattern as Codex and Claude Code — the harness auto-loads `AGENTS.md` from the working directory onto the system prompt.
- **Workspace:** A directory the agent owns. Every path is confined to it.

## Files

| File | Action |
|------|--------|
| `src/harness/instructions.py` | Written — `load_instructions()`, `make_system_prompt()`, `build_system_message()` |
| `src/harness/agent.py` | Modified — added `workspace` param, system message prepended before every call |
| `tests/test_ch03.py` | Created — 9 tests covering loader, builder, and agent integration |
| `src/main.py` | Updated — default model to `gemma4:e4b`, demo labels CH03 |
| `AGENTS.md` | Used as-is — auto-loaded from workspace |

## Implementation Details

### `instructions.py`

Three public functions:

- **`load_instructions(workspace)`** — Reads `AGENTS.md` from the workspace directory. Returns empty string if file is missing or unreadable (graceful fallback).
- **`make_system_prompt(agents_content)`** — Combines a built-in prompt ("You are barenode, a helpful coding assistant built from scratch") with the AGENTS.md content.
- **`build_system_message(workspace)`** — Returns a `{"role": "system", "content": ...}` dict, or `None` for graceful fallback.

### `agent.py` changes

| Addition | Purpose |
|----------|---------|
| `self.workspace` | Directory for AGENTS.md lookup (defaults to cwd) |
| `build_system_message(self.workspace)` | Called on every `send()` to build fresh system message |
| `messages_to_send` | System message + conversation history — rebuilt every turn, not stored in `self.messages` |

## Demo

```
$ uv run agent
> Who are you?
I am barenode, a helpful coding assistant and educational agent.
> What is your name?
My name is barenode.
> What are your rules?
(System prompt from AGENTS.md — chapter cycle, tracking, security)
```

## Acceptance Criteria

- [x] Agent responds with the personality defined in AGENTS.md
- [x] Changing AGENTS.md changes behavior without code changes
- [x] Absent AGENTS.md does not crash — graceful fallback

## Test Results

```
$ uv run pytest tests/ -v
============================= 18 passed in 0.03s ==============================
```

CH03-specific tests (9 total):
- 5 unit tests on `load_instructions()` and `make_system_prompt()`
- 3 integration tests via Agent class
- All tests pass with fake provider, no real model needed

## Learnings

- System messages should NOT be appended to `self.messages` — they're rebuilt fresh on every call to avoid accumulating stale instructions.
- The `build_system_message()` returns `None` when there's no content, allowing the Agent to skip the system message entirely. This keeps the CH01/CH02 tests passing without modification.
- The workspace concept maps naturally: AGENTS.md lives in the workspace, and future chapters will confine file tools to the same boundary.

## Verification

```
$ uv run demo
barenode demo — CH03
4 messages tracked, system prompt loaded from AGENTS.md

$ uv run agent  (with real model)
> Who are you?  → I am barenode, a helpful coding assistant...
> What is your name?  → My name is barenode.
```

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch03/barenode-ch03-01.png` | *(to annotate)* |
| 2 | `docs/research/images/ch03/barenode-ch03-02.png` | *(to annotate)* |