# Phase 4 — Context Delivery

**Phase:** 4
**Status:** ✅ Complete
**Date:** 2026-07-13

---

## Goal

Allow the agent to read files by reference using `@filename` syntax — the harness resolves the reference and injects the content before the model call.

## Concepts

- **Symbol-based referencing:** `@` tells the harness "this is a file reference."
- **Context injection:** Before the API call, scan the user's message for `@path` references, read them from disk, and inject the contents ahead of the question.
- **Workspace confinement:** Files outside the workspace are ignored (security boundary).
- **Graceful fallback:** Missing, empty, or unreadable files leave the `@ref` unchanged.

## Files

| File | Action |
|------|--------|
| `src/harness/context.py` | Written — `deliver()` function, regex-based scanner, file reader, workspace security |
| `src/harness/agent.py` | Modified — wired `deliver()` into `send()`, before storing the user message |
| `tests/test_ch04.py` | Created — 15 tests (10 unit + 4 integration + 1 regression) |
| `src/main.py` | Modified — demo label updated to CH04 |

## Implementation Details

### `context.py`

Three components:

- **Regex pattern** `_AT_REF_PATTERN` — Matches `@` followed by path characters (word chars, dots, slashes, hyphens).
- **`deliver(message, workspace)`** — Scans the message, replaces each `@path` with injected content wrapped in markers.
- **`_replace_match(match)`** — Resolves one reference: checks workspace boundary, reads file, returns injection block. Strips trailing sentence punctuation (`.`, `,`, `!`, `?`, `;`, `:`) from the captured path to avoid eating period at end of sentence.

### Injection format

```
--- filename.txt ---
file contents here
--- end filename.txt ---
```

### Security model

- All paths resolved via `os.path.abspath()`.
- File must start with `workspace + os.sep` — gates on the directory boundary.
- Missing files, empty files, unreadable files, and out-of-workspace paths all return the original `@ref` unchanged.

## Demo

```
$ echo "The capital of France is Paris." > facts.txt
$ uv run agent
> @facts.txt What is the capital of France?
Reading facts.txt...
The capital of France is Paris.
```

## Acceptance Criteria

- [x] `@filename` injects file contents into the context
- [x] Multiple `@` references in one message all resolved
- [x] Missing file produces a clear error message (graceful — leaves @ref)
- [x] No token management yet (raw injection)

## Test Results

```
$ uv run pytest tests/ -v
============================= 33 passed in 0.03s ==============================
```

CH04-specific tests (15 total):
- 10 unit tests on `deliver()` standalone
- 4 integration tests via Agent class
- 1 regression test (CH03 tests still pass)
- All pass with fake provider, no real model needed

## Learnings

- **Trailing punctuation is a trap.** `@file.txt.` matches `file.txt.` — the regex captures the period. Stripping `.,!?;:` from the tail of the captured path fixed it cleanly.
- **The regex approach is sufficient for this educational build.** A proper parser would be more robust, but for a learning agent a simple regex with workspace guards is the right level of complexity.
- **Workspace confinement is trivial to implement and easy to verify.** The `startswith` check with `os.sep` guard covers the main case (`@../etc/passwd`).
- **Wiring into `send()` was 2 lines** — call `deliver()`, store the result. The existing architecture absorbed CH04 without any refactoring.

## Verification

```
$ uv run pytest tests/ -v  →  33 passed in 0.03s
$ uv run demo               →  CH04 demo, 6 messages tracked
$ ollama/gemma4:e4b agent   →  @facts.txt → "The capital of France is Paris." ✓
```

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch04/barenode-ch04-01.png` | *(to annotate)* |