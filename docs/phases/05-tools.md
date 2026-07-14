# Phase 5 — Tools

**Status:** ✅ Complete (2026-07-14)

---

## Goal

Give the agent the ability to act — not just talk. Tools are functions the model can invoke, with approval gates for dangerous operations.

## Concepts

- **Tool = function + schema.** That's it. The model sees the schema (name, description, parameters), decides to call it, and the harness executes it.
- **Tool registry:** `tools.py` holds all tool specs and dispatches calls by name.
- **Split responsibility:** The model decides *what* to call. The harness decides *how* and actually runs it.
- **Approval gates:** Some tools (bash, file writes) require human approval before execution. No approval → fails safe.
- **Tool loop:** Send with tool specs → model reaches for a tool → run it → hand back results → repeat. Capped at 6 iterations.

## Plan (completed)

1. ✅ Built `tools.py` with `Tool` dataclass + `ToolRegistry`
2. ✅ Built `ToolRegistry` with register, get, specs, execute, requires_approval, needs_workspace
3. ✅ Implemented calculator tool (safe eval, no builtins, math module access)
4. ✅ Implemented read_file and write_file tools (workspace confinement, path security)
5. ✅ Built approval gate (`approval.py`) — y/n prompt on stderr
6. ✅ Wired tool loop into `agent.send()` — capped at 6 iterations

## Files

| File | Purpose |
|------|---------|
| `src/harness/tools.py` | Tool dataclass, tool registry, calculator tool |
| `src/harness/approval.py` | Approval gate (prompt + accept/reject) |
| `src/harness/agent.py` | Wire tool loop into send() |

## Demo

```
$ uv run agent
> Calculate 256 * 8
[Using calculator tool: 256 * 8 = 2048]
2048

> Write a file called hello.txt with "Hello, world!"
[APPROVAL REQUIRED] Write to hello.txt? (y/n): y
File written.

> Write a file called /etc/pwned.txt with "oops"
[APPROVAL REQUIRED] Write to /etc/pwned.txt? (y/n): n
Blocked: path outside workspace.
```

## Acceptance Criteria

- [x] Calculator tool returns correct results without approval
- [x] Write file tool prompts for approval
- [x] Paths outside workspace are rejected
- [x] Tool loop caps at 6 iterations
- [x] Model can chain multiple tool calls

## Learnings

### Key Design Decisions
- **Tool = function + schema.** The `Tool` dataclass holds the function, its JSON schema, and metadata (approval, workspace needs).
- **ModelResponse dataclass.** The provider now returns structured responses (content + tool_calls) instead of plain strings. This is a non-breaking change — existing tests pass.
- **`needs_workspace` flag.** File tools (read_file, write_file) need the workspace path injected by the harness. Calculator does not. Rather than passing workspace to all tools, we mark which tools need it.
- **Fake provider tool call simulation.** The fake provider supports a one-shot `_FAKE_NEXT_TOOL_CALLS` mechanism for tests. Each test queues the tool calls it wants the model to make, and the fake provider returns them on the next call.

### Pain Points
- **Workspace injection in all tools.** Initially injected workspace into every tool call, but calculator doesn't accept it. Fixed by adding `needs_workspace` flag.
- **Test design for tool loop.** The fake provider's one-shot nature means we can't easily test the max iteration cap (which requires the model to *keep* calling tools). A future improvement could add a persistent fake mode.

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch05/barenode-ch05-01.png` | *(to annotate)* |
| 2 | `docs/research/images/ch05/barenode-ch05-02.png` | *(to annotate)* |