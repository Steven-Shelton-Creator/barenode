# Phase 7 — Skills

**Status:** ✅ Complete (2026-07-14)

---

## Goal

Give the agent operational memory — procedures it can follow without being told every time. A skill is a reusable recipe the agent can load on demand.

## Concepts

- **Skill = a directory with `skill.md`:** Contains name (frontmatter), description, and instructions.
- **Progressive disclosure:** Only the one-line description is advertised in the system prompt. The full body stays on disk until the model decides it's relevant and reads it with the read-file tool (which it already has from Phase 5).
- **Skills array:** Added to the system prompt alongside the built-in prompt and AGENTS.md.

## Plan (completed)

1. ✅ Built `skills.py` — frontmatter parser, Skill class, load_skills(), build_skills_section()
2. ✅ Updated `instructions.py` — skills section appended to system prompt
3. ✅ Skills directory with sign-off skill pre-loaded
4. ✅ Progressive disclosure: only name + description in prompt, full body on disk

## Files

| File | Purpose |
|------|---------|
| `src/harness/skills.py` | Skill loader, frontmatter parser, system prompt builder |
| `src/harness/instructions.py` | Skills section injected into system prompt |
| `skills/sign-off/skill.md` | Example skill — signs off with code word |
| `tests/test_ch07.py` | 26 tests — frontmatter, Skill, loader, integration, regression |

## Demo

```
$ uv run agent
> Sign off for me.
[Reads skill: sign-off]
hila
```

The codename "hila" lives nowhere in the prompt — it's only in the skill file on disk. The model read it on demand.

## Acceptance Criteria

- [x] Skill descriptions appear in system prompt (name + one-liner only)
- [x] Model reads full skill body only when relevant
- [x] Multiple skills work alongside each other
- [x] Missing skills directory does not crash

## Learnings

### Key Design Decisions
- **Progressive disclosure.** Only skill name + description go in the system prompt. The model uses `read_file` (from CH05) to load full instructions when needed.
- **Frontmatter parsing.** Simple `---` delimiter parsing. No YAML dependency needed for name/description key-value pairs.
- **Fallback to directory name.** If `skill.md` has no frontmatter name, the directory name is used.

### Real Model Demo
```
> Please sign off for me.
> The task is complete.
>
> hila
```
The code word "hila" lived only in `skills/sign-off/skill.md` on disk — never in the prompt.

## Reference Images

| # | File | Description |
|---|------|-------------|
| 1 | `docs/research/images/ch07/barenode-ch07-01.png` | *(to annotate)* |