# Phase 11 — Subagents

**Status:** 📝 Not Started

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

- [ ] `delegate` runs a subtask in a fresh agent
- [ ] `fan_out` runs multiple subtasks in parallel
- [ ] Subtask contexts are fully isolated
- [ ] Results are returned in order
- [ ] Subagent errors don't crash the parent

## Learnings

*(To be filled during implementation.)*