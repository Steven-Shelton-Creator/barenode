# barenode Schema Map

> Quick-reference directory map for fresh session orientation.  
> **Last updated:** 2026-07-15  
> **Tags:** CH01 through CH14  
> **Branch:** `main`  
> **HEAD:** `(current)` (CH14 — Terminal UI)  
> **Remote:** `origin` → `github.com/Steven-Shelton-Creator/barenode.git`

---

## Start Here (Fresh Session)

When you load up fresh, read these in order:

1. **This file** — get your bearings
2. **`CHANGELOG.md`** — full commit history organized by tag/release
3. **`docs/workflow-reflections.md`** — master index of daily process reflections
4. **`docs/reflections/YYYY-MM-DD.md`** — most recent daily reflection (what we did last session)
5. **`docs/2026-07-14-session.md`** — most recent session log (detailed checklist)
6. **`BUILD_PLAN.md`** — what's next on the chapter roadmap

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
│   │   ├── provider.py      #     chat(messages: list[dict]) — 4 backends
│   │   └── pricing.py       #     ✅ CH13 — cost tables per model
│   ├── harness/             #   Agent loop & primitives
│   │   ├── __init__.py
│   │   ├── agent.py         #     Agent class — CH02 history, CH03 instructions, CH04 @file
│   │   ├── instructions.py  #     ✅ CH03 — system prompt + AGENTS.md loader
│   │   ├── context.py       #     ✅ CH04 — @file context delivery
│   │   ├── tools.py         #     ✅ CH05 — Tool registry, 6 tools
│   │   ├── compaction.py    #     ✅ CH06 — context management
│   │   ├── limits.py        #     ✅ CH06 — token budget
│   │   ├── skills.py        #     ✅ CH07 — skill loader
│   │   ├── sandbox.py       #     ✅ CH08 — Docker isolation
│   │   ├── memory.py        #     ✅ CH09 — JSONL persistence
│   │   ├── orchestrator.py  #     ✅ CH10 — planning
│   │   ├── subagent.py      #     ✅ CH11 — delegation
│   │   ├── verify.py        #     ✅ CH12 — self-verification gate
│   │   ├── tracer.py        #     ✅ CH13 — observability spans, sinks
│   │   └── events.py        #     ✅ CH13 — GenAI event semantics
│   └── ui/                  #   Terminal UI
│       ├── __init__.py
│       ├── app.py           #     ✅ CH14 — TUI app
│       └── widgets.py       #     ✅ CH14 — TUI widgets
│
├── tests/                   # Python test suite (pytest)
│   ├── __init__.py
│   ├── test_smoke.py        #   Import checks (2 tests)
│   ├── test_ch01.py         #   CH01 stateless model tests (4 tests)
│   ├── test_ch02.py         #   CH02 history tests (4 tests)
│   ├── test_ch03.py         #   CH03 instructions tests (9 tests)
│   ├── test_ch04.py         #   CH04 context delivery tests (15 tests)
│   ├── test_ch05.py         #   CH05 tool tests (38 tests)
│   ├── test_ch06.py         #   CH06 compaction tests (29 tests)
│   ├── test_ch07.py         #   CH07 skills tests (26 tests)
│   ├── test_ch08.py         #   CH08 sandbox tests (15 tests)
│   ├── test_ch09.py         #   CH09 memory tests (20 tests)
│   ├── test_ch10.py         #   CH10 planning tests (19 tests)
│   ├── test_ch11.py         #   CH11 subagent tests (16 tests)
│   ├── test_ch12.py         #   CH12 verification tests (28 tests)
│   ├── test_ch13.py         #   CH13 observability tests (30 tests)
│   └── test_ch14.py         #   CH14 TUI tests (17 tests)
│
├── docs/                    # Documentation
│   ├── reflections/         #   [TRACKING SYSTEM 3] Daily process reflections
│   │   ├── 2026-07-11.md    #     Day 1: CH00+CH01 (scaffold, model)
│   │   ├── 2026-07-12.md    #     Day 2: CH02+CH03 (history, instructions)
│   │   └── 2026-07-13.md    #     Day 3: CH04 (context delivery)
│   ├── phases/              #   [TRACKING SYSTEM 1] Chapter blueprints
│   │   ├── 00-foundation.md #     ✅ Complete
│   │   ├── 01-model.md      #     ✅ Complete
│   │   ├── 02-history.md    #     ✅ Complete
│   │   ├── 03-instructions.md   # ✅ Complete
│   │   ├── 04-context.md    #     ✅ Complete
│   │   ├── 05-tools.md      #     ✅ Complete
│   │   ├── 06-compaction.md #     ✅ Complete
│   │   ├── 07-skills.md     #     ✅ Complete
│   │   ├── 08-sandbox.md    #     ✅ Complete
│   │   ├── 09-memory.md     #     ✅ Complete
│   │   ├── 10-planner.md    #     ✅ Complete
│   │   ├── 11-subagents.md  #     ✅ Complete
│   │   ├── 12-verification.md   # ✅ Complete
│   │   ├── 13-observability.md  # ✅ Complete
│   │   └── 14-ui.md         #     ✅ Complete
│   ├── verification/        #   Test run logs per chapter
│   │   ├── CH01-verification.md  # ✅ Complete
│   │   ├── CH02-verification.md  # ✅ Complete
│   │   ├── CH03-verification.md  # ✅ Complete
│   │   ├── CH04-verification.md  # ✅ Complete
│   │   ├── CH05-verification.md  # ✅ Complete
│   │   ├── CH06-verification.md  # ✅ Complete
│   │   ├── CH07-verification.md  # ✅ Complete
│   │   ├── CH08-verification.md  # ✅ Complete
│   │   ├── CH09-verification.md  # ✅ Complete
│   │   ├── CH10-verification.md  # ✅ Complete
│   │   ├── CH11-verification.md  # ✅ Complete
│   │   ├── CH12-verification.md  # ✅ Complete
│   │   ├── CH13-verification.md  # ✅ Complete
│   │   └── CH14-verification.md  # ✅ Complete
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
│   ├── 2026-07-12-session.md    #   [TRACKING SYSTEM 2] Session log — Day 2
│   └── 2026-07-13-session.md    #   [TRACKING SYSTEM 2] Session log — Day 3
│   └── 2026-07-14-session.md    #   [TRACKING SYSTEM 2] Session log — Day 4
│
├── skills/                  # Skill directories (progressive disclosure)
│   └── sign-off/
│       └── skill.md         #   Signs off with code word "hila"
│
├── scripts/                 # Run scripts
│   └── intake.sh            #   Credential/configuration bootstrap
├── examples/                # Demo scenarios (empty)
├── logs/                    # Runtime logs (empty)
├── workspace/               # Sandbox working directory (empty)
│
├── AGENTS.md                # Agent system prompt (auto-loaded)
├── ARCHITECTURE.md          # Three-package layering
├── BUILD_PLAN.md            # Phase-by-phase blueprint (master tracker)
├── ROADMAP.md               # Long-term vision
├── DECISIONS.md             # ADR records (ADR-001 through ADR-005)
├── CONTRIBUTING.md          # Development guide
├── README.md                # Project intro
├── CHANGELOG.md             # Full commit history organized by tag/release
├── transcript.md            # Full video transcript (130 lines)
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
| CH03 — Instructions | `docs/phases/03-instructions.md` | ✅ Complete |
| CH04 — Context Delivery | `docs/phases/04-context.md` | ✅ Complete |
| CH05 — Tools | `docs/phases/05-tools.md` | ✅ Complete |
| CH06 — Context Management | `docs/phases/06-compaction.md` | ✅ Complete |
| CH07 — Skills | `docs/phases/07-skills.md` | ✅ Complete |
| CH08 — Sandbox | `docs/phases/08-sandbox.md` | ✅ Complete |
| CH09 — Durable State | `docs/phases/09-memory.md` | ✅ Complete |
| CH10 — Planning | `docs/phases/10-planner.md` | ✅ Complete |
| CH11 — Subagents | `docs/phases/11-subagents.md` | ✅ Complete |
| CH12 — Self-Verification | `docs/phases/12-verification.md` | ✅ Complete |
| CH13 — Observability | `docs/phases/13-observability.md` | ✅ Complete |
| CH14 — Terminal UI | `docs/phases/14-ui.md` | ✅ Complete |

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
| `CH03` | Instructions | System prompt + AGENTS.md auto-load + workspace |
| `CH04` | Context Delivery | `@file` reference injection via deliver() |
| `CH05` | Tools | Function registry, calculator, file tools, approval gates |
| `CH06` | Context Management | Compaction, token budget, clamping |
| `CH07` | Skills | Progressive disclosure, skill.md frontmatter loader |
| `CH08` | Sandbox | Docker isolation, workspace fencing, local fallback |
| `CH09` | Durable State | JSONL session persistence, keyword search |
| `CH10` | Planning | Orchestrator, JSON plan, step execution, retry |
| `CH11` | Subagents | Delegate, fan-out, context isolation |
| `CH12` | Self-Verification | Test gate, exit-code check, verification prompt |
| `CH13` | Observability | Tracer, spans, pricing, ConsoleSink, JsonlSink |
| `CH14` | Terminal UI | Two-pane TUI, trace stream, approval modal |

