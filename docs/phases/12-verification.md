# Phase 12 — Self-Verification

**Status:** 📝 Not Started

---

## Goal

"Done" is a sentence, not a fact. The harness should demand receipts — a test must pass before accepting that the work is complete.

## Concepts

- **Self-serve verification:** The model runs the test (via bash tool). The harness watches the transcript for a passing exit code.
- **`[testing]` section in AGENTS.md:** Names the test command (`uv run verify`, `npm test`, `go test`, etc.).
- **Code-change gate:** Verification only fires when a turn wrote a code file (determined by file extension). Plain questions skip verification.

## Plan

1. Build `verify.py` — reads the `[testing]` section from AGENTS.md.
2. After a tool call that writes a code file, arm the verification gate.
3. The harness won't accept "done" until the test command returns exit 0.
4. Agent runs the test itself (via bash tool). Harness checks the result.

## Files

| File | Purpose |
|------|---------|
| `src/harness/verify.py` | Verification gate, test runner |
| `src/harness/agent.py` | Wire verification into post-tool loop |

## Demo

```
$ uv run agent
> Tidy a docstring in src/harness/agent.py
[Edit made — code file changed. Verification armed.]
Running: uv run verify...
[Test passes: exit 0]
Done.

> What's the weather?
[No code files changed. Verification skipped.]
I can't answer that — I don't have internet access.
```

## Acceptance Criteria

- [ ] Verification fires only when a code file was written
- [ ] Test command comes from AGENTS.md `[testing]` section
- [ ] Agent runs the test, harness checks for exit 0
- [ ] Harness rejects "done" without a passing test
- [ ] Non-code tasks skip verification

## Learnings

*(To be filled during implementation.)*