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

## ADR-003: CH01 — Provider Abstraction & REPL Design

**Status:** Closed

**Date:** 2026-07-11

### Context

Chapter 01 requires a bare model call — the first primitive. We need a provider seam so the agent can talk to any LLM backend, and a REPL so the user can interact. The transcript says: *"The call goes through a seam: a free `chat` function over a provider (LM Studio, Ollama, or OpenRouter)."* and *"If you want to have fake provider to run the test, we just swap the provider in one line."*

### Options Considered

| Provider | Setup | Pros | Cons |
|----------|-------|------|------|
| **Ollama** | `ollama pull <model>` | Free, local, dead simple API | Requires Ollama daemon |
| **OpenRouter** | API key | No local install, free tier | Needs internet + API key |
| **LM Studio** | Download + GUI | Matches video exactly | Heavier setup |
| **Fake/Echo** | No dependencies | Perfect for tests | Not a real LLM |

### Decision

1. **Default provider:** Ollama (we already have it with 8b models)
2. **Config format:** Single environment variable `BARENODE_MODEL=provider/model`
3. **Default model:** `ollama/qwen2.5:8b` (or whichever we have locally)
4. **Provider-agnostic:** All providers (ollama, openrouter, lstudio, fake) built into the seam from day one — user picks by changing one env var
5. **No keys in repo:** The `.env.example` documents the vars, `.gitignore` blocks `.env`
6. **REPL:** Simple `input()` loop with `/quit` to exit

### Rationale

- The provider seam is the entire point of CH01 — making it swappable in one line teaches the architecture
- Ollama is the simplest local setup (no Docker, no GUI, just a daemon + CLI)
- OpenRouter is the easiest path for users who don't want to run local models
- Fake provider means tests run without any model at all — critical for CI
- The `provider/model` format is unambiguous and extensible (adding a new provider is just another branch)

### Consequences

- Every user must bring their own model or API key — nothing is pre-configured
- The fake provider becomes the test bedrock for all future chapters
- Later chapters will add history, tools, etc. on top of this same send() interface