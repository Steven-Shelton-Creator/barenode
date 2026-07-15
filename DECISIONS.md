# Architectural Decision Records

This file logs every major architectural decision made during the barenode project. Each entry follows a lightweight ADR format: context, options considered, decision, and rationale.

---

## ADR-001: Repository Layout

**Status:** Closed

**Date:** 2026-07-11

### Context

After the initial scaffold, we had two competing repository layouts. The current layout (Option A — `src/` with 3 flat packages) was built first. A second layout (Option B — `agent/` with 9+ sub-packages, organized docs) was proposed. We needed to choose one and commit to it before beginning implementation.

### Option A — Current Layout

```
├── src/
│   ├── harness/          # agent loop, tools, sandbox, memory, etc.
│   ├── model/            # provider abstraction
│   └── ui/               # TUI stubs
```

### Option B — Suggested Layout

```
├── agent/
│   ├── model/   harness/   memory/   tools/   planner/
│   ├── subagents/   verifier/   telemetry/   ui/
├── docs/                # organized into subdirectories
├── examples/   workspace/   scripts/
```

### Decision

**Keep Option A as the core (3-package model under `src/`) and selectively merge infrastructure from Option B.**

Specifically:

- **Keep** `src/` with 3 packages (harness, model, ui) — the code stays put
- **Add** `docs/` subdirectories: `architecture/`, `phases/`, `decisions/`, `research/`, `diagrams/`
- **Add** `workspace/` — sandbox working directory
- **Add** `examples/` — demo scenarios
- **Rename** `PLAN.md` → `BUILD_PLAN.md` for blueprint alignment
- **Add** `ROADMAP.md`, `CONTRIBUTING.md`, `README.md`
- **Keep** existing: `AGENTS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `transcript.md`, `skills/`, `tests/`, `logs/`, `scripts/`

### Rationale

- The 3-package model directly mirrors the video source material (UI → Harness → Model)
- Separating each primitive into its own `agent/` subdirectory is over-engineering for a ~2500 line educational project
- The infrastructure additions (organized docs, workspace, examples, root docs) give us the engineering rigor without bloating the code structure
- Easy to split packages later if the project outgrows the flat layout

---

## ADR-002: Project Language & Toolchain

**Status:** Closed

**Date:** 2026-07-11

### Context

The video tutorial builds the agent in Python using `uv`. The initial scaffold was created as a Node.js project by mistake.

### Decision

Use **Python 3.11+** with **uv** as the package manager and runtime toolchain.

### Rationale

- Directly matches the video source material
- `uv` provides fast, reproducible environments
- Python is the standard language for AI/LLM agent development

---

## ADR-003: CH01 — Provider Abstraction & REPL Design

**Status:** Closed

**Date:** 2026-07-11

### Context

Chapter 01 requires a bare model call — the first primitive. We need a provider seam so the agent can talk to any LLM backend, and a REPL so the user can interact. The transcript says: *"The call goes through a seam: a free `chat` function over a provider (LM Studio, Ollama, or OpenRouter)."* and *"If you want to have fake provider to run the test, we just swap the provider in one line."*

### Options Considered

| Provider | Setup | Pros | Cons |
|----------|-------|------|------|
| **Ollama** | `ollama pull <model>` | Free, local, dead simple API | Requires Ollama daemon |
| **OpenRouter** | API key | No local install, free tier | Needs internet + API key |
| **LM Studio** | Download + GUI | Matches video exactly | Heavier setup |
| **Fake/Echo** | No dependencies | Perfect for tests | Not a real LLM |

### Decision

1. **Default provider:** Ollama (we already have it with 8b models)
2. **Config format:** Single environment variable `BARENODE_MODEL=provider/model`
3. **Default model:** `ollama/qwen2.5:8b` (or whichever we have locally)
4. **Provider-agnostic:** All providers (ollama, openrouter, lstudio, fake) built into the seam from day one — user picks by changing one env var
5. **No keys in repo:** The `.env.example` documents the vars, `.gitignore` blocks `.env`
6. **REPL:** Simple `input()` loop with `/quit` to exit

### Rationale

- The provider seam is the entire point of CH01 — making it swappable in one line teaches the architecture
- Ollama is the simplest local setup (no Docker, no GUI, just a daemon + CLI)
- OpenRouter is the easiest path for users who don't want to run local models
- Fake provider means tests run without any model at all — critical for CI
- The `provider/model` format is unambiguous and extensible (adding a new provider is just another branch)

### Consequences

- Every user must bring their own model or API key — nothing is pre-configured
- The fake provider becomes the test bedrock for all future chapters
- Later chapters will add history, tools, etc. on top of this same send() interface

---

## ADR-004: CH02 — Provider Signature Change for Conversation History

**Status:** Closed

**Date:** 2026-07-12

### Context

Chapter 02 adds conversation history — the Agent keeps a `self.messages` list and replays it on every call. This means the provider `chat()` function needs to accept the full messages list instead of a single string.

We had two options:

### Option A — Change `chat()` signature to accept `list[dict]`

| Pros | Cons |
|------|------|
| Directly matches every LLM API (Ollama, OpenAI, OpenRouter all expect a messages array) | Requires updating all 4 provider implementations and any existing callers |
| Clean — no wrapping or internal assembly | |
| Transparent — the provider sees exactly what the harness sends | |

### Option B — Keep `chat(message: str)`, assemble messages list inside each provider

| Pros | Cons |
|------|------|
| No signature change needed | Each provider has to wrap the single message into a list internally |
| Existing callers unchanged | Hides the real API shape from the caller |
| | Adds a hidden transformation in every provider backend |
| | Would need to change again when we add system prompts (CH03) |

### Decision

**Option A — Change `chat()` signature to accept `messages: list[dict]`.**

All four provider implementations (`_call_ollama`, `_call_openrouter`, `_call_lstudio`, `_call_fake`) updated to accept and use the full messages list. The fake provider now finds the last user message from the list instead of echoing a raw string.

### Rationale

- Every LLM API (Ollama, OpenAI, OpenRouter, LM Studio) expects a messages array — the provider should accept that format natively
- CH03 adds system prompts (another message in the list) — this change anticipates that cleanly
- Keep the provider seam thin and honest: no hidden transformations
- The REPL (`main.py`) required zero changes — history management is entirely in the Agent

### Consequences

- All existing CH01 tests still pass (fake provider behavior is semantically equivalent for those test cases)
- The change rippled across 4 provider functions, but was mechanical and safe
- The `chat()` function now matches the transcript's description: it sends a conversation, not a single message
- Future chapters (CH03 instructions, CH04 context delivery) will add messages to the list naturally

---

## ADR-005: Intake Valve — Memory-Only Credential Security Model

**Status:** Closed

**Date:** 2026-07-12

### Context

The agent needed a way to authenticate with GitHub (push commits) and check provider availability without leaking credentials into the repository. Initial approaches had security issues:

1. **Embedding token in remote URL** (v1 of `intake.sh`): `git remote set-url origin https://oauth2:TOKEN@github.com/...` — token written to `.git/config` on disk
2. **GIT_ASKPASS temp script** (v2): Wrote token to a `/tmp/` script file — cleaned on exit but briefly on disk
3. **Credential helper with expanded token** (v3): `git config --local credential.helper ...` with expanded token — token value written to `.git/config`

