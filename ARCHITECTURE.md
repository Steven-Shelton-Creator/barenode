# barenode Architecture

## Core Principle

**An agent = a Model + a Harness + a UI.**

The model is a stateless reasoning engine behind one API call. The UI is how a human reaches it. Everything that makes it feel like an agent lives in the middle — the harness.

---

## Repository Layout

```
├── src/                          # 3-package core
│   ├── harness/                  #   agent loop, tools, sandbox, memory, etc.
│   ├── model/                    #   provider abstraction
│   └── ui/                       #   terminal UI (textual)
│
├── docs/                         # organized documentation
│   ├── architecture/             #   deep-dive design docs
│   ├── phases/                   #   one file per build phase
│   ├── decisions/                #   ADR records
│   ├── research/                 #   reference material, screenshots, links
│   └── diagrams/                 #   ascii / mermaid diagrams
│
├── skills/                       # skill directories (progressive disclosure)
├── tests/                        # Python test suite
├── examples/                     # scripted demo scenarios
├── scripts/                      # run scripts
├── logs/                         # runtime logs
├── workspace/                    # sandbox working directory
│
├── AGENTS.md                     # agent system prompt (auto-loaded)
├── ARCHITECTURE.md               # this file
├── BUILD_PLAN.md                 # phase-by-phase implementation blueprint
├── ROADMAP.md                    # long-term vision
├── DECISIONS.md                  # architectural decision records
├── CONTRIBUTING.md               # how to develop / contribute
├── README.md                     # project intro
├── transcript.md                 # source video transcript
├── pyproject.toml                # project config (uv)
└── .gitignore
```

---

## Three-Package Layering

```
┌─────────────────┐
│      UI         │  (textual-based TUI / CLI REPL)
│  (src/ui/)      │
└────────┬────────┘
         │  imports / depends
         ▼
┌─────────────────────────────────┐
│           Harness               │  (loop, context, tools, sandbox,
│  (src/harness/)                 │   memory, planning, verification,
│                                 │   observability, subagents, skills)
└────────┬────────────────────────┘
         │  imports / depends
         ▼
┌─────────────────────────────────┐
│           Model                 │  (provider abstraction — OpenAI-compatible)
│  (src/model/)                   │
└─────────────────────────────────┘
```

**Arrows only point one way:** UI → Harness → Model. The core harness never knows about the screen. The model package is a thin seam so providers are swappable.

---

## Harness Internals (src/harness/)

All primitives live in one flat package — the harness is the agent. Each file maps to one chapter:

| File              | Chapter | Primitive          |
|-------------------|---------|--------------------|
| `agent.py`        | CH01–02 | Model call + history |
| `instructions.py` | CH03    | System prompt + agents.md loader |
| `context.py`      | CH04    | @file reference injection |
| `tools.py`        | CH05    | Tool registry, approval gates |
| `compaction.py`   | CH06    | Context compression |
| `limits.py`       | CH06    | Token budget, clamping |
| `skills.py`       | CH07    | Progressive disclosure skill loader |
| `sandbox.py`      | CH08    | Docker isolation / scrubbed subprocess |
| `memory.py`       | CH09    | JSONL session persistence |
| `orchestrator.py` | CH10    | Planning control plane |
| `subagent.py`     | CH11    | Delegation, fan-out |
| `verify.py`       | CH12    | Self-verification gate |
| `tracer.py`       | CH13    | OpenTelemetry spans |
| `events.py`       | CH13    | GenAI event semantics |

---

## Primitives (in build order)

| #  | Primitive           | Package    | What it adds                                      |
|----|---------------------|------------|---------------------------------------------------|
| 0  | Model               | model      | Single chat call, stateless REPL                  |
| 1  | History             | harness    | `self.messages` list, append user + reply each turn |
| 2  | Instructions        | harness    | System prompt + `agents.md` auto-load             |
| 3  | Context Delivery    | harness    | `@file` syntax → read file, inject content        |
| 4  | Tools               | harness    | Function + schema registry, approval gates        |
| 5  | Context Management  | harness    | Compress middle, keep head/tail, clamp sizes      |
| 6  | Skills              | harness    | `skill.md` directories, progressive disclosure    |
| 7  | Sandbox             | harness    | Docker isolation (or scrubbed local fallback)     |
| 8  | Durable State       | harness    | JSONL session persistence, keyword search         |
| 9  | Planning            | harness    | Orchestrator: model plans steps, harness drives   |
| 10 | Subagents           | harness    | Fresh agent per subtask, context isolation        |
| 11 | Self-Verification   | harness    | Run tests, don't accept "done" without green run  |
| 12 | Observability       | harness    | OpenTelemetry spans, cost tracking, multi-sink    |
| 13 | Terminal UI         | ui         | Two-pane TUI, trace stream, approval modals       |

---

## Grouped Tiers

```
Tier 1 — Core Agent        Tier 2 — Action Layer     Tier 3 — Intelligence
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Model           │      │  Tools           │      │  Skills          │
│  History         │      │  Context Mgmt    │      │  Sandbox         │
│  Instructions    │      └──────────────────┘      │  Memory          │
│  Context         │                                 │  Planning        │
└──────────────────┘                                 │  Subagents       │
                                                     └──────────────────┘
                         Tier 4 — Reliability       Tier 5 — Interface
                         ┌──────────────────┐      ┌──────────────────┐
                         │  Verification    │      │  Terminal UI     │
                         │  Observability   │      │  (future: Web)   │
                         └──────────────────┘      └──────────────────┘
```

Each tier ends with a working, usable system.

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Model is stateless** | All statefulness lives in the harness (messages list replayed every call) |
| **Tools are functions + schemas** | Model decides *what*, harness decides *how* |
| **Sandbox starts closed** | No network, no credentials, drop capabilities, climb only as needed |
| **Context is finite** | Never let history grow unbounded — compress before drift |
| **Skills use progressive disclosure** | Advertise one line, load full body on demand |
| **Verification is self-serve** | Model runs the test, harness checks for exit 0 |
| **Observability is pluggable** | OpenTelemetry seam means traces can go anywhere |
| **UI is a consumer of events** | Runs agent in a worker thread, renders tracer output — not an owner |

## Guardrails

- File tools scoped to workspace directory
- Bash runs in sandbox (Docker or subprocess)
- Dangerous tools hit approval gate (no approval → fails safe)
- Secrets never reach the model prompt (don't give them, don't tell it not to touch them)
- Tool loops capped at 6 iterations