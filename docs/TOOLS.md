# Tools Matrix & Security Architecture (Model Context Protocol)

This document provides a comprehensive catalog of all tools exposed via GigBid Model Context Protocol (MCP) servers, their permission boundaries, safety annotations, and third-party trust rationale.

---

## 1. Tool Directory & Authorization Matrix

| MCP Server | Tool Name | Allowed Agent Roles | Input Schema | Output Schema | Annotations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `portfolio` | `search_evidence` | Matcher, Writer, Verifier, Critic | `{requirement: str, k: int, filters: dict}` | `List[EvidenceItem]` | `readOnlyHint: true` |
| `portfolio` | `get_case_study` | Matcher, Writer, Verifier, Critic | `{id: str}` | `CaseStudyDetail` | `readOnlyHint: true` |
| `portfolio` | `list_skills` | Matcher | `{persona: str}` | `List[str]` | `readOnlyHint: true` |
| `marketplace`| `search_jobs` | Scout | `{query: str, category: str, limit: int}` | `List[JobPosting]` | `readOnlyHint: true` |
| `marketplace`| `get_job` | Scout, Risk, Pricing | `{job_id: str}` | `JobPosting` | `readOnlyHint: true` |
| `marketplace`| `get_client_history`| Risk, Pricing | `{client_id: str}` | `ClientProfile` | `readOnlyHint: true` |
| `marketplace`| `get_connects_balance`| Scout, Pricing | `{freelancer_id: str}` | `ConnectsBalance` | `readOnlyHint: true` |
| `marketplace`| `list_messages` | Client Liaison | `{thread_id: str}` | `List[Message]` | `readOnlyHint: true` |
| `marketplace`| `create_proposal_draft`| Writer, Human Approver | `ProposalDraftInput` | `DraftRecord` | `readOnlyHint: false, idempotentHint: true` |
| `marketplace`| `submit_proposal` | Human Approver / System Bridge | `SubmitProposalInput` | `SubmissionReceipt` | `destructiveHint: true, idempotentHint: true` |
| `marketplace`| `send_message` | Client Liaison | `SendMessageInput` | `MessageReceipt` | `idempotentHint: true` |
| `workspace` | `get_free_calendar_slots`| Client Liaison | `{days_ahead: int, duration: int}` | `List[FreeSlot]` | `readOnlyHint: true` |
| `workspace` | `create_tentative_interview_hold`| Client Liaison | `TentativeHoldInput` | `HoldRecord` | `idempotentHint: true` |
| `workspace` | `create_email_draft`| Client Liaison | `EmailDraftInput` | `EmailDraftRecord` | `idempotentHint: true` |

---

## 2. Invariant & Agent Discipline Enforcement
1. **Zero Direct Access (Rule 4):** No LangGraph node or agent may import `gigsim`, SQLite, or local files directly. All reads/writes traverse `agent/mcp_client.py`.
2. **Strict Allowlists:** Each agent role is hardcoded to a minimal subset of tools. For example, `Job Analyst` and `Compliance Guard` have an empty toolset (`set()`), preventing hallucinations or unauthorized data exfiltration.
3. **Idempotency & Destructive Gates:** `submit_proposal` carries `destructiveHint: true` and requires a non-empty `idempotency_key`. Double invocations return cached responses without consuming platform Connects.

---

## 3. Third-Party Trust Rationale

### Upwork Live MCP Server (`https://mcp.upwork.com/mcp`)
- **Trust Boundary:** Official Upwork enterprise MCP gateway.
- **Authentication:** OAuth 2.1 authorization code flow with PKCE and refresh token rotation.
- **Safety Mechanism:** GigBid operates with `force_draft_only: true` by default. Any live proposal submission is intercepted and converted to a pending draft on Upwork unless the human user explicitly approves the submission in the Proposal Studio.
- **Token Security:** Tokens are stored using AES-256 Fernet symmetric encryption with environment-provided keys (`OAUTH_FERNET_KEY`).

### GitHub MCP Server (`https://api.github.com`)
- **Trust Boundary:** Used strictly for read-only repository synchronization and code snippet extraction.
- **Permissions:** Scoped to read-only `public_repo` permissions. Never requests write or administrative tokens.

