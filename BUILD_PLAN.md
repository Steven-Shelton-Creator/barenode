# barenode Build Plan

**Source:** [Building an AI Agent From Scratch in Python — One Primitive at a Time](https://www.youtube.com/watch?v=oUBgqzcV1qw)

## Milestones

Each milestone maps to one chapter / git tag. Every chapter builds one primitive and ends with a working, demonstrable agent against a real model.

---

### Phase 1 — Foundation (Chapters 0–2)

| Step | Tag        | What We Build                          | Files Touched                  |
|------|------------|----------------------------------------|--------------------------------|
| 0    | `CH00`     | Scaffold: `pyproject.toml`, `uv`, dirs | project setup                  |
| 1    | `CH01`     | ✅ Bare model call — stateless REPL       | `src/model/`, `src/harness/`    |
| 2    | `CH02`     | ✅ History — `self.messages` list         | `src/harness/agent.py`, `src/model/provider.py` |

**Demo:** Start REPL, type "my name is X", next turn ask "what is my name?" — CH01 forgets, CH02 remembers.

---

### Phase 2 — Personality & Context (Chapters 3–4)

| Step | Tag    | What We Build                          | Files Touched                    |
|------|--------|----------------------------------------|----------------------------------|
| 3    | `CH03` | ✅ Instructions + `agents.md` + workspace | `src/harness/instructions.py`, `src/harness/agent.py`, `tests/test_ch03.py` |
| 4    | `CH04` | ✅ Context delivery (`@file` references)  | `src/harness/context.py` |

**Demo:** Create `agents.md` with personality. Reference `@facts.txt` — model reads and answers from it.

---

### Phase 3 — Action (Chapters 5–6)

| Step | Tag    | What We Build                          | Files Touched                    |
|------|--------|----------------------------------------|----------------------------------|
| 5    | `CH05` | ✅ Tool registry, calculator tool,        | `src/harness/tools.py`,          |
|      |        | ✅ approval gates                       | `src/harness/approval.py`,        |
|      |        | ✅ tool loop in agent                   | `src/harness/agent.py`,           |
|      |        | ✅ ModelResponse structured return      | `src/model/provider.py`          |
| 6    | `CH06` | ✅ Context management (compress + clamp) | `src/harness/compaction.py`,     |
|      |        | ✅ token budget, token estimator        | `src/harness/limits.py`          |

**Demo:** Ask calculator tool — exact answer. Write file — approval gate pauses. Flood context — compaction fires, head/tail survive.

---

### Phase 4 — Memory & Isolation (Chapters 7–9)

| Step | Tag    | What We Build                          | Files Touched                    |
|------|--------|----------------------------------------|----------------------------------|
| 7    | `CH07` | ✅ Skills — `skill.md` directories        | `src/harness/skills.py`,          |
|      |        | ✅ frontmatter parser, prompt injection    | `src/harness/instructions.py`    |
| 8    | `CH08` | ✅ Sandbox — Docker isolation, local fallback | `src/harness/sandbox.py`,          |
|      |        | ✅ bash tool runs through sandbox          | `src/harness/tools.py`             |
| 9    | `CH09` | ✅ Durable state — JSONL session files    | `src/harness/memory.py`,          |
|      |        | ✅ session load/save, keyword search      | `src/harness/agent.py`            |

**Demo:** Skill loaded on demand from disk. Sandbox blocks `/etc/passwd`. Kill process, restart — session resumes.

---

### Phase 5 — Workflow (Chapters 10–11)

| Step | Tag    | What We Build                          | Files Touched                    |
|------|--------|----------------------------------------|----------------------------------|
| 10   | `CH10` | ✅ Planning — orchestrator, step gates    | `src/harness/orchestrator.py`,    |
|      |        | ✅ plan gen, step exec, retry              | `src/main.py`                    |
| 11   | `CH11` | ✅ Subagents — delegate + fan_out tools   | `src/harness/subagent.py`,        |
|      |        |                                       | `src/harness/tools.py`             |

**Demo:** `/plan` with multi-step calculation — steps executed in order. Fan out two parallel subtasks — answers come back, contexts isolated.

---

### Phase 6 — Quality & Visibility (Chapters 12–13)

| Step | Tag    | What We Build                          | Files Touched                    |
|------|--------|----------------------------------------|----------------------------------|
| 12   | `CH12` | ✅ Self-verification — test gate          | `src/harness/verify.py`,          |
|      |        |                                        | `src/harness/agent.py`,           |
|      |        |                                        | `AGENTS.md`                        |
| 13   | `CH13` | ✅ Observability — tracer, spans, pricing | `src/harness/tracer.py`,         |
|      |        |                                        | `src/harness/events.py`,         |
|      |        |                                        | `src/model/pricing.py`,          |
|      |        |                                        | `src/harness/agent.py`            |

**Demo:** Edit code file — harness won't accept "done" until `uv run verify` passes. Multi-step trace shows every call with token/cost breakdown.

---

### Phase 7 — Face (Chapter 14)

| Step | Tag    | What We Build                          | Files Touched                    |
|------|--------|----------------------------------------|----------------------------------|
| 14   | `CH14` | Terminal UI — two-pane TUI             | `src/ui/app.py`,                 |
|      |        |                                        | `src/ui/widgets.py`              |

**Demo:** `uv run tui` — left pane conversation, right pane live trace. Approval gate shows unified diff modal.

---

## How to Use This Plan

1. Each tag is a checkpoint. `git checkout CHXX` to see the agent at that stage.
2. `uv run agent` — live REPL at any tag.
3. `uv run demo` — scripted demo at any tag.
4. `uv run tui` — terminal UI (CH14+ only).
5. `uv run verify` — run the self-verification suite.

## Running the Project

```bash
# Prerequisites
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and run
git clone <repo-url> barenode
cd barenode
uv run agent          # REPL
uv run tui            # Terminal UI (CH14)
uv run demo           # Scripted demo
uv run verify         # Test suite
```

## Reference

- Original video: https://www.youtube.com/watch?v=oUBgqzcV1qw
- Reference repository: (linked in video description)