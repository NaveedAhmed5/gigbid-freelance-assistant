from rag.verify import split_into_atomic_claims, verify_claims


def test_split_into_atomic_claims():
    text = (
        "I have 8 years of enterprise experience with PyTorch and LangGraph. "
        "We achieved a 42% latency reduction in production. "
        "Would you like to review the architecture?"
    )
    claims = split_into_atomic_claims(text)
    assert len(claims) == 3


def test_verify_claims_grounding_and_sanitization():
    evidence = [
        {
            "id": "cs_01",
            "title": "High-Throughput Enterprise Ingestion Engine",
            "summary": "Engineered scalable pipeline with sub-50ms latency.",
            "skills": ["Python", "PyTorch", "FastAPI"],
            "metric_improvement_pct": 42.0,
            "content": "Delivered a 42% measurable efficiency improvement in production.",
        }
    ]

    proposal_with_hallucinations = (
        "I am an expert in Python and PyTorch. "
        "In our recent deployment we achieved a 42% measurable efficiency improvement in production. "
        "I also personally managed a $100M budget at NASA and guarantee 100% bug-free delivery."
    )

    report = verify_claims(proposal_with_hallucinations, evidence)

    assert len(report.claims) == 3
    # First two claims should be SUPPORTED / PARTLY_SUPPORTED
    assert report.claims[0].status in ("SUPPORTED", "PARTLY_SUPPORTED")
    assert report.claims[1].status == "SUPPORTED"
    # Third claim ($100M budget at NASA) must be tagged UNSUPPORTED
    assert report.claims[2].status == "UNSUPPORTED"
    assert report.unsupported_claims_before == 1
    assert report.unsupported_claims_after == 0
    # Sanitized text must not contain the ungrounded $100M claim
    assert "$100M" not in report.sanitized_text
    assert "NASA" not in report.sanitized_text
