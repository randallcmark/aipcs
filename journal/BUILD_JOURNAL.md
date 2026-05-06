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

### Entry 009 — 2026-05-06

**Type:** Decision

**Summary:** Evaluation framing established: separate memory-system quality from agent/model capability, with OpenAI as the first agent-class reference.

**Context:**
While planning the experimental baseline, the original Application Tracker proving-ground assumption was revisited. The stronger current implementation candidate is `agent-memory-v2`, now canonical at `/Users/markrandall/GitHub/agent-memory-v2`. The older NAS checkout at `/Volumes/Media/Repository/agent_memory_v2` was identified as stale and should not be used for future baselines.

The key methodological issue: `agent-memory-v2` currently runs against local Ollama models such as `llama3:8b`. That is not equivalent to AIPCS running inside an agent harness such as ChatGPT, Claude, or Gemini, where the model can reliably follow instructions and use tools.

**Detail:**
The experiment will be structured as two layers:

1. **Layer 1 — memory mechanics:** evaluate capture, extraction, recall, conflict handling, prompt-context cleanliness, storage growth, and maintenance behavior independently of live model quality.
2. **Layer 2 — agent behavior:** evaluate an instruction-following model operating through a minimal tool-loop harness, measuring tool-use validity, tool-use judgment, answer correctness, grounding, latency, and call count.

The first API-backed agent-class reference will be OpenAI. Claude and Gemini remain useful future comparisons, but adding them immediately would expand scope before the baseline is stable. Local models remain part of the model ladder (`llama3:8b`, `gpt-oss:20b`, `gemma3:12b`, `gemma3:27b`), but no AIPCS claim should rely on `llama3:8b` behavior alone.

An execution plan was created at `docs/exec-plans/active/aipcs-experiment-baseline-and-agent-harness.md`.

**Decision made:**
Evaluation results must distinguish memory-system performance from agent/model capability. The first agent-class comparison should use an OpenAI-backed, provider-neutral mini harness. Cloud GPU use is deferred unless local open-model comparison becomes a blocker.

**Alternatives considered:**
- Treat the whole assistant as one end-to-end unit. Rejected because it would make weak-model behavior look like memory-system failure.
- Use only deterministic memory tests. Rejected because AIPCS is an agentic pattern and must eventually be evaluated through agent decisions.
- Rent cloud GPU first. Rejected for the initial baseline because stronger open-weight inference does not directly test the expected AIPCS configuration of a tool-using instruction-following agent.
- Implement Claude and Gemini immediately. Deferred to keep the first harness bounded and reproducible.

**Implications:**
The paper's Evaluation section must report two categories of evidence: model-independent memory mechanics and agent-class behavior. `application_tracker` should be treated as a fixed-schema contrast rather than the main experimental baseline. The current baseline path is `/Users/markrandall/GitHub/agent-memory-v2`; the stale NAS path should be avoided in all future baseline commands.

**Paper notes:**
Section 5 (Evaluation) — this is a central methodological point. The paper should explicitly state that AIPCS assumes an instruction-following agent harness, so evaluation separates memory substrate quality from model/tool-use capability. Section 6 (Discussion) — model dependence becomes an important limitation and future-work axis: as local/open models improve, AIPCS may become more viable without frontier API access.

**Open questions:**
- Which OpenAI model should become the first reference once the harness is implemented?
- How much local open-model parity is needed before claiming that AIPCS is practical outside frontier API agents?
- Should Claude or Gemini be added before the first paper draft, or only after the OpenAI reference run?

---

### Entry 010 — 2026-05-06

**Type:** Milestone

**Summary:** First `agent-memory-v2` baseline evidence recorded for the AIPCS evaluation plan.

**Context:**
After the evaluation framing was established, the canonical `agent-memory-v2` repository was used to run the current fixed-memory baseline. The baseline artifacts remain in `/Users/markrandall/GitHub/agent-memory-v2`; AIPCS now keeps a concise evidence note at `docs/references/evaluation-baseline-2026-05-06.md`.

**Detail:**
The baseline includes deterministic eval history, live Ollama eval history, and qualitative scenario artifacts. The inspected clean implementation SHA was `39d633664f377fa442a6bc698ae527abbf6a377d` on branch `main`.

