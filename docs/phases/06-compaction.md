# Phase 6 — Context Management

**Status:** 📝 Not Started

---

## Goal

The moment tools were introduced, everything started piling into the conversation — tool calls, results, file reads. The context window is finite, so the harness must manage what fits.

## Concepts

- **Four moves:** Select, Compress, Write, Isolate. This phase builds **Compress**.
- **Compress strategy:** When history crosses a token budget, summarize the middle into a single note. Protect the head (system prompt, recent context) and tail (latest turn).
- **Clamp:** Limit the maximum size of any single item (file content, tool output) so no one message blows the budget.
- **Token estimation:** Estimate tokens (simple heuristic) to decide when to compact.

## Plan

1. Build `limits.py` — token budget constants, max item characters, token estimation heuristic.
2. Build `compaction.py` — `compact()` method that keeps head/tail, summarizes the middle.
3. Build `clamp()` — truncate any single item to max characters.
4. Wire compaction into the agent's `send()` method, triggered when the budget is exceeded.

## Files

| File | Purpose |
|------|---------|
| `src/harness/limits.py` | Token budget, max item size, token estimator |
| `src/harness/compaction.py` | Context compaction (summarize middle, keep head/tail) |
| `src/harness/agent.py` | Wire compaction into send() |

## Demo

```
$ uv run agent
[Set a tiny context budget for testing]
> [Spam 50 turns of chatter to blow past the budget]
[Bury a codename in the middle: "codename is CrimeMasterGogo"]
> What is the codename?
[Context compacted — middle summarized, head/tail preserved]
The codename is CrimeMasterGogo.
```

The middle got compressed, but the critical fact survived because it was near the tail.

## Acceptance Criteria

- [ ] Compaction fires when token budget is exceeded
- [ ] Head (system + instructions) and tail (last N turns) survive compaction
- [ ] Middle is summarized into a single note
- [ ] Clamp prevents any single item from exceeding max characters
- [ ] Agent still answers accurately after compaction

## Learnings

*(To be filled during implementation.)*

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch06/barenode-ch06-01.png` | *(to annotate)* |
| 2 | `docs/research/images/ch06/barenode-ch06-02.png` | *(to annotate)* |
| 3 | `docs/research/images/ch06/barenode-ch06-03.png` | *(to annotate)* |