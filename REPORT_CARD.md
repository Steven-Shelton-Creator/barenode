# Barenode — Project Report Card

**Date:** 2026-07-15
**Architect:** Ghoststack Systems Analysis
**Build:** 14 chapters, 271 tests, 14 git tags

---

## Overall Rating: 6.5 / 10

**Strong for an educational prototype. Weak for production.**

---

## What Actually Worked Well (+)

| Area | Grade | Why |
|------|-------|-----|
| **Architecture** | B+ | Three-package layering (Model → Harness → UI) is clean. Arrows point one way. No circular deps. |
| **Test coverage** | A- | 271 tests, regression tests per chapter, fake provider for deterministic testing. Solid. |
| **Git discipline** | B+ | Chapter tags, changelog, ADRs, verification logs. The tracking system is over-engineered but effective. |
| **Tracer/Sink design** | B | MultiSink pattern is extensible. ConsoleSink + JsonlSink + StoreSink is a good start. |
| **Security defaults** | B | Sandbox starts closed (no network, read-only, memory-limited). Approval gates on dangerous tools. |

---

## What's Actually Weak (-)

| Area | Grade | Why |
|------|-------|-----|
| **Token estimation** | B- | The local heuristic (`len(text) // 4`) is rough, but the real model (Gemma 4 via Ollama) handles actual tokenization natively. API calls use real token counts. Budget pre-checks are conservative — they may fire early, never late. |
| **Compaction** | D | Head/tail truncation with a summary message is the laziest compaction strategy. No semantic compression, no summarization, no embedding-based retrieval. A real agent would lose context on turn 20. |
| **Memory** | D | JSONL keyword search is not memory. It's a flat file with grep. No vector embeddings, no semantic recall, no decay. Your agent can't remember anything it didn't literally type. |
| **Planning** | C- | The orchestrator generates a JSON plan, but the model has to re-plan every time. No plan persistence, no plan repair, no dependency graph. One retry and no backoff. |
| **Subagents** | C | `ThreadPoolExecutor` is not an agent framework. No timeout, no result streaming, no error propagation beyond a string. A subagent crash is just a string saying "error." |
| **Verification gate** | C | Parsing `[exit code: N]` from bash output is fragile. No test timeout, no parallel test execution, no coverage analysis. |
| **TUI** | C- | The TUI is functional but bare. No scrollback in the trace pane, no message search, no model selection, no session picker, no theme support. The approval modal shows a diff but doesn't let you edit it. |
| **Provider abstraction** | C | The fake provider is useful for tests, but the real providers (ollama, openrouter, lstudio) share no retry logic, no rate limiting, no fallback, no streaming. |
| **Error handling** | D | Bare `except Exception` in the worker thread. If the agent crashes, the TUI just shows "[error] ..." and unlocks the input. No recovery, no retry, no stack trace visible to the user. |
| **Docker sandbox** | C | Works if Docker is installed. The local fallback is completely unsecured — no seccomp, no landlock, no cgroups. A malicious prompt in local mode has full access. |

---

## The Hard Truths

1. **This is not an agent. It's a REPL with a tool belt.** Real agents plan, reflect, correct course, and learn. This one fires a prompt, gets a response, loops tools, and calls it a day. There's no metacognition, no self-correction loop, no learning between sessions.

2. **The "memory" is a lie.** JSONL grep is not a memory system. You can't ask "what did we discuss about project X last week" and get a meaningful answer. The session files are append-only logs, not a knowledge base.

3. **The token budget heuristic is conservative, not imaginary.** The local `len(text) // 4` pre-check may fire early but will never miss an over-budget condition. The actual model call uses Gemma 4's real tokenizer via Ollama. The budget is a safety net, not a precision instrument — and it works.

4. **The TUI is a thin skin.** It wraps the agent but doesn't enhance it. No multi-turn editing, no conversation branching, no inspection of the agent's internal state. The trace pane shows raw Span objects — useful for debugging, not for understanding.

5. **No observability integration.** The tracer writes to stdout and JSONL. No OpenTelemetry exporter, no metrics, no alerting. If this ran in production and broke, you'd have zero signal.

---

## What I'd Actually Ship

| Feature | Priority | Why |
|---------|----------|-----|
| Real tokenization (tiktoken or tokenizers) | **P0** | Everything depends on this — budget, cost estimation, compaction |
| Semantic memory (embeddings + vector store) | **P0** | Without it, the agent is amnesiac |
| Provider retry + fallback | **P0** | One provider failure kills the entire agent |
| Proper error recovery | **P0** | The agent should survive a model crash |
| OpenTelemetry export | **P1** | You can't debug what you can't see |
| Plan repair + dependency graph | **P1** | The orchestrator is a to-do list, not a planner |
| Subagent timeout + streaming | **P1** | Fan-out without timeout is a resource leak |
| TUI: scrollback, search, session picker | **P2** | Usability, not survival |
| Docker sandbox for local fallback | **P2** | Local mode is currently wide open |

---

## Verdict

**6.5/10** — A solid educational prototype that proves the architecture works. But it's a prototype, not a product. The foundation is clean (three-package layering, test discipline, tracer design), but every primitive is the minimum viable version of itself.

The good news: the architecture is clean enough to upgrade each primitive independently. You could swap JSONL memory for a vector store without touching the agent loop. That's worth something.

The bad news: if you shipped this today, a real user would hit a wall by turn 30.