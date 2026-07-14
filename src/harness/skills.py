"""Skills — progressive disclosure skill loader (CH07).

A skill is a directory containing a ``skill.md`` file with YAML
frontmatter (name, description) and a body with instructions.

Progressive disclosure:
  - Only the skill name and one-line description are advertised in the
    system prompt.
  - The full body stays on disk until the model reads it with the
    existing ``read_file`` tool (CH05).
"""

import os
import re


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n(.*)",
    re.DOTALL,
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse YAML-like frontmatter from a skill.md file.

    Parameters
    ----------
    text : str
        The full content of a ``skill.md`` file.

    Returns
    -------
    tuple[dict[str, str], str]
        A ``(frontmatter, body)`` pair.  ``frontmatter`` is a dict of
        key-value pairs (e.g. ``{"name": "sign-off", "description": "..."}``).
        ``body`` is the remaining text after the frontmatter block.
        Returns ``({}, text)`` if no frontmatter is found.
    """
    match = _FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}, text

    raw_fm = match.group(1)
    body = match.group(2).strip()

    frontmatter: dict[str, str] = {}
    for line in raw_fm.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body


# ---------------------------------------------------------------------------
# Skill dataclass
# ---------------------------------------------------------------------------

class Skill:
    """A single skill loaded from a ``skill.md`` file.

    Attributes
    ----------
    name : str
        The skill name (from frontmatter).
    description : str
        One-line description (from frontmatter).
    body : str
        The full skill instructions (after frontmatter).
    directory : str
        The directory path containing this skill.
    """

    def __init__(self, directory: str) -> None:
        self.directory = directory
        self.name = os.path.basename(directory)
        self.description = ""
        self.body = ""
        self._load()

    def _load(self) -> None:
        """Read and parse the skill.md file from this skill's directory."""
        path = os.path.join(self.directory, "skill.md")
        if not os.path.isfile(path):
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            return

        frontmatter, self.body = parse_frontmatter(text)
        self.name = frontmatter.get("name", os.path.basename(self.directory))
        self.description = frontmatter.get("description", "")

    def description_line(self) -> str:
        """Return a one-line summary for the system prompt."""
        return f"  - {self.name}: {self.description}" if self.description else f"  - {self.name}"


# ---------------------------------------------------------------------------
# Skill loader
# ---------------------------------------------------------------------------

def load_skills(skills_dir: str | None = None) -> list[Skill]:
    """Load all skills from the skills directory.

    Scans *skills_dir* for subdirectories containing ``skill.md`` files.

    Parameters
    ----------
    skills_dir : str or None
        Path to the skills directory.  Defaults to ``skills/`` relative
        to the current working directory.

    Returns
    -------
    list[Skill]
        A list of loaded ``Skill`` objects.  Empty if the directory
        doesn't exist or contains no valid skills.
    """
    if skills_dir is None:
        skills_dir = os.path.join(os.getcwd(), "skills")

    if not os.path.isdir(skills_dir):
        return []

    skills: list[Skill] = []
    for entry in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, entry)
        if os.path.isdir(skill_path) and os.path.isfile(os.path.join(skill_path, "skill.md")):
            skills.append(Skill(skill_path))

    return skills


def build_skills_section(skills_dir: str | None = None) -> str:
    """Build the skills section for the system prompt.

    Returns a string with a list of available skills (name + description
    only), or an empty string if no skills are found.

    Parameters
    ----------
    skills_dir : str or None
        Path to the skills directory.

    Returns
    -------
    str
        The skills section text, or empty string.
    """
    skills = load_skills(skills_dir)
    if not skills:
        return ""

    lines = ["\n\n## Available Skills", ""]
    for skill in skills:
        lines.append(skill.description_line())
    lines.append("")
    lines.append("To use a skill, read its full instructions with the read_file tool.")
    lines.append("Example: Read the file skills/sign-off/skill.md")

    return "\n".join(lines)