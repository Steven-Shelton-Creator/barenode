# CH02 Verification Log

**Date:** 2026-07-12  
**Tag:** `CH02` — History  
**Status:** ✅ All checks passed

---

## Shipped Files

| File | What Changed |
|---|---|
| `src/model/provider.py` | `chat()` signature: `message: str` → `messages: list[dict]`. All 4 provider implementations updated. |
| `src/harness/agent.py` | Added `self.messages = []`, `send()` now appends & replays full history |
| `src/main.py` | Demo updated to show CH02 message count |
| `tests/test_ch02.py` | **New** — 4 tests: message growth, full history forwarding, turn order, instance isolation |
| `tests/test_ch01.py` | Updated `test_invalid_model_spec` for new `chat()` signature |
| `docs/phases/02-history.md` | Status → ✅ Complete, learnings + conversation log recorded |
| `docs/2026-07-12-session.md` | Full session log |
| `DECISIONS.md` | ADR-004 added (provider signature change) |
| `BUILD_PLAN.md`, `ROADMAP.md` | CH02 marked complete |

---

## Test Run 1 — Fake Provider (no model required)

```bash
$ cd /home/steven/projects/barenode
$ BARENODE_MODEL=fake/echo uv run demo
barenode demo — CH02
========================================

> Hello! What is your name?
Echo (echo): Hello! What is your name?

> My name is Gemma.
Echo (echo): My name is Gemma.

> What is my name?
Echo (echo): What is my name?

========================================
History now contains 6 messages.
The harness replays the full conversation on every call.
With a real model, the agent would 'remember' your name.
```

**Observation:** 6 messages tracked across 3 turns (3 user + 3 assistant). The messages list grows correctly and is replayed on every call.

---

## Test Run 2 — Real Model (Ollama + qwen3.5:9b)

```bash
$ cd /home/steven/projects/barenode
$ BARENODE_MODEL=ollama/qwen3.5:9b uv run agent
barenode [ollama/qwen3.5:9b]
Type /quit to exit.

> My name is Gemma.
Hello Gemma! Nice to meet you.

> What is my name?
Your name is Gemma!
```

**Observation:** Agent **remembers** across turns. The harness replays the full message history so the model sees the previous exchange.

This is the key fix: CH01 demonstrated the *problem* (stateless model forgets), CH02 demonstrates the *solution* (harness replays history).

---

## Automated Test Results

```bash
$ uv run pytest tests/ -v
============================= 10 passed in 0.02s ==============================
tests/test_ch01.py::test_agent_echoes_with_fake_provider PASSED
tests/test_ch01.py::test_agent_is_stateless PASSED
tests/test_ch01.py::test_agent_default_model PASSED
tests/test_ch01.py::test_invalid_model_spec PASSED
tests/test_ch02.py::test_messages_list_grows PASSED
tests/test_ch02.py::test_full_history_forwarded_to_provider PASSED
tests/test_ch02.py::test_history_preserves_turn_order PASSED
tests/test_ch02.py::test_new_agent_starts_empty PASSED
tests/test_smoke.py::test_repl_imports PASSED
tests/test_smoke.py::test_demo_imports PASSED
```

All 10 tests pass. The 4 CH02-specific tests confirm:
1. Messages list grows with each turn (2 messages per turn)
2. Full history is forwarded to the provider
3. User/assistant turn order is preserved
4. Each new Agent instance starts with an empty history

---

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Provider signature change | `chat(messages: list[dict])` | Every LLM API expects a messages array. No hidden wrapping. Anticipates CH03 (system prompts). |

Recorded as **ADR-004** in `DECISIONS.md`.

---

## CH02 Diff Summary

```python
# CH01 — stateless
def send(self, message: str) -> str:
    return chat(self.model, message)

# CH02 — history-aware
self.messages: list[dict] = []

def send(self, message: str) -> str:
    self.messages.append({"role": "user", "content": message})
    reply = chat(self.model, self.messages)
    self.messages.append({"role": "assistant", "content": reply})
    return reply
```

---

## Quick Start (for future sessions)

```bash
# Fake provider (no model needed)
cd /home/steven/projects/barenode
BARENODE_MODEL=fake/echo uv run agent

# Real model (Ollama)
BARENODE_MODEL=ollama/qwen3.5:9b uv run agent

# Scripted demo
uv run demo

# Run tests
uv run pytest tests/ -v
```