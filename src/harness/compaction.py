"""Context compaction — compress the middle of a conversation (CH06).

When the conversation exceeds the token budget, the harness compacts
it by keeping the head (oldest turns) and tail (newest turns), and
replacing the middle with a single summary note.

Individual message content is also clamped to prevent any single item
from blowing the budget.
"""

from harness.limits import (
    MAX_CONTEXT_TOKENS,
    MAX_ITEM_CHARS,
    HEAD_TURNS,
    TAIL_TURNS,
    is_budget_exceeded,
    estimate_messages_tokens,
)


def _count_turns(messages: list[dict]) -> int:
    """Count the number of user/assistant turns in the message list.

    A turn is a user message followed by its assistant response(s).
    We count user messages as turn boundaries.
    """
    return sum(1 for m in messages if m["role"] == "user")


def clamp_content(messages: list[dict], max_chars: int | None = None) -> list[dict]:
    """Clamp any single message content to *max_chars* characters.

    Content longer than the limit is truncated with a note.
    Operates on a **copy** of the messages list — does not mutate.

    Parameters
    ----------
    messages : list[dict]
        The conversation history.
    max_chars : int or None
        Maximum characters per content field.  Defaults to ``MAX_ITEM_CHARS``.

    Returns
    -------
    list[dict]
        A new list with clamped content.
    """
    if max_chars is None:
        max_chars = MAX_ITEM_CHARS

    clamped = []
    for msg in messages:
        msg_clamped = dict(msg)
        content = msg.get("content", "") or ""
        if isinstance(content, str) and len(content) > max_chars:
            msg_clamped["content"] = content[:max_chars] + (
                f"\n[... truncated: {len(content) - max_chars} characters removed ...]"
            )
        clamped.append(msg_clamped)

    return clamped


def compact(
    messages: list[dict],
    budget: int | None = None,
    head_turns: int | None = None,
    tail_turns: int | None = None,
) -> list[dict]:
    """Compact the conversation if it exceeds the token budget.

    Keeps the head (oldest *head_turns* turns) and tail (newest
    *tail_turns* turns), and replaces the middle with a single summary
    note.  Operates on a **copy** — does not mutate the original.

    If the budget is not exceeded, returns the messages unchanged
    (after clamping).

    Parameters
    ----------
    messages : list[dict]
        The conversation history to compact.
    budget : int or None
        Token budget.  Defaults to ``MAX_CONTEXT_TOKENS``.
    head_turns : int or None
        Number of turns to keep at the head.  Defaults to ``HEAD_TURNS``.
    tail_turns : int or None
        Number of turns to keep at the tail.  Defaults to ``TAIL_TURNS``.

    Returns
    -------
    list[dict]
        The compacted (or original) messages.
    """
    if budget is None:
        budget = MAX_CONTEXT_TOKENS
    if head_turns is None:
        head_turns = HEAD_TURNS
    if tail_turns is None:
        tail_turns = TAIL_TURNS

    # First clamp individual content
    clamped = clamp_content(messages, MAX_ITEM_CHARS)

    # Check if compaction is needed
    if not is_budget_exceeded(clamped, budget):
        return clamped

    # Identify turn boundaries (user messages)
    user_indices = [i for i, m in enumerate(clamped) if m["role"] == "user"]
    total_turns = len(user_indices)

    # If there aren't enough turns to have a middle, just return clamped
    if total_turns <= head_turns + tail_turns:
        return clamped

    # Find the split points
    # Head: first head_turns user messages + their assistant responses
    if head_turns > 0 and user_indices:
        head_end = user_indices[head_turns]
    else:
        head_end = 0

    # Tail: last tail_turns user messages + their assistant responses + tool results
    if tail_turns > 0:
        tail_start = user_indices[-tail_turns]
    else:
        tail_start = len(clamped)

    # Middle: everything between head_end and tail_start
    middle = clamped[head_end:tail_start]

    if not middle:
        return clamped

    # Build the compacted list
    head = clamped[:head_end]
    tail = clamped[tail_start:]

    # Count what was in the middle
    middle_user_count = sum(1 for m in middle if m["role"] == "user")
    total_middle = len(middle)

    # Create a summary note for the middle
    summary = {
        "role": "system",
        "content": (
            f"[... compressed: {middle_user_count} previous turns "
            f"({total_middle} messages) summarized ...]"
        ),
    }

    compacted = head + [summary] + tail

    # If still over budget after first pass, compact again (recursive)
    # This handles extreme cases where even head + tail exceed budget.
    # Head and tail are never reduced below 1 to preserve essential context.
    if is_budget_exceeded(compacted, budget):
        next_head = max(0, head_turns - 1) if head_turns > 1 else 1
        next_tail = max(0, tail_turns - 1) if tail_turns > 1 else 1
        # Only recurse if we can actually reduce further
        if next_head < head_turns or next_tail < tail_turns:
            return compact(
                compacted,
                budget=budget,
                head_turns=next_head,
                tail_turns=next_tail,
            )

    return compacted