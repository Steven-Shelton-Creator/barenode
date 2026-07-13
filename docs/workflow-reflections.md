# barenode Workflow Reflections — Master Index

## Purpose

This is the master index for all daily workflow reflection files. Each day's reflection is a **post-hoc record** of the actions we actually took while building the agent, sequenced and abstracted into a repeatable pattern. These are created at the end of each session.

**These are not prescriptive playbooks — they are records of what we did**, so we can identify loops, improve our process, and potentially formalize automation later.

---

## Index

| Date | File | Chapter(s) | Key Events |
|------|------|------------|------------|
| 2026-07-11 | `docs/reflections/2026-07-11.md` | CH00, CH01 | Scaffold, provider seam, model REPL, workflow pattern identified |
| 2026-07-12 | `docs/reflections/2026-07-12.md` | CH02, CH03 | History, instructions, context tracking fixup |
| 2026-07-13 | `docs/reflections/2026-07-13.md` | CH04 | Context delivery (@file), deliver(), workspace security |

---

## Reference: The Observed Cycle

```
  1. READ     ──→  2. PLAN    ──→  3. DECIDE  ──→  4. BUILD   ──→  5. TEST
                                                                      │
                                                                      ▼
  8. NEXT    ←──  7. LOG     ←──  6. VERIFY  ←────────────────────────
```

Each chapter follows these steps organically. See individual daily reflection files for details of what happened at each step.

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

## File Map

```
docs/reflections/           — daily end-of-session reflection files
docs/phases/                — one doc per chapter (plan + record)
docs/verification/           — test run logs per chapter
docs/research/images/        — reference screenshots by chapter
docs/YYYY-MM-DD-session.md   — daily session logs (detailed operations)
DECISIONS.md                 — architectural decision records
BUILD_PLAN.md                — master progress tracker
```

---

## Philosophy

**Plan like an architect, build like a craftsman, log like a historian.**

These reflections help us see the shape of our own process — and decide what to keep, drop, or automate.