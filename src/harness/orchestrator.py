"""Orchestrator — planning control plane (CH10).

The orchestrator sits outside the agent's main loop.  The model plans
steps as JSON, and the harness drives each step through execution.

Split:
  - Model decides *what* steps to take.
  - Harness decides *how* to execute each step.
"""

import json
import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Plan types
# ---------------------------------------------------------------------------

@dataclass
class Step:
    """A single step in a plan.

    Attributes
    ----------
    number : int
        Step number (1-based).
    description : str
        What this step does (sent to the agent as a user message).
    expected : str or None
        Optional expected outcome (informational only).
    result : str or None
        The actual result after execution.
    status : str
        One of ``"pending"``, ``"running"``, ``"done"``, ``"failed"``, ``"skipped"``.
    """

    number: int = 0
    description: str = ""
    expected: str | None = None
    result: str | None = None
    status: str = "pending"


@dataclass
class Plan:
    """A structured plan consisting of multiple steps.

    Attributes
    ----------
    task : str
        The original user task.
    steps : list[Step]
        The steps in execution order.
    """

    task: str = ""
    steps: list[Step] = field(default_factory=list)

    def is_complete(self) -> bool:
        """Check whether all steps are done or skipped."""
        return all(s.status in ("done", "skipped") for s in self.steps)

    def current_step(self) -> Step | None:
        """Return the first step that is not done or skipped."""
        for s in self.steps:
            if s.status not in ("done", "skipped"):
                return s
        return None


# ---------------------------------------------------------------------------
# Plan generation
# ---------------------------------------------------------------------------

_PLAN_SYSTEM_PROMPT = """You are a planning assistant. Given a task, break it down into a JSON array of steps.

Each step must have:
  - "step": step number (integer, 1-based)
  - "description": what needs to be done (a clear, complete instruction)
  - "expected": the expected outcome (optional)

Return ONLY a valid JSON array. No markdown, no explanation, no code fences.

Example:
[
  {"step": 1, "description": "Calculate 256 * 8", "expected": "2048"},
  {"step": 2, "description": "Add 100 to 2048", "expected": "2148"}
]"""


def _extract_json(text: str) -> str:
    """Extract a JSON array from a model response, stripping markdown fences."""
    # Try to find a JSON array between markdown code fences
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # Try to find a JSON array directly in the text
    array_match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
    if array_match:
        return array_match.group(0)

    return text.strip()


def generate_plan(task: str, agent) -> Plan:
    """Ask the model to break a task into steps and return a Plan.

    Parameters
    ----------
    task : str
        The user's task description.
    agent : Agent
        The agent instance (used to call the model).

    Returns
    -------
    Plan
        A structured plan with steps.
    """
    from model.provider import chat
    from harness.instructions import build_system_message

    # Build a planning prompt
    sys_msg = build_system_message(agent.workspace)
    planning_messages = [
        {"role": "system", "content": _PLAN_SYSTEM_PROMPT},
        {"role": "user", "content": f"Plan this task:\n\n{task}"},
    ]

    # Call the model without tool specs (pure text planning)
    response = chat(agent.model, planning_messages, tools=None)
    raw = response.content or ""

    # Extract JSON
    json_str = _extract_json(raw)

    plan = Plan(task=task)

    try:
        steps_data = json.loads(json_str)
        if isinstance(steps_data, list):
            for item in steps_data:
                if isinstance(item, dict) and "description" in item:
                    plan.steps.append(Step(
                        number=item.get("step", len(plan.steps) + 1),
                        description=item["description"],
                        expected=item.get("expected"),
                    ))
    except (json.JSONDecodeError, TypeError):
        # If parsing fails, create a single-step plan with the raw response
        plan.steps.append(Step(
            number=1,
            description=raw,
        ))

    # Ensure step numbers are sequential
    for i, step in enumerate(plan.steps):
        step.number = i + 1

    return plan


def format_plan(plan: Plan) -> str:
    """Format a plan as a human-readable string.

    Parameters
    ----------
    plan : Plan
        The plan to format.

    Returns
    -------
    str
        Human-readable plan representation.
    """
    lines = [f"Plan for: {plan.task}", ""]
    for step in plan.steps:
        status_mark = {
            "pending": " ",
            "running": "→",
            "done": "✓",
            "failed": "✗",
            "skipped": "–",
        }.get(step.status, " ")
        desc = step.description
        if step.expected:
            desc += f"  (expected: {step.expected})"
        if step.result:
            desc += f"  → {step.result[:80]}"
        lines.append(f"  [{status_mark}] Step {step.number}: {desc}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Plan execution
# ---------------------------------------------------------------------------

def execute_plan(plan: Plan, agent, approve_step=None, max_retries: int = 1) -> str:
    """Execute each step of a plan through the agent.

    Parameters
    ----------
    plan : Plan
        The plan to execute.
    agent : Agent
        The agent instance.
    approve_step : callable or None
        Optional callback ``approve_step(step) -> bool``.  If ``None``,
        all steps are auto-approved.
    max_retries : int
        Number of retries on failure per step.

    Returns
    -------
    str
        A summary of the execution results.
    """
    results = []

    for step in plan.steps:
        step.status = "running"

        # Approval gate
        if approve_step is not None and not approve_step(step):
            step.status = "skipped"
            results.append(f"Step {step.number}: skipped")
            continue

        # Execute with retries
        last_error = ""
        for attempt in range(max_retries + 1):
            try:
                response = agent.send(step.description)
                step.result = response
                step.status = "done"
                results.append(f"Step {step.number}: {response[:200]}")
                break
            except Exception as exc:
                last_error = str(exc)
                if attempt < max_retries:
                    continue
                step.status = "failed"
                step.result = f"Error: {last_error}"
                results.append(f"Step {step.number}: FAILED — {last_error}")

    # Build summary
    summary_lines = [f"Plan complete: {plan.task}", ""]
    for step in plan.steps:
        icon = "✓" if step.status == "done" else "✗" if step.status == "failed" else "–"
        summary_lines.append(f"  {icon} Step {step.number}: {step.status}")
    summary_lines.append("")
    summary_lines.append("---")
    for r in results:
        summary_lines.append(f"  {r}")

    return "\n".join(summary_lines)