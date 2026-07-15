# CH08 Sandbox — Verification Log

**Date:** 2026-07-14
**Tag:** `CH08` — Sandbox
**Provider:** `fake/echo` (test suite)

---

## Acceptance Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| Sandbox runs commands via Docker | ✅ Pass | `--network none`, `--read-only`, `--user 1000:1000`, `--memory 256m`, `--pids-limit 50` |
| Docker unavailable falls back to local subprocess | ✅ Pass | Clean subprocess with no Docker dependency |
| Sandbox blocks network access | ✅ Pass | `--network none` in Docker mode |
| Sandbox restricts filesystem to read-only | ✅ Pass | `--read-only` in Docker mode |
| Bash tool routes through sandbox | ✅ Pass | Tool calls `sandbox.run()`, output captured with `[exit code: N]` marker |
| Workspace fencing prevents path traversal | ✅ Pass | Commands scoped to workspace directory |

---

## Test Results

```
$ uv run pytest tests/test_ch08.py -v
============================= 15 passed in 0.58s ==============================
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Docker first, subprocess fallback** | Try Docker, catch `FileNotFoundError` | Works everywhere, no forced dependency |
| **Sandbox defaults** | No network, read-only, limited memory | Security-first: start closed, open only as needed |
| **Exit code marker** | `[exit code: N]` in stdout | Parsable by agent and harness, no stderr confusion |
| **User mapping** | `--user 1000:1000` | Matches host user, prevents permission issues |

---

## Real Model Verification

*(Pending — requires manual test with a real model)*