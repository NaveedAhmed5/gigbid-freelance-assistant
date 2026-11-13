"""GigSim Simulator In-Memory State & Client Simulation Engine."""

import random
import uuid
from typing import Dict, List, Optional, Tuple

from gigsim.models import (
    ClientEvaluationResult,
    ClientProfile,
    ConnectsBalance,
    JobPosting,
    Message,
    ProposalSubmission,
)

GENERIC_OPENINGS = [
    "dear hiring manager",
    "i am writing to apply",
    "i am writing to express",
    "i am the perfect fit",
    "i have read your job post with great interest",
    "to whom it may concern",
    "hello sir/madam",
]


class GigSimEngine:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.clients: Dict[str, ClientProfile] = {}
        self.jobs: Dict[str, JobPosting] = {}
        self.proposals: Dict[str, ProposalSubmission] = {}
        self.messages: Dict[str, List[Message]] = {}  # thread_id -> messages
        self.connects: Dict[str, ConnectsBalance] = {}
        self.rate_limits: Dict[str, int] = {}

    def reset(self):
        self.clients.clear()
        self.jobs.clear()
        self.proposals.clear()
        self.messages.clear()
        self.connects.clear()
        self.rate_limits.clear()

    def get_or_create_connects(self, freelancer_id: str) -> ConnectsBalance:
        if freelancer_id not in self.connects:
            self.connects[freelancer_id] = ConnectsBalance(
                freelancer_id=freelancer_id, balance=150
            )
        return self.connects[freelancer_id]

    def add_job(self, job: JobPosting):
        self.jobs[job.id] = job
        if job.client:
            self.clients[job.client.id] = job.client

    def get_job(self, job_id: str) -> Optional[JobPosting]:
        job = self.jobs.get(job_id)
        if job and job.client_id in self.clients:
            job.client = self.clients[job.client_id]
        return job

    def search_jobs(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        skills: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[JobPosting]:
        results = list(self.jobs.values())
        if category:
            results = [j for j in results if j.category.lower() == category.lower()]
        if skills:
            skill_set = {s.lower() for s in skills}
            results = [
                j for j in results if any(s.lower() in skill_set for s in j.skills)
            ]
        if query:
            q = query.lower()
            results = [
                j
                for j in results
                if q in j.title.lower() or q in j.description.lower()
            ]
        # Attach client profiles
        for j in results:
            if j.client_id in self.clients:
                j.client = self.clients[j.client_id]
        return results[offset : offset + limit]

    def evaluate_proposal(
        self, proposal: ProposalSubmission
    ) -> ClientEvaluationResult:
        """Deterministic simulated client evaluation of a proposal submission."""
        job = self.jobs.get(proposal.job_id)
        if not job:
            return ClientEvaluationResult(
                proposal_id=proposal.id,
                decision="REJECTED",
                reasons=["Job no longer exists."],
                match_score=0.0,
            )

        client = self.clients.get(job.client_id)
        reasons: List[str] = []
        score = 0.50  # Base prior

        # Check for generic openings penalty
        lower_cover = proposal.cover_letter.lower()
        has_generic = any(gen in lower_cover[:120] for gen in GENERIC_OPENINGS)
        if has_generic:
            if client and client.dislike_generic_openings:
                score -= 0.35
                reasons.append("Client penalized generic cover letter opening.")
            else:
                score -= 0.15

        # Check budget fit
        if job.budget_usd and job.budget_usd > 0:
            ratio = proposal.bid_amount_usd / job.budget_usd
            if ratio > 1.25:
                score -= 0.25
                reasons.append(f"Bid exceeds client budget (${proposal.bid_amount_usd} vs ${job.budget_usd}).")
            elif 0.8 <= ratio <= 1.05:
                score += 0.15
                reasons.append("Bid aligns closely with client target budget.")
            elif ratio < 0.5:
                score -= 0.10
                reasons.append("Suspiciously low bid raises quality concerns.")

        # Check skill mentions
        req_skills = job.skills
        if req_skills:
            matched_skills = [
                s for s in req_skills if s.lower() in lower_cover
            ]
            coverage = len(matched_skills) / len(req_skills)
            score += coverage * 0.30
            if coverage >= 0.7:
                reasons.append(f"Strong skill alignment ({len(matched_skills)}/{len(req_skills)} skills addressed).")
            else:
                reasons.append(f"Weak skill alignment ({len(matched_skills)}/{len(req_skills)} skills addressed).")

        # Check for evidence markers (metrics, numbers, percentages, architectures)
        has_evidence_markers = any(
            char.isdigit() or sym in lower_cover for sym in ["%", "$", "latency", "benchmark", "accuracy", "roi"]
            for char in lower_cover
        )
        if has_evidence_markers:
            score += 0.15
            reasons.append("Proposal cites concrete metrics and historical evidence.")

        # Screening questions completeness
        if job.screening_questions:
            answered = len(proposal.screening_answers)
            if answered >= len(job.screening_questions):
                score += 0.10
            else:
                score -= 0.20
                reasons.append("Screening questions were skipped or incomplete.")

        # Cap score between 0.0 and 1.0
        final_score = max(0.0, min(1.0, score))

        # Outcome decision mapping
        if final_score >= 0.82:
            decision = "HIRED"
            reply = "Hi, your proposal was exceptionally well tailored. We would like to move forward and extend an offer!"
        elif final_score >= 0.68:
            decision = "INTERVIEW"
            reply = "Hi! Thanks for the thoughtful proposal. Can we hop on a quick 15-minute call this week to align on technical details?"
        elif final_score >= 0.50:
            decision = "REPLIED"
            reply = f"Hello, thanks for applying. Could you share a bit more detail on your experience with {job.skills[0] if job.skills else 'this tech'}?"
        elif final_score >= 0.35:
            decision = "VIEWED"
            reply = None
        else:
            decision = "REJECTED"
            reply = None

        return ClientEvaluationResult(
            proposal_id=proposal.id,
            decision=decision,
            reasons=reasons,
            match_score=round(final_score, 3),
            simulated_reply=reply,
        )

    def submit_proposal(
        self, proposal: ProposalSubmission
    ) -> Tuple[ProposalSubmission, ClientEvaluationResult]:
        """Submit a proposal, deduct Connects, evaluate with client engine, and record outcome."""
        job = self.jobs.get(proposal.job_id)
        if not job:
            raise ValueError(f"Job {proposal.job_id} not found.")

        # Deduct connects
        connects_needed = job.connects_required
        balance = self.get_or_create_connects(proposal.freelancer_id)
        if balance.balance < connects_needed:
            raise ValueError(
                f"Insufficient Connects: required {connects_needed}, available {balance.balance}."
            )

        balance.balance -= connects_needed
        proposal.connects_spent = connects_needed

        # Evaluate with client
        eval_result = self.evaluate_proposal(proposal)
        proposal.status = eval_result.decision
        proposal.client_feedback = " | ".join(eval_result.reasons)

        self.proposals[proposal.id] = proposal

        # If client replied or invited to interview, create initial message thread
        if eval_result.simulated_reply:
            thread_id = f"thread_{job.id}_{proposal.freelancer_id}"
            msg = Message(
                id=f"msg_{uuid.uuid4().hex[:8]}",
                thread_id=thread_id,
                sender_id=job.client_id,
                recipient_id=proposal.freelancer_id,
                text=eval_result.simulated_reply,
            )
            self.messages.setdefault(thread_id, []).append(msg)

        return proposal, eval_result
