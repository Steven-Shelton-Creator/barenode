# Changelog

All notable changes to the barenode project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to **chapter tags** (CH00, CH01, CH02, ...).

---

## [CH06] — 2026-07-14 — Context Management

### Added
- `src/harness/limits.py`: Token budget constants (MAX_CONTEXT_TOKENS, MAX_ITEM_CHARS, HEAD_TURNS, TAIL_TURNS), token estimator (`estimate_tokens`, `estimate_messages_tokens`, `is_budget_exceeded`)
- `src/harness/compaction.py`: `compact()` — keeps head/tail, summarizes middle; `clamp_content()` — truncates over-long items
- `tests/test_ch06.py`: 29 tests — limits, clamp, compact, agent integration, regression

### Changed
- `src/harness/agent.py`: Wired `compact()` into `send()` — fires after user message appended, before tool loop. Supports `BARENODE_CONTEXT_BUDGET` env var.
- `docs/phases/06-compaction.md`: Status → ✅ Complete, learnings filled
- `BUILD_PLAN.md`: CH06 marked complete
- `ROADMAP.md`: CH06 marked complete

---

## [CH05] — 2026-07-14 — Tools

### Added
- `src/model/provider.py`: `ModelResponse` dataclass — structured return type (content + tool_calls)
- `src/harness/tools.py`: `Tool` dataclass, `ToolRegistry`, `default_registry()` — calculator, read_file, write_file
- `src/harness/approval.py`: `prompt_approval()` — y/n gate for dangerous operations
- `tests/test_ch05.py`: 38 tests — full coverage

### Changed
- `src/harness/agent.py`: Tool loop wired into `send()` — capped at 6 iterations, workspace injection only for tools that need it
- `src/model/provider.py`: `chat()` returns `ModelResponse`, all providers extract tool_calls, fake provider supports test simulation
- `docs/phases/05-tools.md`: Status → ✅ Complete, learnings filled
- `BUILD_PLAN.md`: CH05 marked complete
- `ROADMAP.md`: CH05 marked complete

---

## [FIX] — 2026-07-14 — Git Branch Discipline

### Fixed
- Resolved detached HEAD at `CH01` tag — working tree was showing CH01 code instead of CH04

### Added
- `AGENTS.md`: Git Discipline guardrail + Git Branch Verification section

### Changed
- `docs/schema-map.md`: Updated HEAD hash to `9670fa7`

---

## [CH04] — 2026-07-13 — Context Delivery

### Added
- `src/harness/context.py`: `deliver()` function — scans for `@path` references, reads files from workspace, injects content inline with markers
- `tests/test_ch04.py`: 15 tests — 10 unit, 4 integration, 1 regression
- `docs/2026-07-13-session.md`: Session log
- `docs/reflections/2026-07-13.md`: Daily reflection
- `docs/verification/CH04-verification.md`: Verification log — fake + real model

### Changed
- `src/harness/agent.py`: Wired `deliver()` into `send()` — 2 lines added
- `src/main.py`: Demo updated to CH04 label, added @missing.txt test message
- `docs/phases/04-context.md`: Status → ✅ Complete, learnings filled
- `BUILD_PLAN.md`: CH04 marked complete
- `ROADMAP.md`: CH04 marked complete

---

## [CH03] — 2026-07-12 — Instructions

### Added
- `src/harness/instructions.py`: `load_instructions()`, `make_system_prompt()`, `build_system_message()` — system prompt builder with AGENTS.md auto-loader
- `tests/test_ch03.py`: 9 tests — loader, builder, and agent integration
- `docs/verification/CH03-verification.md`: Verification log
- `scripts/intake.sh`: Memory-only credential/configuration bootstrap

### Changed
- `src/harness/agent.py`: Added `workspace` param, system message prepended fresh each turn
- `src/main.py`: Default model updated to `gemma4:e4b`, demo labels CH03
- `AGENTS.md`: Self-orientation instructions, tracking update table, intake valve instructions
- `DECISIONS.md`: Added ADR-005 (intake valve credential security)
- `BUILD_PLAN.md`: CH03 marked complete
- `ROADMAP.md`: CH03 marked complete

---

## [CH02] — 2026-07-12 — Conversation History

