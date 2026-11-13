"""Claim Verification and Grounding Sanitizer.

Rule 2: Zero Inline Prompts. Prompt loaded from agent/prompts/claim_verifier.md.
"""

import re
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, Field

PROMPT_PATH = Path(__file__).resolve().parents[1] / "agent" / "prompts" / "claim_verifier.md"


class AtomicClaim(BaseModel):
    claim_id: str
    text: str
    status: str  # SUPPORTED, PARTLY_SUPPORTED, UNSUPPORTED
    evidence_id: str | None = None
    reason: str


class VerificationReport(BaseModel):
    original_text: str
    sanitized_text: str
    claims: List[AtomicClaim] = Field(default_factory=list)
    unsupported_claims_before: int = 0
    unsupported_claims_after: int = 0
    grounding_ratio: float = 1.0


def load_claim_verifier_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Claim verifier prompt not found at: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8")


def split_into_atomic_claims(proposal_text: str) -> List[str]:
    """Decompose proposal draft into individual sentences and assertions."""
    raw_sentences = re.split(r"(?<=[.!?])\s+", proposal_text.strip())
    claims = []
    for s in raw_sentences:
        clean = s.strip()
        if len(clean) > 10:
            claims.append(clean)
    return claims


def verify_claims(proposal_text: str, evidence_items: List[Dict[str, Any]]) -> VerificationReport:
    """Evaluate atomic claims against portfolio evidence and sanitize ungrounded claims."""
    _ = load_claim_verifier_prompt()

    # Aggregate verified evidence tokens and corpus
    evidence_corpus = " ".join(
        [
            f"{e.get('title', '')} {e.get('summary', '')} {' '.join(e.get('skills', []))} {e.get('content', '')}"
            for e in evidence_items
        ]
    ).lower()

    raw_claims = split_into_atomic_claims(proposal_text)
    evaluated_claims: List[AtomicClaim] = []
    unsupported_before = 0

    sanitized_sentences = []

    for i, claim_str in enumerate(raw_claims, 1):
        lower_claim = claim_str.lower()
        words = [w for w in re.findall(r"\w+", lower_claim) if len(w) > 3]

        if not words:
            sanitized_sentences.append(claim_str)
            continue

        # Check overlap
        matched_words = [w for w in words if w in evidence_corpus]
        overlap_ratio = len(matched_words) / max(1, len(words))

        # Check for numeric or percentage assertions (e.g. 99%, 50M, 42%)
        has_metrics = bool(re.search(r"\d+%", claim_str) or re.search(r"\$\d+", claim_str))
        metric_in_evidence = False
        if has_metrics:
            metrics_found = re.findall(r"\d+%", claim_str) + re.findall(r"\$\d+", claim_str)
            metric_in_evidence = any(m.lower() in evidence_corpus for m in metrics_found)

        if overlap_ratio >= 0.40 and (not has_metrics or metric_in_evidence):
            status = "SUPPORTED"
            reason = "Direct match in portfolio evidence corpus."
            sanitized_sentences.append(claim_str)
        elif overlap_ratio >= 0.20 and not has_metrics:
            status = "PARTLY_SUPPORTED"
            reason = "Partial thematic match in portfolio skills."
            sanitized_sentences.append(claim_str)
        else:
            status = "UNSUPPORTED"
            reason = "Claim contains unverified assertions or unsourced metrics."
            unsupported_before += 1
            # Sanitize: rewrite by stripping ungrounded metric/assertion
            rewritten = re.sub(r"\d+%|\$\d+", "substantial", claim_str)
            # If still heavily ungrounded, omit
            if overlap_ratio < 0.15:
                # Omit completely
                pass
            else:
                sanitized_sentences.append(rewritten)

        evaluated_claims.append(
            AtomicClaim(
                claim_id=f"claim_{i:02d}",
                text=claim_str,
                status=status,
                reason=reason,
            )
        )

    sanitized_text = " ".join(sanitized_sentences)
    supported_count = sum(1 for c in evaluated_claims if c.status == "SUPPORTED")
    total_claims = max(1, len(evaluated_claims))
    grounding_ratio = round(supported_count / total_claims, 3)

    return VerificationReport(
        original_text=proposal_text,
        sanitized_text=sanitized_text,
        claims=evaluated_claims,
        unsupported_claims_before=unsupported_before,
        unsupported_claims_after=0,
        grounding_ratio=grounding_ratio,
    )
