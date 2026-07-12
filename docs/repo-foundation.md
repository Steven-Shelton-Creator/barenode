# Phase 0 — Repository Foundation & Engineering Workflow

> **⚠️ Suggested Outline — Not the defined source of truth.**
> This document captures a proposed repository structure and workflow for discussion. The actual source of truth is the repository as built.

> At this point, stop writing planning documents and start building the repository itself. The repository becomes the "source of truth"; Obsidian remains the place for raw research and notes.
>
> Organize this as an **engineering project** rather than a tutorial project.

---

## Repository Structure

```
ai-agent/

├── .github/
│   └── workflows/
│
├── .vscode/
│
├── docs/
│   ├── architecture/
│   ├── phases/
│   ├── decisions/
│   ├── research/
│   └── diagrams/
│
├── agent/
│   ├── model/
│   ├── harness/
│   ├── memory/
│   ├── tools/
│   ├── planner/
│   ├── subagents/
│   ├── verifier/
│   ├── telemetry/
│   └── ui/
│
├── tests/
├── examples/
├── scripts/
├── workspace/
│
├── AGENT.md
├── ARCHITECTURE.md
├── BUILD_PLAN.md
├── ROADMAP.md
├── DECISIONS.md
├── CONTRIBUTING.md
├── README.md
└── pyproject.toml
```

Intentionally clean and scalable.

---

## Branch Strategy

Each primitive gets its own feature branch.

```
main
develop
feature/01-model
feature/02-history
feature/03-instructions
feature/04-context
feature/05-tools
feature/06-compaction
feature/07-skills
feature/08-sandbox
feature/09-memory
feature/10-planner
feature/11-subagents
feature/12-verification
feature/13-observability
feature/14-ui
```

Each phase is merged only after it passes tests.

---

## Commit Strategy

Every commit represents one meaningful unit of work.

```
git commit -m "Initialize repository structure"
git commit -m "Add model abstraction"
git commit -m "Implement conversation history"
git commit -m "Add system instruction loader"
git commit -m "Implement context injection"
git commit -m "Add tool registry"
git commit -m "Implement context compression"
git commit -m "Add skills loader"
git commit -m "Sandbox bash execution"
git commit -m "Persist session memory"
git commit -m "Add planning orchestrator"
git commit -m "Implement subagent delegation"
git commit -m "Add verification pipeline"
git commit -m "Implement telemetry"
git commit -m "Build terminal UI"
```

Clean Git history — easy to review or bisect.

---

## Development Workflow

For every phase:

1. Read the documentation.
2. Create a feature branch.
3. Implement only that phase.
4. Run tests.
5. Update documentation.
6. Commit.
7. Merge into `develop`.
8. Repeat.

No skipping ahead.

---

## Documentation Workflow

Each phase has its own document under `docs/phases/`.

```
docs/phases/

01-model.md
02-history.md
03-instructions.md
...
14-ui.md
```

Each file contains:

- Goal
- Background
- Architecture
- Files
- Dependencies
- Tests
- Acceptance Criteria
- Future Improvements

---

## GitHub Project Board

Columns:

```
Backlog → Ready → In Progress → Review → Testing → Done
```

Each phase becomes an issue that moves across the board.

---

## AI Workflow

Every coding session begins by reading:

```
ARCHITECTURE.md
AGENT.md
BUILD_PLAN.md
DECISIONS.md
Current Phase Document
```

Then the AI is instructed to:

- implement only the current phase,
- avoid unrelated refactoring,
- update documentation when architecture changes,
- keep commits focused on a single concern.

---

## Grouped Phases (Separation by Function)

Instead of treating each primitive as a standalone project, group them into logical stages:

### Tier 1 — Core Agent

- Model
- History
- Instructions
- Context

### Tier 2 — Action Layer

- Tools
- Sandbox
- Skills

### Tier 3 — Intelligence

- Memory
- Planning
- Subagents

### Tier 4 — Reliability

- Verification
- Observability

### Tier 5 — Interface

- Terminal UI
- Future Web UI

Each tier ends with a working, usable system.

---

## Recommendation

Since screenshots exist for every phase, make them the backbone of documentation.

Rather than manually transcribing, build this repository **one phase at a time** by converting each screenshot into:

1. A detailed phase document (`docs/phases/01-model.md`, etc.).
2. The implementation tasks for that phase.
3. The corresponding code.
4. The Git commits.
5. The tests.
6. The pull request checklist.

This turns the screenshots into a complete, version-controlled engineering specification — from an empty repository to a production-ready agent.