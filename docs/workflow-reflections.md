# The barenode Workflow Reflections

This document is a **post-hoc reflection** of the actions we actually took while building the agent, sequenced and abstracted into a repeatable pattern. It was created *after* CH01 was complete, by observing and cataloging the steps we naturally followed.

This is not a prescriptive playbook we follow — it's a record of what we did, so we can identify loops, improve our process, and potentially formalize automation later.

---

## The Observed Cycle

```
  1. READ     ──→  2. PLAN    ──→  3. DECIDE  ──→  4. BUILD   ──→  5. TEST
                                                                      │
                                                                      ▼
  8. NEXT    ←──  7. LOG     ←──  6. VERIFY  ←────────────────────────
```

Each chapter followed these steps organically. Below is what each step looked like in practice.

---

## Step 1 — READ

**Observed behavior:** We consumed the source material before writing any code.

- Read the relevant section of `transcript.md` (video transcript)
- Looked at the screenshots in `docs/research/images/chXX/`
- Read the phase doc in `docs/phases/XX-name.md`
- Internalized what the chapter adds and why

**Output:** Nothing produced — just comprehension.

**CH01 example:** Read transcript section on model seam, looked at CH01 screenshots, understood the stateless call pattern.

---

## Step 2 — PLAN

**Observed behavior:** We wrote an implementation plan before touching code.

- Stated the **goal** in one sentence
- Listed the **concepts** being introduced
- Defined the **acceptance criteria**
- Identified every **file** that needs to change
- Outlined the **implementation steps** in order
- Noted what is **NOT** being built (scope boundary)

**Output:** Phase doc updated with plan section.

**CH01 plan:** *"Build the bare minimum agent: a stateless chat call with a REPL so you can type messages and get responses — but every turn is an independent call with no memory."*

---

## Step 3 — DECIDE

**Observed behavior:** When architectural choices arose, we stopped to evaluate options.

- Listed the open choices (e.g., which provider? how to configure?)
- Presented options with pros/cons
- Chose one and wrote the rationale
- Recorded it in `DECISIONS.md` as a new ADR entry

**Output:** New ADR entry in `DECISIONS.md`.

**CH01 example:** ADR-003 — Provider abstraction & REPL design. Chose Ollama as default, `BARENODE_MODEL=provider/model` format, all providers built in from day one.

---

## Step 4 — BUILD

**Observed behavior:** We wrote the code file by file.

- Created or modified each file listed in the plan
- One concern per file
- Wrote real code, not pseudocode
- Included docstrings and error handling

**Output:** Source code files changed.

**CH01 files touched:** `src/model/provider.py`, `src/harness/agent.py`, `src/main.py`, `tests/test_ch01.py`, `.env.example`

---

## Step 5 — TEST

**Observed behavior:** We wrote automated tests and ran them.

- Wrote pytest tests covering the new behavior
- Tests used the fake provider (no real model needed)
- Ran `uv run pytest tests/ -v` — all tests must pass
- Tested edge cases (invalid input, missing config, etc.)

**Output:** Test file(s) in `tests/`.

---

## Step 6 — VERIFY

**Observed behavior:** We manually verified the feature end-to-end.

- Ran the fake provider REPL: `BARENODE_MODEL=fake/echo uv run agent`
- Ran the real model REPL: `BARENODE_MODEL=ollama/<model> uv run agent`
- Ran the demo: `uv run demo`
- Observed the expected behavior
- If it failed, debugged and fixed

**Output:** Results logged in `docs/verification/CHXX-verification.md`.

---

## Step 7 — LOG

**Observed behavior:** After completion, we recorded what happened.

- Updated the phase doc status to ✅ Complete
- Filled in the **Learnings** section
- Wrote a session log in `docs/YYYY-MM-DD-session.md`
  - What was completed
  - Key decisions made
  - Notes for next session
- Created git tag: `git tag -a CHXX -m "CHXX — description"`

**Output:** Updated phase doc, session log file, git tag.

---

## Step 8 — NEXT

**Observed behavior:** We prepared for the next chapter.

- Updated `BUILD_PLAN.md` — marked current chapter complete
- Read the next chapter's transcript section
- The cycle began again

---

## The Observed Checklist (for any chapter)

```
□ READ    — transcript, screenshots, existing phase doc
□ PLAN    — goal, concepts, files, steps, acceptance criteria
□ DECIDE  — list choices, weigh options, record ADR
□ BUILD   — write code (one concern per file)
□ TEST    — automated tests with fake provider, all pass
□ VERIFY  — manual REPL test, real model test, demo run
□ LOG     — status update, learnings, session log, git tag
□ NEXT    — update BUILD_PLAN, move to next chapter
```

---

## CH02 Reflection Notes

**What was actually different from CH01:**

- The BUILD step revealed a ripple effect: changing `chat(message: str)` → `chat(messages: list[dict])` required updating all 4 provider implementations. The phase doc initially underestimated the files touched (it said only `agent.py`, but `provider.py` needed a signature change too).
- The DECIDE step was lightweight — one decision (provider signature change) with no real alternatives considered. The right choice was obvious.
- The LOG step captured the surprise: "only 3 lines in agent.py, but the provider seam needed a full refactor."

## File Map

```
docs/phases/              — one doc per chapter (plan + record)
docs/verification/         — test run logs per chapter
docs/research/images/      — reference screenshots by chapter
docs/YYYY-MM-DD-session.md — daily session logs
DECISIONS.md               — architectural decision records
BUILD_PLAN.md              — master progress tracker
```

## Philosophy

**Plan like an architect, build like a craftsman, log like a historian.**

These reflections help us see the shape of our own process — and decide what to keep, drop, or automate.
