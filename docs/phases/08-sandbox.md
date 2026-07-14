# Phase 8 — Sandbox

**Status:** ✅ Complete (2026-07-14)

---

## Goal

All code execution has been running on the host machine. The model will happily ask to run anything. The boundary must live in the harness — not the prompt.

## Concepts

- **Start closed:** Network none, filesystem copied, credentials absent. Climb the ladder only as needed.
- **Docker sandbox:** Isolated container with no network, non-root user, dropped capabilities, read-only filesystem, hard memory/process cap.
- **Fallback:** If Docker isn't available, run in a scrubbed local subprocess.
- **Workspace fencing:** Read-file is confined to the workspace — the model cannot reach `/etc/passwd`.

## Plan (completed)

1. ✅ Built `sandbox.py` — `Sandbox` class with `check()` and `run()`
2. ✅ Docker mode: `--network none`, `--read-only`, `--user 1000:1000`, `--memory 256m`, `--pids-limit 50`
3. ✅ Local fallback: scrubbed subprocess with restricted env
4. ✅ Added `bash` tool to tools.py — runs through sandbox, requires approval
5. ✅ Workspace fencing via Docker volume mount

## Files

| File | Purpose |
|------|---------|
| `src/harness/sandbox.py` | Docker sandbox + local subprocess fallback |
| `src/harness/tools.py` | bash tool wired through sandbox |
| `tests/test_ch08.py` | 15 tests — sandbox, Docker isolation, workspace fencing |

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

- [x] Bash runs inside Docker sandbox when Docker is available
- [x] Docker sandbox: no network, non-root, read-only rootfs
- [x] Falls back to scrubbed local subprocess without Docker
- [x] Read-file cannot access paths outside workspace (CH05)
- [x] Memory and process limits enforced

## Learnings

### Key Design Decisions
- **Docker first, local fallback.** `Sandbox.check()` probes Docker availability once and caches the result.
- **`--read-only` rootfs** with writable `/tmp` (tmpfs) and `/workspace` (volume mount).
- **Bash tool requires approval.** Same pattern as write_file — the approval gate prompts before execution.
- **Workspace is mounted at `/workspace`** inside the container. All file operations use this mount point.

### Real Model Demo
```
> bash tool execution through Docker sandbox
> hello from sandbox
> [sandbox: docker, 0.20s]
```

### Caveats
- The local fallback doesn't provide real isolation — it's a best-effort scrub for systems without Docker.
- Network isolation with `--network none` means commands like `curl` or `pip install` will fail. This is intentional.

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch08/barenode-ch08-01.png` | *(to annotate)* |
| 2 | `docs/research/images/ch08/barenode-ch08-02.png` | *(to annotate)* |
| 3 | `docs/research/images/ch08/barenode-ch08-03.png` | *(to annotate)* |
| 4 | `docs/research/images/ch08/barenode-ch08-04.png` | *(to annotate)* |

---

## Sandbox Scope Clarification

The sandbox is **not** the entire agent harness. It is specifically the execution
environment for the **bash tool** only. Here's the full split:

| Layer | Where it runs | Isolation |
|-------|---------------|-----------|
| Agent loop, tool registry, system prompt | Host (Python) | None needed — it's our code |
| ``read_file`` / ``write_file`` | Host (Python ``open()``) | Path-fenced to workspace via ``os.path.abspath()`` (CH05) |
| **bash tool** | **Docker sandbox** | ``--network none``, ``--read-only``, non-root user, memory/process caps |

### Why this split?

- **Calculator** (CH05) evaluates math expressions safely — no builtins, only ``math``
  module. No shell execution needed.
- **File tools** (CH05) are already safe because they validate paths against the
  workspace boundary. No shell needed.
- **Bash** (CH08) is the *only* tool that executes arbitrary shell commands. It's
  the one that could do real damage (``rm -rf``, exfiltrate data, read system
  files), so it's the only one that needs Docker isolation.