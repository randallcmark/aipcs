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

### Entry 002 — 2026-05-04

**Type:** Decision

**Summary:** Trigger model refined — Model A is a hint, not an instruction. Tool seed concept established.

**Context:**
Working through the three core v1 design questions: trigger, mechanism, registration.

**Detail:**
Model A (explicit user instruction) is retained as a valid initiation path but reframed. The user instruction is a *hint* — sufficient to trigger the agent to evaluate what it knows about the domain. The agent should not wait for a complete specification before acting.

The **tool seed** concept emerged: when a user hint is received, the agent immediately plants a minimal domain marker — enough to describe the domain intent even if there is nothing yet to persist. The seed is a first-class object, queryable immediately ("what domains am I tracking?"). It carries:
- Domain name
- Discovery metadata stub
- Intent description
- Confidence level (seeded vs materialised)
- Timestamp

The seed transitions to a materialised service as the agent accumulates sufficient domain knowledge. This gives AIPCS two operating states per domain:

```
SEEDED       — marker exists, schema forming, not yet deployed
MATERIALISED — schema deployed, tools active, queryable
```

**Decision made:**
Tool seed is a first-class AIPCS primitive. `aipcs_service_seed` is always the first action when a persistence need is recognised, before any schema design begins.

**Implications:**
The `aipcs_service_list` tool must return both seeded and materialised services, with state indicated. The agent can inspect seeds to resume domain modelling across sessions.

**Paper notes:**
Section 4 (Reference Implementation) — the two-state model (seeded/materialised) is a concrete architectural decision worth describing. Section 5 (Evaluation) — how quickly do seeds materialise in practice? What is the average number of interactions before materialisation?

**Open questions:**
- What is the minimum viable seed payload? Domain name + intent description + timestamp is probably sufficient for v1. (→ Q007)
- Should seeds have a TTL — auto-expire if never materialised after N sessions? (→ Q008)

---

### Entry 003 — 2026-05-04

**Type:** Decision

**Summary:** Compaction identified as a primary Model B (proactive) trigger for AIPCS instantiation.

**Context:**
Exploring when an agent should proactively recognise a persistence need without explicit user instruction.

**Detail:**
Compaction — the process by which an agent summarises and compresses its context window — is a natural AIPCS trigger point. The agent is already performing a meta-cognitive act when it compacts: evaluating what is worth preserving. AIPCS adds a second question to that evaluation: *should this be preserved as structured data rather than compressed text?*

Key insight: persistence at compaction time should be **closer to the source** than a compacted summary. A summarised summary is further from truth than the original. AIPCS should capture the structured essence of the domain knowledge before compression degrades it.

This gives Model B a concrete, implementable trigger: the AIPCS skill hooks into the compaction process and evaluates each domain of knowledge for persistence candidacy.

**Decision made:**
Compaction is a primary Model B trigger. The AIPCS skill must include compaction hook guidance — "at compaction time, evaluate all active domains for AIPCS persistence candidacy before compressing."

**Implications:**
The skill definition becomes more specific — it needs to describe both the explicit hint trigger (Model A) and the compaction trigger (Model B). This makes the skill richer and more portable.

**Paper notes:**
Section 3 (Pattern) — the compaction hook is a novel contribution to the trigger design. No prior art explicitly connects context compaction with structured memory instantiation. Worth a dedicated paragraph.

---

### Entry 004 — 2026-05-04

**Type:** Decision

**Summary:** Mechanism selected — Option 3. AIPCS as MCP-native self-referential primitive server.

**Context:**
Evaluating CLI, sidecar, MCP-native, and prompt-only approaches for the scaffolding mechanism.

**Detail:**
Options evaluated:
- Option 1 (pure prompt/skill): Too weak — agent describes but does not act. Undermines the pattern.
- Option 2 (CLI): Platform distribution complexity, non-developer friction, support burden.
- Option 3 (MCP-native): AIPCS is itself an MCP server exposing management primitives. Self-referential — MCP tools that create MCP tools. Agent-autonomous. No CLI, no sidecar management API.
- Option 4 (sidecar HTTP API): Good for developer/infrastructure users, but adds complexity and friction for non-technical users. Also environment-dependent — IT/security constraints may block sidecar services.

