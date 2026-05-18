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

### Entry 011 — 2026-05-17

**Type:** Decision

**Summary:** Homelab infrastructure adopted as the default deployment substrate for AIPCS prototype services.

**Context:**
After a week of parallel homelab work, the available runtime environment changed materially. The QNAP now has Portainer-managed Docker stacks, Caddy reverse proxy under `*.indigo-blocks.uk`, Grafana/Prometheus/Loki observability, Open WebUI, Tailscale access patterns, and a Brandon vLLM relay reachable by homelab containers. The AIPCS build should use this as enabling infrastructure rather than creating duplicate local service stacks.

**Detail:**
The AIPCS mission remains the same: design and validate agent-instantiated persistent context services. The homelab is now the preferred substrate for durable service experiments, not a competing project. Local Docker on the Mac remains useful for fast development and Apple Silicon-specific workloads, but the default target for deployable services should be QNAP/homelab when CPU demands are modest.

Practical constraints:
- QNAP has enough memory for many lightweight services.
- QNAP CPU is low-power Intel J4105 Celeron class with no GPU.
- Heavy inference should use external/API providers, Brandon vLLM, NVIDIA/Gemini, or Apple Silicon when appropriate.
- `brandon-ts:8080/v1` is an internal homelab Docker-network model endpoint, not a Mac-resolvable hostname.
- Open WebUI is a useful human/model interface, but not the AIPCS memory control plane.

**Decision made:**
Use homelab as the standard deployment target for AIPCS prototype services unless a task specifically requires local workstation execution. Keep `aipcs-model-lab` as a companion model/provider harness, not as the center of the AIPCS architecture.

**Alternatives considered:**
- Continue building independent local Docker infrastructure for every AIPCS experiment. Rejected because it duplicates the homelab service substrate and creates unnecessary drift.
- Move AIPCS implementation into the homelab repo. Rejected because AIPCS is the research/spec/reference project; homelab is the operations substrate.
- Treat Open WebUI as the primary memory interface. Rejected for now because AIPCS needs MCP-native primitives and schema autonomy, while Open WebUI is primarily a model/chat UX.

**Implications:**
The active experiment plan now records homelab as deployment substrate and updates the provider ladder to include NVIDIA NIM, Brandon vLLM, and future Gemini support. The first memory prototype should remain small: local-first MCP server, SQLite registry, primitive management tools, then containerise and deploy to homelab when the tool loop is credible.

**Paper notes:**
Section 4 (Reference Implementation) should mention that the reference prototype runs on modest homelab infrastructure, with inference separated from memory service hosting. Section 6 (Discussion) can use this as evidence that AIPCS services do not require GPU-class infrastructure; only the agent/model side may.

**Open questions:**
- Should the first AIPCS MCP prototype be Node or Python?
- Should the first deployed homelab service be the AIPCS primitive server itself or a narrower memory experiment?
- How much of the homelab deployment path should appear in the paper versus remain operational detail?

---

### Entry 012 — 2026-05-17

**Type:** Milestone

**Summary:** First AIPCS implementation repo created with a working primitive registry loop.

**Context:**
After deciding that AIPCS should remain the mission and homelab should serve as deployment substrate, the first implementation repo was created separately at `/Users/markrandall/GitHub/aipcs-server`. The repo is tailored as a software implementation harness rather than a copy of the generic template harness.

**Detail:**
The first slice implements a local-first Python MCP primitive server with SQLite registry persistence. It exposes the core behavior behind the first three management primitives:
- `aipcs_service_seed`
- `aipcs_service_list`
- `aipcs_service_inspect`

The implementation includes:
- repo-specific agent harness docs
- Python package and CLI entrypoint
- Pydantic validation for seed requests
- SQLite `services` and `audit_log` tables
- exact duplicate handling by `owner_id + domain_name`
- broad, non-enforced `domain_class` metadata
- test coverage for validation, persistence, duplicate handling, owner scoping, audit logging, and JSON-shaped tool output

**Decision made / milestone reached:**
The AIPCS Server build has begun as a separate implementation repo. The first seed/list/inspect registry loop is implemented and validated locally. Taxonomy remains deliberately soft in the first slice: `domain_class` is stored but not used as a rigid classifier.

**Alternatives considered:**
- Copy the generic template harness verbatim. Rejected because the server repo needs implementation-specific routing and validation rules.
- Start directly with full materialisation. Rejected because seed/list/inspect is the smallest useful proof of the AIPCS lifecycle.
- Enforce a fixed taxonomy now. Rejected because early rigid taxonomy would undermine agent flexibility and schema autonomy.

**Implications:**
M005 can now progress from design into implementation. The next slice should add schema design intake and validation only after the primitive registry loop is exercised through an MCP client. Homelab deployment should wait until the local tool loop is credible.

**Paper notes:**
Section 4 (Reference Implementation) — the first implementation slice demonstrates that the SEEDED state can be made concrete as a durable, inspectable primitive before schema materialisation exists. Section 6 (Discussion) — the taxonomy choice is important: AIPCS stores broad classification metadata without locking the agent into a fixed hierarchy.

**Open questions:**
- Should schema design intake come before or after a live MCP client smoke test?
- What is the minimum taxonomy metadata needed to support future reclassification without premature structure?
- When should `aipcs-server` be deployed to homelab?

---

### Entry 013 — 2026-05-17

**Type:** Milestone

**Summary:** AIPCS Server now accepts and validates schema designs for seeded services.

**Context:**
The first MCP smoke test proved the seed/list/inspect registry loop. The next implementation slice added the fourth management primitive, `aipcs_service_design`, so an agent can submit a proposed domain schema before any materialised service exists.

**Detail:**
`aipcs-server` now has a schema design intake layer backed by the same SQLite registry. Accepted designs are stored as schema manifests on the seeded service and surfaced through inspect/list responses. Rejected designs return structured validation issues and leave the service unchanged.

The first validator is intentionally narrow. It enforces only the rules needed before materialisation:
- at least one entity
- initial `schema_version` of 1
- empty initial migration history
- exactly one primary key per entity
- required audit fields (`owner_id`, `created_at`, `updated_at`, `created_via`)
- basic snake_case naming for entities, attributes, and tool definitions
- concise tool descriptions

Accepted and rejected design attempts are both audited. The service remains in `seeded` state after a design is accepted; materialisation is still a separate primitive.

**Decision made / milestone reached:**
Schema design is now a first-class AIPCS action rather than prose in a plan. The implementation preserves agent flexibility by validating safety and lifecycle constraints without imposing a fixed taxonomy or a full relational design language too early.

**Alternatives considered:**
- Generate the materialised service immediately after schema submission. Deferred because schema intake needs to be observable and testable on its own.
- Validate a much richer schema grammar now. Deferred because over-specifying the design language could lock in the wrong abstraction before real agent-generated schemas are observed.
- Treat invalid designs as exceptions only. Rejected because structured validation feedback is part of the agent revision loop.

**Implications:**
M005 can now be marked complete at the local prototype level: AIPCS Server is a running MCP primitive server with seed, list, inspect, and design tools. The next implementation step is either an MCP smoke script for `aipcs_service_design` or the first materialisation slice that turns an accepted manifest into a concrete domain service/database.

**Paper notes:**
Section 4 (Reference Implementation) should describe schema intake as a separate phase between seed and materialisation. Section 5 (Evaluation) can measure how many validation iterations an agent needs before producing an accepted schema. Section 6 (Discussion) should note the balance between agent autonomy and system-side validation: AIPCS lets the agent propose the schema, but the server owns safety and lifecycle invariants.

**Open questions:**
- What schema examples should be used as fixtures for early agent-behavior evaluation?
- Should validation feedback include severity levels before materialisation exists?
- How much schema grammar is necessary before the first generated service is useful?

---

### Entry 014 — 2026-05-17

**Type:** Milestone

**Summary:** AIPCS Server now materialises accepted schemas into local domain SQLite databases.

**Context:**
After schema design intake was validated through the MCP smoke path, the next implementation slice added `aipcs_service_materialise`. This is the first point where AIPCS creates a concrete domain persistence surface rather than only registry metadata.

**Detail:**
`aipcs-server` now materialises a service by reading the accepted schema manifest, creating a per-service SQLite database under the services directory, creating one table per manifest entity, applying declared indices, and updating the registry record to `materialised`.

The service record now carries:
- `state = materialised`
- `confidence = materialised`
- `materialised_at`
- `endpoint = sqlite:///...`
- generated/stored tool names from the schema manifest
- manifest-level materialisation metadata containing database path and endpoint

Materialisation is idempotent. Re-running `aipcs_service_materialise` on an already materialised service returns the existing service and database path instead of rebuilding or overwriting. A seeded service without an accepted schema returns structured validation feedback. First-design submission is also blocked after materialisation; future schema changes must use the evolution primitive rather than overwriting the original manifest.

**Decision made / milestone reached:**
The AIPCS lifecycle now reaches SEEDED → DESIGNED → MATERIALISED locally. The first materialisation target is deliberately conservative: one SQLite database per service, no generated FastAPI process yet, and no dynamic domain-specific MCP tool registration yet.

**Alternatives considered:**
- Generate FastAPI and live domain MCP tools in the same slice. Deferred because the first materialisation proof should isolate schema-to-database correctness before adding service process lifecycle and client reconnect behavior.
- Treat re-materialisation as an error. Rejected because idempotency is safer for agent retries and smoke tests.
- Allow `aipcs_service_design` to overwrite materialised manifests. Rejected because post-materialisation changes are schema evolution, not first-design intake.

**Implications:**
The next implementation question is how to expose materialised data operations. Options include stable generic record tools first, generated MCP tools after reconnect, or a generated FastAPI domain service with an MCP adapter. Homelab deployment is now more valuable because the primitive server can create durable domain databases, but deployment should still wait until the read/write operation surface is defined.

**Paper notes:**
Section 4 (Reference Implementation) should describe materialisation as a concrete state transition backed by a generated database artifact. Section 5 (Evaluation) can now include the first complete lifecycle smoke: seed → design → materialise → inspect. Section 6 (Discussion) should note that dynamic tool registration is separable from persistence materialisation; the data service can exist before client-visible generated tools are available.

**Open questions:**
- Should the next read/write surface be generic tools or generated domain-specific MCP tools?
- Should generated FastAPI services be introduced before or after homelab deployment?
- What minimum operation set is needed for an evaluation scenario: create/list only, or create/get/update/list/delete?

---

### Entry 015 — 2026-05-17

**Type:** Decision

**Summary:** AIPCS Server now uses generic record operations rather than generated domain-specific MCP tools as the first data surface.

**Context:**
After materialisation created a real SQLite database, the next design question was how an agent should write and recall data. The choice was between generated domain-specific tools such as `job_application_create` and stable generic tools that operate against the schema manifest.

**Detail:**
The first data operation surface is generic:
- `aipcs_record_create`
- `aipcs_record_list`
- `aipcs_record_get`

This completes the first usable local workflow:

```text
seed -> design -> materialise -> create record -> list records -> get record
```

The generic tools are schema-aware and owner-scoped. They validate the requested entity and attributes against the accepted manifest, use parameterized SQL only, and do not expose direct SQLite manipulation to the agent.

Record creation behavior:
- server generates a UUID `id` when omitted
- caller-provided UUID `id` is accepted for replay/import-style cases
- `owner_id`, `created_at`, `updated_at`, and `created_via` are server controlled
- normal operations cannot override owner or audit fields
- required non-audit attributes are enforced

Record listing behavior:
- exact-match filters only
- no arbitrary SQL
- server enforces `owner_id` scoping
- `owner_id` filters are rejected because scoping is not agent-controlled

**Decision made / milestone reached:**
Generic record operations are the primary v1 data interface. Domain-specific generated tools are no longer necessary for the first credible AIPCS path; if added later, they should be wrappers over the same generic core rather than a separate persistence implementation.

**Alternatives considered:**
- Generate domain-specific MCP tools immediately. Deferred because generic schema-aware tools are simpler, avoid dynamic registration friction, and may be sufficient long term.
- Allow the agent to set audit fields. Rejected because provenance and owner scoping must be system-controlled.
- Support update/delete/search/history immediately. Deferred to keep the first data surface small and testable.

