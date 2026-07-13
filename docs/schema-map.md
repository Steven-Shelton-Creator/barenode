# barenode Schema Map

> Quick-reference directory map for fresh session orientation.  
> **Last updated:** 2026-07-12  
> **Tags:** CH01, CH02  
> **Branch:** `master`  
> **HEAD:** `1203984` — chore: fix context tracking  
> **Remote:** `origin` → `github.com/Steven-Shelton-Creator/barenode.git`

---

## Start Here (Fresh Session)

When you load up fresh, read these in order:

1. **This file** — get your bearings
2. **`docs/workflow-reflections.md`** — master index of daily process reflections
3. **`docs/reflections/YYYY-MM-DD.md`** — most recent daily reflection (what we did last session)
4. **`docs/2026-07-12-session.md`** — most recent session log (detailed checklist)
5. **`BUILD_PLAN.md`** — what's next on the chapter roadmap

---

## Three Tracking Systems

We maintain three parallel tracking systems. Each serves a different purpose:

| # | System | Location | Purpose | Format |
|---|--------|----------|---------|--------|
| 1 | **Chapter Phase Docs** | `docs/phases/CHXX-name.md` | Pre-planned blueprint per chapter. Status updated on completion. | One doc per chapter, drafted before implementation, completed after |
| 2 | **Session Logs** | `docs/YYYY-MM-DD-session.md` | Detailed daily checklist of everything completed. Operational log. | One file per day, bullet-point checklist |
| 3 | **Workflow Reflections** | `docs/reflections/YYYY-MM-DD.md` | Post-hoc process reflection. Tracks the *actions we took* to complete daily executables. | One file per day, narrative process record |

Master index: `docs/workflow-reflections.md`

---

## Root Layout

```
/home/steven/projects/barenode/
├── src/                     # Source code (3 packages)
│   ├── model/               #   Provider abstraction (provider seam)
│   │   ├── __init__.py
│   │   ├── provider.py      #     chat() — 4 backends (ollama, openrouter, lstudio, fake)
│   │   └── pricing.py       #     Cost tables (CH13 stub)
│   ├── harness/             #   Agent loop & primitives
│   │   ├── __init__.py
│   │   ├── agent.py         #     Agent class with send() — CH02 has history
│   │   ├── instructions.py  #     CH03 stub
│   │   ├── context.py       #     CH04 stub
│   │   ├── tools.py         #     CH05 stub
│   │   ├── compaction.py    #     CH06 stub
│   │   ├── limits.py        #     CH06 stub
│   │   ├── skills.py        #     CH07 stub
│   │   ├── sandbox.py       #     CH08 stub
│   │   ├── memory.py        #     CH09 stub
│   │   ├── orchestrator.py  #     CH10 stub
│   │   ├── subagent.py      #     CH11 stub
│   │   ├── verify.py        #     CH12 stub (has run() placeholder)
│   │   ├── tracer.py        #     CH13 stub
│   │   └── events.py        #     CH13 stub
│   └── ui/                  #   Terminal UI
│       ├── __init__.py
│       ├── app.py           #     CH14 stub (uv run tui)
│       └── widgets.py       #     CH14 stub
│
├── tests/                   # Python test suite (pytest)
│   ├── __init__.py
│   ├── test_smoke.py        #   Import checks (2 tests)
│   ├── test_ch01.py         #   CH01 stateless model tests (4 tests)
│   └── test_ch02.py         #   CH02 history tests (4 tests)
│
├── docs/                    # Documentation
│   ├── reflections/         #   [TRACKING SYSTEM 3] Daily process reflections
│   │   ├── 2026-07-11.md    #     Day 1: CH00+CH01 (scaffold, model)
│   │   └── 2026-07-12.md    #     Day 2: CH02 (history)
│   ├── phases/              #   [TRACKING SYSTEM 1] Chapter blueprints
│   │   ├── 00-foundation.md #     ✅ Complete
│   │   ├── 01-model.md      #     ✅ Complete
│   │   ├── 02-history.md    #     ✅ Complete
│   │   └── 03-14.md         #     ❌ Stubs (not started)
│   ├── verification/        #   Test run logs per chapter
│   │   ├── CH01-verification.md  # ✅ Complete
│   │   └── CH02-verification.md  # ✅ Complete
│   ├── research/images/     #   24 reference screenshots (ch01-ch14)
│   │   ├── ch01/            #     2 images
│   │   ├── ch02/            #     1 image
│   │   ├── ch03/            #     2 images
│   │   ├── ch04/            #     1 image
│   │   ├── ch05/            #     2 images
│   │   ├── ch06/            #     3 images
│   │   ├── ch07/            #     1 image
│   │   ├── ch08/            #     4 images
│   │   ├── ch09/            #     2 images
│   │   ├── ch10/            #     1 image
│   │   ├── ch11/            #     1 image
│   │   ├── ch12/            #     1 image
│   │   ├── ch13/            #     2 images
│   │   └── ch14/            #     1 image
│   ├── architecture/        #   Deep-dive design docs (empty)
│   ├── decisions/           #   ADR backups (empty)
│   ├── diagrams/            #   ASCII / mermaid diagrams (empty)
│   ├── schema-map.md        #   THIS FILE — directory map for orientation
│   ├── workflow-reflections.md  # Master index for daily reflection files
│   ├── build-blueprint.md   #   Early outline document
│   ├── repo-foundation.md   #   Early outline document
│   ├── github-token-guide.md    #   Reference doc
│   ├── 2026-07-11-session.md    #   [TRACKING SYSTEM 2] Session log — Day 1
│   └── 2026-07-12-session.md    #   [TRACKING SYSTEM 2] Session log — Day 2
│
├── skills/                  # Skill directories (progressive disclosure)
│   └── sign-off/
│       └── skill.md         #   Signs off with code word "hila"
│
├── scripts/                 # Run scripts (empty)
├── examples/                # Demo scenarios (empty)
├── logs/                    # Runtime logs (empty)
├── workspace/               # Sandbox working directory (empty)
│
├── AGENTS.md                # Agent system prompt (auto-loaded)
├── ARCHITECTURE.md          # Three-package layering
├── BUILD_PLAN.md            # Phase-by-phase blueprint (master tracker)
├── ROADMAP.md               # Long-term vision
├── DECISIONS.md             # ADR records (ADR-001 through ADR-004)
├── CONTRIBUTING.md          # Development guide
├── README.md                # Project intro
├── transcript.md            # Full video transcript (8500 lines)
├── pyproject.toml           # UV project config
├── uv.lock                  # UV dependency lockfile
├── .env.example             # Provider config template
└── .gitignore               # Git exclusion rules
```

