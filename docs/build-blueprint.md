# AI Build Blueprint — Project Methodology

> **⚠️ Suggested Outline — Not the defined source of truth.**
> This document captures a proposed methodology for discussion. The actual source of truth is the repository structure and the build plan as implemented.

**Key insight:** Stop thinking about "building the agent" and start thinking about **"building the knowledge required to build the agent."**

Raw knowledge lives **outside** the repository (Obsidian / documentation). The GitHub repository only contains **implementation**. AI needs persistent context so it doesn't lose architectural decisions while coding.

---

## File Structure

```
Repository/
│
├── ARCHITECTURE.md
├── AGENT.md
├── BUILD_PLAN.md
├── ROADMAP.md
├── DECISIONS.md
└── docs/
```

The AI reads these before touching code.

---

## What BUILD_PLAN.md Is

The master implementation document. Instead of being code, it explains:

- what phase we're on
- why it exists
- expected outcome
- files involved
- dependencies
- completion criteria

---

## Phase Structure

### Overall Phases

```
Phase 0   — Project Foundation
Phase 1   — Core Model Layer
Phase 2   — Harness
Phase 3   — Memory
Phase 4   — Context
Phase 5   — Tools
Phase 6   — Planning
Phase 7   — Subagents
Phase 8   — Verification
Phase 9   — Observability
Phase 10  — User Interfaces
Phase 11  — Production
```

Each phase is independent.

### Phase Template

Every phase uses this same template:

```
Phase N
<Name>

Purpose
--------
...

Goals
------
Implement:

- Feature 1
- Feature 2

Dependencies
-------------
...

Files
------

file1.py

file2.py

Tests
-----

...

Deliverables
------------

...

Acceptance
----------

...

Status
------

Not Started
```

---

## Screenshots Become Phases

From screenshots collected:

```
Screenshot 01   →   Phase 1
Screenshot 02   →   Phase 2
Screenshot 03   →   Phase 3
```

Rather than dumping screenshots into AI, extract:

- Purpose
- Concepts
- Files
- Flow
- Deliverables

The screenshots become documentation — not implementation.

---

## Every Phase Should Have

- Overview
- Architecture
- Why
- Responsibilities
- Inputs
- Outputs
- Files
- Dependencies
- Risks
- Testing
- Definition of Done
- Next Phase

That gives AI everything it needs.

---

## AI Prompt Template

Instead of prompting:

> "Build Context Management"

you prompt:

```
Read:

ARCHITECTURE.md
AGENT.md
BUILD_PLAN.md
ROADMAP.md

Current Phase:
Phase 4

Only implement Phase 4.
Do not begin Phase 5.
Update BUILD_PLAN.md when complete.
Update DECISIONS.md if architecture changes.
Produce clean commits.
```

Now every conversation starts with identical context.

---

## Phase Dependency Graph

```
Foundation
      │
      ▼
Model
      │
      ▼
History
      │
      ▼
Instructions
      │
      ▼
Context
      │
      ▼
Tools
      │
      ▼
Memory
      │
      ▼
Planning
      │
      ▼
Subagents
      │
      ▼
Verification
      │
      ▼
Observability
      │
      ▼
UI
      │
      ▼
Production
```

The AI always knows what comes next.

---

## Build Artifacts

| Document            | Purpose                                                        |
|---------------------|----------------------------------------------------------------|
| **ARCHITECTURE.md** | High-level system design and principles.                       |
| **AGENT.md**        | Rules, constraints, coding standards, AI operating instructions.|
| **BUILD_PLAN.md**   | Phase-by-phase implementation blueprint and current progress.  |
| **ROADMAP.md**      | Long-term feature milestones beyond initial implementation.    |
| **DECISIONS.md**    | Architectural Decision Record (ADR) log.                       |
| **CHANGELOG.md**    | Summary of completed work across phases.                       |
| **docs/phases/**    | One detailed doc per phase, from screenshots.                  |

---

## Recommended Workflow

1. **Extract each screenshot into its own phase document** (one Markdown file per chapter/phase).
2. **Generate `BUILD_PLAN.md`** that links all phases together into a dependency graph.
3. **Update `ARCHITECTURE.md`** to reference each phase and explain how the overall system fits.
4. **Update `AGENT.md`** with instructions telling any coding AI to always consult the architecture, build plan, and current phase before making changes.
5. **Use the phase documents as the only implementation context** during development, marking phases complete as work progresses.

This approach creates a durable knowledge base that any AI session can reload, making it much easier to maintain consistent architectural decisions throughout the entire build.