Option 3 selected as the target architecture.

**Identified impediments and resolutions:**

| Impediment | Resolution |
|-----------|------------|
| Dynamic tool registration not universal in MCP clients | Session reconnect acceptable for v1; design assumes dynamic as target |
| Agent must know AIPCS exists before using it | Deployment concern — AIPCS is always-on in the stack, always connected |
| Schema quality depends on model capability | Schema validation layer in AIPCS — agent proposes, system validates, agent revises |
| Bootstrapping — no domain tools before first seed | AIPCS skill teaches agent: first action is always `aipcs_service_seed` |

**Decision made:**
Option 3. AIPCS is an MCP server. All management operations are MCP tool calls. No CLI, no separate HTTP management API.

**Paper notes:**
Section 3 (Pattern) — the self-referential nature of AIPCS (MCP tools that create MCP tools) is architecturally distinctive and worth emphasising. Section 4 — document the impediments and resolutions as lessons learned.

---

### Entry 005 — 2026-05-04

**Type:** Decision

**Summary:** Schema evolution requirement formalised — schema-forward, additive-only by default.

**Context:**
Exploring schemaless (KVS), protobuf, and relational approaches to schema evolution.

**Detail:**
The schemaless/protobuf discussion was an illustration of the problem space rather than a concrete proposal. The requirement is clear: AIPCS must support schema evolution in a backward-compatible way as the agent accumulates more domain knowledge.

Resolution: SQLite with a migration-tracked schema manifest.

Rules:
- Additive migrations only by default (add columns, add tables, add indices)
- Destructive changes (drop column, rename, type change) require explicit agent-proposed migration with confirmation
- Each migration is versioned and stored in the schema manifest
- Schema manifest travels with the service and is human-readable
- Agent proposes migrations; AIPCS validation layer enforces backward-compatibility rules before applying

This preserves structured queryability (the core AIPCS principle) while allowing the agent to evolve its understanding of a domain.

**Decision made:**
Schema-forward, additive-by-default, migration-tracked. This is a v1 requirement, not a deferred feature.

**Implications:**
The schema manifest format needs to be defined early — it is the versioning and audit record for the data model. It should include: domain name, version, migration history, entity definitions, relationship definitions, index definitions, created_at, last_evolved_at.

**Paper notes:**
Section 3 (Pattern) — schema evolution as an agent act is part of the lifecycle definition. Section 5 (Evaluation) — how many evolutions occur in practice during a typical domain tracking lifecycle?

---

### Entry 006 — 2026-05-04

**Type:** Decision

**Summary:** Three-tier access model established for transparency and auditability.

**Context:**
Discussing implicit transparency requirements — user, IT/security/compliance, and elevated stakeholder access to agent memory.

**Detail:**
The md-file harness paradigm provides implicit transparency (human-readable files) but suffers from summaries-of-summaries drift and hallucination proximity. AIPCS's structured approach provides better transparency because data is in a relational store that can be queried precisely.

Three-tier access model:

**Tier 1 — Agent access**
Full read/write via MCP tools. Normal operating mode.

**Tier 2 — User access**
Query and inspect via natural language. Agent mediates using its MCP tools. User can request exports, deletions, corrections. No direct database access required.

**Tier 3 — Elevated access (IT / compliance / practitioner / stakeholder)**
Direct read-only access to the service's HTTP query API or structured export. Scoped export tools. Audit log access. Cannot write — preserves agent memory integrity. Requires explicit user consent to grant.

The medical scenario is the clearest use case: a user's agent accumulates implicit medical context across conversations. The user can consent to share a structured export with a medical practitioner's AI-supported workflow. The practitioner receives richer, more accurate context than an anecdotal interview.