---

## Implementation Status

| Tier | Chapters | Status |
|------|----------|--------|
| 1 — Core Agent | CH01–04 | ✅ **100% complete** |
| 2 — Action Layer | CH05–08 | ✅ **100% complete** |
| 3 — Intelligence | CH09–11 | ✅ **100% complete** |
| 4 — Reliability | CH12–13 | ✅ **100% complete** |
| 5 — Interface | CH14 | ✅ **100% complete** |

---

## Decision Records

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Repository Layout | Closed |
| ADR-002 | Project Language & Toolchain | Closed |
| ADR-003 | CH01 Provider Abstraction & REPL | Closed |
| ADR-004 | CH02 Provider Signature Change | Closed |
| ADR-005 | Intake Valve — Memory-Only Credential Security | Closed |
| ADR-006 | CH04 Context Delivery — @file Design | Closed |
| ADR-007 | CH11 Subagent Session Persistence | Open (deferred) |
| ADR-008 | Pi vs Barenode — Session Forking vs Subagent Delegation | Informational |
| ADR-009 | CH11 Subagent Harness Weight — Full Clone vs Lightweight | Open (deferred) |

---

## Recent Commits (Latest 10)

| Commit | Description |
|--------|-------------|
| `c49d1b0` | **CH12: implement Self-Verification — code-change gate, test runner, exit-code check** |
| `2c61c10` | fix: move CH11 comparison doc to tests/compare_CH11.py, remove docs/tests |
| `8f26494` | docs: add ADR-009 — subagent harness weight, full clone vs lightweight |
| `048a26e` | docs: add ADR-008 — Pi vs barenode subagent architecture comparison |
| `3aaeaa3` | docs: add ADR-007 — subagent session persistence decision (deferred) |
| `252cc9a` | **CH11: implement Subagents — delegate, fan-out, context isolation** |
| `de1b1b4` | **CH10: implement Planning — orchestrator, JSON plan generation, step execution** |
| `6fe1a1b` | docs: add CH11 implementation vs blueprint comparison to docs/tests |
| `8f26494` | docs: add ADR-009 — subagent harness weight, full clone vs lightweight |
| `048a26e` | docs: add ADR-008 — Pi vs barenode subagent architecture comparison |

> Full history: `CHANGELOG.md` (organized by tag) or `git log --oneline`

---

## Quick Reference: Where to Find Things

| What you need | Go to |
|---------------|-------|
| What did we do last session? | `docs/reflections/2026-07-14.md` (most recent) |
| What's the next chapter to build? | `BUILD_PLAN.md` |
| What decisions did we make? | `DECISIONS.md` |
| What are the test results? | `docs/verification/CH12-verification.md` |
| What does the architecture look like? | `ARCHITECTURE.md` |
| What does the agent system prompt say? | `AGENTS.md` |
| What's the full commit history? | `CHANGELOG.md` |
| What's the full video transcript? | `transcript.md` |
| What model should I use? | `.env.example` |