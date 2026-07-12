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

- [ ] Agent remembers facts from previous turns
- [ ] Messages list grows with each turn
- [ ] No external storage yet (in-memory only)

## Learnings

*(To be filled during implementation.)*