# CH11 Subagent Architecture: Implementation vs. Blueprint Comparison

**Date:** 2026-07-14
**Source:** Architecture review session — `tests_compare_ch11.py` design analysis

---

## The Blueprint (External Reference)

```python
def run_subagent(
    task: str,
    *,
    system: str | None = None,
    model: str | None = None,
    tools: ToolRegistry | None = None,
) -> str:
    
    from harness.agent import Agent  # lazy: avoids an import cycle at module load
    
    sub = Agent(system=system or DEFAULT_WORKER_SYSTEM,
                tools=tools or default_tools(), model=model)
    
    return sub.send(task)


def fan_out(tasks: list[str], *, model: str | None = None,
            max_workers: int = 4) -> list[str]:
    # ...
    
    with ThreadPoolExecutor(...) as pool:
        return list(pool.map(lambda t: run_subagent(t, model=model), tasks))
```

### Blueprint Architectural Claims

- **Two tools, isolated context:** `delegate` for one subtask, `fan_out` for a parallel batch. Each runs a fresh agent.
- **Answers, not transcripts:** Each subagent returns just its result; the main window never sees the sub-conversation.
- **Challenge:** State propagation and partial failures — if 1 of 4 tasks fails, does the master halt?

---

## Our Implementation (CH11 — `src/harness/subagent.py`)

```python
def run_subagent(
    message: str,
    model: str | None = None,
    workspace: str | None = None,
) -> str:
    agent = Agent(
        model=model,
        workspace=workspace,
        session_name=_next_session_name(),
    )
    return agent.send(message)


def delegate(task: str) -> str:
    try:
        result = run_subagent(task)
        return f"[Subagent result]\n{result}"
    except Exception as exc:
        return f"[Subagent error] {exc}"


def fan_out(tasks: list[str]) -> str:
    if not tasks:
        return "No tasks provided."

    model = os.environ.get("BARENODE_MODEL")
    workspace = os.getcwd()
    results: dict[int, str] = {}

    def _run_one(index: int, task: str) -> tuple[int, str]:
        try:
            agent = Agent(
                model=model,
                workspace=workspace,
                session_name=_next_session_name(),
            )
            reply = agent.send(task)
            return index, f"  Subagent {index + 1}: {reply}"
        except Exception as exc:
            return index, f"  Subagent {index + 1}: [error] {exc}"

    with ThreadPoolExecutor(max_workers=min(len(tasks), 10)) as pool:
        futures = [pool.submit(_run_one, i, t) for i, t in enumerate(tasks)]
        for future in as_completed(futures):
            idx, line = future.result()
            results[idx] = line

    lines = ["[Fan-out results]"]
    for i in range(len(tasks)):
        lines.append(results.get(i, f"  Subagent {i + 1}: [error] no result"))
    return "\n".join(lines)
```

---

## Direct Comparison

### Similarities

| Aspect | Our Implementation | Blueprint | Match |
|--------|-------------------|-----------|-------|
| Lazy import to avoid circular dependency | `from harness.subagent import delegate as _delegate` inside wrapper functions in `tools.py` | `from harness.agent import Agent` inside `run_subagent` | ✅ Same pattern |
| Two tools: delegate + fan_out | `delegate` + `fan_out` registered in default registry | `delegate` + `fan_out` | ✅ Same design |
| Fresh Agent per subtask | `Agent(model=..., workspace=..., session_name=...)` | `Agent(system=..., tools=..., model=...)` | ✅ Same concept |
| Answers, not transcripts | Returns `result` string, agent discarded | Returns `sub.send(task)` result | ✅ Same |
| Parallel execution engine | `concurrent.futures.ThreadPoolExecutor` | `concurrent.futures.ThreadPoolExecutor` | ✅ Same engine |
| Error isolation | Per-subtask `try/except`, one failure doesn't crash | *Asked as a challenge question* | ✅ We have this |

### Differences