### Added
- `src/harness/agent.py`: `self.messages = []` list, `send()` now appends user message, passes full history, appends reply
- `src/model/provider.py`: `chat()` signature changed from `message: str` to `messages: list[dict]` — all 4 backends updated
- `src/model/provider.py`: Fake provider now extracts last user message from list (more realistic simulation)
- `tests/test_ch02.py`: 4 new tests — message growth, full forwarding, turn order, instance isolation
- `src/main.py`: Demo updated to show CH02 message count
- `docs/verification/CH02-verification.md`: Verification log
- `docs/reflections/2026-07-11.md`, `docs/reflections/2026-07-12.md`: Daily workflow reflections
- `docs/schema-map.md`: Full directory map with tracking systems summary, phase status table, start-here guide
- `AGENTS.md`: Self-orientation instructions, intake valve instructions, tracking update table, observed chapter cycle
- `scripts/intake.sh`: Credential/configuration bootstrap script
- `.env.example`: Added `GITHUB_TOKEN` configuration

### Changed
- `tests/test_ch01.py`: Updated `test_invalid_model_spec` for new `chat()` signature
- `docs/workflow-reflections.md`: Refactored from single playbook → master index with daily reflection files
- `DECISIONS.md`: Added ADR-004 (provider signature change)
- `docs/phases/00-foundation.md`, `docs/phases/02-history.md`: Normalized status headers (Phase, Status, Date)
- `.env.example`: Added GITHUB_TOKEN field

### Fixed
- Context tracking: Verification log, schema map, daily reflections, phase doc status all brought up to date
- AGENTS.md: Now instructs agent where to log updates automatically

### Commits
```
befed26 CH02: implement conversation history — messages list, replay, provider refactor
c96a0db chore: rename workflow-playbook → workflow-reflections, add ADR-004, log CH02 conversation summary
1203984 chore: fix context tracking — CH02 verification log, schema map, daily reflections
94cdd29 chore: expand schema map — add tracking systems, phase status table, session logs, start-here guide
7d1057e chore: finalize tracking — normalize phase doc headers, update session log, update reflection state
eeed4c5 chore: add self-orientation and tracking update instructions to AGENTS.md
9bdf45e feat: add intake valve — credential/configuration bootstrap for agent
```

---

## [CH01] — 2026-07-11 — The Model

### Added
- `src/model/provider.py`: Provider seam with 4 backends — ollama, openrouter, lstudio, fake
- `src/harness/agent.py`: Agent class with stateless `send()` method
- `src/main.py`: REPL (`uv run agent`) + demo (`uv run demo`)
- `tests/test_ch01.py`: 4 tests using fake provider
- `docs/phases/00-14.md`: All 15 phase docs (plan + record)
- `docs/verification/CH01-verification.md`: Verification log
- `docs/2026-07-11-session.md`: Session log
- `docs/workflow-reflections.md`: Initial workflow reflection (later refactored)
- `DECISIONS.md`: ADR-001 (repo layout), ADR-002 (Python/uv), ADR-003 (provider abstraction)
- `ARCHITECTURE.md`, `BUILD_PLAN.md`, `ROADMAP.md`, `CONTRIBUTING.md`, `README.md`: Project docs
- `AGENTS.md`: Agent system prompt
- `transcript.md`: Full video transcript
- `pyproject.toml`: UV project config
- `.env.example`: Provider configuration template
- 24 research screenshots across 14 chapter directories

### Commits
```
6939e5b initial scaffold: bare-bones Node.js project with src, tests, scripts, logs dirs
7a59e00 full scaffold: transcript, architecture, plan, AGENTS.md, three-package structure, stub modules for all 15 chapters
86dd546 docs: fine-grained GitHub token creation guide
ea668a3 Create README.md
b016259 docs: add repo foundation doc, mark docs as suggested outlines only
5fd941a ADR-001: finalize merged layout, draft ARCHITECTURE.md, add ROADMAP/CONTRIBUTING/README
4cd35a6 docs: add phase docs (00-14) — plan, work log, and learnings for every chapter
aa2b02e research: add 24 phase screenshots organized by chapter, link to phase docs
30389d0 plan: finalize CH01 implementation plan with decisions table and acceptance criteria
3fc15d5 decision: ADR-003 — CH01 provider abstraction, Ollama default, env var config
55519d2 CH01: implement bare model call — provider seam, Agent class, REPL, tests
d772e79 chore: add egg-info to gitignore
27d2f68 ch01: add verification record — fake provider + real model test run logged
42c8b47 ch01: add verification log — fake provider and real model test results
6ed1ad9 log: session log for 2026-07-11 — scaffold + CH01 complete
a0807d7 docs: add workflow playbook — the repeatable chapter cycle
```