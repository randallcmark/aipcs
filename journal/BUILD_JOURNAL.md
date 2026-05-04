# AIPCS Build Journal

> **Project:** Agent-Instantiated Persistent Context Services
> **Author:** Randall Mark
> **Started:** May 2026
> **Purpose:** Running record of decisions, learnings, and observations during the reference implementation. This is the raw material for the arXiv paper's implementation and evaluation sections.

---

## How to use this journal

Add an entry every time you:
- Make a non-obvious architectural decision
- Hit a problem you didn't anticipate
- Discover something interesting about how agents interact with the pattern
- Change your mind about something in the spec
- Observe a behaviour that confirms or challenges a design principle
- Complete a milestone

Be honest. Surprises and failures are more valuable than confirmations. The paper is stronger for them.

Each entry follows the template below. Entries are appended chronologically — do not edit past entries, add new ones instead.

---

## Entries

---

### Entry 001 — 2026-05-04

**Type:** Milestone

**Summary:** Initial invention disclosure and pattern specification published to GitHub.

**Context:**
AIPCS emerged from Application Tracker's MCP architecture design. The pattern was recognised while solving the API access friction problem for job seekers — users who hold consumer AI subscriptions but cannot afford separate developer API keys.

Two documents published:
- `AIPCS_Invention_Disclosure_v2.docx` — timestamped novelty claims
- `AIPCS_Pattern_Specification_v0.1.docx` — implementation-agnostic pattern spec

**Key decisions made:**
- Attribution via arXiv preprint, not commercial restriction
- CC BY 4.0 for documents, MIT for code
- Application Tracker as the reference implementation proving ground
- OAuth 2.0 + DCR as the consumer access model (not API keys)

**Open questions at this point:**
- CLI vs sidecar vs skill — how does the agent trigger instantiation?
- Schema versioning format — what travels with the service?
- Service registry — how does the agent discover what memory already exists?

**Paper notes:**
The irony of manually journalling AIPCS's own development — without AIPCS — is noted and should appear in the paper introduction. It is a concrete illustration of the pattern's value.

---

<!-- COPY THIS BLOCK FOR EACH NEW ENTRY -->
<!--
### Entry NNN — YYYY-MM-DD

**Type:** Decision | Problem | Observation | Milestone | Spec Change | Surprise

**Summary:** One sentence.

**Context:**
What were you working on? What led to this entry?

**Detail:**
The full description. Be specific. Include code snippets, diagrams, or schema fragments if useful.

**Decision made / Problem encountered / Observation:**
The specific thing worth recording.

**Alternatives considered:**
What else did you think about? Why did you reject it?

**Implications:**
What does this change or affect? Does it update the spec?

**Paper notes:**
Would this appear in the paper? Which section? What does it illustrate?

**Open questions:**
Anything this raises that isn't yet resolved.

-->

---

## Decision Log

A compact summary of all significant decisions, updated as entries are added.
Use this for quick orientation when resuming work after a break.

| # | Date | Decision | Rationale | Entry |
|---|------|----------|-----------|-------|
| D001 | 2026-05-04 | Attribution via arXiv, not patent | Open contribution goal | 001 |
| D002 | 2026-05-04 | OAuth 2.0 + DCR as consumer access model | Reduce API key friction | 001 |
| D003 | 2026-05-04 | Application Tracker as reference implementation | Already building it; proven ground | 001 |

---

## Spec Change Log

Record every time a build decision causes a change to the pattern specification.

| # | Date | Spec Section | Change | Reason | Entry |
|---|------|-------------|--------|--------|-------|
| S001 | — | — | — | — | — |

---

## Open Questions

Running list of unresolved questions. Close them with a decision log entry when resolved.

| # | Question | Raised | Resolved | Decision |
|---|----------|--------|----------|----------|
| Q001 | CLI vs sidecar vs skill — how does the agent trigger instantiation? | 001 | — | — |
| Q002 | Schema versioning format — what travels with the service manifest? | 001 | — | — |
| Q003 | Service registry — how does the agent discover existing memory? | 001 | — | — |
| Q004 | Multi-agent access — locking model when multiple clients hit same service? | 001 | — | — |
| Q005 | Schema conflict resolution — what if agent proposes conflicting evolution? | 001 | — | — |
| Q006 | Portability — export/import of schema + data between deployments? | 001 | — | — |

---

## Milestone Tracker

| # | Milestone | Target | Completed | Notes |
|---|-----------|--------|-----------|-------|
| M001 | Invention disclosure published | 2026-05-04 | ✅ 2026-05-04 | |
| M002 | Pattern spec v0.1 published | 2026-05-04 | ✅ 2026-05-04 | |
| M003 | Public GitHub repo live | 2026-05-04 | ✅ 2026-05-04 | |
| M004 | v1 technical design complete | — | — | |
| M005 | AIPCS sidecar prototype running | — | — | |
| M006 | OAuth/DCR foundation implemented | — | — | |
| M007 | First MCP tool registered by agent | — | — | |
| M008 | End-to-end flow validated in App Tracker | — | — | |
| M009 | Framework extracted from app-specific code | — | — | |
| M010 | arXiv preprint submitted | — | — | |

---

## Paper Sections — Running Notes

Use this to accumulate raw material for each paper section as you build.
Copy useful observations from entries into the relevant section below.

### Abstract (draft when close to done)

*Not yet drafted.*

### 1. Introduction

- The statelessness problem is well known but solutions remain developer-defined
- AIPCS inverts the relationship: agent as architect, not consumer of pre-designed schema
- Motivated by a concrete application: career management for job seekers
- The irony of building AIPCS without AIPCS — illustrates the pattern's own value proposition
- Consumer access equity: DCR as a design constraint, not an afterthought

### 2. Background and Related Work

*Captured in invention disclosure. Refine during write-up.*

Key works to cite:
- MemFabric (MrBoor, 2025)
- PISA (2024)
- Nemori (2025)
- MemGPT / Letta
- mcp-memory-service
- Hindsight (Vectorize, 2026)
- SchemaAgent (2025)
- MCP specification (Anthropic)
- RFC 7591 — OAuth 2.0 Dynamic Client Registration

### 3. The AIPCS Pattern

*Captured in pattern specification. Distil to paper length during write-up.*

### 4. Reference Implementation

*To be populated during build. Record:*
- Architecture diagram
- Key technology choices and why
- How the agent triggers instantiation
- Schema design examples (career domain)
- Tool taxonomy examples
- OAuth/DCR implementation notes
- Docker Compose structure

### 5. Evaluation

*To be populated during build. Record:*
- What workflows became possible that weren't before?
- What was the latency cost of schema design vs a pre-defined schema?
- How many tokens does the schema design step consume?
- How did the agent handle schema evolution in practice?
- What prompt patterns worked best for triggering recognition?
- What failed or surprised you?

### 6. Discussion

*To be populated. Seed questions:*
- How general is the pattern really? Where does it break down?
- What are the security implications of agent-designed schemas?
- How does AIPCS interact with model capability — does it get better as models improve?
- What would a mature AIPCS ecosystem look like?

### 7. Conclusion

*Draft when rest is complete.*

---

*This journal is the memory of the build. Write in it as if explaining to a colleague who will pick up the project after you. Future you will thank present you.*
