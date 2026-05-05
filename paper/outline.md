# AIPCS Paper Outline

**Working title:** Agent-Instantiated Persistent Context Services: A Pattern for Autonomous Domain-Adaptive Memory via MCP

**Author:** Randall Mark
**Target venue:** arXiv preprint (→ optionally HotOS / SOSP / AI systems workshop)
**Target length:** 6–10 pages (systems paper style)
**Status:** Outline — sections seeded from BUILD_JOURNAL running notes

---

## Abstract

*Draft when all other sections are complete.*

AIPCS is a pattern for autonomous, domain-adaptive memory infrastructure in which an AI agent designs its own domain-specific data schema, scaffolds a persistent queryable service around it, and registers that service as an MCP tool. Unlike prior work — which either pre-defines memory schemas or organises existing data — AIPCS makes the agent the schema architect. We present the pattern, a reference implementation in a career management platform, and an evaluation of the approach.

---

## 1. Introduction

**Key points:**
- The statelessness problem: AI tools are session-bound; structured context management is left to the user or developer
- The inversion: AIPCS flips the model — agent proposes the structure of its own memory, subject to runtime governance
- Consumer access equity: the pattern emerged from solving API key friction for job seekers (OAuth 2.0 + DCR as a design constraint, not an afterthought)
- The AIPCS irony: we built AIPCS without AIPCS — manually managing context that the pattern would structure automatically. This is the pattern's clearest illustration of its own value.
- Paper structure overview

**Claim framing note (from ADR-002, Entry 010):** The contribution statement must use the safer external framing: "AIPCS is an early pattern for governed agent-directed structured memory, where an agent can propose and evolve persistence schemas under runtime validation instead of relying solely on developer-defined memory models." Do not use "universal primitive" — not yet demonstrated. Do not lead with MCP as the primary novelty. The strongest novelty formulation (from external critique): agent recognition + agent proposal of memory structure + runtime materialisation + governed schema evolution + portable tool surface.

**From BUILD_JOURNAL:**
> "The irony of manually journalling AIPCS's own development — without AIPCS — is noted and should appear in the paper introduction."

---

## 2. Background and Related Work

**Key works to cite and contrast:**

| Work | What it does | How it differs from AIPCS |
|---|---|---|
| MemFabric (MrBoor, 2025) | LLM organises knowledge as markdown files | Flat file-based; not structured queryable schema |
| PISA (2024) | Task-oriented memory via Piaget's schema theory | Academic architecture; not MCP-native or deployable |
| Nemori (2025) | Self-organising experience memory (MAG paradigm) | Organises experience, not schema design |
| MemGPT / Letta | OS-inspired context paging; agent manages storage tiers | Pre-defined storage structure; agent manages paging, not schema |
| mcp-memory-service | Knowledge graph via MCP | Fixed developer-defined schema |
| Hindsight (Vectorize, 2026) | Semantic memory retrieval via MCP | Semantic search; developer-defined structure |
| SchemaAgent (2025) | LLM-driven schema generation for existing data | Schema generation for existing problems, not persistent memory primitive |

**Standards to cite:**
- MCP specification (Anthropic, 2024)
- RFC 7591 — OAuth 2.0 Dynamic Client Registration

---

## 3. The AIPCS Pattern

**Key points:**
- 10 core principles (P1–P10) from pattern spec — distil to paper length
- The full lifecycle: Recognition → Seed → Design → Materialise → Operate → Evolve

**Two-state lifecycle (from Entry 002 / D004, D005):**
- SEEDED: domain marker planted, schema forming, not yet deployed. First-class primitive — queryable immediately. Agent resumes domain modelling across sessions via seed inspection.
- MATERIALISED: schema deployed, tools active, queryable. Progression from hint → seed → accumulated knowledge → schema design → materialisation.
- The seed is not a placeholder — it is the pattern's earliest observable state of persistence intent.

**Compaction hook as Model B trigger (from Entry 003 / D006, reframed per D014):**
- A designed Model B trigger — connects context compaction with structured memory candidacy evaluation
- Before compacting context, the agent evaluates all active knowledge domains for AIPCS persistence candidacy
- Key insight: persistence at compaction time captures structured knowledge before compression degrades it
- Pending field validation: whether compaction is the *primary* real-world trigger in practice is an open empirical question. Do not claim "primary trigger" before evaluation data (Phase 1) supports it. Write as "a designed trigger" in the paper.

**Authority chain and governance (from Entry 009 / ADR-001):**
- The authority chain is a first-class design contribution alongside the two-state lifecycle: Agent proposes → Validator constrains → User consents → Service persists → Audit log explains
- "Agent-directed" only means something if the governance chain makes it safe. Without governance, the pattern is not distinguishable from unconstrained agent persistence.
- §3 should describe the constraint categories (structural, semantic, sensitive-data) and the consent tier model
- The governance model is part of the pattern definition — not implementation detail or future work

**Self-referential MCP-native mechanism (from Entry 004 / D007):**
- Option 3: AIPCS is an MCP server. MCP tools that create MCP tools.
- Architecturally distinctive — worth emphasising
- Options rejected: Option 1 (too weak), Option 2 (CLI friction), Option 4 (sidecar HTTP — environment-dependent)

**Schema evolution as agent act (from Entry 005 / D008):**
- Additive migrations by default; destructive require explicit confirmation
- Agent proposes, AIPCS validates and applies
- Schema manifest travels with the service — versioned, human-readable JSON
- Every migration recorded in history — the schema's audit trail

**Tool taxonomy:**
- Workflow-oriented tools, not database-oriented
- Naming convention: `domain_object_action` (e.g. `job_application_status_update` not `job_application_update`)
- Tool names maximum 60 characters; descriptions maximum 250