**Decision made:**
Three-tier model is a design input for v1 even if Tier 3 is not fully implemented. Architecture must accommodate it. Tier 3 access is consent-gated and read-only by design.

**Note on Tier 3 and platform coverage:**
Major AI platforms (Claude, ChatGPT) already handle data governance via their ToS/EULA frameworks. Tier 3 in AIPCS is specifically relevant for self-hosted deployments where the user owns all data and needs explicit mechanisms for controlled sharing.

**Paper notes:**
Section 6 (Discussion) — the transparency and auditability question is a significant design consideration for agent memory systems generally. The three-tier model is a contribution worth describing. The medical use case is a compelling illustration.

---

### Entry 007 — 2026-05-04

**Type:** Decision

**Summary:** Taxonomy question raised — top-level domain taxonomy may aid interoperability.

**Context:**
Discussing whether a shared taxonomy is needed for AIPCS services to interoperate across applications and deployments.

**Detail:**
If AIPCS is a universal primitive, and multiple agents or applications instantiate services for similar domains, some consistency in top-level taxonomy could enable interoperability. A career management AIPCS service instantiated by one agent should be recognisable and usable by another agent in a different context.

Two levels where taxonomy could help:
- **Top-level domain taxonomy** — a shared vocabulary of common domains (career, medical, financial, project, legal, etc.) that allows agents to recognise and connect to existing services
- **Sub-level object taxonomy** — within a domain, shared entity naming conventions that allow cross-agent queries

This is not a v1 requirement but is an architectural consideration — the schema manifest should include a domain classification field that could eventually map to a shared taxonomy.

**Decision made:**
Taxonomy is a deferred but designed-for feature. Schema manifest must include a `domain_class` field from v1. A reference taxonomy will be developed alongside the reference implementation.

**Open questions:**
- Should the domain taxonomy be an open registry (community-contributed) or a curated set? (→ Q009)
- How do you handle domain overlap — is "job application" a subset of "career" or its own domain class? (→ Q010)

**Paper notes:**
Section 6 (Discussion) — taxonomy and interoperability as future work. The domain_class field in the manifest enables this without requiring it.

---

### Entry 008 — 2026-05-04

**Type:** Milestone

**Summary:** Working model for Claude.ai / Claude Code collaboration established.

**Detail:**
Claude.ai (this chat) = thinking, design, architecture decisions, document drafting.
Claude Code = repo operations, file placement, git commits.

Handoff pattern: at end of each Claude.ai session, a summary is produced containing decisions made, files to commit, open questions, and a suggested commit message. Claude Code handles the rest.

Repo location: ~/GitHub/aipcs

---

### Entry 009 — 2026-05-04

**Type:** Decision

**Summary:** Formal governance model adopted — authority chain established; constraint categories defined; minimum governance standard set.

**Context:**
External critique identified the constraint model as the primary gap in the v1 architecture. The Schema Validator enforced structural rules, but the overall governance model — who has authority to do what, under what conditions, with what audit trail — was not formally specified. The claim "agent proposes, runtime governs" was asserted but not substantiated.

**Detail:**
The governance model is structured around a five-layer authority chain:

```
Agent proposes → Validator constrains → User consents → Service persists → Audit log explains
```

Constraint categories:
1. **Proposal constraints** — what the agent may do unilaterally (seed, list, inspect) versus what requires a validator gate (design, additive migration) versus what requires explicit user consent (destructive migration, Tier 3 access grant, sensitive column addition).
2. **Structural constraints** — what the Schema Validator must enforce before materialisation: naming conventions, primary keys, tool name format, reserved column names.
3. **Semantic constraints** — what automated enforcement cannot yet cover (domain appropriateness, no credential columns, no host-app schema references). Partially deferred as Q013.
4. **Sensitive-data constraints** — column name patterns triggering `sensitive: true` declaration and user notification at materialisation.

User transparency requirements: 7 things a user must be able to determine at any time (list domains, inspect data, view migration history, query audit log, export data, delete data, see Tier 3 grants).

