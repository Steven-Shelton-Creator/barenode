# Phase 2 — History

**Phase:** 2
**Status:** ✅ Complete
**Date:** 2026-07-12

---

## Goal

Fix the stateless model by keeping a conversation history that gets replayed on every call.

## Concepts

- **Statefulness lives in the harness:** The model API is stateless. The harness keeps the conversation and replays it on every call.
- **Messages list:** `self.messages` — a list that grows with every turn.

## Plan

1. Add `self.messages = []` to the Agent class.
2. On each turn: append user message, send the whole list, append the reply.
3. That's it — three lines of code (the list, two appends).

## Files

| File | Purpose |
|------|---------|
| `src/harness/agent.py` | Add messages list, append logic |

## Diff (from Phase 1)

```python
# Before: stateless send()
def send(self, message: str) -> str:
    return chat(self.model, message)

# After: history-aware send()
self.messages: list[dict] = []

def send(self, message: str) -> str:
    self.messages.append({"role": "user", "content": message})
    reply = chat(self.model, self.messages)
    self.messages.append({"role": "assistant", "content": reply})
    return reply
```

## Demo

```
$ uv run agent
> My name is Gemma.
Hi Gemma! Nice to meet you.
> What is my name?
Your name is Gemma! You told me in the previous turn.
```

The model **remembers** — because the harness feeds the history back into every call.

## Acceptance Criteria

- [x] Agent remembers facts from previous turns
- [x] Messages list grows with each turn
- [x] No external storage yet (in-memory only)

## Learnings

- The provider seam needed a signature change: `chat(message: str)` → `chat(messages: list[dict])`. All four provider implementations had to be updated to pass the raw messages list instead of wrapping a single message.
- The fake provider needed updating too — it now finds the last user message from the list instead of echoing the raw input string.
- Only 3 lines of code in the Agent (`self.messages = []`, two appends), but the provider signature change rippled across 4 provider functions. Worth it for correctness — the provider should accept the same format every LLM API expects.
- Old CH01 tests still pass because the fake provider behavior is semantically equivalent for those test cases.
- The REPL (`uv run agent`) required zero changes — all history management is internal to the Agent.

## Verification

```
$ BARENODE_MODEL=fake/echo uv run demo
History now contains 6 messages.

$ BARENODE_MODEL=ollama/qwen3.5:9b uv run agent
> My name is Gemma.
> What is my name?
Your name is Gemma!   ← remembers across turns
```

## Conversation Log (2026-07-12 Session)

This section captures the full conversation summary and decision logic from the implementation session, preserving the reasoning for future reference.

### Session Start

- **Context:** Continued from CH01 (tagged/complete). All other files were scaffolded stubs.
- **Goal:** Add conversation history so the agent "remembers" across turns.
- **Approach:** Follow the observed workflow cycle (READ → PLAN → DECIDE → BUILD → TEST → VERIFY → LOG).

### Key Observations During Implementation

1. **The phase doc underestimated scope.** It said only `agent.py` would change, but the provider seam needed a signature change too. The actual files touched: `agent.py`, `provider.py`, `main.py`, `test_ch01.py`, `test_ch02.py` (new).

2. **The provider signature change was the real work.** While the Agent change was literally 3 lines (`self.messages = []`, two appends), updating all 4 provider implementations to accept `messages: list[dict]` took the bulk of the effort.

3. **The fake provider had to be smarter.** Previously it echoed the raw input string. Now it must find the last user message from the messages list — a more realistic simulation of how a real model consumes the conversation.

4. **No REPL changes needed.** The `main.py` entry point calls `agent.send(msg)` which handles history internally. The user-facing interface is unchanged.

### Decision Made

**Provider signature change:** `chat(model_spec: str, message: str)` → `chat(model_spec: str, messages: list[dict])`

Rationale: Every LLM API expects a messages array. The provider seam should match that format natively. No hidden transformations, no wrapping. This also anticipates CH03 (system prompts are just another message in the list).

Recorded as **ADR-004** in `DECISIONS.md`.

### Verification Results

```
$ uv run pytest tests/ -v           → 10 passed (0.02s)
$ BARENODE_MODEL=fake/echo uv run demo  → 6 messages tracked
$ BARENODE_MODEL=ollama/qwen3.5:9b uv run agent
  > My name is Gemma.
  > What is my name?
  Your name is Gemma!   ← remembers across turns
```

What actually happened during the real model test:
- First turn: "My name is Gemma." → model responded "Hello Gemma! Nice to meet you."
- Second turn: "What is my name?" → model responded "Your name is Gemma!" — confirming memory works

### Documentation Updates Made

- `docs/workflow-reflections.md` — Renamed from `workflow-playbook.md`, reframed as post-hoc reflection
- `DECISIONS.md` — Added ADR-004 documenting the provider signature change
- `docs/2026-07-12-session.md` — Session log with full details
- `BUILD_PLAN.md` — CH02 marked complete
- `ROADMAP.md` — CH01 + CH02 marked complete

### Next Steps

Proceed to **CH03 — Instructions**: Add system prompt, auto-load `agents.md`, and workspace confinement.

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch02/barenode-ch02-01.png` | *(to annotate)* |