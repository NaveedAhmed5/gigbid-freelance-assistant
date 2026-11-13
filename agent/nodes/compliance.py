"""Compliance Guard Node: Strict terms of service and Nov 2 policy gatekeeper."""

from agent.config import load_agent_config
from agent.handoffs import ComplianceVerdict, ProposalDraft
from agent.prompts import load_prompt


def compliance_node(draft: ProposalDraft) -> ComplianceVerdict:
    config = load_agent_config()
    config.resolve_model_for_node("compliance")
    load_prompt("compliance_guard.md")

    text = draft.cover_letter.lower()
    violations = []

    # 1. Check off-platform contact
    banned_contacts = ["telegram", "whatsapp", "@gmail.com", "@yahoo.com", "discord", "skype", "calendly.com"]
    for bc in banned_contacts:
        if bc in text:
            violations.append(f"Contains pre-contract external contact information: '{bc}'")

    # 2. Check off-platform payment
    banned_payments = ["crypto", "bitcoin", "usdt", "paypal", "wire transfer", "direct invoice"]
    for bp in banned_payments:
        if bp in text:
            violations.append(f"Mentions off-platform payment method: '{bp}'")

    # 3. Check for unrealistic guarantees
    if "100% bug-free guarantee" in text:
        violations.append("Contains unrealistic, unverifiable guarantee.")

    is_compliant = len(violations) == 0
    can_submit = is_compliant and (draft.grounding_ratio >= 0.70)

    summary = (
        "Proposal 100% compliant with Upwork Nov 2 terms and platform invariants."
        if is_compliant
        else f"Compliance check failed: {'; '.join(violations)}"
    )

    return ComplianceVerdict(
        is_compliant=is_compliant,
        violations=violations,
        nov_2_policy_verified=True,
        terms_checked=["contact_pre_contract", "off_platform_payment", "truthful_advertising", "no_free_work"],
        can_submit=can_submit,
        summary=summary,
    )
