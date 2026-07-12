# Phase 3 — Instructions

**Status:** 📝 Not Started

---

## Goal

Give the agent a standing personality and rules via a system prompt that's prepended on every turn, auto-loaded from an `AGENTS.md` file.

## Concepts

- **System prompt:** A message the harness prepends on every turn. Set once, it sticks.
- **`AGENTS.md` convention:** Same pattern as Codex and Claude Code — the harness auto-loads `AGENTS.md` from the working directory onto the system prompt.
- **Workspace:** A directory the agent owns. Every path is confined to it.

## Plan

1. Add `self.system` to the Agent for the built-in prompt.
2. Build `instructions.py` that reads `AGENTS.md` from the workspace.
3. Merge both into a single system message on every turn.

## Files

| File | Purpose |
|------|---------|
| `src/harness/instructions.py` | System prompt + AGENTS.md loader |
| `src/harness/agent.py` | Wire instructions into send() |
| `AGENTS.md` | Auto-loaded system prompt (already exists) |

## Demo

```
$ uv run agent
> What is your name?
I am barenode, a helpful coding assistant.
> What are your rules?
I follow the instructions in AGENTS.md — I'm concise, I use tools when needed, and I never expose secrets.
```

Without instructions, the model would answer "I'm an AI" or "I don't have a name."

## Acceptance Criteria

- [ ] Agent responds with the personality defined in AGENTS.md
- [ ] Changing AGENTS.md changes behavior without code changes
- [ ] Absent AGENTS.md does not crash — graceful fallback

## Learnings

*(To be filled during implementation.)*