| Aspect | Our Implementation | Blueprint | Analysis |
|--------|-------------------|-----------|----------|
| **`run_subagent` signature** | `run_subagent(message, model=None, workspace=None)` | `run_subagent(task, *, system=None, model=None, tools=None)` | Blueprint is more configurable — explicit `system` + `tools` params allow custom subagent personality per subtask |
| **Agent construction** | Full `Agent()` with all defaults (instructions, skills, registry) | `Agent(system=..., tools=..., model=...)` — explicit injection | Blueprint supports per-subtask tool sets and system prompts; ours uses global defaults |
| **`fan_out` return type** | `str` — formatted block with `[Fan-out results]` header | `list[str]` — raw ordered results | Blueprint returns structured data suitable for programmatic consumption; ours is display-oriented |
| **`fan_out` parallelism** | `pool.submit()` + `as_completed()` + manual dict reassembly | `pool.map()` — simpler, preserves order natively | Blueprint is cleaner; ours is equivalent but more verbose |
| **`max_workers` default** | `min(len(tasks), 10)` | `4` | Blueprint is conservative (4); ours allows up to 10 |
| **Rate limiting / back-off** | ❌ None | ❌ None | Both have the same gap — no protection against API bursts |
| **Token bucket** | ❌ None | ❌ None | Both have the same gap |
| **Workspace handling** | Passes `workspace` to Agent for file tool confinement | No workspace param in signature | We have workspace isolation; blueprint doesn't address file sandboxing |
| **Session persistence** | Writes `logs/subagent_N.jsonl` per subagent (see ADR-007) | Not mentioned | Blueprint doesn't address the file clutter concern |
| **Thread safety** | `threading.Lock()` on session counter | No lock needed (uses `pool.map()`, which doesn't need a global counter) | Our lock is a consequence of our session naming strategy |

---

## The Hard Truth — Does It Apply to Us?

| Accusation | Verdict | Details |
|------------|---------|---------|
| "Lazy import hides architectural rot — tight coupling" | ⚠️ Partially true | Our lazy import is in `tools.py` (wrapper functions). The circular dep is `tools → subagent → agent → tools`. We dodged it, but didn't fix the coupling at the root. |
| "No rate-limiting, no back-off, no token bucket" | ✅ True | We have zero protection. If `fan_out` launches 10 parallel LLM calls, OpenRouter/Ollama sees a burst of 10 concurrent requests. |
| "Will choke upstream API keys instantly" | ⚠️ Partially true | True for OpenRouter (cloud rate limits, 429s). False for Ollama (local, handles bursts fine). |

---

## The Challenge: Partial Failure Handling

**Question:** If 1 of 4 tasks fails, does the master halt entirely?

**Our current answer:** No — we have per-subtask `try/except` in both `delegate` and `fan_out`:

```python
# delegate
try:
    result = run_subagent(task)
    return f"[Subagent result]\n{result}"
except Exception as exc:
    return f"[Subagent error] {exc}"

# fan_out
try:
    agent = Agent(...)
    reply = agent.send(task)
    return index, f"  Subagent {index + 1}: {reply}"
except Exception as exc:
    return index, f"  Subagent {index + 1}: [error] {exc}"
```

**What's missing:** The error is just a string `"[error] ..."` — there's no structured error protocol. The master agent receives a text blob and must parse it to understand what happened. The blueprint's `list[str]` return type is slightly better, but still just strings.

### Proposed Structured Result Protocol

A proper protocol for future implementation:

```python
@dataclass
class SubagentResult:
    success: bool
    task_index: int
    result: str | None = None
    error: str | None = None
    duration_ms: float = 0.0
```

---

## Summary Verdict

| Area | Verdict |
|------|---------|
| Core architecture | ✅ Both same — fresh agents, isolated context, two tools ($delegate$ + $fan\_out$) |
| Error isolation | ✅ We have it — per-subtask `try/except` |
| Rate limiting | ❌ **Both missing** — gap in both designs |
| Structured error protocol | ❌ **Both missing** — errors are plain strings |
| Cleanliness of `fan_out` | ⬇ Blueprint's `pool.map()` is cleaner than our `as_completed()` + dict |
| Configurability | ⬇ Blueprint's explicit `system`/`tools` params are more flexible |

---

## Related ADRs

- **ADR-007:** Subagent Session Persistence — subagents write `logs/subagent_N.jsonl` (deferred)
- **ADR-008:** Pi vs Barenode — Session Forking vs Subagent Delegation (informational)
- **ADR-009:** Subagent Harness Weight — Full Clone vs Lightweight (deferred)
