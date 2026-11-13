import json
from pathlib import Path

from gigsim.engine import GigSimEngine
from gigsim.models import ClientProfile, JobPosting, ProposalSubmission

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
PERSONAS = ["ai_ml_engineer", "fullstack_web_dev", "data_analyst"]


def test_persona_corpora_generation():
    """Verify that all 3 personas have complete, valid corpora."""
    for p in PERSONAS:
        p_dir = DATA_DIR / "personas" / p
        assert (p_dir / "cv.md").exists(), f"Missing CV for {p}"
        assert (p_dir / "case_studies.json").exists(), f"Missing case studies for {p}"
        assert (p_dir / "reviews.json").exists(), f"Missing reviews for {p}"
        assert (p_dir / "past_proposals.json").exists(), f"Missing proposals for {p}"

        # Check case studies count
        case_studies = json.loads((p_dir / "case_studies.json").read_text(encoding="utf-8"))
        assert len(case_studies) >= 15, f"{p} has fewer than 15 case studies"

        # Check past proposals count and outcome labels
        proposals = json.loads((p_dir / "past_proposals.json").read_text(encoding="utf-8"))
        assert len(proposals) == 150, f"{p} proposals count != 150"
        outcomes = {item["outcome"] for item in proposals}
        assert outcomes == {"won", "replied", "ignored"}


def test_policy_pack():
    """Verify marketplace policy pack exists and specifies core constraints."""
    policy_file = DATA_DIR / "policy_pack" / "marketplace_rules.md"
    assert policy_file.exists()
    content = policy_file.read_text(encoding="utf-8")
    assert "Contact Pre-Contract Prohibited" in content
    assert "Off-Platform Payment Strictly Banned" in content
    assert "Zero Tolerance for Fabricated Experience" in content


def test_job_stream_and_dev_set():
    """Verify job stream (~1500 jobs) and dev evaluation set."""
    job_stream_file = DATA_DIR / "processed" / "job_stream.json"
    assert job_stream_file.exists()
    jobs = json.loads(job_stream_file.read_text(encoding="utf-8"))
    assert len(jobs) >= 1400

    has_scam = any(j.get("is_scam") for j in jobs)
    has_injection = any(j.get("has_injection") for j in jobs)
    assert has_scam, "Job stream missing scam jobs"
    assert has_injection, "Job stream missing injection jobs"

    dev_set_file = ROOT_DIR / "evals" / "datasets" / "dev_set.json"
    assert dev_set_file.exists()
    dev_set = json.loads(dev_set_file.read_text(encoding="utf-8"))
    assert len(dev_set) >= 50
    for item in dev_set:
        assert "gold_decision" in item
        assert "fair_price_band" in item


def test_gigsim_engine_deterministic_flow():
    """Verify GigSim engine handles jobs, connects, and deterministic client responses."""
    engine = GigSimEngine(seed=42)
    engine.reset()

    client = ClientProfile(
        id="client_test_01",
        name="Acme Health AI",
        industry="Healthcare",
        country="USA",
        total_spend_usd=50000.0,
        hire_rate=0.85,
        jobs_posted=12,
        open_jobs=1,
        rating=4.95,
        payment_verified=True,
        must_have_skills=["Python", "PyTorch", "RAG Systems"],
        budget_ceiling=4000.0,
        dislike_generic_openings=True,
    )
    job = JobPosting(
        id="job_test_01",
        title="Build Enterprise RAG Pipeline in PyTorch",
        description="Looking for an engineer with deep PyTorch and RAG Systems skills.",
        client_id=client.id,
        client=client,
        category="AI/ML",
        subcategory="Healthcare",
        skills=["Python", "PyTorch", "RAG Systems"],
        job_type="fixed_price",
        budget_usd=3500.0,
        duration="1 to 3 months",
        experience_level="Expert",
        connects_required=8,
        posted_at="2026-11-13T10:00:00Z",
    )
    engine.add_job(job)

    # Check search
    results = engine.search_jobs(query="PyTorch")
    assert len(results) == 1
    assert results[0].id == "job_test_01"

    # Freelancer balance
    balance = engine.get_or_create_connects("freelancer_alex")
    initial_balance = balance.balance

    # Test generic opening penalty
    generic_proposal = ProposalSubmission(
        id="prop_gen_01",
        job_id="job_test_01",
        freelancer_id="freelancer_alex",
        cover_letter="Dear Hiring Manager, I am the perfect fit for your job. I have 10 years experience.",
        bid_amount_usd=3500.0,
        estimated_duration="1 month",
    )
    p_gen, res_gen = engine.submit_proposal(generic_proposal)
    assert p_gen.connects_spent == 8
    assert engine.get_or_create_connects("freelancer_alex").balance == initial_balance - 8
    assert res_gen.decision in ("REJECTED", "VIEWED")

    # Test tailored winning proposal with proof points and skills
    tailored_proposal = ProposalSubmission(
        id="prop_tailored_01",
        job_id="job_test_01",
        freelancer_id="freelancer_alex",
        cover_letter=(
            "Hi team — your objective for PyTorch enterprise RAG directly mirrors a recent deployment "
            "where we engineered a high-throughput RAG Systems pipeline with sub-50ms latency and 94% recall. "
            "Our benchmark demonstrated a 42% latency reduction. Would you like to review the technical design?"
        ),
        bid_amount_usd=3400.0,
        estimated_duration="1 month",
    )
    p_tailored, res_tailored = engine.submit_proposal(tailored_proposal)
    assert res_tailored.decision in ("HIRED", "INTERVIEW", "REPLIED")
    assert res_tailored.match_score > res_gen.match_score
