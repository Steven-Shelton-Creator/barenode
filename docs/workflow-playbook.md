# The barenode Workflow — A Chapter-by-Chapter Playbook

Every chapter follows the same repeatable cycle. This is the process we used for CH01 and will use for every chapter going forward.

---

## The Full Cycle

```
  1. READ     ──→  2. PLAN    ──→  3. DECIDE  ──→  4. BUILD   ──→  5. TEST
                                                                      │
                                                                      ▼
  8. NEXT    ←──  7. LOG     ←──  6. VERIFY  ←────────────────────────
```

---

## Step 1 — READ

**What:** Consume the source material for this chapter.

- Read the relevant section of `transcript.md` (video transcript)
- Look at the screenshots in `docs/research/images/chXX/`
- Read the phase doc in `docs/phases/XX-name.md`
- Understand what the chapter adds and why

**Artifact:** Nothing new — just comprehension.

---

## Step 2 — PLAN

**What:** Write the implementation plan.

- State the **goal** in one sentence
- List the **concepts** being introduced
- Define the **acceptance criteria** (how will we know it's done?)
- Identify every **file** that needs to change
- Outline the **implementation steps** in order
- Note what is **NOT** being built (scope boundary)

**Artifact:** Update `docs/phases/XX-name.md` with the full plan section.

**CH01 example:** *"Build the bare minimum agent: a stateless chat call with a REPL so you can type messages and get responses — but every turn is an independent call with no memory."*

---

## Step 3 — DECIDE

**What:** Make the architectural decisions this chapter requires.

- List the open choices (e.g., which provider? how to configure?)
- Present options with pros/cons
- Choose one and write the rationale
- Record it in `DECISIONS.md` as a new ADR entry

**Artifact:** New ADR entry in `DECISIONS.md`.

**CH01 example:** *ADR-003 — Provider abstraction & REPL design. Chose Ollama as default, `BARENODE_MODEL=provider/model` format, all providers built in from day one.*

---

## Step 4 — BUILD

**What:** Write the code.

- Create or modify each file listed in the plan
- One concern per file
- Write real code, not pseudocode
- Include docstrings and error handling

**Artifact:** Source code files changed.

**CH01 files:** `src/model/provider.py`, `src/harness/agent.py`, `src/main.py`, `tests/test_ch01.py`, `.env.example`

---

## Step 5 — TEST

**What:** Verify the code works.

- Write automated tests (pytest) that test the new behavior
- Tests should use the fake provider so they don't need a real model
- Run `uv run pytest tests/ -v` — all tests must pass
- Test edge cases (invalid input, missing config, etc.)

**Artifact:** Test file(s) in `tests/`.

**CH01 tests:**
```python
def test_agent_echoes_with_fake_provider()
def test_agent_is_stateless()
def test_agent_default_model()
def test_invalid_model_spec()
```

---

## Step 6 — VERIFY

**What:** Manual verification that the feature works end-to-end.

- Run the fake provider REPL: `BARENODE_MODEL=fake/echo uv run agent`
- Run the real model REPL: `BARENODE_MODEL=ollama/<model> uv run agent`
- Run the demo: `uv run demo`
- Observe the expected behavior
- If it fails, debug and fix

**Artifact:** Results logged in `docs/verification/CHXX-verification.md`.

**CH01 verification:**
```
$ BARENODE_MODEL=fake/echo uv run agent
> my name is x
Echo (echo): my name is x
> what is my name
Echo (echo): what is my name
```

---

## Step 7 — LOG

**What:** Record what happened.

- Update the phase doc status to ✅ Complete
- Fill in the **Learnings** section (what surprised you, what broke, what you'd do differently)
- Write a session log in `docs/YYYY-MM-DD-session.md`
  - What was completed
  - Key decisions made
  - Notes for next session
- Git tag: `git tag -a CHXX -m "CHXX — description"`

**Artifacts:** Updated phase doc, session log file, git tag.

---

## Step 8 — NEXT

**What:** Prepare for the next chapter.

- Update `BUILD_PLAN.md` — mark current chapter complete
- Read the next chapter's transcript section
- The cycle begins again at Step 1

---

## The Full Checklist (for any chapter)

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

## Branching Strategy (for contributors)

```
main                 — stable, released
develop              — integration branch
feature/CHXX-*       — one per primitive
```

When implementing a chapter:

```bash
git checkout -b feature/CHXX-description
# ... implement ...
git commit -m "CHXX: implement <primitive>"
git checkout develop
git merge feature/CHXX-description
```

---

## Commit Message Convention

```
CH01: implement bare model call with REPL
CH02: add conversation history
CH03: implement system instructions loader
...
```

One commit per meaningful unit. Clean history, easy to bisect.

---

## File Map (where everything lives)

```
docs/phases/              — one doc per chapter (plan + record)
docs/verification/         — test run logs per chapter
docs/research/images/      — reference screenshots by chapter
docs/YYYY-MM-DD-session.md — daily session logs
DECISIONS.md               — architectural decision records
BUILD_PLAN.md              — master progress tracker
```

---

## The One-Line Philosophy

**Plan like an architect, build like a craftsman, log like a historian.**

The plan ensures you know where you're going. The build ensures it works. The log ensures you can come back tomorrow and not have to rediscover everything.