Auditability requirements: 8 auditable actions; 6-field audit entry structure (event_id, event_type, service_id, actor, timestamp, outcome).

Consent model: 3 tiers — implicitly allowed in bounded local context, explicit confirmation recommended, high bar.

Correction and redress: 8 operations (inspect, amend, dispute, deprecate, merge, tombstone, export, delete).

Minimum governance standard: 7-point checklist that must be met before any prototype is used beyond solo development.

**Decision made:**
Adopt `docs/architecture/governance.md` as the authoritative governance specification. This is a v1 design requirement, not a v2 deferral. Without it, the "agent proposes, runtime governs" claim cannot be substantiated.

**Alternatives considered:**
Deferring governance to v2 — rejected. It leaves the core claim unsubstantiated and prevents the prototype from being used for user evaluation.

**Implications:**
Phase 2 (AIPCS Server Prototype) must include: audit_log table in Registry DB, sensitive-data column heuristics in Schema Validator, and a v1 consent surface for materialisation. See implementation-sequencing.md.

**Paper notes:**
§3 (The AIPCS Pattern) — the authority chain is a first-class design contribution alongside the two-state lifecycle. "Agent-directed" does not mean "agent-controlled" — this distinction is the core of the governance claim. §6 (Discussion) — governance as a necessary condition for the pattern to be safe in practice.

**Open questions:**
- Q012: Can a validator reliably detect whether a proposed schema is semantically appropriate for its declared domain?
- Q013: How should the Schema Validator detect PII/credential column names automatically?
- Q014: In v1 local trust mode (no UI), how is user consent for materialisation surfaced?

---

### Entry 010 — 2026-05-04

**Type:** Spec Change

**Summary:** Claims narrowed — "universal primitive" retired; authoritative claims boundary document created; compaction reframed.

**Context:**
External critique identified four areas of claim overreach in existing repo language: "universal primitive" language outpacing evidence, MCP positioned as the primary novelty claim, compaction framed as "primary Model B trigger" without field evidence, and no single authoritative claims document allowing language to drift independently across files.

**Detail:**
Working core claim adopted:
> AIPCS is a constrained runtime pattern for agent-directed creation and evolution of structured persistent memory services.

Safer external framing adopted (for paper abstract, README, presentations):
> AIPCS is an early pattern for governed agent-directed structured memory, where an agent can propose and evolve persistence schemas under runtime validation instead of relying solely on developer-defined memory models.

Specific language changes:
- "Universal primitive" → "general-purpose pattern" in README.md. Cannot claim universality before multi-domain generalisation evidence exists.
- "The agent is the architect of its own memory" → "the agent proposes the structure of its own memory, subject to runtime governance."
- Compaction: "primary Model B trigger" → "a designed Model B trigger" pending field validation of whether compaction is the primary real-world trigger in practice.
- MCP positioning: reduced from primary novelty claim to chosen interface surface. The novelty is agent-directed structured persistence, not MCP per se.

`docs/architecture/claims-and-scope.md` created as the single authoritative claims boundary. All novelty language in the repo must be consistent with it. It is the tie-breaker where language conflicts.

**Decision made:**
The narrower, more defensible claim is adopted. Inline qualifications per document are rejected in favour of a single authoritative document.

**Alternatives considered:**
Inline qualifications per document — rejected because they drift and are inconsistently applied over time.

**Implications:**
README.md and paper/outline.md §1 and §3 require targeted language updates. No structural changes to the architecture.

**Spec change:** S002 — see Spec Change Log.

**Paper notes:**
§1 (Introduction) — use the safer external framing in the abstract and opening contribution statement. §3 — compaction framing note. Do not lead with MCP as the primary novelty in the abstract.

---

### Entry 011 — 2026-05-04

**Type:** Milestone

**Summary:** Formal evaluation framework adopted — 6 research questions, 3 baselines, 4-phase evaluation sequencing aligned to implementation phases.

