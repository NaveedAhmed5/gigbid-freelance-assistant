# LLM Proposal Judge Rubric & Calibration Standard
Version: 1.0.0

## Evaluation Dimensions (Scored 1.0 – 5.0)

### 1. Grounding & Truthfulness (Weight: 35%)
- 5.0: Every assertion, metric, and skill claim is backed by cited evidence. Zero hallucinations.
- 3.0: Moderate alignment; general claims match, but minor unsourced metrics exist.
- 1.0: Severe ungrounded claims, fabricated experience, or unrealistic guarantees.

### 2. Client Focus & Relevance (Weight: 25%)
- 5.0: Opening hook immediately addresses the client's core pain point. Highly tailored technical proposal.
- 3.0: Generic pleasantries before reaching the technical substance.
- 1.0: Boilerplate copy-paste template ("Dear Hiring Manager...").

### 3. Proof Points & Specificity (Weight: 25%)
- 5.0: Cites concrete quantified outcomes (e.g. "42% latency reduction", "sub-50ms latency").
- 3.0: Vague descriptions ("optimized system speed").
- 1.0: Pure buzzwords without architectural or quantifiable evidence.

### 4. Marketplace Policy Compliance (Weight: 15%)
- 5.0: 100% compliant with Upwork Nov 2 policy guidelines. No off-platform contact or payment requests.
- 1.0: Proposes off-platform contact (Telegram, WhatsApp, email) or payment methods.

## Output Standard
Return an overall weighted score between 1.0 and 5.0, dimension breakdown, and classification:
- `EXCELLENT` (Score >= 4.2)
- `GOOD` (3.5 <= Score < 4.2)
- `ADEQUATE` (2.8 <= Score < 3.5)
- `POOR` (Score < 2.8)

