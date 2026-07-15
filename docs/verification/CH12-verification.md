# CH12 Self-Verification — Verification Log

**Date:** 2026-07-14
**Tag:** N/A (not yet tagged)
**Provider:** `fake/echo` (test suite)

---

## Acceptance Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| Verification fires only when a code file was written | ✅ Pass | `was_code_file_written()` checks `write_file` with `CODE_EXTENSIONS` |
| Test command comes from AGENTS.md `[testing]` section | ✅ Pass | `parse_test_command()` parses `## Testing` section with regex |
| Agent runs the test, harness checks for exit 0 | ✅ Pass | Agent calls `bash`, harness checks `[exit code:` marker |
| Harness rejects "done" without a passing test | ✅ Pass | `_pending_verification` persists until `check_test_result()` returns True |
| Non-code tasks skip verification | ✅ Pass | `.txt` and non-write_file tool calls don't arm the gate |

---

## Test Results (Fake Provider)

```
$ uv run pytest tests/test_ch12.py -v
============================= 28 passed in 0.06s ==============================
```

## Full Regression Suite

```
$ uv run pytest tests/ -v
============================= 224 passed in 2.52s ==============================
```

---

## Test Breakdown

| Test | Type | Result |
|------|------|--------|
| `test_code_extensions_contains_py` | Unit | ✅ |
| `test_code_extensions_contains_md` | Unit | ✅ |
| `test_code_extensions_contains_js` | Unit | ✅ |
| `test_code_extensions_does_not_contain_txt` | Unit | ✅ |
| `test_parse_test_command_found` | Unit | ✅ |
| `test_parse_test_command_no_section` | Unit | ✅ |
| `test_parse_test_command_no_file` | Unit | ✅ |
| `test_parse_test_command_empty_command` | Unit | ✅ |
| `test_get_tool_call_path_from_string_args` | Unit | ✅ |
| `test_get_tool_call_path_from_dict_args` | Unit | ✅ |
| `test_get_tool_call_path_no_path` | Unit | ✅ |
| `test_get_tool_call_path_invalid_json` | Unit | ✅ |
| `test_was_code_file_written_py_file` | Unit | ✅ |
| `test_was_code_file_written_txt_file` | Unit | ✅ |
| `test_was_code_file_written_not_write_file` | Unit | ✅ |
| `test_was_code_file_written_mixed` | Unit | ✅ |
| `test_was_code_file_written_empty_list` | Unit | ✅ |
| `test_check_test_result_pass` | Unit | ✅ |
| `test_check_test_result_fail` | Unit | ✅ |
| `test_check_test_result_no_sandbox_marker` | Unit | ✅ |
| `test_build_verification_prompt_contains_command` | Unit | ✅ |
| `test_build_verification_prompt_contains_verification_label` | Unit | ✅ |
| `test_agent_starts_without_verification` | Integration | ✅ |
| `test_agent_arms_verification_on_code_write` | Integration | ✅ |
| `test_agent_skips_verification_for_non_code` | Integration | ✅ |
| `test_ch01_regression` | Regression | ✅ |
| `test_ch05_tools_unchanged` | Regression | ✅ |
| `test_ch11_subagents_unchanged` | Regression | ✅ |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Detection method** | Check tool call arguments for `write_file` with code extension | Simple, avoids false positives, no file I/O needed |
| **Test result parsing** | Parse `[exit code: N]` from bash tool output | Leverages existing sandbox result format, no new infrastructure |
| **Verification state machine** | Three states: Idle → Armed → Waiting | Clear separation of concerns, prevents re-injection loops |
| **Prompt injection** | Append user message to `self.messages` | Agent sees it as a natural instruction, responds with bash tool call |

---

## Real Model Verification

*(Pending — requires manual test with a real model)*