**Context:**
The paper outline §5 (Evaluation) was seeded with informal metrics from journal running notes. No structured research questions, baselines, or success/failure criteria existed. A formal evaluation framework has been produced to ground the paper's evaluation section and make results comparable across runs.

**Detail:**
Six research questions formalised:
- RQ1: Recognition — does the agent reliably recognise AIPCS-appropriate situations?
- RQ2: Initial Design Quality — does the agent produce a schema that covers the domain at first attempt?
- RQ3: Evolution Quality — does the agent propose appropriate additive evolutions?
- RQ4: Retrieval and Continuity Utility — does AIPCS-backed memory improve task continuation vs baselines?
- RQ5: Governance Effectiveness — does the constraint model prevent harmful proposals?
- RQ6: Runtime Portability — can an AIPCS service be exported and re-materialised in a different runtime?

Three baselines:
- Baseline A: Harness memory (markdown/index files — the status quo pattern this repo uses)
- Baseline B: Developer-defined structured memory (hand-written schema with equivalent domain coverage)
- Baseline C: Minimal generic KV/document store (no domain structure)

Baselines B and C exist to isolate the specific contributions. Baseline B tests whether agent-design adds value over developer-defined structure. Baseline C tests whether schema quality matters at all.

Four evaluation phases mapped to implementation phases:
- Phase 1 (Concept Validation) — RQ1, RQ2 — triggers at M007
- Phase 2 (Governance Validation) — RQ3, RQ5; adversarial suite — triggers at M008
- Phase 3 (Portability Validation) — RQ6 — between M008 and M009
- Phase 4 (Comparative) — RQ4 across all three baselines — triggers at M009

Five early success criteria and five early failure conditions defined. Failure conditions are honest pre-commitments — if any trigger, the issue must be resolved before paper submission.

**Decision made:**
Adopt `docs/quality/evaluation-plan.md` as the authoritative evaluation specification. Paper §5 will be structured around the 6 RQs and 3 baselines.

**Implications:**
Implementation phases 4–7 must accommodate evaluation artefact requirements (session transcripts, schema manifests, audit logs, token cost records). Adversarial prompting suite (RQ5) must be designed before Phase 5 work begins. Phase 5 in implementation-sequencing.md updated to align.

**Paper notes:**
§5 (Evaluation) — the 6 RQs define the section structure. The 3 baselines ground any comparative claims. The pre-defined failure conditions strengthen the paper — they signal intellectual honesty rather than post-hoc rationalisation.

**Open questions:**
- Q015: What does the evaluation harness look like? How are artefacts captured systematically?
- Q016: What is the human review rubric for schema quality (RQ2, RQ3)?

---

### Entry 012 — 2026-05-04

**Type:** Observation

**Summary:** External critique received and processed — findings confirm core novelty; 5 gaps and 5 steering recommendations fully dispositioned.

**Context:**
An independent formal critique of AIPCS was received and reviewed (May 2026). This entry records the synthesis.

**Detail:**
The critique's novelty assessment confirms the strongest claim combination:
> agent recognition of persistence need + agent proposal of memory structure + runtime materialisation + governed schema evolution + portable tool surface

This is more specific and more defensible than "universal primitive." The critique notes that MCP matters as an interface surface but is not the novelty itself — the deeper idea survives even if MCP mechanics change.

Critique findings dispositioned (full details in `docs/quality/critique-response.md`):
1. **Constraint model under-specified** → actioned: governance.md + ADR-001
2. **Validation too structural** → partially actioned: governance.md §Semantic Constraints; full semantic automation deferred as Q013
3. **Dynamic tool registration may be less robust than assumed** → actioned: claims-and-scope.md explicit non-claim item 2
4. **Compaction is useful but not foundational** → actioned: reframed from "primary" to "designed" trigger
5. **Authority and truth chain not explicit** → actioned: governance.md §Authority Chain

