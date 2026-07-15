# Phase 12 — Self-Verification

**Status:** ✅ Complete
**Date:** 2026-07-14

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

- [x] Verification fires only when a code file was written
- [x] Test command comes from AGENTS.md `[testing]` section
- [x] Agent runs the test, harness checks for exit 0
- [x] Harness rejects "done" without a passing test
- [x] Non-code tasks skip verification

## Learnings

### Verification Flow

The verification gate has three states:
1. **Idle** — no code changes detected, no prompt needed
2. **Armed** (`_pending_verification = True`) — code file was written, inject the "run tests" prompt on next model call
3. **Waiting** (`_verification_waiting = True`) — prompt was injected, waiting for the bash tool to return a test result

The gate transitions: Code written → Arm → Prompt injected → Wait for bash → Check exit code → Pass (reset) or Fail (re-arm)

### Detection Method

We check tool calls for `write_file` with a path extension in `CODE_EXTENSIONS`. This is simple and avoids false positives from read-only operations or non-code files.

### Test Result Parsing

The bash tool appends `[exit code: N]` when the exit code is non-zero. If the string lacks this marker, exit was 0 (success). If it contains `[exit code: 1]`, the test failed.

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch12/barenode-ch12-01.png` | *(to annotate)* |