We needed an approach that never writes the token value to any file, at any point.

### Options Considered

| Option | Disk writes | Token on disk? | Works? |
|--------|-------------|-----------------|--------|
| **Embedded remote URL** | `.git/config` | ✅ Token value | ✅ Push works |
| **GIT_ASKPASS temp script** | `/tmp/` file | ✅ Token value | ✅ Push works |
| **Credential helper, expanded** | `.git/config` | ✅ Token value | ✅ Push works |
| **Credential helper, unexpanded** | `.git/config` | ❌ Only `$GITHUB_TOKEN` literal | ✅ Push works |

### Decision

**Option 4 — Credential helper storing unexpanded `$GITHUB_TOKEN` variable reference.**

The `.git/config` file stores the literal string `$GITHUB_TOKEN`, not the token value. At push time, git evaluates the credential helper in a subshell that inherits the environment, so `$GITHUB_TOKEN` expands from the environment variable in memory.

```bash
# In .git/config (stored literally, never expanded):
[credential]
    helper = "!f() { echo username=oauth2; echo password=$GITHUB_TOKEN; }; f"

# Token value comes from environment at push time:
export GITHUB_TOKEN=github_pat_...  # in .env (gitignored) or env var
```

### Rationale

- The token value **never touches disk** in any form — only the literal string `$GITHUB_TOKEN` is stored
- Without the environment variable, the credential helper returns an empty password — zero value even if `.git/config` is exfiltrated
- Works with standard git push/pull/fetch — no custom wrappers needed
- The `.env` file (where the actual token lives) is gitignored
- On shell exit, the environment variable disappears — only the inert `$GITHUB_TOKEN` reference remains

### Intake Valve Flow

```
source scripts/intake.sh
  → 1. Source .env (gitignored) — loads GITHUB_TOKEN into memory
  → 2. Clean remote URL — remove any previously-embedded tokens
  → 3. Set credential.helper with $GITHUB_TOKEN (literal, unexpanded)
  → 4. Check provider availability (Ollama, OpenRouter)
  → 5. Report status — no secrets printed, just ✓/✗ indicators
```

### Security Sweep (verified)

| Check | Result |
|-------|--------|
| `git grep "github_pat"` — token in tracked files? | ✅ Zero results |
| `git config --get remote.origin.url` — token in remote? | ✅ Clean HTTPS URL |
| `.git/config` — token value on disk? | ✅ Only `$GITHUB_TOKEN` literal |
| `.env` — gitignored? | ✅ Confirmed |

### Consequences

