"""Prompt loader and Rule 2 verification utility."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent

REQUIRED_PROMPT_FILES = [
    "scout_filter.md",
    "job_analyst.md",
    "risk_assessor.md",
    "fit_matcher.md",
    "pricing_strategist.md",
    "proposal_writer.md",
    "claim_verifier.md",
    "critic.md",
    "compliance_guard.md",
    "client_liaison.md",
    "judge_rubric.md",
]


def load_prompt(prompt_filename: str) -> str:
    """Load a versioned markdown prompt template from agent/prompts/."""
    path = PROMPTS_DIR / prompt_filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt template '{prompt_filename}' not found in {PROMPTS_DIR}")
    return path.read_text(encoding="utf-8")


def verify_no_inline_prompts():
    """CI Check ensuring all required prompt files exist and are populated."""
    missing = []
    for f in REQUIRED_PROMPT_FILES:
        p = PROMPTS_DIR / f
        if not p.exists() or len(p.read_text(encoding="utf-8").strip()) < 20:
            missing.append(f)
    if missing:
        raise AssertionError(f"Rule 2 violation: Missing or empty prompt files: {missing}")
    return True
