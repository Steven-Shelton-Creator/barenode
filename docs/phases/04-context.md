# Phase 4 — Context Delivery

**Status:** 📝 Not Started

---

## Goal

Allow the agent to read files by reference using `@filename` syntax — the harness resolves the reference and injects the content before the model call.

## Concepts

- **Symbol-based referencing:** Pick a symbol (e.g., `@`) that tells the harness "this is a file reference."
- **Context injection:** Before the API call, scan the user's message for `@path` references, read them from disk, and inject the contents ahead of the question.
- **Raw blocks (for now):** No truncation or compression yet — that comes in Phase 6.

## Plan

1. Build `context.py` with a `deliver()` function that scans for `@` references.
2. For each `@path`, read the file and inject its contents into the message.
3. Wire `deliver()` into the agent's `send()` method, before the API call.

## Files

| File | Purpose |
|------|---------|
| `src/harness/context.py` | @file reference scanner + injector |
| `src/harness/agent.py` | Wire context delivery into send() |

## Demo

```
$ cat facts.txt
Raveena is Karishma and Karishma is Raveena.

$ uv run agent
> @facts.txt Who is Raveena?
Reading facts.txt...
Karishma.
```

## Acceptance Criteria

- [ ] `@filename` injects file contents into the context
- [ ] Multiple `@` references in one message all resolved
- [ ] Missing file produces a clear error message
- [ ] No token management yet (raw injection)

## Learnings

*(To be filled during implementation.)*

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch04/barenode-ch04-01.png` | *(to annotate)* |