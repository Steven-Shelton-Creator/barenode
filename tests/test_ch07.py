"""Tests for CH07 — Skills (progressive disclosure).

Tests the skill loader, frontmatter parser, system prompt injection,
and the progressive disclosure pattern.
"""

import os
import tempfile

import pytest

from harness.skills import parse_frontmatter, Skill, load_skills, build_skills_section
from harness.instructions import make_system_prompt


# =========================================================================
# Frontmatter parsing
# =========================================================================


def test_parse_frontmatter_basic() -> None:
    """Basic frontmatter is parsed correctly."""
    text = """---
name: sign-off
description: Signs off with a code word
---

When asked to sign off, end with **hila**.
"""
    fm, body = parse_frontmatter(text)
    assert fm["name"] == "sign-off"
    assert fm["description"] == "Signs off with a code word"
    assert "**hila**" in body


def test_parse_frontmatter_no_frontmatter() -> None:
    """Text without frontmatter returns empty dict and full body."""
    text = "Just some text without frontmatter."
    fm, body = parse_frontmatter(text)
    assert fm == {}
    assert body == text


def test_parse_frontmatter_empty() -> None:
    """Empty string returns empty dict and empty body."""
    fm, body = parse_frontmatter("")
    assert fm == {}
    assert body == ""


def test_parse_frontmatter_partial() -> None:
    """Frontmatter with only some fields still works."""
    text = """---
name: test-skill
---

Body text here.
"""
    fm, body = parse_frontmatter(text)
    assert fm["name"] == "test-skill"
    assert "description" not in fm
    assert body == "Body text here."


# =========================================================================
# Skill class
# =========================================================================


def test_skill_loads_from_directory(tmp_path) -> None:
    """Skill loads skill.md from its directory."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "skill.md").write_text("""---
name: my-skill
description: A test skill
---

Execute the following steps:
1. Step one
2. Step two
""")

    skill = Skill(str(skill_dir))
    assert skill.name == "my-skill"
    assert skill.description == "A test skill"
    assert "Execute the following steps" in skill.body


def test_skill_missing_file(tmp_path) -> None:
    """Skill directory without skill.md returns empty values."""
    skill_dir = tmp_path / "empty"
    skill_dir.mkdir()
    skill = Skill(str(skill_dir))
    assert skill.name == "empty"
    assert skill.description == ""


def test_skill_description_line(tmp_path) -> None:
    """description_line() returns a one-line summary."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "skill.md").write_text("""---
name: test-skill
description: A skill for testing
---

Body
""")
    skill = Skill(str(skill_dir))
    assert "test-skill" in skill.description_line()
    assert "A skill for testing" in skill.description_line()


def test_skill_description_line_no_description(tmp_path) -> None:
    """description_line() works even without description."""
    skill_dir = tmp_path / "bare-skill"
    skill_dir.mkdir()
    (skill_dir / "skill.md").write_text("""---
name: bare-skill
---

No description provided.
""")
    skill = Skill(str(skill_dir))
    assert "bare-skill" in skill.description_line()
    assert ":" not in skill.description_line()  # no colon after name


# =========================================================================
# Skill loader
# =========================================================================


def test_load_skills_from_directory(tmp_path) -> None:
    """load_skills() finds all skill directories."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    for name in ["alpha", "beta"]:
        sd = skills_dir / name
        sd.mkdir()
        (sd / "skill.md").write_text(f"""---
name: {name}
description: Skill {name}
---

{name} instructions.
""")

    skills = load_skills(str(skills_dir))
    assert len(skills) == 2
    names = {s.name for s in skills}
    assert names == {"alpha", "beta"}


def test_load_skills_empty_directory(tmp_path) -> None:
    """load_skills() returns empty list for empty directory."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    assert load_skills(str(skills_dir)) == []


def test_load_skills_missing_directory() -> None:
    """load_skills() returns empty list for non-existent directory."""
    assert load_skills("/nonexistent/path") == []


def test_load_skills_ignores_non_skill_dirs(tmp_path) -> None:
    """Directories without skill.md are ignored."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "not-a-skill").mkdir()  # no skill.md inside
    (skills_dir / "README.txt").write_text("not a directory")
    assert load_skills(str(skills_dir)) == []


# =========================================================================
# Skills section builder
# =========================================================================


def test_build_skills_section(tmp_path) -> None:
    """build_skills_section() returns a formatted skills block."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    sd = skills_dir / "sign-off"
    sd.mkdir()
    (sd / "skill.md").write_text("""---
name: sign-off
description: Signs off with a code word
---

