# barenode — Roadmap

> Long-term vision beyond the initial build. Not a commitment — a compass.

---

## Phase 0 — Foundation *(current)*

- [x] Repository scaffold
- [x] Build blueprint methodology
- [x] Architecture decision records
- [x] Three-package core layout
- [ ] GitHub project board configured
- [ ] CI pipeline (lint + test on push)

---

## Tier 1 — Core Agent

- [x] **CH01** — Model: bare stateless chat call
- [x] **CH02** — History: message list, append, replay
- [x] **CH03** — Instructions: system prompt, agents.md loader
- [x] **CH04** — Context Delivery: @file injection

*End state: REPL-based agent that remembers the conversation and follows instructions.*

---

## Tier 2 — Action Layer

- [x] **CH05** — Tools: function registry, calculator, approval gates
- [x] **CH06** — Context Management: compression, clamping
- [x] **CH07** — Skills: progressive disclosure, skill.md loader
- [x] **CH08** — Sandbox: Docker isolation, workspace fencing

*End state: Agent can act (run tools, read/write files) inside a sandbox.*

---

## Tier 3 — Intelligence

- [x] **CH09** — Durable State: JSONL session persistence, keyword search
- [x] **CH10** — Planning: orchestrator, step gates, /plan command
- [ ] **CH11** — Subagents: delegate, fan-out, context isolation

*End state: Agent survives restart, plans multi-step tasks, delegates subtasks.*

---

## Tier 4 — Reliability

- [ ] **CH12** — Self-Verification: test gate, agents.md [testing] section
- [ ] **CH13** — Observability: OpenTelemetry traces, cost tracking, multi-sink

*End state: Agent verifies its own work; every call is traceable.*

---

## Tier 5 — Interface

- [ ] **CH14** — Terminal UI: two-pane TUI, live trace stream, approval modals

*End state: Full agent = model + harness + UI, demonstrable with `uv run tui`.*

---

## Post-Build (Future)

- [ ] Web UI (Streamlit / FastAPI frontend)
- [ ] Multi-provider routing (fallback between OpenRouter, Ollama, LM Studio)
- [ ] Embedding-based memory retrieval (replace keyword search)
- [ ] Plugin system for custom tools
- [ ] Docker Compose for one-command agent startup