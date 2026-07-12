# Phase 10 — Planning

**Status:** 📝 Not Started

---

## Goal

A turn is still one loop, one shot. Real tasks need planning — the model should plan steps as JSON, and the harness should drive each step through approval and execution.

## Concepts

- **Orchestrator (`orchestrator.py`):** A control plane that sits outside the agent's main loop.
- **Split:** The model plans the steps. The harness drives them.
- **Step gates:** Each step goes through approval, execute, retry on failure.
- **`/plan` command:** A new command in the REPL that hands the task to the orchestrator.

## Plan

1. Build `orchestrator.py` — plan parser, step executor, retry logic.
2. Model plans task as JSON array of steps.
3. Harness executes each step, gates through approval.
4. Wire `/plan` command in the REPL.

## Files

| File | Purpose |
|------|---------|
| `src/harness/orchestrator.py` | Planning control plane |
| `src/harness/agent.py` | Wire /plan command |
| `src/main.py` | REPL updates for /plan |

## Demo

```
$ uv run agent
> /plan Calculate 256 * 8, then add 100
Plan:
1. Calculate 256 * 8 = 2048
2. Add 100 to 2048 = 2148

Step 1: Calculate 256 * 8
[Tool: calculator(256 * 8) = 2048]
Step 2: Add 100 to 2048
[Tool: calculator(2048 + 100) = 2148]

Result: 2148
```

## Acceptance Criteria

- [ ] `/plan` command produces a structured plan
- [ ] Each step is executed in order
- [ ] Each step can be individually approved (or skipped)
- [ ] Step failure handles retry or abort
- [ ] Plan is visible before execution

## Learnings

*(To be filled during implementation.)*

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch10/barenode-ch10-01.png` | *(to annotate)* |