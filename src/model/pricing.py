"""Pricing — cost tables per model (CH13).

Local models (Ollama, LM Studio, fake) are free.  Hosted models
(OpenRouter) are metered per token.  The pricing table maps model
name patterns to per-token costs.

Design
------
- ``ModelPricing`` dataclass: input and output cost per token
- ``PRICING_TABLE``: ordered list of ``(pattern, pricing)`` entries
- ``estimate_cost()``: looks up model, calculates cost from token counts
- ``is_local_model()``: checks whether a model spec is a local provider
"""

import re
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Pricing data type
# ---------------------------------------------------------------------------

@dataclass
class ModelPricing:
    """Per-token cost for a model.

    Attributes
    ----------
    input_cost_per_token : float
        Cost in USD per input token (prompt).
    output_cost_per_token : float
        Cost in USD per output token (completion).
    """

    input_cost_per_token: float = 0.0
    output_cost_per_token: float = 0.0


# ---------------------------------------------------------------------------
# Pricing table — ordered list of (pattern, pricing)
# ---------------------------------------------------------------------------
# Patterns are regex strings matched against the full model spec
# (e.g. "openrouter/anthropic/claude-3-opus").
# First match wins.

PRICING_TABLE: list[tuple[str, ModelPricing]] = [
    # Local providers — always free
    (r"^ollama/", ModelPricing(0.0, 0.0)),
    (r"^lstudio/", ModelPricing(0.0, 0.0)),
    (r"^fake/", ModelPricing(0.0, 0.0)),

    # OpenRouter — Anthropic Claude
    (r"^openrouter/anthropic/claude-3\.5", ModelPricing(0.003, 0.015)),
    (r"^openrouter/anthropic/claude-3-opus", ModelPricing(0.015, 0.075)),
    (r"^openrouter/anthropic/claude-3-sonnet", ModelPricing(0.003, 0.015)),
    (r"^openrouter/anthropic/claude-3-haiku", ModelPricing(0.00025, 0.00125)),
    (r"^openrouter/anthropic/", ModelPricing(0.003, 0.015)),

    # OpenRouter — OpenAI GPT-4
    (r"^openrouter/openai/gpt-4o", ModelPricing(0.0025, 0.01)),
    (r"^openrouter/openai/gpt-4-turbo", ModelPricing(0.01, 0.03)),
    (r"^openrouter/openai/gpt-4", ModelPricing(0.03, 0.06)),
    (r"^openrouter/openai/gpt-3\.5", ModelPricing(0.001, 0.002)),
    (r"^openrouter/openai/", ModelPricing(0.001, 0.002)),

    # OpenRouter — Meta Llama
    (r"^openrouter/meta-llama/llama-3\.1", ModelPricing(0.0005, 0.0005)),
    (r"^openrouter/meta-llama/llama-3", ModelPricing(0.0005, 0.0005)),
    (r"^openrouter/meta-llama/", ModelPricing(0.0005, 0.0005)),

    # OpenRouter — Mistral
    (r"^openrouter/mistralai/", ModelPricing(0.0005, 0.0005)),
    (r"^openrouter/mistral/", ModelPricing(0.0005, 0.0005)),

    # OpenRouter — Google Gemini
    (r"^openrouter/google/gemini-1\.5-pro", ModelPricing(0.00125, 0.005)),
    (r"^openrouter/google/gemini-1\.5-flash", ModelPricing(0.000075, 0.0003)),
    (r"^openrouter/google/gemini-2", ModelPricing(0.0001, 0.0004)),
    (r"^openrouter/google/", ModelPricing(0.0005, 0.0015)),

    # OpenRouter — DeepSeek
    (r"^openrouter/deepseek/", ModelPricing(0.0005, 0.0005)),

    # OpenRouter — Cohere
    (r"^openrouter/cohere/", ModelPricing(0.0005, 0.0005)),

    # OpenRouter — default fallback
    (r"^openrouter/", ModelPricing(0.001, 0.002)),
]

# Default pricing for unknown models
_DEFAULT_PRICING = ModelPricing(0.001, 0.002)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def lookup_pricing(model_spec: str) -> ModelPricing:
    """Look up the pricing for a model spec.

    Iterates through ``PRICING_TABLE`` and returns the first match.
    Falls back to a default of $0.001/$0.002 per token.

    Parameters
    ----------
    model_spec : str
        Full model spec (e.g. ``"ollama/qwen2.5:8b"`` or
        ``"openrouter/anthropic/claude-3-opus"``).

    Returns
    -------
    ModelPricing
        The pricing for the matched model.
    """
    for pattern, pricing in PRICING_TABLE:
        if re.match(pattern, model_spec):
            return pricing
    return _DEFAULT_PRICING


def estimate_cost(
    model_spec: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Estimate the cost of a model call in USD.

    Parameters
    ----------
    model_spec : str
        Full model spec.
    input_tokens : int
        Number of input (prompt) tokens.
    output_tokens : int
        Number of output (completion) tokens.

    Returns
    -------
    float
        Estimated cost in USD.
    """
    pricing = lookup_pricing(model_spec)
    return (
        input_tokens * pricing.input_cost_per_token
        + output_tokens * pricing.output_cost_per_token
    )


def is_local_model(model_spec: str) -> bool:
    """Check whether a model spec uses a local provider.

    Local providers (Ollama, LM Studio, fake) have zero cost and
    no rate limits.

    Parameters
    ----------
    model_spec : str
        Full model spec.

    Returns
    -------
    bool
        ``True`` if the model is local (free).
    """
    return (
        model_spec.startswith("ollama/")
        or model_spec.startswith("lstudio/")
        or model_spec.startswith("fake/")
    )