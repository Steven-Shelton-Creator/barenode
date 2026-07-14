# Phase 10 — Planning

**Status:** ✅ Complete (2026-07-14)

---

## Goal

A turn is still one loop, one shot. Real tasks need planning — the model should plan steps as JSON, and the harness should drive each step through approval and execution.

## Concepts

- **Orchestrator (`orchestrator.py`):** A control plane that sits outside the agent's main loop.
- **Split:** The model plans the steps. The harness drives them.
- **Step gates:** Each step goes through approval, execute, retry on failure.
- **`/plan` command:** A new command in the REPL that hands the task to the orchestrator.

## Plan (completed)

1. ✅ Built `orchestrator.py` — `Step`, `Plan`, `generate_plan()`, `format_plan()`, `execute_plan()`, `_extract_json()`
2. ✅ Model plans steps as JSON array, harness executes them
3. ✅ Step approval gate via `approve_step` callback
4. ✅ Retry logic on step failure
5. ✅ `/plan` command wired into REPL

## Files

| File | Purpose |
|------|---------|
| `src/harness/orchestrator.py` | Planning control plane — Step, Plan, generate, format, execute |
| `src/main.py` | `/plan` command in REPL |
| `tests/test_ch10.py` | 19 tests — Step, Plan, JSON extraction, execution, approval, regression |

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

- [x] `/plan` command produces a structured plan
- [x] Each step is executed in order
- [x] Each step can be individually approved (or skipped)
- [x] Step failure handles retry or abort
- [x] Plan is visible before execution

## Learnings

### Key Design Decisions
- **Model plans as JSON.** The model receives a planning system prompt and returns a JSON array of steps. The harness parses and executes them.
- **`_extract_json()` handles markdown fences.** Some models wrap JSON in ```json...``` blocks. The extractor handles both fenced and plain JSON.
- **Step approval via callback.** The `approve_step` function is passed to `execute_plan()`, allowing the REPL to prompt before each step.
- **Retry logic.** Each step can be retried on failure (default: 1 retry).

### Real Model Demo
```
> /plan Calculate 15 * 3, then add 25
Plan:
  Step 1: Calculate the product of 15 and 3  (expected: 45)
  Step 2: Add 25 to the result (45)  (expected: 70)

Step 1: The product of 15 and 3 is 45.
Step 2: Adding 25 to 45 gives 70.
```

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch10/barenode-ch10-01.png` | *(to annotate)* |