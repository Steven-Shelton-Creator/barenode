# Phase 2 — History

**Status:** 📝 Not Started

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

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch02/barenode-ch02-01.png` | *(to annotate)* |