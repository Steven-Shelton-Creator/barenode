# CH03 Verification Log

**Date:** 2026-07-12  
**Tag:** `CH03` — Instructions  
**Status:** ✅ All checks passed

---

## Shipped Files

| File | What it does |
|---|---|
| `src/harness/instructions.py` | `load_instructions()`, `make_system_prompt()`, `build_system_message()` — reads AGENTS.md, builds system message |
| `src/harness/agent.py` | Added `workspace` param, prepends system message on every `send()` |
| `tests/test_ch03.py` | 9 tests — unit + integration |
| `docs/phases/03-instructions.md` | Plan, learnings, verification recorded |

---

## Test Run 1 — Fake Provider (no model required)

```bash
$ cd /home/steven/projects/barenode
$ uv run demo
barenode demo — CH03
========================================

> Hello! What is your name?
Echo (echo): Hello! What is your name?

> Who are you?
Echo (echo): Who are you?

========================================
Messages tracked: 4
System prompt includes AGENTS.md content.
```

---

## Test Run 2 — Real Model (Ollama + gemma4:e4b)

```bash
$ cd /home/steven/projects/barenode
$ BARENODE_MODEL=ollama/gemma4:e4b uv run agent
```

Then inside the REPL:

```
> Who are you?
I am barenode, a helpful coding assistant and educational agent.
My function is to assist in the systematic development of software,
building solutions one primitive at a time.

> What is your name?
My name is barenode.

> What are your rules?
(Describes chapter cycle, tracking updates, security protocols — all from AGENTS.md)

> My name is Steven.
> What is my name?
Your name is Steven.
```

**Observations:**
- Agent identifies as **barenode** (from AGENTS.md system prompt)
- Agent remembers the conversation across turns (CH02 history still works)
- Agent's rules match AGENTS.md content — "READ → PLAN → DECIDE → BUILD → TEST → VERIFY → LOG → NEXT"
- Changing AGENTS.md would change behavior without code changes

---

## Automated Test Results

```bash
$ uv run pytest tests/ -v
============================= 18 passed in 0.03s ==============================
```

All 18 tests pass. CH03-specific tests (9):
1. `test_load_instructions_returns_empty_when_no_file` — graceful fallback
2. `test_load_instructions_reads_agents_dot_md` — reads AGENTS.md content
3. `test_load_instructions_graceful_on_bad_workspace` — no crash on bad path
4. `test_make_system_prompt_includes_built_in` — built-in prompt present
5. `test_make_system_prompt_appends_agents_content` — AGENTS.md content appended
6. `test_agent_sends_system_message_with_fake_provider` — system message sent
7. `test_agent_works_without_agents_dot_md` — graceful fallback
8. `test_agent_personality_reflects_agents_dot_md` — personality loaded
9. (Implicit) Real model verification — personality matches AGENTS.md

---

## Key Insight

**The agent now has a standing identity.** Without instructions (CH02), the model would answer "I'm an AI" or "I don't have a name." With CH03, it answers based on AGENTS.md — "I am barenode, a helpful coding assistant..." The personality is decoupled from code — edit AGENTS.md, the agent changes.

---

## Quick Start

```bash
# Fake provider (no model needed)
cd /home/steven/projects/barenode
uv run agent            # or: BARENODE_MODEL=fake/echo uv run agent

# Real model (Ollama)
uv run agent

# Scripted demo
uv run demo

# Run tests
uv run pytest tests/ -v
```