---

## Chapter Phase Status

| Phase | Doc | Status |
|-------|-----|--------|
| CH00 — Foundation | `docs/phases/00-foundation.md` | ✅ Complete |
| CH01 — Model | `docs/phases/01-model.md` | ✅ Complete |
| CH02 — History | `docs/phases/02-history.md` | ✅ Complete |
| CH03 — Instructions | `docs/phases/03-instructions.md` | ❌ Stub |
| CH04 — Context Delivery | `docs/phases/04-context.md` | ❌ Stub |
| CH05 — Tools | `docs/phases/05-tools.md` | ❌ Stub |
| CH06 — Context Management | `docs/phases/06-compaction.md` | ❌ Stub |
| CH07 — Skills | `docs/phases/07-skills.md` | ❌ Stub |
| CH08 — Sandbox | `docs/phases/08-sandbox.md` | ❌ Stub |
| CH09 — Durable State | `docs/phases/09-memory.md` | ❌ Stub |
| CH10 — Planning | `docs/phases/10-planner.md` | ❌ Stub |
| CH11 — Subagents | `docs/phases/11-subagents.md` | ❌ Stub |
| CH12 — Self-Verification | `docs/phases/12-verification.md` | ❌ Stub |
| CH13 — Observability | `docs/phases/13-observability.md` | ❌ Stub |
| CH14 — Terminal UI | `docs/phases/14-ui.md` | ❌ Stub |

---

## Running the Project

| Command | What it does |
|---------|--------------|
| `uv run agent` | Interactive REPL |
| `uv run demo` | Scripted demo |
| `uv run tui` | Terminal UI (CH14+ only) |
| `uv run verify` | Self-verification suite (CH12+ only) |
| `uv run pytest tests/ -v` | Run all automated tests |

---

## Provider Options

| `BARENODE_MODEL=` | Provider | Requires |
|-------------------|----------|----------|
| `ollama/<model>` | Ollama | Ollama daemon, model pulled |
| `openrouter/<model>` | OpenRouter | `OPENROUTER_API_KEY` env var |
| `lstudio/<model>` | LM Studio | LM Studio running locally |
| `fake/echo` | Fake/Echo | Nothing — built-in for tests |

---

## Git Tags

| Tag | Chapter | Description |
|-----|---------|-------------|
| `CH01` | Model | Bare model call, stateless REPL, provider seam |
| `CH02` | History | Conversation history, in-memory message list |

---

## Implementation Status

| Tier | Chapters | Status |
|------|----------|--------|
| 1 — Core Agent | CH01–04 | 50% complete (CH01-02 done, CH03-04 stubs) |
| 2 — Action Layer | CH05–08 | ❌ Not started (stubs only) |
| 3 — Intelligence | CH09–11 | ❌ Not started (stubs only) |
| 4 — Reliability | CH12–13 | ❌ Not started (stubs only) |
| 5 — Interface | CH14 | ❌ Not started (stubs only) |

---

## Decision Records

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Repository Layout | Closed |
| ADR-002 | Project Language & Toolchain | Closed |
| ADR-003 | CH01 Provider Abstraction & REPL | Closed |
| ADR-004 | CH02 Provider Signature Change | Closed |

---

## Quick Reference: Where to Find Things

| What you need | Go to |
|---------------|-------|
| What did we do last session? | `docs/reflections/YYYY-MM-DD.md` (most recent) |
| What's the next chapter to build? | `BUILD_PLAN.md` |
| What decisions did we make? | `DECISIONS.md` |
| What are the test results? | `docs/verification/CHXX-verification.md` |
| What does the architecture look like? | `ARCHITECTURE.md` |
| What does the agent system prompt say? | `AGENTS.md` |
| What's the full video transcript? | `transcript.md` |
| What model should I use? | `.env.example` |