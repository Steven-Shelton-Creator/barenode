# Transcript: Building an AI Agent From Scratch in Python — One Primitive at a Time

**Title:** Building an AI Agent From Scratch in Python — One Primitive at a Time  
**URL:** https://www.youtube.com/watch?v=oUBgqzcV1qw  
**Speaker:** (AI Engineering educational series)  
**Captured:** 2026-07-11

---

Okay, here's what we are going to do together in this video. We are going to build a real coding agent from scratch in Python. If you caught my harness engineering masterclass, that one was the theory, the concepts, the vocabulary, the why. This is the practical companion to that masterclass. We take those ideas and turn them into a working code, one primitive per chapter.

Now, a quick framing before we build. This is educational. So the agent we build is small on purpose. Its whole job is to make each primitive concrete in the least code that still teaches the idea. So of course we will not be building the next Claude code or codex. Instead, this is built so we actually understand what is going on.

So here's the whole series in one line: **An agent is a model + a harness + a UI.**

The model is a stateless reasoning engine behind one API call. The UI is just how a human reaches it. And everything that makes it feel like an agent lives in the middle — the harness.

Now, before we write a line, here's where we are headed. By chapter 14, this is going to be a real coding agent. It holds a conversation, it runs behind an approval gate, it plans the task, it checks its own work and traces every call. But here's the part that actually matters: we build the harness ourselves, every primitive, starting from an empty file. It stays small — a few thousand lines across three little packages.

Three layers: UI on top, the model at the bottom, and the harness in between. And the harness is what we spend the whole video on: the loop, the context, the tools, the sandbox, the memory, and so on.

15 chapters (0 through 14), each one adds exactly one primitive: Model, then history, instructions, context, tools, and all the way up to observability. And then finally a real UI.

The whole course ships as one repository of Git tags. It goes from chapter 0 to chapter 14, one per chapter. Check out any chapter, and you get the exact runnable agent at that point in the build. The whole thing runs on `uv`. Two ways to interact: `uv run demo` (scripted demo) and `uv run agent` (live REPL).

Three packages: **UI package**, **Model package**, **Harness package**. Arrows only point one way: UI → Harness → Model.

---

## Chapter-by-Chapter Breakdown

### Chapter 0 / Chapter 1 — The Model
- An agent class with one `send` method.
- A single chat call with no message list at all.
- A small REPL so you can keep typing, but every turn is an independent call.
- The call goes through a seam: a free `chat` function over a provider (LM Studio, Ollama, or OpenRouter).
- **Problem demonstrated:** LLM API is stateless. Tell it your name in one turn, it forgets the next.

### Chapter 2 — History
- The model is stateless, so the harness keeps the conversation and replays it on every call.
- Just a list: `self.messages` in `__init__`. Every turn: append user message, send whole list, append reply.
- **Diff:** three lines — the list in init, two appends.
- **Result:** Agent now "remembers" the conversation.

### Chapter 3 — Instructions
- One message the harness prepends on every turn (system prompt).
- Harness auto-loads `agents.md` from the working directory onto the system prompt (same convention as Codex and Claude Code).
- Adds a `workspace` — a directory the agent owns with every path confined to it.
- **Result:** Agent has a standing personality / rules.

### Chapter 4 — Context Delivery
- Harness picks a symbol (e.g., `@`) to refer to a file.
- Before the call, harness scans for `@path` references, reads files off disk, injects contents ahead of the question.
- **Result:** Agent can read files by reference.

### Chapter 5 — Tools
- A tool = a function + a schema.
- Kept in a registry in `tools.py` — hands the model specs, dispatches each call by name.
- **Split:** Model decides *what* to call, harness decides *how* and actually runs it.
- Loop: send with tool specs → if model reaches for a tool, run it, hand back results, go again.
- Capped at 6 steps to prevent infinite loops.
- **Guardrails:** File tools scoped to workspace. Bash runs in a sandbox (Docker or local subprocess). Dangerous stuff asks for permission (approval gate).

### Chapter 6 — Context Management
- Tools cause everything to pile up — history gets long, context window is finite.
- Four moves: **Select**, **Compress**, **Write**, **Isolate**. This chapter builds **Compress**.
- When history crosses a budget, summarize the middle, protect the head and tail.
- `compaction.py` and `limits.py` — compact (summarize middle) and clamp (max item characters).
- **Result:** Window stays manageable, critical info survives.

### Chapter 7 — Skills (Operational Memory)
- Skill = a directory with a `skill.md` (name, description, instructions).
- **Progressive disclosure:** Advertise only the one-line description in the prompt. Full body stays on disk until model reads it with the read-file tool.
- **Result:** Agent can follow repo-specific procedures without pre-injecting everything.

### Chapter 8 — Sandbox
- Start closed: network none, file system copied, credentials absent. Climb the ladder only as needed.
- Bash tool runs inside the sandbox: Docker with no network, non-root user, dropped capabilities, read-only filesystem, hard cap on memory/processes. Falls back to scrubbed local run if no Docker.
- Read-file fenced to workspace — model can't reach `/etc/passwd`.
- **Rule:** Don't tell the model not to touch secrets — just don't give it secrets.

### Chapter 9 — Durable State / Memory
- Harness writes session to disk as JSONL file (one message per line) in `memory.py`.
- Loads history on startup, saves after every turn. Kill process, restart, pick up where you left off.
- Episodic search: plain keyword search across stored sessions (no embeddings).
- **Result:** State outlives the process.

### Chapter 10 — Planning & Orchestration
- Add a control plane: `orchestrator.py`.
- Model plans steps as JSON, harness drives them. Gate each step through approval, execute, retry on failure.
- Agent's loop doesn't change. Main just gates a `/plan` command.
- **Result:** Multi-step tasks are visible and gated, not one opaque turn.

### Chapter 11 — Subagents
- Fresh agent for a self-contained subtask: its own context, its own tools, run to completion. Keep only the answer.
- `subagent.py` — `run_subagent` builds a fresh agent, returns reply (not transcript).
- Two tools: `delegate` (single subtask) and `fan_out` (batch, runs in parallel).
- **Result:** Context isolation is a feature.

### Chapter 12 — Self-Verification
- Harness watches the transcript. Won't accept "done" until it sees a real passing run.
- Reads from `agents.md` a `[testing]` section that names the command (npm test, go test, uv run verify, etc.).
- Gate arms only when a turn wrote a code file (decided by file extension).
- **Result:** Agent held to the same bar we hold ourselves.

### Chapter 13 — Observability / Tracing
- Tracer runs through the loop and records every step: model calls, tool calls (exact args + results), verify steps, plan steps.
- Pricing table in model package — local models = free, hosted = metered.
- One emit can have many sinks: UI panel, JSONL file, console printer, or OpenTelemetry-compliant collector.
- Uses OpenTelemetry GenAI semantic conventions.
- **Result:** We can see inside every run — tokens, cost, tool inputs/outputs.

### Chapter 14 — Terminal UI
- Final package: UI. Runs with `uv run tui`.
- Two panes: conversation on the left, live trace stream on the right.
- Approval gate as a modal showing a unified diff for file edits.
- UI doesn't re-implement the agent — runs the same agent in a worker thread and renders what the tracer records.
- Only the UI package imports `textual`.
- **Result:** Agent = model + harness + UI, full circle.

---

## Recap

- ~2500 lines of Python
- 15 chapters, one primitive each
- Every chapter = a git tag
- The model barely changed (zero weight changes) — the harness is what turned the model into an agent
- Three packages: `ui` → `harness` → `model`
- Architecture pattern: UI only talks to harness, harness only talks to model