Steering recommendations dispositioned:
1. **Narrow the claim** → actioned: claims-and-scope.md; working core claim adopted
2. **Separate the layers** → actioned: claims-and-scope.md §Scope Boundaries: Pattern vs Implementation
3. **Specify non-goals aggressively** → actioned: claims-and-scope.md §Non-Goals; research-brief.md updated
4. **MCP not the primary novelty** → actioned: README and paper outline language adjusted
5. **Retire "universal primitive"** → actioned: README updated

**Observation:**
The critique is a useful calibration. The core novelty is sound; the surrounding claims infrastructure was underdeveloped. The gap between "this is novel" and "this is well-specified enough to withstand peer review" has been substantially closed by entries 009–011.

**Alternatives considered:**
Treating the critique as confirmation only — rejected. The findings require substantive changes, not acknowledgement.

**Paper notes:**
§1 — the critique's novelty formulation (the combination of 5 elements) can inform the contribution statement directly. §6 (Discussion) — semantic validation gap is an honest acknowledged limitation worth naming: the validator enforces structure but not semantic correctness.

**Open questions:**
Q012–Q016 added to technical-debt.md.

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
| D004 | 2026-05-04 | Tool seed as first-class primitive | Enables immediate domain registration before schema is complete | 002 |
| D005 | 2026-05-04 | Two-state model: SEEDED / MATERIALISED | Reflects real progression of domain knowledge | 002 |
| D006 | 2026-05-04 | Compaction as primary Model B trigger | Natural meta-cognitive moment; captures knowledge before compression degrades it | 003 |
| D007 | 2026-05-04 | Option 3 — AIPCS as MCP-native primitive server | Agent-autonomous, no CLI, no sidecar management API | 004 |
| D008 | 2026-05-04 | Schema-forward, additive-by-default, migration-tracked | Backward compatibility as a v1 requirement | 005 |
| D009 | 2026-05-04 | Three-tier access model | Transparency and auditability are design inputs from v1 | 006 |
| D010 | 2026-05-04 | domain_class field in schema manifest | Enables future taxonomy and interoperability without requiring it now | 007 |
| D011 | 2026-05-04 | Formal governance model adopted — authority chain, constraint categories, minimum governance standard | External critique finding: constraint model was the primary gap; "agent proposes, runtime governs" claim required substantiation | 009 |
| D012 | 2026-05-04 | "Universal primitive" retired; claims-and-scope.md created as authoritative claims boundary | Prevents claim overreach drift; narrower claims are more defensible in peer review | 010 |
| D013 | 2026-05-04 | Evaluation framework formalised — 6 RQs, 3 baselines, 4 evaluation phases | Paper §5 requires structured evaluation; informal journalling is insufficient for comparative claims | 011 |
| D014 | 2026-05-04 | Compaction reframed from "primary Model B trigger" to "a designed Model B trigger" | Pending field evidence; avoids making an evaluable claim before evaluation has occurred | 010 |

---

## Spec Change Log

Record every time a build decision causes a change to the pattern specification.

| # | Date | Spec Section | Change | Reason | Entry |
|---|------|-------------|--------|--------|-------|
| S001 | — | — | — | — | — |
| S002 | 2026-05-04 | Core claim language across repo | Retire "universal primitive"; adopt narrowed working core claim; adopt safer external framing; reframe compaction as "designed" not "primary" trigger | External critique steering advice | 010 |

---

## Open Questions

Running list of unresolved questions. Close them with a decision log entry when resolved.

