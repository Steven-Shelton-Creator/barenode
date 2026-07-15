# Phase 11 — Subagents

**Status:** ✅ Complete
**Date:** 2026-07-14

---

## Goal

Every step in a plan shares a single context window. A big job might pollute it with many tool calls and dead ends. Subagents give each subtask its own clean context.

## Concepts

- **Fresh agent per subtask:** Its own context, its own tools. Runs to completion. Keep only the answer, not the transcript.
- **`delegate` tool:** Single subtask — returns the answer.
- **`fan_out` tool:** Batch of subtasks — runs in parallel, returns answers in order.
- **Context isolation is a feature:** One subtask never sees another's reasoning.

## Plan

1. Build `subagent.py` — `run_subagent()` builds a fresh Agent and returns the reply.
2. Expose `delegate` and `fan_out` as tools in the registry.
3. Fan-out runs subtasks in parallel (threading or asyncio).

## Files

| File | Purpose |
|------|---------|
| `src/harness/subagent.py` | Subagent runner, delegate + fan-out tools |
| `src/harness/tools.py` | Register delegate and fan_out |

## Demo

```
$ uv run agent
> Fan out: compute 12 squared, and name a primary color
[Fan-out started]
  Subagent 1: 12 squared = 144
  Subagent 2: A primary color is red.

Results:
1. 144
2. red
```

Neither subagent saw the other's reasoning — each ran in isolation.

## Acceptance Criteria

- [x] `delegate` runs a subtask in a fresh agent
- [x] `fan_out` runs multiple subtasks in parallel
- [x] Subtask contexts are fully isolated
- [x] Results are returned in order
- [x] Subagent errors don't crash the parent

## Learnings

### Circular Import Trap

The dependency chain `tools.py → subagent.py → agent.py → tools.py` creates a circular import. Fixed with lazy imports (wrapper functions that do a local import inside the function body) rather than top-level imports.

### Threading vs Async

Used `concurrent.futures.ThreadPoolExecutor` for fan-out parallelism. Simpler than asyncio for CPU-bound Python work, no event loop management needed.

### Session Isolation

Each subagent gets a unique session name via a thread-safe counter (`threading.Lock()`). This prevents session file collisions when multiple subagents run in parallel.

### Error Isolation

Each subagent runs in a try/except block. If one subtask fails, its error message is returned as the result — other subtasks proceed unaffected.

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch11/barenode-ch11-01.png` | *(to annotate)* |