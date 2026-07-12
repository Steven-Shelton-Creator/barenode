# Phase 7 — Skills

**Status:** 📝 Not Started

---

## Goal

Give the agent operational memory — procedures it can follow without being told every time. A skill is a reusable recipe the agent can load on demand.

## Concepts

- **Skill = a directory with `skill.md`:** Contains name (frontmatter), description, and instructions.
- **Progressive disclosure:** Only the one-line description is advertised in the system prompt. The full body stays on disk until the model decides it's relevant and reads it with the read-file tool (which it already has from Phase 5).
- **Skills array:** Added to the system prompt alongside the built-in prompt and AGENTS.md.

## Plan

1. Build `skills.py` — load skill descriptions from `skills/` directory.
2. Parse frontmatter from `skill.md` files (name, description).
3. Inject skill descriptions (name + description only) into the system prompt.
4. Model reads the full skill body on demand using the existing read-file tool.

## Files

| File | Purpose |
|------|---------|
| `src/harness/skills.py` | Skill loader, frontmatter parser |
| `src/harness/instructions.py` | Add skills to system prompt assembly |
| `skills/` | Directory of skill directories |

## Demo

```
$ uv run agent
> Sign off for me.
[Reads skill: sign-off]
hila
```

The codename "hila" lives nowhere in the prompt — it's only in the skill file on disk. The model read it on demand.

## Acceptance Criteria

- [ ] Skill descriptions appear in system prompt (name + one-liner only)
- [ ] Model reads full skill body only when relevant
- [ ] Multiple skills work alongside each other
- [ ] Missing skills directory does not crash

## Learnings

*(To be filled during implementation.)*