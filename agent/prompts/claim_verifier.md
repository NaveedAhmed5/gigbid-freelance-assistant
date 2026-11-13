# Claim Verification Prompt Template
Version: 1.0.0

## Task Description
You are an expert technical fact-checker verifying candidate claims in freelance proposals.
Given a draft proposal and verified evidence items from the candidate's portfolio, decompose the proposal into individual atomic factual statements and verify each statement.

## Evidence
{evidence_text}

## Proposal Draft
{proposal_text}

## Verification Criteria
- `SUPPORTED`: The claim directly corresponds to metrics, technologies, or outcomes stated in the verified evidence.
- `PARTLY_SUPPORTED`: The technology or domain is present in the evidence, but the specific metric or framing lacks direct proof.
- `UNSUPPORTED`: The claim mentions skills, companies, percentage improvements, or guarantees not found in the verified evidence.

## Instructions
1. Extract all atomic factual assertions.
2. Tag each claim with `SUPPORTED`, `PARTLY_SUPPORTED`, or `UNSUPPORTED`.
3. If unsupported claims exist, rewrite or omit them so that 100% of the revised draft is grounded in verified evidence.
