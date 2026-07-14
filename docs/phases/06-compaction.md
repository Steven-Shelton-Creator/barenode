# Phase 6 — Context Management

**Status:** ✅ Complete (2026-07-14)

---

## Goal

The moment tools were introduced, everything started piling into the conversation — tool calls, results, file reads. The context window is finite, so the harness must manage what fits.

## Concepts

- **Four moves:** Select, Compress, Write, Isolate. This phase builds **Compress**.
- **Compress strategy:** When history crosses a token budget, summarize the middle into a single note. Protect the head (system prompt, recent context) and tail (latest turn).
- **Clamp:** Limit the maximum size of any single item (file content, tool output) so no one message blows the budget.
- **Token estimation:** Estimate tokens (simple heuristic) to decide when to compact.

## Plan (completed)

1. ✅ Built `limits.py` — token budget constants, max item characters, token estimation heuristic
2. ✅ Built `compaction.py` — `compact()` keeps head/tail, summarizes middle with recursive reduction
3. ✅ Built `clamp()` — truncates any single item to max characters with truncation note
4. ✅ Wired compaction into agent.send() — fires before tool loop, configurable via BARENODE_CONTEXT_BUDGET env var

## Files

| File | Purpose |
|------|---------|
| `src/harness/limits.py` | Token budget, max item size, token estimator |
| `src/harness/compaction.py` | Context compaction (summarize middle, keep head/tail) + clamp |
| `src/harness/agent.py` | Wire compaction into send(), BARENODE_CONTEXT_BUDGET env var |
| `tests/test_ch06.py` | 29 tests — limits, clamp, compact, agent integration, regression |

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

- [x] Compaction fires when token budget is exceeded
- [x] Head (system + instructions) and tail (last N turns) survive compaction
- [x] Middle is summarized into a single note
- [x] Clamp prevents any single item from exceeding max characters
- [x] Agent still answers accurately after compaction

## Learnings

### Key Design Decisions
- **Head/tail floor of 1.** Recursive compaction reduces head and tail turns, but never below 1 to preserve essential context.
- **Non-mutating.** `compact()` and `clamp_content()` both operate on copies — the original `self.messages` is replaced atomically.
- **Compaction fires before every send.** Wired at the top of `send()` after the user message is appended, before the tool loop.
- **Configurable budget.** `BARENODE_CONTEXT_BUDGET` env var lets tests and users tune the budget without code changes.

### Pain Points
- **Tiny budgets in tests.** With a budget of 10, even one message exceeds it because of structural overhead. The head/tail floor (minimum 1) prevents total compression.

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch06/barenode-ch06-01.png` | *(to annotate)* |
| 2 | `docs/research/images/ch06/barenode-ch06-02.png` | *(to annotate)* |
| 3 | `docs/research/images/ch06/barenode-ch06-03.png` | *(to annotate)* |