| # | Question | Raised | Resolved | Decision |
|---|----------|--------|----------|----------|
| Q001 | Trigger model — Model A/B: how does the agent proactively recognise a persistence need? (Mechanism resolved as Option 3 / D007; compaction trigger defined / D006. Remaining: full skill prompt design for Model B proactive recognition.) | 001 | Partial | D006, D007 |
| Q002 | Schema versioning format — resolved by schema manifest design in v1 technical design. Schema manifest travels with every service; format defined in `docs/AIPCS_v1_Technical_Design.md`. | 001 | ✅ 2026-05-04 | See technical design §Schema Manifest Format |
| Q003 | Service registry — resolved by `aipcs_service_list` primitive tool and Registry DB in AIPCS Server. | 001 | ✅ 2026-05-04 | D007, technical design §Service Lifecycle |
| Q004 | Multi-agent access — locking model when multiple clients hit same service? | 001 | — | — |
| Q005 | Schema conflict resolution — what if agent proposes conflicting evolution? | 001 | — | — |
| Q006 | Portability — resolved in part by `aipcs_service_export` primitive tool (json / sqlite / schema_only / data_only / full). Full portability format still TBD. | 001 | Partial | D007, technical design §Management Tools |
| Q007 | Minimum viable seed payload — what fields are required for `aipcs_service_seed`? | 002 | — | — |
| Q008 | Should seeds have a TTL — auto-expire if never materialised after N sessions? | 002 | — | — |
| Q009 | Should domain taxonomy be open registry or curated set? | 007 | — | — |
| Q010 | How to handle domain overlap in taxonomy (e.g. job application vs career)? | 007 | — | — |
| Q011 | Should Tier 3 access be part of v1 spec or explicitly deferred to v2? | 006 | — | — |
| Q012 | Governance — semantic validation: can a validator reliably detect whether a proposed schema is semantically appropriate for its declared domain? Structural checks are insufficient for semantic correctness. | 009 | — | — |
| Q013 | Governance — sensitive-data column detection: how should the Schema Validator detect PII/credential column names automatically? Regex heuristics vs model-assisted? | 009 | — | — |
| Q014 | Governance — v1 local consent mechanism: in v1 local trust mode (no UI), how is user consent for materialisation and sensitive column additions surfaced? | 009 | — | — |
| Q015 | Evaluation — harness design: what does the evaluation harness look like? How are session transcripts, audit logs, and token costs captured systematically across runs? | 011 | — | — |
| Q016 | Evaluation — schema quality rubric: what criteria define a schema as adequate for a domain? Required for RQ2 and RQ3 human review. | 011 | — | — |

---

## Milestone Tracker

| # | Milestone | Target | Completed | Notes |
|---|-----------|--------|-----------|-------|
| M001 | Invention disclosure published | 2026-05-04 | ✅ 2026-05-04 | |
| M002 | Pattern spec v0.1 published | 2026-05-04 | ✅ 2026-05-04 | |
| M003 | Public GitHub repo live | 2026-05-04 | ✅ 2026-05-04 | |
| M004 | v1 technical design complete | 2026-05-04 | ✅ 2026-05-04 | `docs/AIPCS_v1_Technical_Design.md` |
| M005 | AIPCS Server prototype running | — | — | Option 3 — MCP-native server |
| M006 | OAuth/DCR foundation implemented | — | — | |
| M007 | First MCP tool registered by agent | — | — | |
| M008 | End-to-end flow validated in App Tracker | — | — | |
| M009 | Framework extracted from app-specific code | — | — | |
| M010 | arXiv preprint submitted | — | — | |
| M011 | Governance model, claims boundary, and evaluation framework documented | 2026-05-04 | ✅ 2026-05-04 | Entries 009–012; ADR-001–003; EP-001; governance.md; claims-and-scope.md; evaluation-plan.md |

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
- **Claim framing (from D012, Entry 010):** Use the safer external framing for the contribution statement — "an early pattern for governed agent-directed structured memory." Avoid "universal primitive." Do not lead with MCP as the primary novelty. The strongest novelty formulation (from external critique): agent recognition + agent proposal of memory structure + runtime materialisation + governed evolution + portable tool surface.

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