Summary of observed results:
- Deterministic eval: passed with overall score `1.0` across classification, semantic routing, sentiment, profile, recall, and prompt stages.
- Live Ollama eval: passed with overall score `1.0` across memory and sentiment stages using `llama3:8b` and `nomic-embed-text`.
- `conflicting_fact_latest_wins`: profile resolved `identity.location` to `London now`; final prompt injected the latest profile value and suppressed additional recalled memory.
- `semantic_location_candidate`: semantic routing plus structured extraction promoted "I'm based in Edinburgh in the UK" into durable `identity.location` memory.

**Observation:**
`agent-memory-v2` is a credible fixed-memory control. It already includes hybrid promotion from generic utterances into structured durable memory, but that structure is still developer-defined through taxonomy/profile keys. This makes it a useful baseline, not proof of AIPCS schema autonomy.

**Alternatives considered:**
Raw eval artifacts could have been copied into AIPCS, but that would duplicate generated data and risk drift. The chosen approach keeps raw artifacts in the implementation repo and records a compact, citable summary in AIPCS.

**Implications:**
The next implementation step should be the provider-neutral mini agent harness with OpenAI as the first agent-class reference. Future comparisons should cite this baseline note and avoid using the stale NAS checkout.

**Paper notes:**
Section 5 (Evaluation) — this provides the first baseline evidence for the fixed-memory control. It also surfaces an important distinction for the paper: `agent-memory-v2` can structure memory, but the object model is predefined by developers, whereas AIPCS claims agent-generated schema autonomy.

**Open questions:**
- Should the baseline note be promoted into a fuller experiment protocol after the OpenAI harness exists?
- Which additional scenarios should be required before claiming the fixed-memory baseline is sufficiently characterized?

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
| D011 | 2026-05-06 | Evaluation must separate memory mechanics from agent behavior | Prevents model weakness from being misreported as memory-system failure | 009 |
| D012 | 2026-05-06 | OpenAI is the first agent-class reference provider | Closest bounded match to AIPCS assumptions before adding Claude/Gemini/cloud GPU | 009 |

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

Key points to include from design iteration:
- **Two-state lifecycle**: SEEDED → MATERIALISED. The seed is a first-class primitive, not a placeholder. Describe the progression from hint → seed → accumulated knowledge → schema design → materialisation.
- **Compaction as Model B trigger**: Novel contribution — no prior art connects context compaction with structured memory instantiation. Agent evaluates active domains for persistence candidacy before compressing. Captures knowledge closer to the source than a summary.
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

Evaluation questions seeded from design:
- What workflows became possible that weren't before?
- Latency cost of agent schema design vs a pre-defined schema
- Token cost of the schema design step
- **How quickly do seeds materialise?** Average interactions before materialisation (from Entry 002)
- **How many schema evolutions occur** in a typical domain tracking lifecycle? (from Entry 005)
- What prompt patterns worked best for triggering recognition?
- What failed or surprised you?
- **Two-layer evidence model**: report memory mechanics separately from agent behavior. Layer 1 evaluates capture, extraction, recall, conflict handling, prompt cleanliness, storage growth, and maintenance independently of model quality. Layer 2 evaluates tool-use validity, judgment, answer correctness, grounding, latency, and call count through a mini agent harness. (Entry 009)
- **Agent-class reference**: OpenAI-backed harness results become the first reference configuration for AIPCS-like agent behavior. Local models remain a ladder, but `llama3:8b` must not be the sole basis for AIPCS claims. (Entry 009)

*Populate during build (M007–M008)*

### 6. Discussion

- **Three-tier access model** — transparency and auditability as design considerations for agent memory systems generally. Medical use case: agent-accumulated health context shared with practitioner's AI workflow via consent-gated structured export. (Entry 006)
- **Taxonomy and interoperability** — domain_class field enables future cross-agent interoperability without mandating it now. Open vs curated registry question. (Entry 007)
- **Model dependence** — AIPCS assumes an instruction-following, tool-using agent. Evaluation should discuss how far local/open models can approximate that role versus requiring frontier API-class agents. (Entry 009)
- How general is the pattern really? Where does it break down?
- Security implications of agent-designed schemas (schema as injection vector)
- Does AIPCS improve as models improve? (schema design quality is model-dependent)
- What would a mature AIPCS ecosystem look like?

### 7. Conclusion

*Draft when rest is complete.*

---

*This journal is the memory of the build. Write in it as if explaining to a colleague who will pick up the project after you. Future you will thank present you.*
