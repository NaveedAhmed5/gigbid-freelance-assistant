"""Memory Promotion Rules for GigBid.

Enforces strict criteria before promoting data into Style Memory or Outcome Memory.
Never stores raw tool output or unverified prose.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class MemoryCandidate(BaseModel):
    category: str  # "style" or "outcome"
    source_id: str
    original_text: str
    edited_text: Optional[str] = None
    outcome: Optional[str] = None  # "won", "replied", "rejected"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PromotionDecision(BaseModel):
    promoted: bool
    memory_type: str
    promoted_key: Optional[str] = None
    promoted_content: Optional[str] = None
    reason: str


def evaluate_style_promotion(candidate: MemoryCandidate) -> PromotionDecision:
    """Evaluate whether a human edit diff should be promoted to Style Memory."""
    if candidate.category != "style" or not candidate.edited_text:
        return PromotionDecision(
            promoted=False,
            memory_type="style",
            reason="Not a valid style candidate or missing edited text.",
        )

    orig = candidate.original_text.strip()
    edit = candidate.edited_text.strip()

    if orig == edit:
        return PromotionDecision(
            promoted=False,
            memory_type="style",
            reason="No diff between original and edited draft.",
        )

    # Check for meaningful stylistic evolution (e.g., conciseness, removing filler)
    orig_words = orig.split()
    edit_words = edit.split()

    if len(edit_words) < len(orig_words) * 0.90:
        rule_desc = (
            "Human editor demonstrated preference for high conciseness; omit introductory fluff."
        )
    elif any(term in edit.lower() for term in ["architecture", "benchmark", "sub-50ms", "metrics"]):
        rule_desc = "Human editor emphasized quantitative architectural proof points."
    else:
        rule_desc = f"Human editor refined phrasing: '{edit[:60]}...'"

    return PromotionDecision(
        promoted=True,
        memory_type="style",
        promoted_key=f"style_{candidate.source_id}",
        promoted_content=rule_desc,
        reason="Human edit met validated style preference threshold.",
    )


def evaluate_outcome_promotion(candidate: MemoryCandidate) -> PromotionDecision:
    """Evaluate whether a proposal result should be promoted to Outcome Memory."""
    if candidate.category != "outcome":
        return PromotionDecision(
            promoted=False,
            memory_type="outcome",
            reason="Candidate is not an outcome candidate.",
        )

    if candidate.outcome not in ("won", "replied"):
        return PromotionDecision(
            promoted=False,
            memory_type="outcome",
            reason=f"Outcome '{candidate.outcome}' does not meet winning criteria (requires 'won' or 'replied').",
        )

    industry = candidate.metadata.get("industry", "general")
    winning_hook = (
        candidate.original_text.split("\n\n")[0]
        if "\n\n" in candidate.original_text
        else candidate.original_text[:120]
    )

    promoted_rule = f"Winning pattern in {industry}: Hook '{winning_hook}' led to {candidate.outcome.upper()} status."

    return PromotionDecision(
        promoted=True,
        memory_type="outcome",
        promoted_key=f"outcome_{candidate.source_id}",
        promoted_content=promoted_rule,
        reason=f"Validated successful outcome '{candidate.outcome}' in {industry}.",
    )
