# CH05 Tools — Verification Log

**Date:** 2026-07-14
**Tag:** `CH05` — Tools
**Provider:** `fake/echo` (test suite)

---

## Acceptance Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| Tool registry supports function + schema registration | ✅ Pass | `Tool` dataclass, `ToolRegistry`, `default_registry()` |
| Calculator tool returns correct arithmetic results | ✅ Pass | `calculate()` supports +, -, *, /, //, %, ** |
| Read file tool reads from workspace | ✅ Pass | Workspace-scoped, path traversal blocked |
| Write file tool writes to workspace | ✅ Pass | Workspace-scoped, blocks traversal |
| Dangerous tools require approval gate | ✅ Pass | `prompt_approval()` — y/n gate, fails safe on no |
| Tool loop runs up to 6 iterations | ✅ Pass | Capped in `send()`, exits on no tool_calls |
| ModelResponse returns structured output | ✅ Pass | `content` + `tool_calls` fields |

---

## Test Results

```
$ uv run pytest tests/test_ch05.py -v
============================= 38 passed in 0.08s ==============================
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Tool schema** | JSON Schema function calling format | Standard OpenAI-compatible format, all providers support it |
| **Approval gate** | stdin y/n prompt | Simple, no dependencies, fails safe on anything but 'y' |
| **Workspace scoping** | Resolve path relative to workspace, reject `..` | Prevents accidental or malicious file access outside workspace |
| **Tool loop cap** | 6 iterations | Prevents infinite loops, matches Claude/OpenAI defaults |

---

## Real Model Verification

*(Pending — requires manual test with a real model)*