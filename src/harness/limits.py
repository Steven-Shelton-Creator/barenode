"""Limits — token budget, clamping, and token estimation (CH06).

The harness uses a simple heuristic to estimate token counts and
decide when to compact the conversation history.  Individual message
content is also clamped to prevent any single item from blowing the
budget.
"""

# ---------------------------------------------------------------------------
# Budget constants
# ---------------------------------------------------------------------------

# Default context budget in tokens.  When the estimated token count
# exceeds this, compaction fires.
MAX_CONTEXT_TOKENS = 4096

# Maximum characters for any single message content.  Items longer
# than this are truncated with a note.
MAX_ITEM_CHARS = 4000

# Number of turns to protect at the head (oldest) and tail (newest)
# of the conversation during compaction.
HEAD_TURNS = 2
TAIL_TURNS = 3


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a text string.

    Uses a simple heuristic: roughly 4 characters per token for
    English text.  This is a rough estimate — not a real tokenizer.

    Parameters
    ----------
    text : str
        The text to estimate.

    Returns
    -------
    int
        Estimated token count.
    """
    return max(0, len(text) // 4)


def estimate_messages_tokens(messages: list[dict]) -> int:
    """Estimate the total tokens in a list of messages.

    Sums the estimated tokens for each message's ``content`` field,
    plus a small overhead for the message structure (role, metadata).

    Parameters
    ----------
    messages : list[dict]
        List of message dicts with ``content`` and ``role``.

    Returns
    -------
    int
        Estimated total token count.
    """
    total = 0
    for msg in messages:
        # Content tokens
        content = msg.get("content", "") or ""
        total += estimate_tokens(str(content))

        # Tool call overhead
        tool_calls = msg.get("tool_calls")
        if tool_calls:
            for tc in tool_calls:
                fn = tc.get("function", {})
                total += estimate_tokens(fn.get("name", ""))
                total += estimate_tokens(fn.get("arguments", ""))

        # Tool result overhead
        total += estimate_tokens(msg.get("tool_call_id", ""))

        # Structural overhead (role, message wrapper)
        total += 4  # ~4 tokens per message for {"role": "...", "content": "..."}

    return total


def is_budget_exceeded(messages: list[dict], budget: int | None = None) -> bool:
    """Check whether the conversation exceeds the token budget.

    Parameters
    ----------
    messages : list[dict]
        The conversation history.
    budget : int or None
        Token budget.  Defaults to ``MAX_CONTEXT_TOKENS``.

    Returns
    -------
    bool
        ``True`` if the estimated tokens exceed the budget.
    """
    if budget is None:
        budget = MAX_CONTEXT_TOKENS
    return estimate_messages_tokens(messages) > budget