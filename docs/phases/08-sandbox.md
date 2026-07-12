# Phase 8 — Sandbox

**Status:** 📝 Not Started

---

## Goal

All code execution has been running on the host machine. The model will happily ask to run anything. The boundary must live in the harness — not the prompt.

## Concepts

- **Start closed:** Network none, filesystem copied, credentials absent. Climb the ladder only as needed.
- **Docker sandbox:** Isolated container with no network, non-root user, dropped capabilities, read-only filesystem, hard memory/process cap.
- **Fallback:** If Docker isn't available, run in a scrubbed local subprocess.
- **Workspace fencing:** Read-file is confined to the workspace — the model cannot reach `/etc/passwd`.

## Plan

1. Build `sandbox.py` with Docker sandbox execution.
2. Non-root user, read-only rootfs, no network, memory/process caps.
3. Fallback to scrubbed subprocess if Docker is absent.
4. Fence the read-file tool to the workspace directory.
5. Wire sandbox into the bash tool.

## Files

| File | Purpose |
|------|---------|
| `src/harness/sandbox.py` | Docker sandbox + local fallback |
| `src/harness/tools.py` | Wire sandbox into bash tool |

## Demo

```
$ uv run agent
> Run: cat /etc/passwd
[Run in sandbox — blocked]
Path outside workspace: /etc/passwd

> Run: echo "hello" > /workspace/test.txt
[Approval required] Run bash? (y/n): y
File written.
```

## Acceptance Criteria

- [ ] Bash runs inside Docker sandbox when Docker is available
- [ ] Docker sandbox: no network, non-root, read-only rootfs
- [ ] Falls back to scrubbed local subprocess without Docker
- [ ] Read-file cannot access paths outside workspace
- [ ] Memory and process limits enforced

## Learnings

*(To be filled during implementation.)*