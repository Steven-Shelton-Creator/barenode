# Architectural Decision Records

This file logs every major architectural decision made during the barenode project. Each entry follows a lightweight ADR format: context, options considered, decision, and rationale.

---

## ADR-001: Repository Layout

**Status:** Closed

**Date:** 2026-07-11

### Context

After the initial scaffold, we had two competing repository layouts. The current layout (Option A — `src/` with 3 flat packages) was built first. A second layout (Option B — `agent/` with 9+ sub-packages, organized docs) was proposed. We needed to choose one and commit to it before beginning implementation.

### Option A — Current Layout

```
├── src/
│   ├── harness/          # agent loop, tools, sandbox, memory, etc.
│   ├── model/            # provider abstraction
│   └── ui/               # TUI stubs
```

### Option B — Suggested Layout

```
├── agent/
│   ├── model/   harness/   memory/   tools/   planner/
│   ├── subagents/   verifier/   telemetry/   ui/
├── docs/                # organized into subdirectories
├── examples/   workspace/   scripts/
```

### Decision

**Keep Option A as the core (3-package model under `src/`) and selectively merge infrastructure from Option B.**

Specifically:

- **Keep** `src/` with 3 packages (harness, model, ui) — the code stays put
- **Add** `docs/` subdirectories: `architecture/`, `phases/`, `decisions/`, `research/`, `diagrams/`
- **Add** `workspace/` — sandbox working directory
- **Add** `examples/` — demo scenarios
- **Rename** `PLAN.md` → `BUILD_PLAN.md` for blueprint alignment
- **Add** `ROADMAP.md`, `CONTRIBUTING.md`, `README.md`
- **Keep** existing: `AGENTS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `transcript.md`, `skills/`, `tests/`, `logs/`, `scripts/`

### Rationale

- The 3-package model directly mirrors the video source material (UI → Harness → Model)
- Separating each primitive into its own `agent/` subdirectory is over-engineering for a ~2500 line educational project
- The infrastructure additions (organized docs, workspace, examples, root docs) give us the engineering rigor without bloating the code structure
- Easy to split packages later if the project outgrows the flat layout

---

## ADR-002: Project Language & Toolchain

**Status:** Closed

**Date:** 2026-07-11

### Context

The video tutorial builds the agent in Python using `uv`. The initial scaffold was created as a Node.js project by mistake.

### Decision

Use **Python 3.11+** with **uv** as the package manager and runtime toolchain.

### Rationale

- Directly matches the video source material
- `uv` provides fast, reproducible environments
- Python is the standard language for AI/LLM agent development

---

*More ADRs will be added as decisions are made.*