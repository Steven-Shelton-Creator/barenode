# CH13 Observability — Verification Log

**Date:** 2026-07-15
**Tag:** N/A (not yet tagged)
**Provider:** `fake/echo` (test suite)

---

## Acceptance Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| Every model call is traced with token count and cost | ✅ Pass | `tracer.span()` wraps `chat()`, attributes include `total_tokens` and `cost` |
| Every tool call is traced with input args and output result | ✅ Pass | `tracer.span()` wraps tool execution, attributes include `tool`, `arguments`, `result` |
| Pricing table accurately reflects local (free) vs hosted (metered) | ✅ Pass | `PRICING_TABLE` has 20+ entries, local providers are $0, OpenRouter matches published pricing |
| Console sink prints trace after each turn | ✅ Pass | `ConsoleSink.write()` formats and prints spans after each `send()` |
| OpenTelemetry events use GenAI semantic conventions | ✅ Pass | `GenAISpanKind` enum uses `genai.operation`, `genai.tool_call`, etc. |

---

## Test Results (Fake Provider)

```
$ uv run pytest tests/test_ch13.py -v
============================= 30 passed in 0.07s ==============================
```

## Full Regression Suite

```
$ uv run pytest tests/ -v
============================= 254 passed in 2.95s ==============================
```

---

## Test Breakdown

| Test | Type | Result |
|------|------|--------|
| `test_lookup_pricing_local` | Unit | ✅ |
| `test_lookup_pricing_lstudio` | Unit | ✅ |
| `test_lookup_pricing_fake` | Unit | ✅ |
| `test_lookup_pricing_openrouter` | Unit | ✅ |
| `test_lookup_pricing_unknown_default` | Unit | ✅ |
| `test_estimate_cost_zero_local` | Unit | ✅ |
| `test_estimate_cost_hosted` | Unit | ✅ |
| `test_is_local_model_true` | Unit | ✅ |
| `test_is_local_model_false` | Unit | ✅ |
| `test_genai_span_kind_values` | Unit | ✅ |
| `test_make_event` | Unit | ✅ |
| `test_llm_call_event` | Unit | ✅ |
| `test_tool_call_event` | Unit | ✅ |
| `test_completion_event` | Unit | ✅ |
| `test_tracer_start_end_span` | Unit | ✅ |
| `test_tracer_span_context_manager` | Unit | ✅ |
| `test_tracer_add_event` | Unit | ✅ |
| `test_tracer_clear` | Unit | ✅ |
| `test_tracer_total_cost` | Unit | ✅ |
| `test_tracer_total_tokens` | Unit | ✅ |
| `test_console_sink_write_no_output` | Unit | ✅ |
| `test_console_sink_write_llm_span` | Unit | ✅ |
| `test_jsonl_sink_write` | Unit | ✅ |
| `test_multi_sink` | Unit | ✅ |
| `test_agent_has_tracer` | Integration | ✅ |
| `test_agent_traces_model_call` | Integration | ✅ |
| `test_agent_traces_tool_calls` | Integration | ✅ |
| `test_ch01_regression` | Regression | ✅ |
| `test_ch05_tools_unchanged` | Regression | ✅ |
| `test_ch12_verification_unchanged` | Regression | ✅ |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Token estimation** | `len(text) // 4` heuristic | No extra API call needed, good enough for cost estimation |
| **Span lifecycle** | Active → completed | Clean separation, `span()` context manager for easy instrumentation |
| **Sink architecture** | `MultiSink` fans out to registered sinks | New sinks (UI, OpenTelemetry) can be added without changing instrumentation |
| **Pricing lookup** | Regex pattern matching | Flexible, handles model version variations, ordered most-specific first |

---

## Real Model Verification

*(Pending — requires manual test with a real model)*