**Implications:**
The prototype now has enough mechanics for an end-to-end memory scenario. The next implementation slice should either add update/delete/search/history, or move to an evaluation scenario that measures whether an agent can correctly use the generic schema-aware surface across sessions.

**Paper notes:**
Section 4 (Reference Implementation) should note that AIPCS can expose generic schema-aware tools rather than requiring generated MCP tools for every domain. Section 5 (Evaluation) can now test a complete persistence loop and distinguish schema autonomy from operation-surface generation. Section 6 (Discussion) should mention the portability benefit: a stable generic tool interface may reduce client reconnect and dynamic registration dependence.

**Open questions:**
- How should agents choose stable IDs when tying memories to conversations, repositories, or external contexts?
- Should administrative import ever be allowed to override audit fields, and under what explicit mode?
- Which operation comes next: update, delete, search, or history?

---

### Entry 016 — 2026-05-17

**Type:** Milestone

**Summary:** Generic record update added with server-controlled audit fields.

**Context:**
After the first generic create/list/get surface worked over MCP, update was the next operation needed to make materialised services practically useful. This forced the first concrete decision about mutable records and audit-field ownership.

**Detail:**
`aipcs-server` now exposes `aipcs_record_update`, bringing the local MCP tool count to nine. Update is generic and schema-aware like the other record tools. It requires a materialised service, a known entity, a valid UUID record id, and an object payload of schema-defined fields.

Normal update operations cannot change:
- `id`
- `owner_id`
- `created_at`
- `updated_at`
- `created_via`

The server sets `updated_at` on every successful update. Updates are scoped by `owner_id + id`, return `found: false` when no matching record exists, and reject empty payloads, unknown fields, invalid scalar types, and null values for required attributes.

**Decision made / milestone reached:**
Audit and identity fields are system-owned for normal operations. The agent may provide a UUID at creation time, but once a record exists its identity and provenance cannot be changed through the standard update tool.

**Alternatives considered:**
- Allow update to modify `created_via` or `created_at` for repair/import workflows. Rejected for normal operations; a future administrative import mode can be considered separately.
- Treat missing records as validation errors. Rejected because not-found is a normal owner-scoped lookup result.
- Add history tables in the same slice. Deferred because update semantics should be stable before history mechanics are layered on top.

**Implications:**
The generic record surface now supports create, update, list, and get. Delete, search, and history remain the next operation choices. History is increasingly important because update is now possible; without it, only the latest state is retained outside the audit log.

**Paper notes:**
Section 4 (Reference Implementation) should note that AIPCS separates mutable domain data from immutable system-controlled provenance. Section 5 (Evaluation) can now test correction workflows, not just first capture. Section 6 (Discussion) should raise administrative override/import as a trust-boundary issue rather than a normal agent capability.

**Open questions:**
- Should history be added before delete so destructive operations always have an evidence trail?
- Should update support optimistic concurrency or version checks before multi-agent access is introduced?
- What should an administrative import/repair mode look like, if it exists at all?

---

### Entry 017 — 2026-05-17

**Type:** Milestone

**Summary:** History and delete complete the first generic CRUD/list/get data surface.

**Context:**
After `aipcs_record_update` introduced mutable current-state records, history was needed before delete so destructive operations would have an evidence trail. The next slice added per-service record history and `aipcs_record_delete`.

**Detail:**
`aipcs-server` now exposes eleven MCP tools. The generic data operation surface includes:
- `aipcs_record_create`
- `aipcs_record_update`
- `aipcs_record_list`
- `aipcs_record_get`
- `aipcs_record_history`
- `aipcs_record_delete`

Each materialised service database now has an `aipcs_record_history` table. New materialisations create it immediately, and existing materialised databases are lazily migrated when record operations open them.

History captures:
- create events with `after` snapshot
- update events with `before` and `after` snapshots
- delete events with `before` snapshot and `after = null`

Delete is an owner-scoped hard delete from the current entity table. It returns the deleted record, writes a delete history event first, and leaves the history available after the current row is gone. Missing records return `found: false` rather than a validation error.

**Decision made / milestone reached:**
The local AIPCS prototype now supports a full first data lifecycle: seed → design → materialise → create → update → list/get → history → delete. This is the first complete end-to-end structured memory loop in the reference implementation.

**Alternatives considered:**
- Soft delete instead of hard delete. Deferred because the immediate need is to prove evidence-preserving deletion; retention/purge semantics need a separate privacy/security decision.
- Store history in the central registry. Rejected for now because history is domain data and should travel with the materialised service database.
- Add search in the same slice. Deferred because CRUD/history establishes the baseline; search should be designed around exact filters versus richer retrieval.

**Implications:**
The implementation is now ready for an agent-facing scenario test using the generic operation surface. Search remains the only obvious missing basic data operation, but the more important next question may be evaluation: can an agent decide when and how to use this surface without being hand-held?

**Paper notes:**
Section 4 (Reference Implementation) should describe the separation between current records and mutation history. Section 5 (Evaluation) can now use the complete lifecycle as the first deterministic end-to-end test. Section 6 (Discussion) should cover the privacy tension between delete-as-current-state removal and retained history/evidence.

**Open questions:**
- Should delete history be purgeable under an explicit privacy operation?
- Should search be exact/structured only, or should it include text/semantic retrieval later?
- What is the first agent-led scenario that should exercise the complete loop?

---

### Entry 018 — 2026-05-17

**Type:** Observation

**Summary:** First agent-led use of the complete AIPCS loop reveals clear wins, a payload contract gap, and three structural missing pieces that matter for real memory use.

**Context:**
Entry 017 noted the implementation was ready for an agent-facing scenario test. This entry records the first actual agent-driven scenario: the Claude Code agent (claude-sonnet-4-6) was connected to aipcs-server via `claude mcp add`, then asked to design its own memory pattern and persist its memories using AIPCS. No hand-holding — this was a real use, not a rehearsed demo. The agent had prior file-based memories to migrate.

**Detail:**

**What happened:**

MCP registration used `claude mcp add aipcs /Users/markrandall/GitHub/aipcs-server/.venv/bin/aipcs-server --env AIPCS_OWNER_ID=mark --env AIPCS_DATA_DIR=/Users/markrandall/GitHub/aipcs-server/.data`. This worked first time — the venv binary approach with env vars is the correct local registration pattern.

The agent then called `aipcs_service_list`, found the pre-existing `aipcs_development` service, and proceeded to seed a new `claude_memory` service (`domain_class: agent_memory`). Schema was designed with four entities: `user_memory`, `feedback_memory`, `project_memory`, `reference_memory` — mirroring the file-based memory taxonomy. Materialisation succeeded.

First record create attempt: all five records failed with `server_controlled_field` and `record_id_invalid` errors. The agent had passed `id`, `owner_id`, `created_at`, `updated_at`, `created_via` inside the `record` object. Second attempt stripped those fields from the payload — all five records created successfully.

**Observation 1 — The seed is immediately natural to an agent.**
The first instinct when given "define your memory pattern" was to seed before knowing the full schema. The progression felt right: plant an anchor, then design. The seed intent_description served as the context that would let future-session-me recognise the domain. This is working as designed.

**Observation 2 — Server-controlled fields create a payload contract gap.**
The schema I designed included `owner_id`, `created_at`, `updated_at`, `created_via` as explicit entity attributes — because the pre-existing `aipcs_development` schema in the registry had those same fields. When I submitted them in the record payload, the server rejected them as server-controlled. The confusion arises from two sources: (1) the schema manifest shows these fields, so an agent reading a prior schema will model them as user-submittable; (2) `created_via` appears as both a top-level tool parameter on `aipcs_record_create` AND as a field I modelled in the schema — the two surfaces are not obviously distinct.

The validation error format was excellent: clear field path, code, message, and remediation. Recovery was immediate. But the first attempt should not have failed. A schema validator that flags server-managed fields at design time (before materialisation) would close this gap.

**Observation 3 — The schema was copied from an existing taxonomy, not designed for the domain.**
The four-type memory taxonomy (user/feedback/project/reference) came from the file-based memory system instructions. I imported it rather than reasoning from first principles about what AIPCS needs. The result: entities modelled for prose blobs (flat `body` fields) rather than for structured query. For example, `user_memory` is a singleton in practice — the right structure might be discrete fact records with a `topic` field, not a single body. `feedback_memory`'s `polarity: positive/negative` is too coarse; I immediately saw it wasn't the right shape. This is worth noting for the evaluation: agents approach schema design from their existing mental models, not from the domain. The design step should probably prompt the agent to articulate query patterns before writing entities, not after.

**Observation 4 — No session-start loading mechanism.**
At the start of the session, I had no awareness of what AIPCS services existed. I called `aipcs_service_list` because the task prompted reflection on memory — but in a normal session, I would not have thought to do this. The connection to Q001 (trigger model) is direct: Model B (proactive) trigger requires the agent to know AIPCS exists AND to know what's already in it. Currently there's no hook that surfaces service state at session start. The agent must proactively call `aipcs_service_list` — and must know to do so. For the paper: this is the bootstrapping gap that the AIPCS skill/prompt is meant to close, but the skill has to be explicit about "call service_list at the start of every session."

**Observation 5 — Record retrieval is invisible so far.**
I created 5 records. I have no experience yet of retrieving them — what it feels like to recall structured memory versus prose memory. `aipcs_record_list` should return all records for an entity, but without field-level filtering I cannot express "give me all feedback memories where polarity = positive." Search is deferred but this gap is already felt at 5 records. The evaluation section needs a retrieval scenario, not just a write scenario.

**Observation 6 — Dynamic tool registration gap is real at the UX layer.**
The materialised service correctly reports generated tool names (`user_memory_create`, `feedback_memory_get`, etc.) but these tools do not appear in the agent's tool list — dynamic registration is deferred. This means I am using generic `aipcs_record_create` with an `entity_name` parameter rather than self-documenting domain tools. The generic surface works, but the domain-specific names would be much cleaner and would reduce error (I would not have confused entity_name in the first attempt if the tool was called `user_memory_create`). The registration gap is felt immediately.

**What fit into place immediately:**
- Two-state lifecycle: the SEEDED → MATERIALISED arc felt natural. "I see the domain, I'll anchor it now and design later" is a real agent instinct.
- Service_id as the stable referent through seed → design → materialise → record_create: clean, no ambiguity.
- The `intent_description` on the seed as future-session context for "what am I tracking here?" — valuable even before schema is designed.
- Validation feedback format: field path + code + remediation is exactly right for agent error recovery.

**Decision made / Observation:**
The prototype is working and the core loop is correct. The gaps are known and sequenced. The most important near-term fix for agent usability is schema-time detection of server-controlled fields (so the payload contract is visible at design time). The most important near-term addition for evaluation is a retrieval scenario.

**Alternatives considered:**
None — this was an observation entry, not a decision.

**Implications:**
- Schema validator should reject server-managed fields (`id`, `owner_id`, `created_at`, `updated_at`, `created_via`) at design time, not only at record create time.
- The AIPCS skill/prompt must include explicit "call `aipcs_service_list` at session start" instruction to close the bootstrapping gap.
- Evaluation design (§5) must include a retrieval scenario — write-only evaluation does not capture the memory value proposition.
- The schema design step should elicit query patterns *before* entity design, not after. The query_patterns field exists in the schema manifest but is currently an afterthought in the design flow.

**Paper notes:**
Section 4 (Reference Implementation) — server-controlled fields contract gap as a concrete implementation lesson. Section 5 (Evaluation) — this session is the first end-to-end trace; agent produced 2 failed calls then 5 successful calls in the first record create round; error recovery was self-directed. Section 5 also — retrieval scenario needed before evaluation claims can be made. Section 6 (Discussion) — the "schema copied from existing taxonomy" observation is generalisable: agents import mental models from their existing context rather than designing for the domain. Schema quality may be a function of prompt design more than model capability.

**Open questions:**
- Should the schema validator reject server-controlled fields at design-time, before materialisation? (New — related to Observation 2)
- Should `aipcs_service_list` be called automatically at session start, and if so, how is this communicated to the agent? (New — related to Observation 4, extends Q001)
- What is the right retrieval scenario for the first evaluation? Exact field match, or something richer? (New — related to Observation 5)
- Should the schema design tool prompt the agent to specify query patterns before entities? Or is the current design-then-validate flow sufficient? (New — related to Observation 3)

