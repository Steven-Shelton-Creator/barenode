# CH14 Terminal UI — Verification Log

**Date:** 2026-07-15
**Tag:** `CH14` — Terminal UI
**Provider:** `fake/echo` (test suite)

---

## Acceptance Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| `uv run tui` launches the two-pane TUI | ✅ Pass | `BarenodeApp` — Textual App with Header, Footer, Input, two panes |
| Left pane shows conversation history | ✅ Pass | `ConversationPane` — RichLog with color-coded roles (user, assistant, system, tool) |
| Right pane shows live trace stream | ✅ Pass | `TraceStreamPane` — displays spans from last turn with token/cost totals |
| Approval gate appears as a modal with unified diff | ✅ Pass | `ApprovalModal` — ModalScreen with Y/Approve, N/Deny, unified diff display |
| UI runs agent in worker thread — no blocking | ✅ Pass | `@work(exclusive=True, thread=True)` — UI stays responsive |
| Only the UI package imports textual | ✅ Pass | `textual` only imported in `src/ui/` — harness and model are framework-agnostic |

---

## Test Results

```
$ uv run pytest tests/test_ch14.py -v
============================= 17 passed in 0.08s ==============================
```

## Full Regression Suite

```
$ uv run pytest tests/ -v
============================= 271 passed in 2.74s ==============================
```

---

## Test Breakdown

| Test | Type | Result |
|------|------|--------|
| `test_truncate_short` | Unit | ✅ |
| `test_truncate_long` | Unit | ✅ |
| `test_truncate_exact` | Unit | ✅ |
| `test_format_timestamp` | Unit | ✅ |
| `test_agent_runner_creates_agent` | Unit | ✅ |
| `test_agent_runner_send` | Unit | ✅ |
| `test_agent_runner_get_conversation` | Unit | ✅ |
| `test_agent_runner_get_trace_spans` | Unit | ✅ |
| `test_conversation_pane_can_be_constructed` | Integration | ✅ |
| `test_trace_stream_pane_can_be_constructed` | Integration | ✅ |
| `test_approval_modal_can_be_constructed` | Integration | ✅ |
| `test_approval_modal_with_diff` | Integration | ✅ |
| `test_barenode_app_layout_can_be_constructed` | Integration | ✅ |
| `test_barenode_app_instantiation` | Integration | ✅ |
| `test_ch01_regression` | Regression | ✅ |
| `test_ch05_tools_unchanged` | Regression | ✅ |
| `test_ch13_tracer_unchanged` | Regression | ✅ |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **UI framework** | Textual 8.x | Clean async framework, `@work` decorator for threading, `ModalScreen` for dialogs |
| **Worker architecture** | `@work(exclusive=True, thread=True)` | Non-blocking, `call_from_thread()` for safe UI updates from worker |
| **Approval UX** | Unified diff in modal | Shows exactly what changed, Y/Approve or N/Deny |
| **Framework isolation** | Only `src/ui/` imports textual | Proves three-package architecture — harness and model stay framework-agnostic |

---

## Real Model Verification

*(Pending — requires manual test with a real model)*