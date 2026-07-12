# Phase 5 — Tools

**Status:** 📝 Not Started

---

## Goal

Give the agent the ability to act — not just talk. Tools are functions the model can invoke, with approval gates for dangerous operations.

## Concepts

- **Tool = function + schema.** That's it. The model sees the schema (name, description, parameters), decides to call it, and the harness executes it.
- **Tool registry:** `tools.py` holds all tool specs and dispatches calls by name.
- **Split responsibility:** The model decides *what* to call. The harness decides *how* and actually runs it.
- **Approval gates:** Some tools (bash, file writes) require human approval before execution. No approval → fails safe.
- **Tool loop:** Send with tool specs → model reaches for a tool → run it → hand back results → repeat. Capped at 6 iterations.

## Plan

1. Build `tools.py` with a `Tool` dataclass (name, description, parameters, function, requires_approval).
2. Build a `ToolRegistry` that stores tools and provides specs to the model.
3. Implement a calculator tool (safe, no approval needed).
4. Implement read/write file tools (requires approval).
5. Build the approval gate (`approval.py`).
6. Wire the tool loop into the agent's `send()` method.

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

- [ ] Calculator tool returns correct results without approval
- [ ] Write file tool prompts for approval
- [ ] Paths outside workspace are rejected
- [ ] Tool loop caps at 6 iterations
- [ ] Model can chain multiple tool calls

## Learnings

*(To be filled during implementation.)*

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch05/barenode-ch05-01.png` | *(to annotate)* |
| 2 | `docs/research/images/ch05/barenode-ch05-02.png` | *(to annotate)* |