- Must run `source scripts/intake.sh` at the start of every session (or token won't be in environment)
- The credential helper reference in `.git/config` is inert without the env var — safe to leave between sessions
- Pushing from a subshell without sourcing intake first will fail (expected — feature, not bug)
- All future git operations (push, pull, fetch) work transparently after intake

---

## ADR-006: CH04 — Context Delivery Design

**Status:** Closed

**Date:** 2026-07-13

### Context

Chapter 04 adds context delivery — the `@file` syntax where the harness scans the user's message for `@path` references, reads the files from disk, and injects their contents before the model call.

We needed to decide:
1. How to mark file references (symbol choice)
2. Where in the message pipeline injection happens
3. How to format injected content
4. Security boundaries
5. Behavior on missing files

### Options Considered

| Aspect | Option A (chosen) | Option B | Option C |
|--------|-------------------|----------|----------|
| **Symbol** | `@filename` | `#filename` | `[file:path]` |
| **Injection point** | Before storing in `self.messages` | In `messages_to_send` only | In a separate context message |
| **Format** | `--- path ---\ncontent\n--- end path ---` | Inline replacement only | JSON-wrapped block |
| **Missing file** | Leave `@ref` unchanged | Raise error | Empty injection |
| **Security** | Workspace prefix check | Glob patterns | No check |

### Decision

| Choice | Value | Rationale |
|--------|-------|-----------|
| **Symbol** | `@` | Matches the video source material. Common convention (Claude Code, Codex). Distinctive, unlikely to appear naturally in text. |
| **Injection point** | Before storing in `self.messages` | Simplest wiring (2 lines). History stores resolved content, so the model sees file contents on replay too. |
| **Format** | `--- path ---\ncontent\n--- end path ---` with content preceded by markers | Clear visual boundary. Easier for the model to distinguish file content from the user's question. |
| **Missing file** | Leave `@ref` unchanged | Graceful fallback — model can ask the user for the correct path. No crash, no confusing error message. |
| **Security** | Workspace prefix check with `os.path.abspath()` | Blocks `@../etc/passwd` style escapes. Simple, verifiable, no dependencies. |

### Rationale

- The `@` symbol is minimal, intuitive, and matches the source material
- Injecting before storing means the history is always resolved — the model doesn't need to re-read files on subsequent turns
- Markers provide a clear visual boundary that makes it obvious to the model what's file content vs. user text
- The workspace prefix check is a simple security boundary that prevents path traversal attacks
- Graceful fallback for missing files means the agent never crashes on bad references

### Consequences

- The stored history contains resolved file contents, not `@refs` — if files change between turns, stale content persists in history
- No token management yet — large files are injected whole (CH06 adds compression)
- The REPL and demo needed zero structural changes — the injection is transparent to the UI layer
- The security boundary is enforced at the string level (startswith), not the filesystem level (realpath) — sufficient for an educational build

---

## ADR-007: CH11 — Subagent Session Persistence

**Status:** Open (deferred)

**Date:** 2026-07-14

### Context

Chapter 11 adds subagents — fresh `Agent` instances for delegated and fanned-out subtasks. Each subagent is a full `Agent` instance, which means it inherits the CH09 durable state machinery:

- `Agent.__init__` calls `load_session(name, session_dir)`
- `Agent.send()` calls `save_session()` after every reply
- `session_dir` defaults to `logs/` in the current working directory

Since `run_subagent()` assigns each subagent a unique `session_name` (e.g., `subagent_1`, `subagent_2`), every `delegate` or `fan_out` call creates one or more persistent JSONL session files on disk — even though the subagent's full transcript is discarded after returning just the final answer.

### Options Considered

| Option | Behavior | Complexity |
|--------|----------|-------------|
| **A — Status quo** | Subagents write session files to `logs/subagent_N.jsonl` | Zero |
| **B — Null session dir** | Pass `session_dir="/dev/null"` or a temp dir — files are transient | Low |
| **C — Persistence flag** | Add `persist: bool = True` param to Agent, subagents pass `persist=False` | Medium |
| **D — Discard after read** | Run subagent, read reply, delete session file immediately | Low |

### Decision

**Deferred — keep Option A (status quo) for now.**

### Rationale

- The project is small and educational — a handful of tiny JSONL files in `logs/` is negligible
- Every subagent file is a few lines (1 user message + 1 assistant reply), so disk impact is minimal
- The session files are human-readable and could be useful for debugging subagent behavior
- Adding a persistence guard introduces complexity that doesn't serve the current build goals
- This decision can be revisited when/if:
  - The system runs at scale (hundreds of subagents per session)
  - `logs/` clutter becomes a user complaint
  - A `--clean` flag or session lifecycle management is added

### Consequences

- Every `delegate` or `fan_out` call leaves a trace in `logs/` — good for debugging, bad for minimalists
- Subagent session files are tiny and self-cleaning if `logs/` is added to a cleanup cron or gitignored for large-scale use
- No code changes needed now; if Option B/C/D is chosen later, it's a 2-line change in `run_subagent()` and `_run_one()`