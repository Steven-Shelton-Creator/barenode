# Phase 13 — Observability

**Status:** ✅ Complete
**Date:** 2026-07-15

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

- [x] Every model call is traced with token count and cost
- [x] Every tool call is traced with input args and output result
- [x] Pricing table accurately reflects local (free) vs hosted (metered)
- [x] Console sink prints trace after each turn
- [x] OpenTelemetry events use GenAI semantic conventions

## Learnings

### Tracer Design

The tracer uses a two-phase lifecycle: spans are active while in progress, then moved to a completed list when ended. The `span()` context manager makes instrumentation easy — just wrap the operation and it automatically records timing.

### Multi-Sink Architecture

The `MultiSink` fans out to any number of sinks. Currently we use `ConsoleSink` for immediate feedback, and `JsonlSink` for persistent trace files. Future sinks (UI panel, OpenTelemetry collector) can be added without changing the instrumentation code.

### Token Estimation

We use the heuristic `estimate_tokens()` from CH06 (len(text) // 4) for token counting. This is approximate but good enough for cost estimation without making an extra API call.

### Pricing Table

The pricing table uses regex patterns matched against the full model spec. Local providers (ollama, lstudio, fake) are always free. OpenRouter models have per-token costs from published pricing. The table is ordered from most-specific to least-specific.

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch13/barenode-ch13-01.png` | *(to annotate)* |
| 2 | `docs/research/images/ch13/barenode-ch13-02.png` | *(to annotate)* |