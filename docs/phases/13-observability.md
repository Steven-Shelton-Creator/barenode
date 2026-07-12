# Phase 13 — Observability

**Status:** 📝 Not Started

---

## Goal

When a multi-step run breaks, the failure is rarely where the trouble started. We need to see inside every call — model calls, tool calls, token counts, cost.

## Concepts

- **Tracer:** Records every step as it happens — model calls, tool calls (exact args + results), verify steps, plan steps.
- **Multi-sink:** One emit can go to many sinks: UI panel, JSONL file, console printer, or OpenTelemetry collector.
- **Pricing table:** Local models are free, hosted models are metered. Cost comes from the model package.
- **OpenTelemetry GenAI semantics:** Standardized event names (`genai.operation`, `genai.usage`, etc.).

## Plan

1. Build `tracer.py` — span creation, start/end lifecycle.
2. Build `events.py` — OpenTelemetry GenAI semantic events.
3. Build `pricing.py` in the model package — cost from usage.
4. Instrument the agent loop: every model call and tool call gets a span.
5. Sinks: console printer for now (UI sink comes in Phase 14).

## Files

| File | Purpose |
|------|---------|
| `src/harness/tracer.py` | Tracer, span lifecycle |
| `src/harness/events.py` | OpenTelemetry GenAI event semantics |
| `src/model/pricing.py` | Cost table per model |
| `src/harness/agent.py` | Wire instrumentation into send() |

## Demo

```
$ uv run agent
> Calculate 256 * 8

[Trace]
LLM call        : tokens=142, cost=$0.00 (local model)
Tool call       : calculator(256 * 8) → 2048
LLM call        : tokens=85, cost=$0.00 (local model)
---
Total cost      : $0.00
Total tokens    : 227
```

## Acceptance Criteria

- [ ] Every model call is traced with token count and cost
- [ ] Every tool call is traced with input args and output result
- [ ] Pricing table accurately reflects local (free) vs hosted (metered)
- [ ] Console sink prints trace after each turn
- [ ] OpenTelemetry events use GenAI semantic conventions

## Learnings

*(To be filled during implementation.)*

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch13/barenode-ch13-01.png` | *(to annotate)* |
| 2 | `docs/research/images/ch13/barenode-ch13-02.png` | *(to annotate)* |