Key points to include from design iteration:
- **Two-state lifecycle**: SEEDED → MATERIALISED. The seed is a first-class primitive, not a placeholder. Describe the progression from hint → seed → accumulated knowledge → schema design → materialisation.
- **Compaction as Model B trigger (Entry 003):** A designed Model B trigger — connects compaction with structured memory candidacy evaluation. Pending field validation of whether this is the primary real-world trigger in practice. Do not claim "primary" before evaluation data exists.
- **Authority chain as design contribution (Entry 009):** Agent proposes → Validator constrains → User consents → Service persists → Audit log explains. This is as central to the pattern as the two-state lifecycle — "agent-directed" only means something if the governance chain makes it safe.
- **Self-referential MCP-native mechanism**: MCP tools that create MCP tools. Option 3 vs alternatives evaluated (Option 1: too weak; Option 2: CLI friction; Option 4: sidecar HTTP complexity). Impediments and resolutions documented in Entry 004.
- **Schema evolution as agent act**: Agent proposes migrations; AIPCS validates and applies. Additive-by-default, destructive requires confirmation. Schema manifest travels with the service.

### 4. Reference Implementation

Key points from design iteration:
- Architecture: AIPCS Server (MCP-native) + Registry DB + Domain Services. Diagram in `docs/AIPCS_v1_Technical_Design.md`.
- 8 management primitives: seed, design, materialise, evolve, list, inspect, suspend, export
- Schema manifest format (versioned, human-readable JSON) — full example in technical design doc
- Option 3 impediments and resolutions — valuable "lessons learned" material
- Three-tier access model (Tier 1 agent / Tier 2 user / Tier 3 elevated) — architecture accommodates Tier 3 from v1 even if not implemented
- Docker Compose structure: aipcs service alongside app + mcp
- V1 local trust model; v2 OAuth/DCR target

*Populate with implementation details as build progresses (M005–M008)*

### 5. Evaluation

Evaluation framework adopted (Entry 011, evaluation-plan.md). Structure §5 around these:

**Research Questions (RQ1–RQ6):**
- RQ1: Recognition — agent reliably recognises AIPCS-appropriate situations?
- RQ2: Initial Design Quality — first-attempt schema covers the domain?
- RQ3: Evolution Quality — agent proposes appropriate additive evolutions?
- RQ4: Retrieval and Continuity Utility — AIPCS memory improves task continuation vs baselines?
- RQ5: Governance Effectiveness — constraint model prevents harmful proposals?
- RQ6: Runtime Portability — service exportable and re-materialisable in a different runtime?

**Baselines:**
- A: Harness memory (markdown/index files — status quo)
- B: Developer-defined structured memory (isolates value of agent-directed design)
- C: Minimal generic KV/document store (isolates value of schema quality)

**Evaluation phases:** Phase 1 (RQ1/2, M007) → Phase 2 (RQ3/5, M008) → Phase 3 (RQ6) → Phase 4 (RQ4 comparative, M009)

*Populate with results during build (M007–M009). Full framework: docs/quality/evaluation-plan.md*

### 6. Discussion

- **Three-tier access model** — transparency and auditability as design considerations for agent memory systems generally. Medical use case: agent-accumulated health context shared with practitioner's AI workflow via consent-gated structured export. (Entry 006)
- **Taxonomy and interoperability** — domain_class field enables future cross-agent interoperability without mandating it now. Open vs curated registry question. (Entry 007)
- How general is the pattern really? Where does it break down?
- Security implications of agent-designed schemas (schema as injection vector)
- Does AIPCS improve as models improve? (schema design quality is model-dependent)
- What would a mature AIPCS ecosystem look like?
- **Governance as necessary condition (Entry 009):** "agent-directed" is only a meaningful claim if the authority chain makes it safe. This belongs in §6 as a design principle, not a v2 deferral.
- **Limitations to acknowledge honestly (Entry 012):** Semantic validation not yet automated (Q013). Compaction as primary trigger is a design intent, not yet field-validated. Dynamic tool registration is not universally supported. Schema quality is model-dependent.

### 7. Conclusion

*Draft when rest is complete.*

---

*This journal is the memory of the build. Write in it as if explaining to a colleague who will pick up the project after you. Future you will thank present you.*