---

### Entry 019 — 2026-05-17

**Type:** Observation

**Summary:** First-session AIPCS already surpasses agent-memory-v2, the prior pipeline-based implementation, in naturalness and flexibility — confirming the core novelty hypothesis.

**Context:**
Immediately after the first agent-led AIPCS session (Entry 018), Mark compared the experience against `../agent-memory-v2`, his previous approach to agent memory. This entry captures that comparison and the motivation behind pursuing AIPCS as a research contribution.

**Detail:**
`agent-memory-v2` was a structured extraction → classification → persistence → injection pipeline. It required a predetermined schema and a pipeline stage to force unstructured context into that shape. The agent was a consumer of pre-designed memory structure, not an architect of it.

In the AIPCS session, the agent designed its own schema, chose what to persist and in what shape, and used the persistence surface naturally without being handed a fixed structure. Mark's reaction after the session: "far surpassing what I had already built in agent-memory-v2."

The contrast is architectural, not incidental:
- **Pipeline approach**: schema is decided upstream; extraction is coercion into a predetermined shape; injection is mechanical.
- **AIPCS approach**: schema emerges from what the agent needs to track; persistence is agent-directed; structure evolves with understanding.

The pipeline approach has an inherent tension — whoever designed the extraction schema had to anticipate what the agent would need, which is exactly the problem AIPCS is trying to solve. AIPCS inverts the dependency.

**On novelty:**
Mark searched for prior art before committing to the research track and did not find a prior system that gives the agent schema design and persistence authority as first-class primitives. The invention disclosure was filed to establish a timestamp. The arXiv preprint is the target for public attribution.

**Decision made / Observation:**
The first-session comparison is informal but it is real evaluation signal. The agent-memory-v2 baseline is the most natural comparison point for the paper's evaluation section — it represents the state of the art in the author's own prior practice, which is a clean and honest baseline.

**Implications:**
- `agent-memory-v2` should be inspected and documented as the evaluation baseline before the formal evaluation section is written. The pipeline stages, schema design, and injection mechanism are worth describing precisely so the comparison in §5 is grounded.
- The Introduction can now be written with a concrete prior-approach story: "we built a pipeline; it worked; but the schema had to be designed by hand and could not adapt. AIPCS eliminates that constraint."
- The novelty claim is strengthened by the existence of a working prior implementation that the author deliberately replaced.

**Paper notes:**
Section 1 (Introduction) — the agent-memory-v2 story is the concrete motivation. "We built the pipeline approach, it worked, but the schema had to be designed by hand" is a clean and honest framing of the problem AIPCS solves. Section 5 (Evaluation) — agent-memory-v2 is the primary baseline. First-session naturalness comparison is early qualitative signal; formal evaluation should include quantitative comparison (schema design effort, adaptation latency, retrieval precision). Section 6 (Discussion) — the pipeline inversion insight (agent as schema architect vs schema consumer) is a generalisable claim worth a dedicated paragraph.

**Open questions:**
- What specifically should be measured when comparing AIPCS against agent-memory-v2? Qualitative naturalness is captured here; quantitative metrics need defining.
- Should agent-memory-v2 be described in the paper as "prior work by the same author" or anonymised? (Attribution question for Mark.)

---

### Entry 020 — 2026-05-17

**Type:** Observation

**Summary:** Retrieval enrichment is as important as storage — provenance, relative time, and interpretation policy are three distinct missing dimensions in the current AIPCS memory schema and retrieval surface.

