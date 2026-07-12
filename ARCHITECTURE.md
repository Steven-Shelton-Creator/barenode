# barenode Architecture

## Core Principle

**An agent = a Model + a Harness + a UI.**

The model is a stateless reasoning engine behind one API call. The UI is how a human reaches it. Everything that makes it feel like an agent lives in the middle — the harness.

## Three-Package Layering

```
┌─────────────────┐
│      UI         │  (textual-based TUI / CLI REPL)
│  (src/ui/)      │
└────────┬────────┘
         │  imports / depends
         ▼
┌─────────────────┐
│    Harness      │  (loop, context, tools, sandbox, memory,
│  (src/harness/) │   planning, verification, observability)
└────────┬────────┘
         │  imports / depends
         ▼
┌─────────────────┐
│     Model       │  (provider abstraction — OpenAI-compatible API)
│  (src/model/)   │
└─────────────────┘
```

**Arrows only point one way:** UI → Harness → Model. The core harness never knows about the screen. The model package is a thin seam so providers are swappable.

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

## Key Design Decisions

- **Model is stateless** — all statefulness lives in the harness (messages list replayed every call).
- **Tools are functions + schemas** — model decides *what*, harness decides *how*.
- **Sandbox starts closed** — no network, no credentials, drop capabilities, climb only as needed.
- **Context is finite** — never let history grow unbounded. Compress before drift.
- **Skills use progressive disclosure** — advertise one line, load full body on demand.
- **Verification is self-serve** — model runs the test, harness checks for exit 0.
- **Observability is pluggable** — OpenTelemetry seam means traces can go anywhere.
- **UI is a consumer of events**, not an owner — runs agent in a worker thread, renders tracer output.

## Guardrails

- File tools scoped to workspace directory
- Bash runs in sandbox (Docker or subprocess)
- Dangerous tools hit approval gate (no approval → fails safe)
- Secrets never reach the model prompt (don't give them, don't tell it not to touch them)
- Tool loops capped at 6 iterations