Use **hila** to sign off.
""")

    section = build_skills_section(str(skills_dir))
    assert "## Available Skills" in section
    assert "sign-off" in section
    assert "Signs off with a code word" in section
    assert "read_file tool" in section


def test_build_skills_section_empty(tmp_path) -> None:
    """build_skills_section() returns empty string when no skills."""
    skills_dir = tmp_path / "empty-skills"
    skills_dir.mkdir()
    assert build_skills_section(str(skills_dir)) == ""


def test_build_skills_section_missing_dir() -> None:
    """build_skills_section() returns empty string for missing dir."""
    assert build_skills_section("/nonexistent") == ""


# =========================================================================
# System prompt integration
# =========================================================================


def test_make_system_prompt_includes_skills(tmp_path) -> None:
    """make_system_prompt() includes skills section when skills exist."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    sd = skills_dir / "sign-off"
    sd.mkdir()
    (sd / "skill.md").write_text("""---
name: sign-off
description: Signs off responses
---

Use **hila**.
""")

    prompt = make_system_prompt("Be concise.", skills_dir=str(skills_dir))
    assert "## Available Skills" in prompt
    assert "sign-off" in prompt
    assert "Signs off responses" in prompt


def test_make_system_prompt_no_skills(tmp_path) -> None:
    """make_system_prompt() without skills dir works as before."""
    empty_dir = tmp_path / "nope"
    empty_dir.mkdir()
    prompt = make_system_prompt("Be concise.", skills_dir=str(empty_dir))
    assert "## Available Skills" not in prompt
    assert "coding assistant" in prompt


def test_make_system_prompt_empty_skills_dir(tmp_path) -> None:
    """Empty skills directory doesn't add skills section."""
    skills_dir = tmp_path / "empty"
    skills_dir.mkdir()
    prompt = make_system_prompt("Be concise.", skills_dir=str(skills_dir))
    assert "## Available Skills" not in prompt


# =========================================================================
# Agent integration
# =========================================================================


def test_agent_send_works_with_skills(tmp_path) -> None:
    """Agent.send() works when skills are present."""
    from harness.agent import Agent

    # Set up a skill
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    sd = skills_dir / "sign-off"
    sd.mkdir()
    (sd / "skill.md").write_text("""---
name: sign-off
description: Signs off responses
---

Use **hila** to sign off.
""")

    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("hello")
    assert reply.startswith("Echo")


def test_agent_skills_in_system_prompt(tmp_path) -> None:
    """The system prompt includes skill descriptions."""
    from harness.agent import Agent
    from harness.instructions import build_system_message

    # Set up a skill
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    sd = skills_dir / "sign-off"
    sd.mkdir()
    (sd / "skill.md").write_text("""---
name: sign-off
description: Signs off responses
---

Use **hila**.
""")

    sys_msg = build_system_message(workspace=str(tmp_path))
    assert sys_msg is not None
    content = sys_msg["content"]
    assert "sign-off" in content
    assert "Signs off responses" in content


# =========================================================================
# CH01–CH06 regression tests
# =========================================================================


def test_ch01_regression() -> None:
    """CH01 stateless echo still works."""
    from harness.agent import Agent
    agent = Agent(model="fake/echo")
    reply = agent.send("hello")
    assert "hello" in reply


def test_ch02_regression() -> None:
    """CH02 history still grows."""
    from harness.agent import Agent
    agent = Agent(model="fake/echo")
    agent.send("first")
    agent.send("second")
    assert len(agent.messages) >= 4


def test_ch03_regression(tmp_path) -> None:
    """CH03 instructions still work with skills wired in."""
    from harness.agent import Agent
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("You are a test agent.")
    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("Who are you?")
    assert reply.startswith("Echo")


def test_ch04_regression(tmp_path) -> None:
    """CH04 @file references still work."""
    from harness.agent import Agent
    notes = tmp_path / "data.txt"
    notes.write_text("secret data")
    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    reply = agent.send("Read @data.txt")
    assert "secret data" in reply


def test_ch05_regression(tmp_path) -> None:
    """CH05 tools still work."""
    from harness.agent import Agent
    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    assert "calculator" in agent.tools.names()


def test_ch06_regression(tmp_path, monkeypatch) -> None:
    """CH06 compaction still works."""
    from harness.agent import Agent
    monkeypatch.setenv("BARENODE_CONTEXT_BUDGET", "10")
    agent = Agent(model="fake/echo", workspace=str(tmp_path))
    for i in range(10):
        agent.send(f"spam {i} " * 20)
    contents = [m.get("content", "") for m in agent.messages]
    assert any("compressed" in c for c in contents)