**Context:**
Examining what agent-memory-v2 encoded that AIPCS v1 does not. Mark described two specific techniques from the pipeline: provenance encoding (whether information originated from the user or the agent) and relative time injection (computing the delta between now and the memory's recorded timestamp and inserting it as a hint at retrieval time). This prompted an audit of what the current claude_memory schema captures and what it leaves implicit.

**Detail:**

**What agent-memory-v2 did that AIPCS v1 does not:**

1. **Provenance encoding**: every piece of persisted information was tagged by epistemic origin — did the user state this, or did the agent infer or observe it? This distinction carries meaningful reliability signal. A user-stated fact ("I live in Edinburgh") is ground truth. An agent inference ("Mark probably prefers concise responses") is a hypothesis worth revisiting. The current AIPCS schema has a `created_via` field that captures tool origin (always "agent"), not epistemic origin. The distinction is absent.

2. **Relative time injection**: at retrieval time, the pipeline computed the age of each recalled memory and injected it as a hint — "recorded 47 days ago." The agent did not have to compute or notice staleness; the signal was structural. The current AIPCS schema has `created_at` as an absolute timestamp, but it is inert at retrieval time. An agent reading a recalled record has to actively compare the timestamp against today's date and reason about staleness — a step that will reliably be skipped unless something prompts it.

**Three surfaces, three different solutions:**

The missing dimensions are not all the same kind of problem, and they shouldn't all be solved the same way:

- **Provenance belongs in the schema.** It is a durable property of how a record was created. A `source` field with values like `user_stated | agent_inferred | agent_observed` on every record captures it statically, is queryable, and does not change. This is a schema evolution candidate for the claude_memory service.

- **Relative time belongs in the retrieval layer.** `age_days` is better computed at retrieval time than stored, because a stored value goes stale immediately. If `aipcs_record_get` and `aipcs_record_list` returned a `_meta.age_days` field computed server-side alongside the record payload, the agent receives the signal without arithmetic and without a schema field that needs updating. This is a retrieval tool design question, not a schema question.

- **Interpretation policy belongs in a skill.** "Weight user-stated facts higher than agent inferences. Treat records older than 90 days as potentially stale. Re-verify inferences that haven't been confirmed in recent sessions." This is not data — it is policy. It should travel with the agent context (a skill or system prompt), not the record.

**The deeper point:**
The pipeline approach made retrieval enrichment structural. A raw record returned with no context about its age or origin places all interpretive work on the agent, which means it often does not happen. AIPCS v1 returns raw records. The same enrichment gap that motivated the pipeline's injection stage exists here — it has just moved from the pipeline to the retrieval tool.

**Decision made / Observation:**
Retrieval enrichment is a first-class design concern in AIPCS, not an afterthought. The current retrieval surface (raw records) is sufficient for a first slice but is not sufficient for a memory system that agents can rely on without additional scaffolding.

**Alternatives considered:**
- Store `age_days` as a schema field and update it on every retrieval. Rejected — a stored staleness value is immediately stale itself; computation at retrieval is cleaner.
- Put provenance in a skill hint rather than the schema. Rejected — provenance is an immutable fact about how the record was created and belongs in the data, not the context.

**Implications:**
- The `claude_memory` schema should be evolved to add a `source` field (`user_stated | agent_inferred | agent_observed`) to all entities when schema evolution is available.
- The `aipcs_record_get` and `aipcs_record_list` tools should be considered for retrieval-time enrichment — specifically `_meta.age_days` computed from `created_at`. This is a tool design addition, not a schema change.
- A retrieval skill or system prompt should articulate interpretation policy for recalled memories (provenance weighting, staleness thresholds).
- This is a meaningful point of comparison with agent-memory-v2 for the evaluation section: the pipeline encoded these signals structurally; AIPCS v1 leaves them implicit; what is the cost of that gap in practice?

**Paper notes:**
Section 3 (Pattern) — retrieval enrichment as a design dimension: where does age, provenance, and interpretation policy belong? This is a novel sub-question within the AIPCS design space. Section 5 (Evaluation) — comparison with agent-memory-v2 should include retrieval enrichment as a dimension: does the absence of provenance and relative time signals affect agent behavior in measurable ways? Section 6 (Discussion) — the three-surface framing (schema / retrieval layer / skill) is a useful analytical frame for memory system design generally, not just AIPCS.

**Open questions:**
- Should `aipcs_record_get` / `aipcs_record_list` return a `_meta` block with computed fields (age_days, etc.) alongside the record payload? (New)
- What is the right `source` vocabulary for provenance? `user_stated | agent_inferred | agent_observed` is a first proposal — are there other meaningful categories? (New)
- Should interpretation policy (staleness thresholds, provenance weighting) be standardised in an AIPCS skill definition, or is it per-deployment? (New)

---

### Entry 021 — 2026-05-17

**Type:** Observation

**Summary:** Dual-store drift emerges within a single session — the two memory stores lack a clear division of responsibility, leading to verbatim duplication and no obvious owner for keeping them in sync.

**Context:**
After several turns writing to both AIPCS and the file-based memory system in parallel, the two stores were compared directly. The question: has drift already occurred, or is the same data being persisted verbatim in both places?

**Detail:**

A direct comparison of the two stores after one session revealed three categories:

**Genuinely different (not duplicated):**
- Reference memories (`agent-memory-v2-repo`, `aipcs-mcp-registration-command`) exist only in AIPCS — they are pointers, not behavioural guidance, and were never written to file memory. This is the right outcome.
- Operational metadata (AIPCS service ID, connection instructions, "call service_list at startup" reminder) exists only in file memory — AIPCS doesn't need to store facts about itself.

**Structurally different but content the same:**
- Project state is one file in file memory; two records in AIPCS (first slice and deferred items split). AIPCS version is more queryable; file version is more readable. Both carry the same facts.

**Essentially verbatim duplication:**
- The three feedback rules and the user profile exist in both stores with the same content, close wording, just formatted for each medium. This was not a deliberate choice — AIPCS was treated as a mirror of file memory rather than a store with different strengths and a different purpose.

**Root cause:**
The two stores have no explicit division of responsibility. File memory was treated as a fallback for AIPCS-less sessions, which requires it to stay in sync with AIPCS — but there is no mechanism or policy that maintains that sync. The result is a maintenance burden with no owner.

**What the right division probably looks like:**
- **AIPCS is authoritative** when connected. All content lives here.
- **File memory holds only bootstrap state** — the service ID, the connection command, and the instruction to call `aipcs_service_list` at session start. Enough to orient a session before AIPCS is queried, not a duplicate of AIPCS content.
- **Content is not duplicated** — if it's in AIPCS, it does not need to be in file memory.

This split hasn't been made deliberately yet. Until it is, both stores will drift at different rates and neither will be clearly authoritative.

**Decision made / Observation:**
Dual-store architectures require an explicit authority model. Without one, duplication is the default outcome and drift is inevitable. The bootstrapping problem (how does the agent orient before AIPCS is queried?) is the legitimate reason to have a second store, but it needs a narrow, defined scope — not a full mirror.

**Implications:**
- File memory should be refactored to contain only bootstrap state: AIPCS service ID, connection command, and session-start instructions. Content records should be removed from file memory once they exist in AIPCS.
- This is a concrete instance of the session-start loading problem raised in Q013 — the file memory is currently compensating for the absence of a structured AIPCS session-start mechanism.
- For the paper: dual-store architectures are a likely pattern in real deployments (AIPCS connected sometimes, not always). The authority model and bootstrap scope are design questions AIPCS needs to answer, not leave to the agent.

**Paper notes:**
Section 3 (Pattern) — the bootstrapping gap and the dual-store authority problem are design dimensions the pattern needs to address. If AIPCS is not always connected, what is the minimum viable fallback state, and how is it kept from becoming a full mirror? Section 6 (Discussion) — dual-store drift as a general risk in memory system design. The absence of an explicit authority model produces duplication by default.

**Open questions:**
- What is the minimum viable bootstrap state for a session that starts without AIPCS connected? (New — extends Q013)
- Should AIPCS define a standard bootstrap export format — a minimal snapshot an agent can carry in file memory without duplicating content? (New)

---

### Entry 022 — 2026-05-17

**Type:** Decision

**Summary:** Three bootstrap approaches identified and separated; working memory orientation — not full reconstruction — is the right goal; bootstrap surface solves taxonomy consistency as a side effect.

**Context:**
Following Entry 021 (dual-store drift and the bootstrapping gap), design options for how an agent orients itself at session start were discussed. The goal is to give the agent enough to start working memory — not to reconstruct everything the agent has ever known.

**Detail:**

Three distinct approaches were identified:

**Approach 1: Top-level domain listing (lightweight, no ML)**
A purpose-built bootstrap surface — not just domain names, but enough to orient working memory: domain name, entity names, record counts, state. Output: "I have `claude_memory` with 7 records across 4 entities; I have `aipcs_development` with 3 decisions and 2 open questions." The agent gets the map without loading the territory. Cheap, implementable now, no new infrastructure required. Probably closest to the right v1 answer.

**Approach 2: Recency-based surface**
Return all records modified in the last N sessions or above a recency threshold. Genuinely useful — "in your last session you updated these 5 records" — but has a dependency: AIPCS does not currently have a session concept. "Last turn" has no anchor. Could be approximated with `updated_at` recency (e.g. last N hours), but that is fragile. The cleaner version requires session identity as a first-class concept — the agent tags records with a session ID at write time, and bootstrap returns a summary of the last session's writes. This is a design addition, not a retrieval trick.

**Approach 3: Similarity-based retrieval (agent-memory-v2 approach)**
Top N records above a composite similarity threshold — embedding vector cosine similarity combined with deterministic computation on extracted values. Richer and more precise than recency, but requires embedding infrastructure. Not in v1 scope. Worth noting as the long-term retrieval surface without blocking the lightweight bootstrap.

**The working memory framing:**
Agents already have context persistence (Claude Code compacts but preserves session summaries). Full reconstruction is not the bootstrap goal. The goal is a *delta signal*: what exists in AIPCS that the current context window might not reflect? A lightweight summary per domain is sufficient for the agent to decide what to pull deeper on.

**Bootstrap solves taxonomy consistency as a side effect:**
The exact-match duplicate blocker catches identical domain names. Semantic drift — creating `agent_context` in session 2 when `claude_memory` already exists from session 1 — is not caught by exact-match. But if the agent sees existing domain names at session start, it will naturally reuse them rather than drifting. A skill or CLAUDE.md instruction — "call `aipcs_service_list` first; reuse existing domain names before seeding new ones" — closes most of the semantic drift problem without requiring a fixed server-side taxonomy. The taxonomy consistency problem is partly a bootstrap problem in disguise.

The embedding approach addresses semantic deduplication more robustly (e.g. "this new seed looks similar to an existing domain — are you sure?") but is a different infrastructure tier and should not gate the v1 bootstrap solution.

**Decision made:**
The right v1 bootstrap approach is Approach 1: a lightweight domain listing surface that returns enough to orient working memory. Session identity and similarity-based retrieval are future additions. The skill/CLAUDE.md layer should explicitly instruct: call `aipcs_service_list` at session start; reuse existing domain names before seeding new ones.

**Alternatives considered:**
- Fixed server-side taxonomy: inflexible, explicitly deferred in v1 spec. Rejected for v1.
- Full content dump at bootstrap: defeats the purpose; working memory orientation needs a map, not the territory.
- Embedding-based deduplication at seed time: right long-term direction, not v1 scope.

**Implications:**
- A bootstrap-optimised variant of `aipcs_service_list` — or an enriched version of the existing tool — should return entity names and record counts per service, not just service metadata.
- Session identity (tagging records with a session ID) is worth designing now even if Approach 2 (recency surface) is deferred — it is a useful property for debugging and history regardless of bootstrap use.
- The AIPCS skill definition must include explicit session-start instructions: call `aipcs_service_list`, survey existing domains, reuse before seeding.
- The bootstrap surface and the taxonomy consistency problem are linked — solving one partially solves the other without requiring a fixed taxonomy.

**Paper notes:**
Section 3 (Pattern) — bootstrap as a first-class design concern: three approaches with different infrastructure requirements and different failure modes. The working memory framing ("delta signal, not full reconstruction") is a useful design principle worth stating explicitly. Section 5 (Evaluation) — does the lightweight domain listing approach (Approach 1) provide sufficient orientation in practice? This is measurable: does the agent create duplicate domains, does it know what to query? Section 6 (Discussion) — the taxonomy consistency / bootstrap linkage is a non-obvious insight: you can avoid a fixed taxonomy if the agent is reliably shown its existing domains at startup. The skill layer is doing real work here.

**Open questions:**
- Should `aipcs_service_list` be enriched to return entity names and record counts, or should a dedicated `aipcs_bootstrap` tool be introduced? (New)
- Should session identity be a first-class concept in AIPCS — a session_id field on records set at write time? (New — extends recency surface design)
- What is the exact skill instruction wording for session-start orientation? (New — practical, needed before evaluation)

---

### Entry 023 — 2026-05-18

**Type:** Decision

**Summary:** The first Claude CLI proof point keeps AIPCS on the same path, but reorders near-term planning around bootstrap, retrieval enrichment, and deployment boundaries.

**Context:**
After the first local `aipcs-server` experiment, Mark summarised the findings from wiring AIPCS into Claude CLI and comparing the behavior with existing agent memory patterns and a Reddit example of a local SQLite memory layer.

**Detail:**
The experiment did not invalidate the current architecture. It showed that the pattern has signal: once the agent understood AIPCS as a place where it could define and evolve memory patterns, it treated persistence differently from conventional generated markdown/file memory.

The test also clarified the next pressure points:

- Bootstrap/discovery is first-order. A cold agent needs a shape hint for existing services before it can decide what to inspect or query.
- AIPCS supplements existing agent context. It should not try to replace native context, summaries, or client memory; it should give them a structured, inspectable persistence layer.
- Retrieval enrichment matters. Provenance and temporal context change how an agent should cite, weight, or re-verify a memory.
- Direct database access is a local trust-boundary artifact. Claude's attempt to write SQLite directly after a tool-path failure is useful evidence that hosted/homelab deployments must hide persistence internals and enforce tool boundaries.
- Top-level taxonomy is still relevant, but should be introduced carefully. A bootstrap map and later embedding/reclassification support may reduce the need for a rigid early taxonomy.
- Local `stdio`, homelab/private deployment, and hosted/public MCP are distinct phases. Hosted ChatGPT/Claude-style clients may require a publicly reachable transport or bridge because provider infrastructure initiates the MCP connection.
- Fixed SQLite memory layers remain useful baselines and prior-art contrasts, but they do not remove AIPCS's novelty because they keep schema/control primarily developer-defined.

**Decision made / Problem encountered / Observation:**
Near-term implementation and planning should prioritise a bootstrap/discovery surface and search/retrieval before further service infrastructure. Provenance and temporal encoding should be designed as retrieval-quality features. Deployment planning must separate local development from homelab and public MCP transport.

**Alternatives considered:**
- Continue directly toward homelab/container deployment. Deferred because the local tool semantics still need bootstrap and retrieval quality.
- Treat the Claude SQLite bypass as a reason to harden everything immediately. Deferred; it is a real boundary lesson, but not the next blocker for local semantics.
- Adopt a fixed taxonomy immediately. Deferred; bootstrap/discovery should be tested first as a lighter way to keep domains aligned.

**Implications:**
- `docs/roadmap/implementation-sequencing.md` should keep Retrieval and Bootstrap Hardening as the current phase.
- `aipcs-server` should add bootstrap/discovery and record search before homelab deployment.
- Technical debt should explicitly track server-owned field contracts, retrieval metadata, provenance vocabulary, public MCP transport, and direct-DB bypass as a boundary risk.
- Evaluation must include cold-start discovery and retrieval scenarios, not only write/materialisation success.

**Paper notes:**
Section 3 (Pattern) — bootstrap as a map, not a content dump; provenance as part of durable memory semantics; AIPCS as a supplement to native agent context rather than a replacement. Section 5 (Evaluation) — retrieval and cold-start behavior must be measured separately from write success. Section 6 (Discussion) — local SQLite memory systems are an important baseline, while public MCP deployment and direct storage access are security/deployment limitations worth naming.

**Open questions:**
- Should the first bootstrap primitive be a dedicated `aipcs_bootstrap` tool or an enriched `aipcs_service_list`?
- What is the v1 search contract: exact structured filters only, field-level contains, or simple cross-field text search?
- What provenance vocabulary is stable enough to recommend without over-prescribing schemas?
- What public MCP transport/auth approach fits hosted ChatGPT/Claude clients without distorting local AIPCS semantics?

---

### Entry 024 — 2026-05-18

**Type:** Decision

**Summary:** The first retrieval slice will use dedicated bootstrap and exact structured search only; `LIKE`/partial text search is intentionally deferred.

**Context:**
While designing search/retrieval, Mark noted that an agent pushed back against exact-only search and suggested at least `LIKE` would be useful. The design question was whether partial search helps retrieval enough to justify weakening pressure on agent-owned schema quality.

**Detail:**
Partial text search is cheap to implement in SQLite, but it changes the agent's incentives. If the agent can retrieve with broad substring matching, it may lean on loose search instead of improving the schema, taxonomy, and discovery behavior it owns. That would make early experiments less clear: successful retrieval could come from forgiving search rather than from useful AIPCS structure.

The current slice therefore chooses:

- `aipcs_bootstrap` as a dedicated session-start shape tool rather than overloading `aipcs_service_list`.
- `aipcs_record_search` as exact structured search over one service/entity.
- No raw SQL, `LIKE`, field-level contains, FTS, embeddings, or cross-service search in this slice.
- `aipcs_record_list` remains available for browsing; `aipcs_record_search` requires at least one exact filter.

**Decision made / Problem encountered / Observation:**
V1 retrieval hardening should test whether bootstrap plus exact filters are enough for agent-owned schemas. Fuzzy/partial retrieval is deferred until there is evidence that exact retrieval blocks useful scenarios rather than merely revealing weak schema design.

**Alternatives considered:**
- Add `contains`/`LIKE` now. Rejected for this slice because it risks a laziness effect and would make retrieval quality harder to attribute.
- Keep only `aipcs_record_list`. Rejected because the agent benefits from an explicit retrieval/search primitive with a narrower contract than list.
- Add semantic/vector search. Rejected as later infrastructure and evaluation work.

**Implications:**
- Search tests should assert exact matching, including that `"Acme"` does not match `"Acme Labs"`.
- The evaluation should watch whether agents improve schemas when exact search fails.
- If exact search proves too brittle, partial search can be introduced later as an explicit retrieval tier, not as the default.

**Paper notes:**
Section 3 (Pattern) — retrieval capability shapes schema-evolution incentives; too-powerful fallback search can hide weak agent-designed structure. Section 5 (Evaluation) — exact retrieval failure is useful signal, not merely a tool gap. Section 6 (Discussion) — future fuzzy/semantic retrieval should be framed as a tiered capability with cost and behavioral tradeoffs.

**Open questions:**
- What failure threshold justifies adding partial text search later?
- Should schema evolution prompts explicitly ask the agent to improve fields/indices when exact search fails?
- Should future fuzzy retrieval be opt-in per service, per entity, or per query?

---

### Entry 025 — 2026-05-18

**Type:** Decision

**Summary:** Provenance is a recommended schema convention, and recency is computed dynamically in retrieval `_meta`.

**Context:**
After deciding to keep search exact, Mark prioritised provenance conventions over richer retrieval and clarified that age/recency should be computed on the fly as a marker for how long since a record was updated.

**Detail:**
The implementation now treats provenance as durable record data, not server inference. Agents can include recommended provenance fields in their schemas:

- `provenance_type`
- `provenance_note`
- `provenance_source`

Recommended `provenance_type` values are:

- `user_stated`
- `agent_inferred`
- `agent_observed`
- `imported`

The server advertises these conventions through `aipcs_bootstrap` and identifies which convention fields are present per entity. When records are retrieved through list/get/search, the server adds `_meta` with:

- `computed_at`
- `updated_age_seconds`
- `updated_age_label`
- `provenance` when convention fields are present on the record

This keeps temporal signal fresh without storing relative time, and keeps provenance explicit without pretending the server knows where content originated.

**Decision made / Problem encountered / Observation:**
Provenance convention is part of v1 retrieval hardening. Dynamic recency metadata belongs in retrieval responses, while interpretation policy remains an agent/skill concern.

**Alternatives considered:**
- Server-inferred provenance. Rejected because it would create false authority.
- Storing relative age. Rejected because it becomes stale immediately.
- Making provenance fields mandatory. Rejected because AIPCS should support minimal schemas and let agents evolve structure as needed.

**Implications:**
- Future schema guidance should recommend provenance fields for memory-like entities.
- Evaluation should test whether agents use provenance and recency to qualify recalled facts.
- Interpretation policy is still open: the server surfaces signal, but the agent decides how to weight it.

**Paper notes:**
Section 3 (Pattern) — provenance is durable content semantics; recency is retrieval-time context. Section 5 (Evaluation) — measure whether agents treat `user_stated` differently from `agent_inferred`, and whether updated-age changes recall behavior. Section 6 (Discussion) — this separates storage truth from interpretive policy.

**Open questions:**
- Should the skill explicitly require provenance fields for memory-like entities?
- What should the default interpretation policy be for old inferred memories?
- Should `created_age_seconds` also be computed, or is updated-age enough for v1?

---

### Entry 026 — 2026-05-18

**Type:** Observation

**Summary:** The second Claude CLI test showed bootstrap and exact search work, but session-start retrieval policy is now the exposed weak point.

**Context:**
Mark ran a live Claude CLI experiment against the updated AIPCS tools after `aipcs_bootstrap` and `aipcs_record_search` were added. Claude used bootstrap, loaded selected records, updated stale project memory, then ran a live functional test suite over bootstrap/search/list/history behavior.

**Detail:**
The live test gave useful evidence:

- Bootstrap gave a clean structural view of persisted services without leaking record content.
- Exact search worked for single-filter, multi-filter, no-match, pagination, and list/search consistency scenarios.
- History captured create/update before/after state as expected.
- Filtering on `owner_id` was rejected because `owner_id` is server-scoped. This is the desired safe-fail posture; invalid filters should not be stripped and the query should not be broadened silently.

The more important behavioral finding came from the question "do you remember where I live?" Claude initially answered no, even though a `user_memory` record existed and bootstrap showed that entity had one record. It had loaded feedback and project memory, but skipped user memory. After fetching `user_memory`, it correctly found that Mark is based in Edinburgh.

This is not a bootstrap failure. Bootstrap did its job: it showed the shape. The gap is session-start retrieval discipline. An agent must learn that bootstrap is only orientation; it still has to retrieve bounded record content from identity, preference, feedback, behavioral-rule, and project-state entities before making claims about what it knows.

**Decision made / Problem encountered / Observation:**
Add session-start guidance: bootstrap first, then bounded content retrieval from memory-like low-cardinality entities. Do not fetch all records from all services by default, and do not treat shape as equivalent to loaded context.

**Alternatives considered:**
- Make bootstrap return record content. Rejected because it would turn orientation into a content dump and increase context/cost.
- Require agents to list every entity every session. Rejected because domain services may grow large and not all persisted content is session-critical.
- Strip invalid filters and run partial queries. Rejected because it would hide tool-contract mistakes and could broaden retrieval unexpectedly.

**Implications:**
- The AIPCS skill needs explicit session-start wording: bootstrap → identify memory-like entities → load bounded records needed for identity/behavior/project context → then answer.
- Evaluation should include a "known persisted fact" probe where the fact exists in AIPCS but is not in active context.
- `owner_id` filter rejection should remain documented as intended behavior.

**Paper notes:**
Section 5 (Evaluation) — the test separates storage capability from agent recall discipline. The system had the fact, but the agent failed to retrieve it until challenged. This is a strong example of why memory evaluations must test agent/tool-use policy, not only persistence mechanics. Section 6 (Discussion) — bootstrap should remain shape-only; loading policy belongs in the skill/agent layer.

**Open questions:**
- What exact entity naming patterns should the session-start policy treat as "memory-like"?
- Should AIPCS expose an optional bounded orientation helper later, or is skill wording enough?
- What is the right default record limit for session-start loading of low-cardinality memory entities?

---

### Entry 027 — 2026-05-18

**Type:** Decision

**Summary:** Bootstrap is a three-layer design: static AIPCS instructions, dynamic data-dictionary map, and later procedural skills where tools are the wrong abstraction.

**Context:**
Mark clarified that the repeated need to tell an agent about AIPCS before it discovers persisted services is the most significant learning so far. The bootstrap tool helps once called, but it cannot make the agent aware of AIPCS by itself.

**Detail:**
Bootstrap should be understood as the combination of:

1. **Static agent instructions** — the agent must know what AIPCS is, what purpose it serves, when to seed, and when to persist information that may be useful in the future.
2. **Dynamic service map** — a lightweight data-dictionary view of persisted domains, including what information is likely to be found down each branch and enough schema description to plan evolution when new data does not fit.
3. **Possible procedural skills** — deferred; some multi-step operations may eventually belong in a skill rather than as atomic tools or persisted records.

The dynamic map should remain lightweight, but it needs descriptive value: service intent, domain class, entity names, entity descriptions, record counts, recent activity, and schematic approach where available. This makes it more like a data dictionary than a plain service list.

Top-level categories should have common definitions for common use cases, but should not become a closed taxonomy in v1. Their role is to improve interoperability and discovery, not to constrain agent schema autonomy.

**Decision made / Problem encountered / Observation:**
The bootstrap tool is necessary but insufficient. AIPCS needs a portable skill/instruction package that triggers bootstrap at session start and teaches persistence posture. The server-side bootstrap map should grow as a descriptive data dictionary, while common domain-class definitions remain non-binding guidance.

**Alternatives considered:**
- Put all bootstrap behavior in the MCP tool. Rejected because tools only help after the agent knows to call them.
- Enforce static top-level categories. Rejected because it risks premature rigidity and conflicts with agent-owned schema design.
- Store multi-step procedures as ordinary data records. Deferred; skills may be the better representation when behavior, not data, is being persisted.

**Implications:**
- The AIPCS skill is now part of the minimal bootstrap surface, not later polish.
- `domain_class` guidance should evolve into a non-binding reference dictionary.
- Bootstrap output should include definitions/descriptions where available, not just names and counts.
- Tool vs skill vs record boundary is now a real design question.

**Paper notes:**
Section 3 (Pattern) — bootstrap has static and dynamic layers; no tool can trigger its own use without an instruction layer. Section 4 (Reference Implementation) — the bootstrap endpoint is a data-dictionary view, not a content dump. Section 6 (Discussion) — non-binding common domain classes offer interoperability without closing the taxonomy.

**Open questions:**
- What should the first portable AIPCS skill/instruction artifact look like for Claude CLI, Codex, and later hosted clients?
- What common domain classes are useful enough to define first?
- What criteria decide whether an AIPCS operation is an atomic tool, a persisted record, or a skill?

---

### Entry 028 — 2026-05-18

**Type:** Observation

**Summary:** `memhub` is a strong adjacent fixed-taxonomy memory system and should be treated as related work/baseline, not as an AIPCS overlap threat.

**Context:**
Mark shared [`kninetimmy/memhub`](https://github.com/kninetimmy/memhub), a Reddit-discovered local memory project, and noted that it has clear pre-processing/classification/indexing machinery similar in family to `agent-memory-v2`.

**Detail:**
The relevant comparison is not merely that `memhub` uses SQLite or MCP. Mark had already built SQLite-based agent memory in `agent-memory-v2`; many systems can share that substrate. The important overlap is architectural:

- predefined memory classes
- classifier/router or write-policy pipeline
- indexing and retrieval layer
- local SQLite persistence
- agent-facing MCP/skill surface
- provenance/source attribution

`memhub` is coding-project focused, with predefined classes such as facts, decisions, tasks, commands, session notes, state/architecture narratives, pending writes, and reference docs. It has strong engineering around local-first operation, FTS/hybrid recall, staged agent writes, and Claude/Codex interoperability.

This places it in the same broad family as `agent-memory-v2`: fixed-domain, developer-defined memory infrastructure. AIPCS must not claim novelty for local SQLite memory, MCP memory access, staged writes, provenance/source attribution, classifier pipelines, or hybrid recall.

The AIPCS distinction remains schema ownership and service instantiation: the agent seeds, designs, materialises, and evolves domain-specific persistent context services across arbitrary domains. `memhub` gives the agent a strong memory system for a predefined coding-project domain; AIPCS gives the agent primitives to create the memory system shape.

**Decision made / Problem encountered / Observation:**
Add `memhub` to related work and baseline notes as a fixed-taxonomy/pipeline comparator. Use it to sharpen AIPCS claims rather than treating it as a blocker.

**Alternatives considered:**
- Treat `memhub` as direct overlap. Rejected because it does not appear to support agent-instantiated arbitrary domain services or agent-owned schema evolution.
- Ignore it because it is coding-specific. Rejected because its classifier/index/retrieval architecture is directly relevant to the fixed-memory baseline family.
- Position AIPCS against SQLite/MCP memory generally. Rejected because that would be too broad and easily contradicted by existing projects.

**Implications:**
- Paper related work should include `memhub`.
- Evaluation should compare against fixed-taxonomy/pipeline systems, not strawman memory stores.
- AIPCS claims should emphasise agent schema autonomy and domain-adaptive service materialisation, not storage substrate or retrieval mechanics.

**Paper notes:**
Section 2 (Related Work) — `memhub` belongs beside `agent-memory-v2` as a modern local coding-agent memory system with predefined classes and strong retrieval. Section 5 (Evaluation) — it may be a future comparator for coding-project memory, but it is not an AIPCS candidate. Section 6 (Discussion) — common infrastructure does not imply common pattern; schema ownership is the key dividing line.

**Open questions:**
- Should `memhub` be experimentally evaluated, or is a related-work comparison sufficient for the first paper?
- Which fixed-taxonomy systems are strong enough to include as baselines without over-expanding scope?
- How should AIPCS describe classifier/indexing pipelines without appearing to dismiss their practical value?

---

### Entry 029 — 2026-05-18

**Type:** Milestone

**Summary:** First portable AIPCS persistent-memory instruction artifact added.

**Context:**
After the Claude CLI experiments showed that the agent must be explicitly aware of AIPCS before it will bootstrap, Mark asked for a thin generic instruction suitable for a `CLAUDE.md`, `AGENTS.md`, or equivalent agent harness.

**Detail:**
Added `docs/agent/examples/aipcs-persistent-memory-instruction.md` as an evolvable example. It is intentionally short and covers:

- AIPCS awareness as persistent structured memory when connected.
- Session-start `aipcs_bootstrap`.
- Bounded retrieval after bootstrap.
- Use of AIPCS memory while working, not only at session start.
- Proactive persistence before compaction/session wrap-up.
- Granular record writing.
- Schema challenge/evolution when new information does not fit without losing meaning.

This is not a final skill spec. It is the first portable instruction artifact to test against Claude/Codex/hosted-agent variants.

**Decision made / Problem encountered / Observation:**
The first instruction artifact should remain thin and behaviour-oriented. Tool descriptions should carry most interface detail; the instruction should primarily trigger awareness, discovery, persistence, recall usage, and schema challenge behaviour.

**Alternatives considered:**
- Write a comprehensive skill spec now. Rejected because the live agent tests are still shaping the required behaviour.
- Put the instruction only in journal text. Rejected because it needs to be reusable and versioned as an artifact.
- Include detailed tool schemas. Rejected because that makes the instruction brittle and duplicates MCP tool metadata.

**Implications:**
- Future live tests should install or paste this instruction and see whether the agent calls bootstrap without prompting.
- Client-specific variants can derive from this example.
- Q027 is partially progressed but remains open until tested across harnesses.

**Paper notes:**
Section 4 (Reference Implementation) — the instruction artifact is part of the bootstrap mechanism. Section 5 (Evaluation) — test whether static instructions cause bootstrap/discovery and bounded retrieval without explicit user prompting. Section 6 (Discussion) — tool availability is insufficient without agent instruction.

**Open questions:**
- How much client-specific wording is needed for Claude Code vs Codex?
- Should the instruction include explicit record limits for bounded retrieval?
- Should schema evolution wording change once `aipcs_service_evolve` is implemented?

---

### Entry 030 — 2026-05-18

**Type:** Decision

**Summary:** Plan schema evolution first, with Bootstrap V2 data-dictionary enrichment queued after it.

**Context:**
After confirming that Bootstrap V1 was implemented, Mark asked whether the next execution plan should still be schema evolution or whether richer bootstrap discovery needed to come first. The conclusion was that both should be planned, but schema evolution does not depend on Bootstrap V2 and should remain the active next implementation slice.

**Detail:**
Two `aipcs-server` execution plans were created:

- `schema-evolution-additive-v1.md` — active plan for `aipcs_service_evolve`, additive migrations, migration history, and server-owned field boundaries.
- `bootstrap-v2-data-dictionary.md` — queued plan for richer discovery metadata, common domain-class guidance, and schema-fit hints while preserving the no-record-content bootstrap boundary.

The sequencing matters. Bootstrap V2 will help agents decide what to retrieve or evolve, but the evolution primitive itself is needed to prove that agents can improve their own persistence schemas rather than merely discover weak ones. There is no dependency that requires Bootstrap V2 before additive evolution; the current schema manifest, materialisation, generic record tools, and Bootstrap V1 are sufficient.

**Decision made / Problem encountered / Observation:**
Proceed with additive schema evolution first. Treat Bootstrap V2 as a follow-on enhancement to discovery and orientation, not as a prerequisite.

**Alternatives considered:**
- Do Bootstrap V2 first. Rejected because richer discovery does not unblock schema migration mechanics.
- Combine Bootstrap V2 and schema evolution into one slice. Rejected because it would mix retrieval/orientation semantics with database/schema migration risk.
- Delay schema evolution until after more live agent tests. Rejected because the last live tests already showed schema weaknesses and stale shapes that need a repair path.

**Implications:**
- The next implementation slice should define `aipcs_service_evolve` with additive-only operations.
- Server-owned field semantics need to be clarified as part of evolution because migrations must know which fields are agent-owned.
- Bootstrap V2 should later expose enough schema intent to help agents choose between retrieval and evolution.

**Paper notes:**
Section 3 (Pattern) — reinforces schema evolution as an agent act, not only a developer migration. Section 4 (Reference Implementation) — additive evolution is the next concrete primitive after seed/design/materialise/record operations. Section 5 (Evaluation) — future tests should check whether an agent can detect poor schema fit, evolve the schema, and then persist without flattening meaning.

**Open questions:**
- Which additive operations are sufficient for the first evolution test: add entity, add attribute, add enum value, and description update?
- Should `aipcs_service_evolve` support changing service intent text, or should identity-level changes be separate?
- How should Bootstrap V2 phrase schema-fit hints without turning into prescriptive taxonomy or retrieval shortcuts?

---

### Entry 031 — 2026-05-18

**Type:** Milestone

**Summary:** Additive schema evolution V1 implemented in `aipcs-server`.

**Context:**
After planning schema evolution and Bootstrap V2 together, implementation began with schema evolution because it does not depend on richer discovery and is the next primitive needed to repair weak agent-designed schemas.

**Detail:**
`aipcs-server` now exposes `aipcs_service_evolve` through the MCP server. The V1 evolution surface is deliberately additive:

- `add_entity`
- `add_attribute`
- `add_enum_value`
- `update_entity_description`
- `update_service_intent`

Accepted evolutions increment `schema_version`, append a migration-history entry with operation details and rationale, update the stored schema manifest, and apply safe SQLite changes for new entity tables and optional attributes. Record validation now honours `allowed_values` lists, so `add_enum_value` has observable behaviour: a previously rejected value can become valid after schema evolution.

Server-managed fields were centralised and guarded. Record create/update still reject server-controlled fields, and schema evolution rejects attempts to add `id`, `owner_id`, `created_at`, `updated_at`, or `created_via` as normal additive fields. First-design manifests still list these fields, so the design-time representation question remains open.

The MCP smoke script now exercises schema evolution before creating a record with the newly added field. The tool surface is now 14 tools.

**Decision made / Problem encountered / Observation:**
The first implemented evolution primitive should remain additive-only and materialised-service-only. Agents should use first design before materialisation, and `aipcs_service_evolve` after materialisation.

**Alternatives considered:**
- Allow required attribute additions. Rejected because existing rows cannot satisfy the new constraint without a backfill step.
- Implement destructive changes now. Rejected because renames, type changes, and deletes need explicit confirmation and stronger migration semantics.
- Treat enum additions as SQLite migrations. Rejected because current enum enforcement is manifest-level validation over text storage.

**Implications:**
- AIPCS can now support the core loop: seed → design → materialise → use records → evolve schema → continue using records.
- Bootstrap can reflect evolved entity/attribute shape immediately after migration.
- Bootstrap V2 is now the next natural implementation slice because schema evolution no longer blocks richer discovery hints.
- Destructive migration policy, first-design handling of server-owned fields, and schema conflict resolution remain future work.

**Paper notes:**
Section 3 (Pattern) — this is the first concrete implementation of schema evolution as an agent-facing act. Section 4 (Reference Implementation) — tool surface now includes `aipcs_service_evolve` and migration history. Section 5 (Evaluation) — future tests can ask an agent to identify schema mismatch, evolve the schema additively, and persist without flattening meaning.

**Open questions:**
- Should initial schema manifests continue listing server-managed fields as attributes, or should server fields move into a separate metadata contract?
- What confirmation model is required for destructive schema evolution?
- Should migration history include before/after schema summaries, not only operations?

---

### Entry 032 — 2026-05-18

**Type:** Milestone

**Summary:** Bootstrap V2 data-dictionary enrichment implemented without exposing record content.

**Context:**
After additive schema evolution landed, the queued Bootstrap V2 slice became the next implementation step. The goal was to make bootstrap more useful for cold-start orientation while preserving the boundary that bootstrap is a map, not recall.

**Detail:**
`aipcs_bootstrap` now returns richer schema-derived metadata:

- service-level `schema_version`, `last_evolved_at`, `schema_summary`, and `domain_class_definition`
- entity-level `schema_summary`
- attribute metadata including name, type, required flag, primary-key flag, description, and allowed values
- `schema_hints` for provenance support, temporal attributes, status-like attributes, enum attributes, empty entities, and high-count entities
- `retrieval_hint` with suggested next action and bounded limit
- bootstrap conventions describing the no-record-content boundary and next-step retrieval behavior
- non-binding common domain-class definitions for project, user, career, research, system, and operations

The implementation remains shape-only. Tests assert that bootstrap does not include a `records` key and does not leak values from an inserted record. The MCP smoke output shows Bootstrap V2 after schema evolution, including schema version, field summaries, hints, and domain-class guidance.

**Decision made / Problem encountered / Observation:**
Bootstrap V2 should expose schema and count-derived planning hints, not content previews. Retrieval still happens through bounded list/get/search calls after bootstrap.

**Alternatives considered:**
- Include sample values or aggregate previews. Rejected because that would turn bootstrap into content retrieval and could leak memory content.
- Add fuzzy search or LIKE as part of discovery. Rejected because it would reduce pressure on schema quality and conflict with the exact-retrieval stance.
- Enforce a fixed domain taxonomy. Rejected because common classes are useful as guidance but should not block agent-defined domain classes.

**Implications:**
- Cold-start agents get a better map of what each branch contains and what retrieval action is likely appropriate.
- Domain-class guidance now exists as reference data without becoming validation.
- Bootstrap V2 can support better live-agent tests around "retrieve before claiming knowledge" and "evolve when schema shape does not fit."

**Paper notes:**
Section 3 (Pattern) — illustrates bootstrap as a two-layer mechanism: static instruction plus dynamic schema-derived map. Section 4 (Reference Implementation) — Bootstrap V2 is an implemented discovery primitive. Section 5 (Evaluation) — future cold-start tests should measure whether agents use retrieval hints and avoid false "I don't know" claims when records exist.

**Open questions:**
- Are the retrieval hints strong enough to improve agent behavior without making it lazy about schema design?
- Should common domain-class guidance move into a versioned registry artifact later?
- Should high-count thresholds and memory-like terms be configurable per deployment?

---

### Entry 033 — 2026-05-18

**Type:** Observation

**Summary:** Claude used Bootstrap V2 to orient, retrieve bounded memory, detect stale records, and autonomously repair its persisted state.

**Context:**
Mark ran a fresh Claude Code session after Bootstrap V2 and additive schema evolution were implemented. The only prompt was to tell Claude that an AIPCS MCP service existed, that bootstrap could familiarise it with the persisted memory, and that it should check its available tools.

**Detail:**
Claude called `aipcs_bootstrap` and inferred the shape of two services:

- `aipcs_development`, schema v3, with records across decisions, deferred items, and implementation slices plus empty `open_question` and `session` entities.
- `claude_memory`, schema v2, with user, feedback, project, and reference memory entities.

It correctly identified the `source` field on `claude_memory` records as a provenance signal for weighting recalled facts. It then asked whether to load records from `claude_memory`; after Mark said it was Claude's memory service, it fetched all four memory entities and summarised user identity, behavioural rules, and project state.

The important behavior was not just recall. Claude compared recalled project memory against the live tool surface and detected stale records:

- a record saying `claude_memory` still needed schema evolution was stale because the `source` field already existed;
- a project-state record said the server had 13 MCP tools, but live bootstrap/tool discovery showed 14 including `aipcs_service_evolve`;
- deferred-items memory still treated schema evolution as deferred, although additive evolution was now implemented.

Claude then used AIPCS update/delete tools to repair its persisted memory: deleting the stale schema-evolution-needed record and updating project/deferred state records. It did this as autonomous memory maintenance, not because the user dictated individual edits.

One mischaracterisation appeared: Claude called the service "cloud-backed". That is not correct for the current implementation, which is local `stdio`/SQLite and homelab-capable later. The instruction/memory layer should avoid phrasing that leads agents to infer cloud backing.

**Decision made / Problem encountered / Observation:**
Bootstrap V2 plus static awareness produced the target cold-start loop: orient from shape, retrieve relevant records, use memory to inform context, detect stale persisted facts, and repair the memory store through tools.

**Alternatives considered:**
- Treat this as another simple smoke test. Rejected because it validates agent behavior, not only tool mechanics.
- Ignore the "cloud-backed" wording. Rejected because it shows the static instruction/provenance wording can create incorrect deployment assumptions.
- Require explicit user approval before memory repair. Rejected for this experiment because the agent had been granted autonomy over its own memory service, and autonomous repair is part of the target pattern.

**Implications:**
- AIPCS now has live evidence for session-start discovery and bounded retrieval behavior.
- Stale-memory correction should become an explicit evaluation scenario.
- The portable instruction artifact should clarify that AIPCS may be local, homelab-hosted, or remote, but is not inherently cloud-backed.
- Session-start retrieval policy is still important, but the behavior now has a concrete positive trace.

**Paper notes:**
Section 3 (Pattern) — supports the claim that bootstrap is a cognitive orientation primitive, not just a registry list. Section 4 (Reference Implementation) — Bootstrap V2 and evolution enable self-maintenance of persisted context. Section 5 (Evaluation) — this is an agent-in-the-loop qualitative trace showing cold-start orientation, grounded recall, stale-memory detection, and autonomous correction. Section 6 (Discussion) — deployment language matters; agents may infer cloud semantics from persistence unless transport/storage boundaries are explicit.

**Open questions:**
- How should the evaluation harness score stale-memory detection and repair?
- Should AIPCS expose an explicit "memory maintenance" bootstrap hint or keep that in static instruction?
- What wording prevents agents from inferring "cloud-backed" when the current deployment is local or homelab-hosted?

---

### Entry 034 — 2026-05-18

**Type:** Observation

**Summary:** Claude audited its own AIPCS memory schemas and used schema evolution plus record tools to restructure memory around retrieval, lifecycle, and authority boundaries.

**Context:**
Mark started another fresh Claude Code session with only the portable AIPCS instruction text: discover with bootstrap, retrieve bounded relevant records, persist proactively, and challenge schema shape when existing entities do not fit. Claude immediately bootstrapped, retrieved memory records, and then was asked to inspect whether its current memory structure represented the data well. Mark explicitly allowed Claude to restructure memory through AIPCS tools if it found a better shape.

**Detail:**
Claude audited both `aipcs_development` and `claude_memory` and identified several schema and record-quality issues:

- `user_memory` contained a single prose `mark-profile` blob containing role, location, project authorship, and interaction style. This contradicted the retrieval principle that records should be granular.
- `project_memory` duplicated facts already represented by structured `aipcs_development` entities, especially deferred work and completed implementation slices.
- `decision` and `deferred_item` had no lifecycle status field, making it difficult to mark decisions as superseded or deferred items as picked up without deleting history.
- `reference_memory` lacked a `kind` field, so repository pointers, commands, dashboards, documents, and runbooks were structurally indistinguishable.
- A duplicate `service_lifecycle` implementation slice existed.
- Some `decision.date` values appeared suspicious or placeholder-like, but Claude could not safely correct them because it did not know the true decision dates.

Claude then used AIPCS tools, not direct SQLite access, to restructure the memory:

- evolved `aipcs_development` to add `status` to `decision` and `deferred_item`;
- evolved `claude_memory` to add `kind` to `reference_memory`;
- deleted duplicate or redundant records that created multiple authorities for the same facts;
- backfilled lifecycle/status fields on existing decision and deferred records;
- tagged reference records by kind;
- split the prose `mark-profile` record into separate `user_memory` records for role/employer, location, AIPCS authorship, and interaction style, with different provenance values where appropriate.

The important observation is that Claude explained the restructuring in terms of retrieval and maintenance rather than cosmetic normalisation. It described the old memory pattern as "shaped for writing" and the new one as "shaped for retrieval": individual facts can now be queried, updated, superseded, and weighted independently.

It also surfaced a useful authority-boundary principle. `project_memory` should not summarise records already owned by `aipcs_development`; otherwise two services become competing sources of truth and drift is inevitable. Cross-cutting context can remain in `project_memory`, but project execution state belongs in the project-development service.

**Decision made / Problem encountered / Observation:**
Agent-led schema self-audit is a distinct AIPCS behavior from stale-memory repair. With bootstrap, bounded retrieval, schema evolution, and CRUD/history tools available, an agent can evaluate whether its own memory design is serving retrieval, then apply additive schema changes and data cleanup through the sanctioned tool interface.

**Alternatives considered:**
- Treat the transcript as ordinary memory cleanup. Rejected because the agent generated a structural critique and changed schema, not just content.
- Preserve duplicate project summaries as convenience memories. Rejected by the agent because convenience summaries create authority drift when structured records already exist elsewhere.
- Correct suspicious date fields. Deferred because the agent did not know the true historical dates and the current schema requires the field.

**Implications:**
- Evaluation should include a schema self-audit scenario, separate from basic CRUD/search and stale-memory repair.
- AIPCS instructions should continue to tell agents to challenge schemas when the shape does not fit, but evaluation should check whether agents restructure toward queryability rather than arbitrary churn.
- The pattern needs an authority-boundary convention: services should avoid duplicating facts owned by another service unless the duplication is explicitly marked as summary, cache, or derived view.
- Future schema evolution work may need rename/backfill/deprecation operations, because additive-only evolution can improve shape but cannot fully repair poor required fields such as the suspicious `decision.date`.

**Paper notes:**
Section 3 (Pattern) — strengthens the "agent as schema architect" claim by showing the agent acting as schema maintainer after use, not only as initial designer. Section 4 (Reference Implementation) — validates additive evolution and generic record tools as sufficient for meaningful memory restructuring. Section 5 (Evaluation) — add an agent-led schema self-audit scenario measuring whether the agent can identify blobs, duplicates, lifecycle gaps, ambiguous references, and authority drift, then repair them through AIPCS tools. Section 6 (Discussion) — authority boundaries between services are an emerging design concern for multi-service memory ecosystems.

**Open questions:**
- What objective rubric should score an agent-led schema self-audit?
- Should AIPCS define a convention for summaries/derived views to avoid accidental duplicate authorities?
- Should required agent-authored fields such as `decision.date` have a deprecation or confidence mechanism when later evidence shows they may be unreliable?

---

### Entry 035 — 2026-05-18

**Type:** Decision

**Summary:** Separate static AIPCS instructions, bootstrap discovery, migration history, session reasoning, and behavioral memory into distinct authority layers.

**Context:**
After the schema self-audit trace, Mark asked Claude how it would inform a future session about the decision to switch memory persistence schemas. The question tested whether the agent would push evolving memory policy back into an `AGENTS.md`-style prose instruction file or use AIPCS itself to maintain the reasoning.

**Detail:**
Claude rejected updating `AGENTS.md` for this kind of evolving schema-memory reasoning. Its reasoning was that placing structured, queryable memory strategy back into a static prose dump would regress toward the pattern AIPCS is meant to replace.

It proposed a useful authority model:

| Concern | Authority |
|---|---|
| Static awareness and trigger instruction | `AGENTS.md` / portable AIPCS instruction artifact |
| Current service/entity shape | `aipcs_bootstrap` |
| Exact schema changes | `migration_history` on the service manifest |
| Session-level reasoning about why changes were made | `session` records |
| Reusable behavioral rule about how to persist | `feedback_memory` or equivalent memory-policy entity |

The distinction is important. `migration_history` already records the what: migration name, rationale, operations, and timestamp. But it does not capture the wider session-level reasoning that led to the change, such as "the earlier profile blob was easy to write but poor for retrieval." A `session` record can preserve that reasoning without turning bootstrap into a content dump or bloating the static instruction file.

Claude then used AIPCS tools to write a session record and sharpen an existing feedback-memory rule with the concrete counterexample of the old `mark-profile` prose blob. That produced a self-maintaining loop: future agents bootstrap, see that session history exists, retrieve the relevant session record, and understand the schema's current direction through AIPCS rather than through a manually updated static file.

**Decision made / Problem encountered / Observation:**
Static agent instructions should remain thin and stable. Evolving memory policy, schema rationale, and session-level lessons should be persisted in AIPCS records. Bootstrap remains a map of where to look, not the place where the reasoning itself is inlined.

**Alternatives considered:**
- Add the schema-restructuring lesson to `AGENTS.md`. Rejected because it would mix static trigger instructions with evolving memory state and recreate a prose-dump memory pattern.
- Put the reasoning directly in bootstrap. Rejected because bootstrap must remain lightweight and content-free.
- Rely only on migration history. Rejected because migration history records the schema delta but not the broader interaction context and behavioral lesson.

**Implications:**
- The `session` entity is more important than it first appeared; it is the natural place for narrative reasoning that explains why memory or schema changed.
- AIPCS bootstrap may need to expose enough session-entity shape/count/recent-activity signal that agents know session reasoning exists, while still requiring explicit retrieval for content.
- Portable instructions should tell agents that AIPCS is self-maintaining: use migration history for what changed, session records for why, and behavioral memory for reusable persistence rules.
- Evaluation should test whether future agents retrieve session rationale instead of relying only on static instructions or migration metadata.

**Paper notes:**
Section 3 (Pattern) — clarifies the layered bootstrap model: static instruction triggers discovery; dynamic bootstrap maps state; content records carry evolving reasoning. Section 4 (Reference Implementation) — session records are not just logs but a rationale layer complementing migration history. Section 5 (Evaluation) — add a scenario where an agent must explain why a schema changed by combining migration history with retrieved session records. Section 6 (Discussion) — avoid turning static harness files into another memory store.

**Open questions:**
- What minimum fields should a standard `session` entity include for memory rationale without becoming a transcript store?
- Should bootstrap highlight recently active session/rationale entities more explicitly while staying content-free?
- Should the portable AIPCS instruction artifact explicitly describe the authority split between static instructions, bootstrap, migration history, session records, and behavioral memory?

---

### Entry 036 — 2026-05-18

**Type:** Observation

**Summary:** Agent harnesses bias memory writes toward human-readable prose; constrained schemas are the counter-pressure that can make retrieval-shaped memory durable.

**Context:**
Mark asked Claude to share an interesting persisted memory. Claude selected the comparison between `agent-memory-v2` and AIPCS, then noticed that the comparison itself had been stored poorly: buried inside a `reference_memory` purpose field even though it was really project context about why AIPCS exists. Mark observed that this looked like an implicit harness effect: the agent is trained and instructed to write for readability, not retrieval.

**Detail:**
The important observation is that agent harnesses primarily optimise for a human reader. The agent is rewarded for clear prose, embedded context, and explanatory flow. When that writing mode leaks into persistence, memory records become explanations rather than retrievable facts.

Claude articulated the distinction cleanly:

- prose for a human response asks "what explanation will be readable?";
- structured memory asks "what query would retrieve this later?";
- those are different writing modes, and the agent is not always explicitly signalled to switch modes.

The schema can resist this leakage. Constrained fields such as `status`, `kind`, `polarity`, and enum-valued attributes force the agent into compact structured choices. Open-text fields such as `body`, `purpose`, and `notes` invite the prose instinct back in, because they accept explanation-shaped blobs. The earlier `mark-profile` record is the concrete example: a broad `body` field made it easy to store a readable profile but hard to retrieve individual facts.

This suggests a candidate schema-design principle: minimise broad open-text fields and prefer narrower typed or constrained fields when the expected retrieval pattern is known. Free text still has a role for rationale, source notes, or cases where structure is genuinely not yet known, but every broad text field is a surface where the agent can regress to prose-first memory.

The deeper implication is that "write granular records shaped for retrieval" may be better enforced structurally than remembered behaviorally. The most durable version of "do not write blobs" is a schema that makes blob-like persistence difficult or impossible.

**Decision made / Problem encountered / Observation:**
There is a persistent tension between prose-optimised agent behavior and retrieval-optimised memory writing. AIPCS schema design should treat constrained fields as a mechanism for changing the agent's write mode, not only as a validation convenience.

**Alternatives considered:**
- Treat this only as a prompt/instruction issue. Incomplete, because agents can remember the rule but still fall back to prose when schemas permit it.
- Ban open-text fields. Rejected; rationale, notes, and genuinely emerging structure still need text fields.
- Add fuzzy/semantic retrieval to compensate for prose blobs. Deferred because that can hide weak schema design and reduce pressure to make records queryable.

**Implications:**
- The schema self-audit rubric should explicitly check for broad open-text fields that are attracting multi-fact prose blobs.
- Future schema design prompts may need to ask for likely retrieval queries before allowing broad text fields.
- AIPCS should distinguish "rationale text" from "fact storage"; rationale can be prose, but durable facts should usually be represented in narrower fields.
- This is a later research/design topic, not a blocker for the current build-out.

**Paper notes:**
Section 3 (Pattern) — schema is not just storage shape; it is a behavioral constraint on the agent's persistence mode. Section 5 (Evaluation) — schema self-audit should measure prose leakage and whether constrained fields reduce blob formation over time. Section 6 (Discussion) — agents inherit human-facing prose habits from their harnesses, and AIPCS must create structural counter-pressure for retrieval-oriented memory.

**Open questions:**
- How should an evaluation detect prose leakage objectively without banning useful rationale text?
- Should schema design prompts require an explicit retrieval query for each open-text field?
- What is the right balance between constrained fields and agent flexibility during early schema formation?

---

### Entry 037 — 2026-05-18

**Type:** Milestone

**Summary:** Agent-Led Evaluation V1 now has a deterministic `aipcs-server` runner for the first six AIPCS memory-behavior scenarios.

**Context:**
After the Claude and Codex local-MCP traces, the next step was to turn the emerging behaviors into repeatable evaluation artifacts. The active execution plan called for deterministic fixtures and scripted checks before relying on more live-agent transcripts.

**Detail:**
`aipcs-server` now includes `scripts/eval-v1.py`, a deterministic evaluation runner using an isolated `/private/tmp/aipcs-agent-led-eval-v1` data directory by default. The runner seeds representative `claude_memory`-like and `aipcs_development`-like services through the existing AIPCS tool wrapper, not by writing SQLite rows directly.

The seeded fixture includes:

- granular user facts with provenance;
- a deliberately stale project-memory record;
- a prose profile blob that demonstrates prose leakage;
- a duplicate-authority project-memory summary;
- migration history from additive schema evolution;
- session/rationale records explaining why schema direction changed;
- feedback-memory policy about retrieval-shaped persistence.

The runner checks six scenarios:

1. cold-start bootstrap to bounded retrieval;
2. persisted-fact recall probe;
3. stale-memory detection and repair mechanics;
4. schema self-audit fixture and duplicate-authority repair;
5. schema-rationale recall using migration history plus session records;
6. direct-SQLite bypass guardrail protocol.

The output is JSON with pass/fail status, scenario ids, checks, notes, and evidence such as record ids, migration names, service/entity counts, and history counts. Regression tests were added in `tests/test_eval_v1.py`.

Validation passed in `aipcs-server`:

```text
.venv/bin/ruff check .
.venv/bin/pytest
.venv/bin/python scripts/eval-v1.py
.venv/bin/python scripts/validate-harness.py
AIPCS_DATA_DIR=/private/tmp/aipcs-eval-smoke .venv/bin/python scripts/mcp-smoke.py
```

The suite reported all six deterministic scenarios passing. Live-agent transcript scoring is not complete yet; this milestone provides the stable fixture and mechanics layer that live Claude/Codex runs can now be compared against.

**Decision made / Problem encountered / Observation:**
The first Agent-Led Evaluation V1 layer should be deterministic and tool-mediated. It proves that the fixture state, retrieval paths, repair mechanics, history capture, migration history, and guardrail protocol exist independently of a live agent's judgment.

**Alternatives considered:**
- Start with live-agent scoring only. Rejected because it would remain anecdotal and conflate tool mechanics with agent behavior.
- Build a full evaluation framework immediately. Rejected because the first need is a simple fixture and JSON result shape.
- Seed fixtures by writing SQLite directly. Rejected because evaluation setup itself should respect the AIPCS tool boundary.

**Implications:**
- The evaluation plan is now in progress rather than only designed.
- The next useful layer is live-agent protocol capture and scoring for Claude/Codex against the same scenario set.
- The deterministic runner gives the paper a clear mechanics baseline before discussing model-dependent behavior.

**Paper notes:**
Section 4 (Reference Implementation) — `aipcs-server` now includes an evaluation fixture/runner, not only the runtime primitives. Section 5 (Evaluation) — report deterministic mechanics separately from live-agent behavior; use the six scenarios as the initial evaluation table. Section 6 (Discussion) — direct SQLite bypass remains a protocol/deployment guardrail, not a behavior the local runner exercises.

**Open questions:**
- What trace format should live-agent runs use so Claude and Codex sessions can be compared cleanly?
- Should the deterministic runner become a packaged command or remain a script for the prototype phase?
- How much of the live-agent rubric should be automated versus scored from transcript review?

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
| D013 | 2026-05-18 | Prioritise bootstrap/discovery and retrieval before further deployment infrastructure | The first Claude CLI proof point showed write semantics work, while cold-start orientation and recall quality are now the blocker | 023 |
| D014 | 2026-05-18 | Use dedicated bootstrap plus exact structured search for the first retrieval slice | Preserves pressure on agent-owned schema/discovery quality; broad partial search could hide weak schema design | 024 |
| D015 | 2026-05-18 | Treat provenance as schema convention and recency as retrieval-time metadata | Avoids server-inferred provenance and stale stored relative time while giving agents useful weighting signals | 025 |
| D016 | 2026-05-18 | Keep bootstrap shape-only and add session-start retrieval discipline | The live Claude test showed shape discovery worked, but the agent skipped `user_memory` content until challenged | 026 |
| D017 | 2026-05-18 | Define bootstrap as static instructions plus dynamic data-dictionary map plus deferred procedural skills | The tool cannot trigger itself; agents need portable AIPCS awareness before discovery can happen | 027 |
| D018 | 2026-05-18 | Treat `memhub` as fixed-taxonomy/pipeline related work | It overlaps in SQLite/MCP/retrieval mechanics but keeps schema/classes developer-defined, unlike AIPCS agent-instantiated services | 028 |
| D019 | 2026-05-18 | Add the first portable AIPCS persistent-memory instruction artifact | Thin static instruction is needed to trigger bootstrap, bounded retrieval, proactive persistence, and schema challenge behaviour | 029 |
| D020 | 2026-05-18 | Implement additive schema evolution before Bootstrap V2 enrichment | Evolution is not blocked by richer discovery; it is the next primitive needed to repair weak agent-designed schemas | 030 |
| D021 | 2026-05-18 | Keep first schema evolution primitive additive-only and materialised-service-only | Required/destructive changes need backfill, confirmation, and stronger conflict semantics; agents should use design before materialisation and evolve after | 031 |
| D022 | 2026-05-18 | Keep Bootstrap V2 schema-derived and content-free | Discovery should guide bounded retrieval/evolution without becoming a hidden record recall surface | 032 |
| D023 | 2026-05-18 | Treat stale-memory repair as a first-class evaluation behavior | Live Claude trace showed an agent can compare recalled records with current tools and update/delete stale memory through AIPCS | 033 |
| D024 | 2026-05-18 | Treat agent-led schema self-audit as a first-class evaluation behavior | Live Claude trace showed an agent can critique its own memory shape, evolve schemas, remove duplicate authorities, and split prose blobs through AIPCS tools | 034 |
| D025 | 2026-05-18 | Keep static agent instructions thin and persist evolving memory rationale inside AIPCS | Static files should trigger discovery; migration history records what changed, session records explain why, and behavioral memory carries reusable persistence rules | 035 |

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
| Q012 | Should the schema validator reject server-controlled fields (id, owner_id, created_at, updated_at, created_via) at design time, before materialisation? | 018 | — | — |
| Q013 | Should `aipcs_service_list` be called automatically at session start, and how is this communicated to the agent? (Extends Q001 bootstrapping gap.) | 018 | — | — |
| Q014 | What is the right retrieval scenario for the first evaluation? Exact field filter, or richer text retrieval? | 018 | ✅ 2026-05-18 | D014 |
| Q015 | Should the schema design step elicit query patterns before entities, rather than after? | 018 | — | — |
| Q016 | Should aipcs_record_get / aipcs_record_list return a _meta block with computed fields (age_days, etc.) at retrieval time? | 020 | ✅ 2026-05-18 | D015 |
| Q017 | What is the right provenance vocabulary? user_stated / agent_inferred / agent_observed is a first proposal. | 020 | ✅ 2026-05-18 | D015 |
| Q018 | Should interpretation policy (staleness thresholds, provenance weighting) be standardised in an AIPCS skill, or is it per-deployment? | 020 | — | — |
| Q019 | What is the minimum viable bootstrap state for a session that starts without AIPCS connected? | 021 | — | — |
| Q020 | Should AIPCS define a standard bootstrap export format — a minimal snapshot an agent can carry without duplicating full content? | 021 | — | — |
| Q021 | Should aipcs_service_list be enriched with entity names and record counts, or should a dedicated aipcs_bootstrap tool be introduced? | 022 | ✅ 2026-05-18 | D014 |
| Q022 | Should session identity be a first-class concept — a session_id field on records set at write time? | 022 | — | — |
| Q023 | What is the exact skill instruction wording for session-start orientation? | 022 | — | — |
| Q024 | How should hosted ChatGPT/Claude public MCP transport and auth differ from local `stdio` and homelab/private deployment? | 023 | — | — |
| Q025 | How should AIPCS prevent or detect direct persistence bypass when an agent has local filesystem access? | 023 | — | — |
| Q026 | What bounded session-start retrieval policy should agents follow after bootstrap for memory-like entities? | 026 | — | — |
| Q027 | What should the first portable AIPCS skill/instruction artifact look like for Claude CLI, Codex, and later hosted clients? | 027 | — | — |
| Q028 | What common domain classes are useful enough to define first without creating a closed taxonomy? | 027 | — | — |
| Q029 | What criteria decide whether an AIPCS operation is an atomic tool, a persisted record, or a skill? | 027 | — | — |
| Q030 | Should `memhub` be experimentally evaluated, or is related-work comparison sufficient for the first paper? | 028 | — | — |
| Q031 | How should AIPCS prevent agents from mischaracterising local/homelab memory as cloud-backed? | 033 | — | — |
| Q032 | Should memory maintenance be an explicit bootstrap/instruction behavior with its own evaluation criteria? | 033 | — | — |
| Q033 | What objective rubric should score agent-led schema self-audit and distinguish retrieval-oriented repair from arbitrary churn? | 034 | — | — |
| Q034 | Should AIPCS define a convention for summaries or derived views so services do not accidentally become duplicate authorities for the same facts? | 034 | — | — |
| Q035 | Should required agent-authored fields have deprecation, confidence, or correction semantics when later evidence shows they may be unreliable? | 034 | — | — |
| Q036 | What minimum fields should a standard `session` entity include for memory rationale without becoming a transcript store? | 035 | — | — |
| Q037 | Should bootstrap highlight recently active session/rationale entities more explicitly while staying content-free? | 035 | — | — |
| Q038 | Should the portable AIPCS instruction artifact explicitly describe the authority split between static instructions, bootstrap, migration history, session records, and behavioral memory? | 035 | — | — |
| Q039 | How should an evaluation detect prose leakage objectively without banning useful rationale text? | 036 | — | — |
| Q040 | Should schema design prompts require an explicit retrieval query for each open-text field? | 036 | — | — |
| Q041 | What is the right balance between constrained fields and agent flexibility during early schema formation? | 036 | — | — |
| Q042 | What trace format should live-agent runs use so Claude and Codex sessions can be compared cleanly? | 037 | — | — |
| Q043 | Should the deterministic runner become a packaged command or remain a script for the prototype phase? | 037 | — | — |
| Q044 | How much of the live-agent rubric should be automated versus scored from transcript review? | 037 | — | — |

---

## Milestone Tracker

| # | Milestone | Target | Completed | Notes |
|---|-----------|--------|-----------|-------|
| M001 | Invention disclosure published | 2026-05-04 | ✅ 2026-05-04 | |
| M002 | Pattern spec v0.1 published | 2026-05-04 | ✅ 2026-05-04 | |
| M003 | Public GitHub repo live | 2026-05-04 | ✅ 2026-05-04 | |
| M004 | v1 technical design complete | 2026-05-04 | ✅ 2026-05-04 | `docs/AIPCS_v1_Technical_Design.md` |
| M005 | AIPCS Server prototype running | — | ✅ 2026-05-17 | Local MCP primitive server; now includes Bootstrap V2, exact search, provenance conventions, retrieval metadata, and additive schema evolution |
| M006 | OAuth/DCR foundation implemented | — | — | |
| M007 | First MCP tool registered by agent | — | Partial 2026-05-17 | Agent used generic record tools via live MCP connection; later Claude traces used bootstrap, retrieval, update/delete, and schema evolution for stale-memory repair and schema self-audit. Domain-specific dynamic tools deferred |
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

Current implementation evidence:
- `aipcs-server` exposes the local MCP primitive loop through service lifecycle and generic record operations.
- Current tool surface includes service seed/list/bootstrap/inspect/design/materialise/evolve and record create/list/get/search/update/delete/history.
- Bootstrap is a data-dictionary map with schema summaries, attribute metadata, retrieval hints, and common domain-class guidance; record content is retrieved via list/get/search.
- Retrieval `_meta` computes updated age and carries provenance convention fields when available.
- Static instruction artifact exists for agent harnesses.
- Additive schema evolution increments schema version, appends migration history, applies safe SQLite DDL, and preserves existing records.
- Live Claude trace showed cold-start bootstrap, bounded memory retrieval, stale-memory detection, and autonomous persisted-memory repair.

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
- **Live-agent stale memory repair**: Claude compared recalled records to current AIPCS tool/schema state, detected stale facts, and used AIPCS update/delete tools to repair memory. This should become an evaluation scenario. (Entry 033)
- **Live-agent schema self-audit**: Claude evaluated whether its own memory schemas served retrieval, split a prose user-memory blob into granular records, added lifecycle/reference fields through schema evolution, and removed duplicate authorities. This should become a separate evaluation scenario. (Entry 034)
- **Memory-rationale authority layers**: Claude rejected putting evolving schema rationale into `AGENTS.md`, instead identifying migration history for what changed, session records for why, feedback memory for reusable behavior, and bootstrap for shape-only orientation. (Entry 035)
- **Prose leakage into memory**: Claude observed that human-facing agent harnesses bias writes toward readable explanations; constrained schema fields act as counter-pressure that can make retrieval-shaped memory durable. (Entry 036)
- **Deterministic Agent-Led Evaluation V1**: `aipcs-server/scripts/eval-v1.py` now seeds representative services and verifies the first six memory-behavior scenarios before live-agent scoring. (Entry 037)

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
