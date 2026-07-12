# barenode Schema Map

> Quick-reference directory map for fresh session orientation.  
> **Last updated:** 2026-07-12  
> **Tags:** CH01, CH02

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
├── docs/                    # Documentation
│   ├── reflections/         #   Daily end-of-session workflow reflections
│   │   ├── 2026-07-11.md    #     Day 1: CH00+CH01 (scaffold, model)
│   │   └── 2026-07-12.md    #     Day 2: CH02 (history)
│   ├── phases/              #   One doc per chapter (plan + record)
│   │   ├── 00-foundation.md #     ✅ Complete (scaffold)
│   │   ├── 01-model.md      #     ✅ Complete (model seam)
│   │   ├── 02-history.md    #     ✅ Complete (history)
│   │   └── 03-instructions.md ... 14-ui.md  (all stubs)
│   ├── verification/        #   Test run logs per chapter
│   │   ├── CH01-verification.md  # ✅ Complete
│   │   └── CH02-verification.md  # ✅ Complete
│   ├── research/images/     #   Reference screenshots by chapter
│   ├── architecture/        #   Deep-dive design docs
│   ├── decisions/           #   ADR backups
│   ├── diagrams/            #   ASCII / mermaid diagrams
│   ├── build-blueprint.md   #   Early outline
│   ├── repo-foundation.md   #   Early outline
│   └── workflow-reflections.md  # Master index for daily reflection files
│
├── tests/                   # Python test suite (pytest)
│   ├── __init__.py
│   ├── test_smoke.py        #   Import checks (2 tests)
│   ├── test_ch01.py         #   CH01 stateless model tests (4 tests)
│   └── test_ch02.py         #   CH02 history tests (4 tests)
│
├── skills/                  # Skill directories (progressive disclosure)
├── examples/                # Scripted demo scenarios
├── scripts/                 # Run scripts
├── logs/                    # Runtime logs
├── workspace/               # Sandbox working directory
│
├── AGENTS.md                # Agent system prompt (auto-loaded)
├── ARCHITECTURE.md          # Three-package layering
├── BUILD_PLAN.md            # Phase-by-phase blueprint (master tracker)
├── ROADMAP.md               # Long-term vision
├── DECISIONS.md             # ADR records (ADR-001 through ADR-004)
├── CONTRIBUTING.md          # Development guide
├── README.md                # Project intro
├── transcript.md            # Full video transcript
├── pyproject.toml           # UV project config
├── .env.example             # Provider config template
└── .gitignore
```

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
