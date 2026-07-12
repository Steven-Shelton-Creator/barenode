# barenode

**Building an AI Agent From Scratch in Python — One Primitive at a Time.**

A practical, educational build of a real coding agent, following the [Harness Engineering Masterclass](https://www.youtube.com/watch?v=oUBgqzcV1qw) video series. Every chapter adds one primitive — from a bare model call to a full terminal UI.

---

## Core Idea

**An agent = a Model + a Harness + a UI.**

| Layer | Package | Role |
|-------|---------|------|
| Model | `src/model/` | Stateless reasoning engine (provider abstraction) |
| Harness | `src/harness/` | Loop, context, tools, sandbox, memory — the agent |
| UI | `src/ui/` | Terminal interface (consumer of harness events) |

Arrows point one way: **UI → Harness → Model**.

---

## Quick Start

```bash
# Prerequisites: Python 3.11+, uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and run
git clone https://github.com/Steven-Shelton-Creator/barenode.git
cd barenode
uv run agent          # live REPL (CH01+)
uv run tui            # two-pane TUI (CH14+)
uv run demo           # scripted demo
uv run verify         # test suite
```

---

## Build Progress

| Tier | Phases | Status |
|------|--------|--------|
| Foundation | Repo scaffold, docs, decisions | ✅ Done |
| Core Agent | Model, History, Instructions, Context | 📝 Not started |
| Action Layer | Tools, Sandbox, Skills | 📝 Not started |
| Intelligence | Memory, Planning, Subagents | 📝 Not started |
| Reliability | Verification, Observability | 📝 Not started |
| Interface | Terminal UI | 📝 Not started |

---

## Key Documents

| Document | Purpose |
|----------|---------|
| `ARCHITECTURE.md` | System design, layering, guardrails |
| `BUILD_PLAN.md` | Phase-by-phase implementation blueprint |
| `DECISIONS.md` | Architectural Decision Records |
| `ROADMAP.md` | Long-term vision |
| `AGENTS.md` | Agent system prompt (auto-loaded) |
| `transcript.md` | Full video transcript (educational source) |

---

## License

MIT