---

## 4. Reference Implementation

**Key points:**
- Application Tracker as the proving ground (career management for job seekers)
- Why this domain: multi-entity tracking, relational dependencies, cross-session persistence — all strong AIPCS trigger conditions

**Architecture (from technical design):**
- AIPCS Server (MCP-native) + Registry DB + Domain Services
- 8 management primitives: seed, design, materialise, evolve, list, inspect, suspend, export
- Three-tier access: Tier 1 (agent MCP tools), Tier 2 (user via agent), Tier 3 (consent-gated read-only export)
- Docker Compose: aipcs service alongside app + mcp

**Impediments and resolutions (from Entry 004 — valuable "lessons learned" material):**

| Impediment | Resolution |
|---|---|
| Dynamic tool registration not universal | Session reconnect acceptable for v1 |
| Agent must know AIPCS exists | Always-on in the stack |
| Schema quality model-dependent | Validation layer — propose, validate, revise cycle |
| No domain tools before first seed | Skill: first action is always seed |

**Schema manifest format:**
- Versioned JSON, travels with the service
- Includes: entities, relationships, indices, migration history, tool definitions, domain_class
- Full example in `docs/AIPCS_v1_Technical_Design.md`

**Authentication:**
- V1: local trust within Docker network; owner_id from application session
- V2 target: OAuth 2.0 + DCR per pattern specification and Application Tracker's MCP_OAUTH_DCR_PLAN.md

*Populate with implementation detail as build progresses (M005–M008)*

---

## 5. Evaluation

**Research Questions (from evaluation-plan.md):**

| RQ | Question |
|---|---|
| RQ1 | Recognition — does the agent reliably recognise AIPCS-appropriate situations without an explicit user prompt? |
| RQ2 | Initial Design Quality — does the first-attempt schema cover the domain adequately? |
| RQ3 | Evolution Quality — does the agent propose appropriate additive evolutions without breaking existing queries? |
| RQ4 | Retrieval and Continuity Utility — does AIPCS-backed memory produce measurably better task continuation than baselines? |
| RQ5 | Governance Effectiveness — does the constraint model prevent harmful proposals? |
| RQ6 | Runtime Portability — can an AIPCS service be exported and re-materialised in a different runtime? |

**Baselines:**
- A: Harness memory (markdown/index files — status quo; the approach this repo's own development uses)
- B: Developer-defined structured memory (isolates value of agent-directed design specifically)
- C: Minimal generic KV/document store (isolates value of schema quality)

**Evaluation phases:**
- Phase 1 (Concept Validation, M007): RQ1, RQ2 — career tracking scenario with/without hint; Baselines A and B
- Phase 2 (Governance Validation, M008): RQ3, RQ5 — multi-session lifecycle; adversarial prompting suite; audit log inspection
- Phase 3 (Portability Validation): RQ6 — export/import test in clean environment
- Phase 4 (Comparative, M009–M010): RQ4 — comparative task tests across all three baselines

**Early success criteria:** see evaluation-plan.md §Early Success Criteria (5 items)
**Early failure conditions:** see evaluation-plan.md §Early Failure Conditions (5 items — pre-committed)

Full framework: `docs/quality/evaluation-plan.md`

*Populate with results during build (M007–M010)*

---

## 6. Discussion

**Three-tier access model and transparency (from Entry 006 / D009):**
- The md-file harness paradigm provides implicit transparency but suffers from summaries-of-summaries drift
- AIPCS structured approach: data in a relational store, queryable precisely
- Medical use case: agent accumulates health context; user consents to share structured export with practitioner's AI workflow. Practitioner gets richer, more accurate context than an anecdotal interview.
- Tier 3 is consent-gated, read-only, audit-logged — privacy by design

**Taxonomy and interoperability (from Entry 007 / D010):**
- domain_class field enables future cross-agent interoperability without mandating it now
- Open registry vs curated set question (Q009)
- Domain overlap handling (Q010)
- A career management AIPCS service should be recognisable and usable by another agent in a different context

**Open questions from the build:**
- Q004: Multi-agent locking model
- Q005: Schema conflict resolution
- Q008: Seed TTL
- Q011: Tier 3 in v1 or v2?

**Governance as necessary condition (from Entry 009 / ADR-001):**
- "Agent-directed" is only a meaningful claim if the authority chain makes it safe. Governance is not implementation detail — it is part of the pattern definition.
- The adversarial evaluation (RQ5) provides empirical grounding for the governance claim.

**Broader questions:**
- How general is the pattern? Where does it break down?
- Security: schema as injection vector — how does the validation layer hold up in practice?
- Does AIPCS improve as models improve? Schema design quality is model-dependent.
- What would a mature AIPCS ecosystem look like — shared taxonomy, cross-deployment portability, multi-agent coordination?

**Limitations to acknowledge (from Entry 012, ADR-002):**
- Semantic validation is not yet automated — the validator enforces structural rules but not semantic correctness (Q012). A schema can pass the validator but be wrong for the domain.
- Compaction as a trigger is a design intent — whether it is the primary real-world trigger is an open empirical question pending field evaluation.
- Dynamic tool registration is not universally supported across all MCP clients — session reconnect is the v1 fallback.
- Schema design quality is model-dependent and will vary across models and versions.

---

## 7. Conclusion

*Draft last — after all other sections are complete.*

---

## Appendix (if needed)

- Full schema design prompt (skill definition)
- Schema manifest format (reference)
- Tool taxonomy conventions
- Management tool primitive schemas

---

*This outline grows with the build. Promote BUILD_JOURNAL running notes here when they are substantive. See [docs/agent/paper-rules.md](../docs/agent/paper-rules.md) for the journal–paper pipeline.*
