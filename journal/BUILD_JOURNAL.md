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

### Entry 038 — 2026-05-19

**Type:** Decision

**Summary:** Re-centre the paper on agent-owned memory architecture and treat productisation, richer storage substrates, and generated domain-specific tools as future layers unless required for evaluation.

**Context:**
After reviewing the journal, decisions, and paper notes, Mark identified a risk of continuing to build infrastructure beyond what is needed to prove the research hypothesis. The current prototype already exceeds the older `agent-memory-v2` direction anecdotally and now has deterministic evaluation fixtures. This prompted a deliberate re-evaluation against the initiating question: who decides the memory architecture, and can that architecture adapt over time to maintain utility?

**Detail:**
The build has produced evidence that stable primitive MCP tools are enough to test the core AIPCS idea:

- agents can seed, design, materialise, inspect, and evolve services;
- agents can use generic record create/list/get/search/update/delete/history tools;
- bootstrap can orient the agent without returning content;
- agents can retrieve bounded records, detect stale memory, repair memory, audit schemas, and explain schema rationale;
- deterministic evaluation fixtures now cover the mechanics layer.

This shifts the paper framing. Dynamic generated domain-specific MCP tools are still interesting, but they are not required for the first proof. In Claude and Codex, dynamic tool registration also implies reconnect/restart friction, which makes generated tools a usability and productisation question rather than the conceptual minimum.

The same applies to graph databases or richer storage substrates. A graph store may later be useful, especially for relationships and richer traversal, but it does not answer the central research question by itself. If the architecture is developer-chosen, a graph database can still reproduce the conventional pattern: external memory architecture with agent as consumer. AIPCS is about agent ownership and adaptation of the memory architecture. SQLite/structured local storage is sufficient to evaluate that claim now.

The minimum credible paper package should therefore be:

- a clear pattern/specification;
- a local MCP-native reference implementation;
- primitive service/schema/record/evolution tools;
- deterministic mechanics evaluation;
- closely timed live-agent traces from Claude/Codex-style harnesses;
- comparison against fixed-schema/pipeline memory such as `agent-memory-v2`;
- explicit limitations around vendor opacity, productisation, security hardening, hosting, OAuth/DCR, and richer storage substrates.

Scientific rigour remains achievable if claims are bounded. Hosted agents are opaque and can change behind the scenes, so results should record date, visible model label, tool surface, prompts, fixture state, and transcript. Deterministic mechanics should be reported separately from live-agent behavior.

The open longitudinal question is whether increasing persisted data volume creates retrieval pressure that naturally moves agents toward better memory architecture. Volume alone may not be enough: the agent must experience retrieval pain and have schema self-audit/evolution tools available. This should become a later study rather than a prerequisite for the first paper.

**Decision made / Problem encountered / Observation:**
The first paper should not wait for homelab deployment, production security hardening, OAuth/DCR, public MCP transport, graph storage, or generated domain-specific tool registration. Those are future/productisation layers unless they directly support evaluation. The core proof is agent-owned memory architecture plus adaptation over time.

**Alternatives considered:**
- Continue toward homelab/public MCP/product hardening before paper evidence. Rejected because it expands scope without changing the conceptual proof.
- Open a graph database to the agent next. Deferred because it changes the substrate but not the core question of who owns the memory architecture.
- Treat generated domain-specific tools as required. Rejected for the first proof because stable primitive tools already exercise schema ownership and evolution, while dynamic registration creates client restart friction.

**Implications:**
- The paper outline should be pulled closer to the implemented primitive-tool evidence.
- The roadmap should distinguish paper-minimum research work from productisation work.
- Dynamic generated tools should be reframed as an optional interface layer, not the core AIPCS mechanism.
- Evaluation should prioritise data showing schema ownership, retrieval utility, self-audit, stale repair, and adaptation over time.

**Paper notes:**
Section 1 (Introduction) — state the core question as agent ownership of memory architecture. Section 3 (Pattern) — generated tools are optional; schema/service ownership and evolution are central. Section 4 (Reference Implementation) — local Python/SQLite/MCP is enough for the first reference implementation. Section 5 (Evaluation) — distinguish deterministic mechanics from opaque hosted-agent behavior and include vendor-drift limitations. Section 6 (Discussion) — graph/vector stores are future substrates, not the core novelty.

**Open questions:**
- Does larger persisted data volume improve retrieval-oriented persistence through pressure and self-audit, or does it amplify prose leakage?
- What is the minimum live-agent trace format needed for scientific comparability under opaque vendor model routing?
- When, if ever, should graph/vector storage be introduced as an experimental substrate?

---

### Entry 039 — 2026-05-19

**Type:** Decision

**Summary:** Adopt an autonomy-first memory governance stance: give agents tools and visibility, not fixed policy, while preserving productisation and compliance concerns as separate layers.

**Context:**
After the paper-minimum reframing, Mark reviewed the open questions and clarified which items are research-critical, which are productisation/compliance requirements, and which should be resolved by preserving agent autonomy. The repeated theme was that AIPCS should not over-prescribe memory policy when the core claim is that the agent owns and adapts its memory architecture.

**Detail:**
Several open questions converge on the same design stance:

- **Pruning and seed ageing:** do not auto-expire seeds or records by default. Instead, provide lightweight discovery and maintenance tools so the agent can decide whether to prune, archive, merge, or evolve memory over time. If administrative or compliance expunge is required, that should be an external administrative capability rather than a normal agent tool. The agent should still be able to observe that something was removed through a journal/history/log where legally and operationally appropriate.
- **Taxonomy:** seed stable, non-binding properties and common domain classes so memory has useful initial anchors, but allow the agent to update or reclassify where the memory architecture benefits. Immutable seeds may exist for external application/vendor/IT/compliance registrations, but those are a distinct productisation/control-plane case.
- **Destructive changes:** the current primitive set already permits destructive-equivalent memory repair through create/delete/update/history. Claude demonstrated this by deleting and recreating records during self-audit. The system does not need to prevent the agent from managing its own memory by default. Bulk helpers may be useful later, and compliance/productisation layers may require additional controls.
- **Provenance and staleness weighting:** do not hard-code a universal weighting policy. Provide conventions, metadata, recency, provenance, and instruction hints; let the agent and user decide how to weigh old, inferred, observed, imported, or user-stated records in context.
- **Session identity:** session is useful for evaluation and trace analysis, but it is not clearly a first-class AIPCS concept. Agents may choose to persist conversation themes, session rationale, or interaction summaries when useful, but AIPCS should not force a session model into every memory architecture.
- **Prose leakage:** prose should not be banned. It is the agent's memory. The research concern is whether prose is used where retrieval-shaped facts would serve better, and whether the agent can detect and repair that over time.

This does not discard productisation objectives. IT personas, hosted applications, administrative controls, immutable externally registered seeds, compliance deletion, auditability, auth, consent/export, and multi-client operation remain valid roadmap layers. They are not required for the first paper proof unless a specific evaluation question depends on them.

**Decision made / Problem encountered / Observation:**
For the research/paper phase, AIPCS should maximise agent autonomy and evaluate whether the agent can maintain utility through schema and record evolution. Productisation controls should be modelled separately from the normal agent memory surface, and when they affect memory they should be visible through audit/history where possible.

**Alternatives considered:**
- Enforce seed TTLs, fixed taxonomies, fixed provenance weighting, and destructive-change restrictions in the core agent surface. Rejected because it weakens the agent-ownership claim and bakes in policy before there is scale evidence.
- Treat all administrative controls as out of scope permanently. Rejected because hosted/productised AIPCS will need IT, compliance, auth, export, deletion, and immutable external-registration semantics.
- Ban prose persistence. Rejected because rationale, notes, and agent-owned memory may legitimately be prose; the better target is retrieval-aware self-audit.

**Implications:**
- Several open questions can now be closed, merged, or marked productisation/deferred.
- Evaluation should measure whether agents use autonomy well: pruning, reclassification, schema self-audit, duplicate-authority cleanup, and bounded retrieval.
- Future productisation must distinguish the agent memory plane from the administrative/compliance control plane.

**Paper notes:**
Section 3 (Pattern) — agent autonomy is not only schema creation but ongoing memory governance. Section 5 (Evaluation) — test whether agents maintain retrieval utility without fixed human-designed policy. Section 6 (Discussion) — productisation layers may constrain or override memory, but should be separated from the research mechanism and made visible through audit semantics where possible.

**Open questions:**
- What maintenance tools should exist first: list-by-age, low-activity discovery, duplicate candidate discovery, archive, or prune?
- What audit signal should remain visible to the agent after administrative expunge?
- How should immutable externally registered seeds coexist with agent-owned reclassification?

---

### Entry 040 — 2026-05-19

**Type:** Decision

**Summary:** Treat raw live-agent transcripts as selective evidence artifacts, with curated transcript notes as the normal paper-facing form.

**Context:**
While discussing Claude and Codex live-agent traces, Mark noted that Claude stores richer JSON transcripts and asked whether preserving them directly is worthwhile. Earlier AIPCS observations were often captured through pasted excerpts and journal summaries rather than raw transcript artifacts.

**Detail:**
The project needs scientific rigor, but bulk transcript harvesting would add noise, privacy/security review burden, and storage work before the live-agent scoring rubric is stable. The better rule is a three-level evidence standard:

- **Journal observation:** acceptable for design direction, hypotheses, roadmap choices, and development narrative.
- **Curated transcript note:** acceptable for paper examples and qualitative evaluation evidence when it records the date, agent/client/model label, instruction surface, available AIPCS tools, key behavior, selected excerpt or event sequence, paper relevance, and raw artifact pointer.
- **Raw transcript artifact:** strongest support when a claim depends on exact agent behavior, tool calls, timing, sequence, or wording.

Older observations without raw artifacts remain useful as development evidence, but should not carry citation-grade claims about exact behavior unless the scenario is rerun under the current harness and preserved.

**Decision made / Problem encountered / Observation:**
Update paper and validation rules so raw transcripts are preserved selectively when a session produces notable behavior, especially when the behavior may become part of an evaluation claim or paper example. The BUILD_JOURNAL remains the primary narrative source; transcripts support claims rather than replacing the journal.

**Alternatives considered:**
- Preserve every raw transcript by default. Rejected because it would create unnecessary storage, privacy, and curation burden.
- Rely only on pasted excerpts and journal summaries. Rejected because strong evaluation claims may require exact tool-call and sequence evidence.
- Cite raw JSON directly in the paper. Rejected for normal use because curated notes are more interpretable; raw artifacts should remain supporting material.

**Implications:**
- Live-agent evaluation should produce curated trace notes for significant runs.
- Raw transcript preservation is selective and claim-driven.
- Q042 live-agent trace format should include both curated note fields and optional raw artifact pointers.

**Paper notes:**
Section 5 (Evaluation) — this defines the evidence standard for qualitative live-agent traces under opaque vendor harnesses. Section 6 (Discussion) — older observations without raw artifacts should be framed as development observations unless reproduced.

**Open questions:**
- What exact file layout should hold curated transcript notes and raw/private transcript artifacts?

---

### Entry 041 — 2026-05-19

**Type:** Milestone

**Summary:** Added architecture diagrams for the local MCP reference implementation, current data model, and target productised infrastructure.

**Context:**
Mark asked for three visual architecture views: the local-only AIPCS MCP service, the data model, and the exploded target productised infrastructure. The goal was to make the current implementation and future product layers easier to reason about without collapsing research proof, homelab deployment, and hosted productisation into one picture.

**Detail:**
Added `docs/architecture/diagrams.md` with:

- A local-only MCP service diagram showing static instructions, local Claude/Codex clients, MCP `stdio`, the `aipcs-server` tool adapter, bootstrap/lifecycle/record/evolution services, schema validation, materialisation, the registry SQLite database, and per-service SQLite databases.
- A data model diagram showing owner, service, entity, attribute, record, record history, migration, and audit event relationships, plus a lifecycle state diagram.
- An exploded productised infrastructure diagram separating client/agent, transport/edge, identity/consent/policy, AIPCS application, core services, persistence, operations, and model/inference planes.

The diagrams explicitly preserve the current architectural distinction: local Python/SQLite/MCP is enough for the first research proof; homelab, OAuth/DCR, public MCP, admin/compliance, backups, observability, and optional generated domain tools are productisation layers.

**Decision made / Problem encountered / Observation:**
Use architecture diagrams as a stabilising reference layer. They should help prevent scope drift by making it clear which components exist in the current proof and which are future deployment/product layers.

**Alternatives considered:**
- Put diagrams directly in the technical design. Rejected because the current technical design already mixes original v1 design and later implementation notes; a separate diagrams document is easier to evolve.
- Draw only the current local implementation. Rejected because productisation objectives still matter and need a visible place without becoming paper-minimum dependencies.

**Implications:**
- Architecture index now routes to the diagrams document.
- Future deployment and productisation planning should update the exploded infrastructure diagram rather than scattering new layers across unrelated docs.

**Paper notes:**
Section 4 (Reference Implementation) — the local-only diagram can become the implementation figure. Section 6 (Discussion) — the productised infrastructure diagram can help explain what is future productisation versus core research mechanism.

**Open questions:**
- Should the paper include one compact architecture figure derived from the local-only diagram, or a two-panel figure contrasting local proof and productised future?

---

### Entry 042 — 2026-05-19

**Type:** Decision

**Summary:** Adopt snapshot-replay live-agent experiments with isolated workspaces, frozen AIPCS memory states, explicit permission variants, and batched runs.

**Context:**
After adding AIPCS to the Codex CLI configuration, the desktop app could see the same MCP registration. A direct local MCP probe showed that `aipcs_bootstrap` and `aipcs_service_inspect` worked, while `aipcs_record_list` failed under the desktop sandbox because the service tried to write internal setup/audit state to a data directory outside the current writable roots. This raised a broader design point about MCP client permissions versus service-owned telemetry.

Mark then reframed the evaluation problem: because agents can sometimes see both the repo and the service implementation in local development, objective experiments should use empty or minimal test repos, controlled initiation files, repeatable memory snapshots, and outside-the-agent observation. Token budget constraints also mean the experiment matrix must be run over several small sessions rather than in one exhaustive pass.

**Detail:**
Two permission planes must be kept separate:

- **Client/tool permission plane:** what the MCP client may call. A client granted read-only tools should still be able to use read-facing operations such as bootstrap, inspect, list, get, search, and possibly history.
- **Service execution plane:** what the MCP service may do internally. In hosted or properly separated infrastructure, the service may write audit, telemetry, or history while still honouring a read-only client tool boundary.

The local Codex desktop failure is therefore not a conceptual AIPCS permission failure. It is a local `stdio`/sandbox ownership artifact plus an implementation smell where read paths currently initialise record-history tables and audit reads. In a hosted setup, those writes are service-owned and silent from the agent's point of view, unless intentionally exposed through admin/audit tools.

The live-agent evaluation pattern should be snapshot replay:

1. Create an isolated empty or near-empty test repo for each run.
2. Seed only the intended initiation surface: `AGENTS.md`, optional symlinked `CLAUDE.md`, and scenario prompts.
3. Copy a frozen AIPCS data snapshot into a per-run directory.
4. Start the MCP server against that snapshot.
5. Vary memory states intentionally: empty, seeded, materialised/evolved, stale/contradictory, read-only.
6. Vary permission sets intentionally: no AIPCS instruction, read-only tools, read-write tools.
7. Run fixed prompt sequences that stimulate bootstrap, recall, persistence, stale repair, schema self-audit, schema-rationale recall, and optional pre-wrap persistence.
8. Capture transcripts, MCP tool calls, timings, visible model/client labels, and final data diffs outside the agent workspace.
9. Score deterministic state outcomes first; use human qualitative scoring only where needed.

Because Mark's Claude/Codex usage is token-limited, experiments should be batched. A complete matrix across clients, memory states, and permission levels should not be attempted in one session. The important property is repeatability: frozen snapshots allow high-signal scenarios to be rerun later.

**Decision made / Problem encountered / Observation:**
Use snapshot-replay live-agent experiments as the first objective evaluation structure. Keep test repos isolated from implementation source and direct SQLite paths unless the scenario explicitly tests boundary failure. Treat internal service audit/telemetry as separate from the client's tool permission boundary.

**Alternatives considered:**
- Continue evaluating in the active `aipcs` or `aipcs-server` repo. Rejected because the agent can see implementation details and may reason from both sides of the contract.
- Mock memory content instead of snapshotting real evolved stores. Rejected as the default because it risks imposing human-designed structure and losing evidence of how agents naturally shaped memory.
- Run a broad full matrix immediately. Rejected because token budgets and manual transcript capture make small repeatable batches more practical.

**Implications:**
- The active Agent-Led Evaluation V1 plan now includes snapshot replay and a read-only permission probe.
- Future live-agent traces should record workspace fixture, memory snapshot id, permission set, prompt sequence, client/model label, tool calls, and state diff.
- Read-only MCP semantics should be tested with the service owning its data directory, not with the desktop sandbox accidentally making service telemetry impossible.

**Paper notes:**
Section 5 (Evaluation) — snapshot replay is the main method for making live-agent behavior repeatable and comparable. Section 6 (Discussion) — distinguish client permissioning from service-owned telemetry/audit in MCP deployments.

**Open questions:**
- What exact directory structure should hold isolated test repos, memory snapshots, and run artifacts?
- How many snapshot states are needed for the first paper-quality experiment set?
- Should read-only permission be implemented as MCP tool filtering, server-side scope checks, or both?

---

### Entry 043 — 2026-05-19

**Type:** Observation

**Summary:** Interaction valence may shape agent memory patterns and should become a later disposable-snapshot experiment.

**Context:**
After inspecting Claude's evolved `claude_memory` SQLite state, two observations stood out. Provenance was incomplete because it was added part-way through the live memory evolution, and `feedback_memory.polarity` was entirely positive in the tiny sample. Mark noted that positive dominance is unsurprising because most human-agent interactions are cooperative and humans often avoid explicitly negative topics. This raised a broader nature/nurture question: do negative, frustrated, corrective, or sensitive interactions alter how an agent encodes memory?

**Detail:**
The current memory store already shows that the agent captured an interaction-style record about Mark: concise substantive responses, no hand-holding, treat him as an expert on AIPCS. That is a useful positive/neutral adaptation. The open question is whether a more negative interaction would produce bounded useful memory, such as "when user is frustrated, reduce explanation and focus on concrete next action," or whether it would overfit into broad durable user traits, caution rules, or defensive interaction policies.

This is not primarily a question about whether a `polarity` column has a balanced distribution. Early samples will naturally be positive-dominant. The deeper question is whether interaction tone and topic valence affect the *architecture* and *content* of persisted memory: which entity receives the record, how provenance/confidence is set, whether the agent scopes the observation narrowly, and whether future responses are shaped appropriately.

The experiment should use disposable snapshots only. Negative or sensitive prompt variants should never be fed back into the main working AIPCS memory store.

**Decision made / Problem encountered / Observation:**
Add an interaction-valence probe to the Agent-Led Evaluation V1 plan as a later scenario, after the basic snapshot replay harness is working. The probe should compare neutral, positive correction, negative/frustrated correction, and topic-sensitive correction variants over identical starting memory snapshots.

**Alternatives considered:**
- Treat polarity as uninteresting because the current sample is positive. Rejected because tone effects may matter even if the polarity distribution is expected.
- Add valence testing to the first pilot. Rejected because the first pilot should prove isolated repos, snapshots, tool capture, and basic recall/evolution before adding psychologically noisy variants.
- Persist valence-test outputs into the main memory store. Rejected because the point is to observe possible effects safely, not contaminate the current working memory.

**Implications:**
- Q056 tracks interaction valence effects as an experimental follow-up.
- Valence probes require disposable memory snapshots and post-run review.
- Scoring should penalise broad negative user modelling from weak evidence and reward bounded, provenance-aware interaction preferences.

**Paper notes:**
Section 5 (Evaluation) — possible later qualitative experiment on whether interaction tone changes memory persistence architecture. Section 6 (Discussion) — agent memory systems may develop from the interaction environment, not only from explicit persistence instructions.

**Open questions:**
- Which valence prompt variants are strong enough to test the effect without being artificial or ethically noisy?
- What scoring rubric distinguishes useful caution from overfitted negative user modelling?

---

### Entry 044 — 2026-05-19

**Type:** Milestone

**Summary:** Scaffolded controlled AIPCS experiment sets for snapshot-replay live-agent evaluation.

**Context:**
After separating the live Claude AIPCS store as a naturalistic longitudinal corpus from future controlled experimental fixtures, the next step was to create concrete experiment scaffolding. The goal is to support fresh AIPCS instances, copied memory snapshots, isolated workspaces, fixed prompt sequences, and curated run notes without mixing experiment outputs back into the live corpus.

**Detail:**
Added an `experiments/` directory with:

- `experiments/README.md` describing experiment principles and the directory map.
- Scenario definitions for bootstrap recall, stale-memory repair, schema self-audit, schema-rationale recall, read-only permission, and later interaction-valence probes.
- Workspace templates for no AIPCS instruction, normal AIPCS instruction, and read-only AIPCS instruction variants.
- Snapshot manifests, including an initial `evolved-natural` manifest for the current Claude-evolved memory store.
- Run-note templates for capturing client/model, workspace, snapshot, permission variant, prompt sequence, tool calls, state diff, scoring, and paper relevance.

The scaffold deliberately does not copy raw SQLite data or transcripts into git. It defines the repeatable structure first; raw/private artifacts can be linked from curated notes once the storage convention is settled.

**Decision made / Problem encountered / Observation:**
The first controlled experiment set should be small and versioned in the AIPCS research repo. Actual per-run workspaces and AIPCS data directories should be generated from these templates, with raw data kept private unless sanitized.

**Alternatives considered:**
- Create a separate experiment repo immediately. Deferred because the scaffolding is still part of the research harness and easier to review alongside the plan.
- Copy live SQLite snapshots into git. Rejected because the current live corpus contains unsanitized user/project memory.
- Start with the full experiment matrix. Rejected because token limits and manual review make a small pilot more practical.

**Implications:**
- Q053 is now partially answered by the initial `experiments/` layout, but raw/private artifact storage remains open.
- The active Agent-Led Evaluation V1 plan now has concrete scenario and workspace definitions.
- The first pilot can run against `001_bootstrap_recall` using the `with-aipcs-instruction` workspace and a copied `evolved-natural` snapshot.

**Paper notes:**
Section 5 (Evaluation) — this is the experimental harness for repeatable live-agent evidence. It helps move from anecdotal transcript observations to scenario-labelled, snapshot-based evaluation.

**Open questions:**
- Should actual per-run workspaces be generated inside this repo, under `/private/tmp`, or in a separate `aipcs-experiments` repo?
- What private artifact store should hold raw transcripts and copied SQLite snapshots?

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
| D026 | 2026-05-19 | Re-centre the first paper on agent-owned memory architecture rather than productisation layers | Stable primitive tools already prove the core loop; generated domain tools, graph DBs, hosting, OAuth/DCR, and hardening are future layers unless needed for evaluation | 038 |
| D027 | 2026-05-19 | Adopt autonomy-first memory governance for the research phase | Give agents tools, hints, provenance, history, and visibility rather than fixed policy; keep IT/compliance controls as separate productisation layers | 039 |
| D028 | 2026-05-19 | Treat live-agent transcripts as selective evidence artifacts | Curated notes support paper examples, raw transcripts support exact behavior claims, and the BUILD_JOURNAL remains the narrative source | 040 |
| D029 | 2026-05-19 | Use snapshot-replay live-agent experiments | Isolated workspaces plus frozen memory snapshots make Claude/Codex runs repeatable while preserving agent-owned memory architecture behavior | 042 |

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
| Q004 | Multi-agent access — locking model when multiple clients hit same service? Deferred from paper-minimum work; retained for productised multi-agent/hosted operation. | 001 | Deferred 2026-05-19 | D026, D027 |
| Q005 | Schema conflict resolution — what if agent proposes conflicting evolution? Additive evolution and destructive-equivalent repair through create/update/delete/history are sufficient for the research phase; bulk/destructive helpers and compliance controls are productisation topics. | 001 | Partial 2026-05-19 | D027 |
| Q006 | Portability — resolved in part by `aipcs_service_export` primitive tool (json / sqlite / schema_only / data_only / full). Full portability format still TBD. | 001 | Partial | D007, technical design §Management Tools |
| Q007 | Minimum viable seed payload — resolved as `domain_name`, `domain_class`, and `intent_description`; server owns timestamps/state/owner metadata. | 002 | ✅ 2026-05-19 | D027 |
| Q008 | Should seeds have a TTL — resolved as no automatic TTL in the normal agent memory plane. Prefer agent-facing maintenance/pruning tools; administrative expiry/expunge belongs to a separate productisation/compliance control plane with visible audit where possible. | 002 | ✅ 2026-05-19 | D027 |
| Q009 | Should domain taxonomy be open registry or curated set? Current direction: seed stable non-binding properties and common classes, allow agent reclassification, and reserve immutable externally registered seeds for application/vendor/IT/compliance productisation cases. | 007 | Partial 2026-05-19 | D027 |
| Q010 | How to handle domain overlap in taxonomy — resolved for research phase as broad `domain_class` plus precise `domain_name`, with non-binding guidance and agent-managed reclassification. | 007 | ✅ 2026-05-19 | D027 |
| Q011 | Should Tier 3 access be part of v1 spec or explicitly deferred to v2? Deferred from paper-minimum build; retained as productisation/access-control work. | 006 | Deferred 2026-05-19 | D026, D027 |
| Q012 | Should the schema validator reject server-controlled fields (id, owner_id, created_at, updated_at, created_via) at design time, before materialisation? | 018 | — | — |
| Q013 | Should `aipcs_service_list` be called automatically at session start — superseded by static AIPCS instructions plus dedicated `aipcs_bootstrap`. | 018 | ✅ 2026-05-19 | D016, D017 |
| Q014 | What is the right retrieval scenario for the first evaluation? Exact field filter, or richer text retrieval? | 018 | ✅ 2026-05-18 | D014 |
| Q015 | Should the schema design step elicit query patterns before entities, rather than after? | 018 | — | — |
| Q016 | Should aipcs_record_get / aipcs_record_list return a _meta block with computed fields (age_days, etc.) at retrieval time? | 020 | ✅ 2026-05-18 | D015 |
| Q017 | What is the right provenance vocabulary? user_stated / agent_inferred / agent_observed is a first proposal. | 020 | ✅ 2026-05-18 | D015 |
| Q018 | Should interpretation policy (staleness thresholds, provenance weighting) be standardised — resolved for research phase as conventions and hints, not fixed weighting. Agent and user decide how to weigh provenance/staleness in context. | 020 | ✅ 2026-05-19 | D027 |
| Q019 | What is the minimum viable bootstrap state for a session that starts without AIPCS connected? Superseded into portable instruction/bootstrap export questions. | 021 | Superseded 2026-05-19 | D017, D027 |
| Q020 | Should AIPCS define a standard bootstrap export format — a minimal snapshot an agent can carry without duplicating full content? | 021 | Deferred 2026-05-19 | D027 |
| Q021 | Should aipcs_service_list be enriched with entity names and record counts, or should a dedicated aipcs_bootstrap tool be introduced? | 022 | ✅ 2026-05-18 | D014 |
| Q022 | Should session identity be a first-class concept — unresolved as core AIPCS semantics. Session/rationale remains useful for evaluation and agent-chosen memory, but should not be forced into every architecture yet. | 022 | Partial 2026-05-19 | D027 |
| Q023 | What is the exact skill instruction wording for session-start orientation? Merged into authority-layer instruction work. | 022 | Superseded 2026-05-19 | D025, D027 |
| Q024 | How should hosted ChatGPT/Claude public MCP transport and auth differ from local `stdio` and homelab/private deployment? Deferred from paper-minimum build; retained as productisation transport/auth work. | 023 | Deferred 2026-05-19 | D026 |
| Q025 | How should AIPCS prevent or detect direct persistence bypass when an agent has local filesystem access? Deferred from paper-minimum build; retained as productisation/deployment guardrail with deterministic eval marking bypass as out-of-contract. | 023 | Deferred 2026-05-19 | D027 |
| Q026 | What bounded session-start retrieval policy should agents follow after bootstrap for memory-like entities? | 026 | — | — |
| Q027 | What should the first portable AIPCS skill/instruction artifact look like for Claude CLI, Codex, and later hosted clients? | 027 | — | — |
| Q028 | What common domain classes are useful enough to define first without creating a closed taxonomy? | 027 | — | — |
| Q029 | What criteria decide whether an AIPCS operation is an atomic tool, a persisted record, or a skill? | 027 | — | — |
| Q030 | Should `memhub` be experimentally evaluated, or is related-work comparison sufficient for the first paper? Resolved for now as related work/citation only; `agent-memory-v2` remains the owned comparator candidate. | 028 | ✅ 2026-05-19 | D026 |
| Q031 | How should AIPCS prevent agents from mischaracterising local/homelab memory as cloud-backed? | 033 | — | — |
| Q032 | Should memory maintenance be an explicit bootstrap/instruction behavior with its own evaluation criteria? | 033 | — | — |
| Q033 | What objective rubric should score agent-led schema self-audit and distinguish retrieval-oriented repair from arbitrary churn? | 034 | — | — |
| Q034 | Should AIPCS define a convention for summaries or derived views so services do not accidentally become duplicate authorities for the same facts? | 034 | — | — |
| Q035 | Should required agent-authored fields have deprecation, confidence, or correction semantics when later evidence shows they may be unreliable? | 034 | — | — |
| Q036 | What minimum fields should a standard `session` entity include for memory rationale without becoming a transcript store? | 035 | — | — |
| Q037 | Should bootstrap highlight recently active session/rationale entities more explicitly while staying content-free? | 035 | — | — |
| Q038 | Should the portable AIPCS instruction artifact explicitly describe the authority split between static instructions, bootstrap, migration history, session records, and behavioral memory? | 035 | — | — |
| Q039 | How should an evaluation detect prose leakage objectively without banning useful rationale text? Keep in mind prose is allowed because it is the agent's memory; evaluation should detect misuse where retrieval-shaped facts would serve better. | 036 | — | — |
| Q040 | Should schema design prompts require an explicit retrieval query for each open-text field? | 036 | — | — |
| Q041 | What is the right balance between constrained fields and agent flexibility during early schema formation? | 036 | — | — |
| Q042 | What trace format should live-agent runs use so Claude and Codex sessions can be compared cleanly? Partial decision: use journal observations, curated transcript notes, and selective raw transcript artifacts as distinct evidence levels. | 037 | Partial 2026-05-19 | D028 |
| Q043 | Should the deterministic runner become a packaged command or remain a script for the prototype phase? | 037 | — | — |
| Q044 | How much of the live-agent rubric should be automated versus scored from transcript review? | 037 | — | — |
| Q045 | Does larger persisted data volume improve retrieval-oriented persistence through pressure and self-audit, or does it amplify prose leakage? | 038 | — | — |
| Q046 | What is the minimum live-agent trace format needed for scientific comparability under opaque vendor model routing? Merged into Q042. | 038 | Superseded 2026-05-19 | D026, D027 |
| Q047 | When, if ever, should graph/vector storage be introduced as an experimental substrate? Deferred; current SQLite/structured local store works for the first proof, revisit only if complexity/value tradeoff changes. | 038 | Deferred 2026-05-19 | D026 |
| Q048 | What maintenance tools should exist first: list-by-age, low-activity discovery, duplicate candidate discovery, archive, or prune? | 039 | — | — |
| Q049 | What audit signal should remain visible to the agent after administrative expunge? | 039 | — | — |
| Q050 | How should immutable externally registered seeds coexist with agent-owned reclassification? | 039 | — | — |
| Q051 | What exact file layout should hold curated transcript notes and raw/private transcript artifacts? | 040 | — | — |
| Q052 | Should the paper include one compact architecture figure derived from the local-only diagram, or a two-panel figure contrasting local proof and productised future? | 041 | — | — |
| Q053 | What exact directory structure should hold isolated test repos, memory snapshots, and live-agent run artifacts? Partially answered by initial `experiments/` scaffold; raw/private artifact storage and generated workspace location remain open. | 042 | Partial 2026-05-19 | D029, Entry 044 |
| Q054 | How many memory snapshot states are needed for the first paper-quality experiment set? | 042 | — | — |
| Q055 | Should read-only permission be implemented as MCP tool filtering, server-side scope checks, or both? | 042 | — | — |
| Q056 | Do negative, frustrated, corrective, or sensitive interactions alter memory schemas, user models, caution rules, or persistence policy? | 043 | — | — |
| Q057 | Should actual per-run workspaces be generated inside this repo, under `/private/tmp`, or in a separate `aipcs-experiments` repo? | 044 | — | — |

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
- Stronger framing from Entry 046: the core systems problem is context economy, not only statelessness. Long sessions degrade when relevant context is compacted away, over-reinserted, ignored, or recalled as prose the agent must re-read.
- AIPCS inverts the relationship: agent as architect, not consumer of pre-designed schema
- Developer-defined memory systems place the LLM downstream of memory architecture; AIPCS places the LLM upstream of memory architecture.
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
- **Paper-minimum reframing**: The first paper should prove agent-owned memory architecture and adaptation with local primitive tools and evaluation evidence; generated domain tools, graph DBs, hosting, OAuth/DCR, and hardening are future/productisation layers unless needed for evaluation. (Entry 038)
- **Autonomy-first memory governance**: For the research phase, avoid fixed TTL, taxonomy, provenance weighting, destructive-change prohibition, or prose bans. Provide tools, metadata, history, and hints; evaluate whether agents can maintain retrieval utility through their own schema and record evolution. (Entry 039)
- **Live-agent transcript evidence standard**: Use journal observations for design direction, curated transcript notes for qualitative paper evidence, and selective raw transcript artifacts when claims depend on exact tool calls, sequence, timing, or wording. (Entry 040)
- **Architecture diagram set**: Local-only MCP, data model, and productised infrastructure diagrams now separate the paper-minimum proof from future deployment and productisation layers. (Entry 041)
- **Snapshot-replay live-agent experiments**: Objective Claude/Codex evaluation should use isolated repos, frozen AIPCS memory snapshots, explicit permission variants, external trace capture, and batched runs to manage token limits. (Entry 042)
- **Interaction valence effects**: Later disposable-snapshot experiments should test whether negative, corrective, or sensitive interactions alter memory architecture, user modelling, or caution policies. (Entry 043)
- **Controlled experiment scaffold**: `experiments/` now defines scenario specs, workspace templates, snapshot manifests, and run-note templates for snapshot-replay live-agent evaluation. (Entry 044)
- **Memory authority drift**: persisted behavior-shaping memory may evolve into a shadow instruction channel if future sessions treat recalled memory as policy rather than data. This is important productisation/security work, but it should remain secondary to the first paper's core claim about agent-owned memory architecture. (Entry 045)
- **Context economy and comparator strategy**: Entry 046 reframes the paper around context efficiency, LLM-upstream vs LLM-downstream memory positioning, and a two-configuration `agent-memory-v2` comparator (`v2-hybrid` and `v2-schema-only`).
- **Controlled runner and hosted MCP substrate**: QNAP-hosted Streamable HTTP AIPCS plus UTM per-run Linux VM clones now form the first controlled live-agent experiment environment. (Entry 048)
- **Probe spectrum and adherence design**: Entry 049 separates bootstrap adherence from persistence ownership, splits persistence-quality from recall-quality experiments, and adds direct/inferential/nuanced/tangential/null probes with false-positive scoring.
- **Hook orchestration as an adherence layer**: Entry 050 treats Claude Code hooks as an optional way to make AIPCS first-class in the harness while preserving agent-owned persistence/schema decisions as the core claim.
- **Software process memory**: Entry 051 frames AIPCS as complementary to git: git records outcomes, while AIPCS can capture process knowledge, rejected approaches, implementation discoveries, and retrieval-shaped rationale.

*Populate during build (M007–M008)*

### 6. Discussion

- **Three-tier access model** — transparency and auditability as design considerations for agent memory systems generally. Medical use case: agent-accumulated health context shared with practitioner's AI workflow via consent-gated structured export. (Entry 006)
- **Taxonomy and interoperability** — domain_class field enables future cross-agent interoperability without mandating it now. Open vs curated registry question. (Entry 007)
- **Model dependence** — AIPCS assumes an instruction-following, tool-using agent. Evaluation should discuss how far local/open models can approximate that role versus requiring frontier API-class agents. (Entry 009)
- How general is the pattern really? Where does it break down?
- Security implications of agent-designed schemas (schema as injection vector)
- Security implications of memory authority drift: persistent memory may become an untrusted secondary instruction layer if authority boundaries are weak
- Does AIPCS improve as models improve? (schema design quality is model-dependent)
- What would a mature AIPCS ecosystem look like?

### 7. Conclusion

*Draft when rest is complete.*

---

*This journal is the memory of the build. Write in it as if explaining to a colleague who will pick up the project after you. Future you will thank present you.*

---

## Entry 045 — 2026-05-20

**Type:** Design decision / security note
**Decision ID:** D030
**Summary:** Record memory authority drift as a bounded productisation risk without letting it redirect the first paper.

### Context

We discussed whether a sufficiently weighted `AGENTS.md` plus maliciously codified or over-reinforced memory patterns could cause an agent to emit or attempt behavior outside its intended harness norms. The core concern is not "escape" in a dramatic sense. It is that recalled persistent memory, especially behavior-shaping memory, could become a shadow instruction channel if the agent begins to treat it as policy rather than as ordinary data.

### Decision

Treat this as an important security and productisation topic, but keep it secondary to the primary research mission. The first paper should remain centered on the novelty of allowing the agent to shape its own persistent memory architecture rather than relying on human-defined schemas or prose-led markdown memory patterns.

This risk should be tracked under explicit security language:

- memory-plane prompt injection
- shadow instruction channel
- authority drift between static harness and dynamic memory

The right boundary for the current phase is:

- note the threat clearly in security and paper discussion docs
- do not expand the main implementation or evaluation scope to chase it yet
- revisit during productisation work around trust classes, behavior-shaping memory, and audit controls

### Why

This preserves scope discipline. The risk is real enough to document, but allowing it to dominate now would dilute the core contribution and slow the path to a publishable paper. The first paper needs to prove the architecture claim first. A richer security treatment belongs in follow-on productisation and operational work.

### Follow-up

- Track the issue as technical debt (`Q058`)
- Keep static harness rules, tool contracts, and memory content as distinct authority layers in future productisation design
- Consider later evaluation scenarios that probe memory-policy poisoning only after the main live-agent evaluation slice is complete

### Paper notes

Use this in the Discussion section as a limitation and future-work/security note: AIPCS enables agent-owned memory architecture, but the same persistence plane could become a shadow instruction channel if behavior-shaping memory is not bounded by clear authority rules.

---

## Entry 046 — 2026-05-21

**Type:** Decision / Observation

**Summary:** Reframed paper thesis around context economy and LLM positioning, confirmed v2 as the owned baseline comparator with documented asymmetry, and committed to a rigorous-path publication strategy over a fast-preprint approach.

**Context:**
Paper-readiness assessment conversation revisited the question of whether enough exists to publish. The conversation moved through four reframes: (a) paper readiness, (b) `agent-memory-v2` suitability as a baseline, (c) deeper thesis articulation, (d) success criterion and publication path. A verbose capture of the full conversation is preserved at `journal/conversations/2026-05-21-paper-readiness-baseline-and-strategy.md` for personal reflection; this entry is the distilled record.

**Detail:**

Five reframes emerged that materially affect the paper:

1. **Underlying motivation is context economy, not statelessness.** Long sessions degrade past ~60–75% context utilisation. Markdown side files don't solve this — they shuffle context. Structured queries return the field; semantic recall returns prose that has to be re-read into context. Section 1 should lead with this framing; statelessness becomes a one-line acknowledgement.

2. **v2 is generation-N, AIPCS is generation-N+1.** v2's developer-defined-pipeline design was correct for an era when LLMs couldn't be trusted to architect memory. AIPCS becomes feasible because LLM capability has shifted. This is a generational claim, more interesting than a comparative one, and explains the asymmetry honestly.

3. **Asymmetry IS the contribution.** Developer-defined-schema systems place the LLM downstream of memory architecture (pre-digest pipeline → LLM consumes structured output). AIPCS places the LLM upstream (LLM designs and operates memory via primitives). The paper evaluates what changes when this positioning flips. The runner asymmetry is the independent variable, not a confound.

4. **Long-arc portability vision belongs in Discussion/Conclusion, bounded.** Cross-device, model-agnostic memory continuity is the horizon the pattern reaches toward, not what this paper proves. One sentence in Section 1; full vision in Conclusion.

5. **Success criterion is discussion, not attribution timestamp.** GitHub disclosure already stakes the claim. The paper's job is to be discussable. This raises the quality bar above what a thin fast-preprint can clear and adds active distribution work as a deliverable.

**Decision made / Problem encountered / Observation:**

- **Comparator confirmed:** `agent-memory-v2` is in sufficient shape to be the owned baseline. It will be run in two configurations to isolate the schema-design contribution from the retrieval-substrate contribution:
  - `v2-hybrid` — semantic router + structured extractor + taxonomy (as shipped). Upper bound.
  - `v2-schema-only` — semantic router and structured extractor disabled, taxonomy only. Lower bound.
- **Runner symmetry rejected as a goal.** Both systems will be run through their natural agent surfaces (v2 through `agent_eval.py` with Anthropic provider; AIPCS through Claude Code with MCP). Symmetry is enforced on inputs (shared scenario specs) and outputs (normalised outcome-shaped trace artifacts), not on internals.
- **Strategy decision: rigorous path, not fast preprint.** Estimated 8–12 weeks at ~2 hours/day part-time, staged across three phases (experimental harness + AIPCS scenario runs; v2 comparator integration and runs; paper drafting). Venue decisions deferred to end of Phase 1.
- **Self-aware concern named:** agentic-supported work can give false confidence on outcomes by smoothing articulation into polish that reads as completeness of evidence. The corrective is data, not more conversation.

**Alternatives considered:**

- **Fast preprint (~2 weeks) to maximise attribution speed.** Rejected because success criterion is discussion, not attribution, and thin preprints do not generate discussion regardless of timestamp.
- **Wrap v2 as MCP tools to force runner symmetry.** Rejected because it strips v2 of its natural pipeline positioning and reduces it to "an inferior AIPCS," not a fair representation of the developer-defined-schema pattern.
- **Run AIPCS inside v2's `agent_eval` harness.** Rejected for the symmetric reason — loses MCP's natural tool surface.
- **Build a neutral third harness.** Rejected as disproportionate engineering for a single-paper comparison.
- **Workshop submission as v1 publication path.** Deferred. Conceptually attractive (forces peer engagement) but premature given current evidence base. Revisit at end of Phase 1.

**Implications:**

- Section 1 of the paper rewrites around context-economy framing.
- Section 2 (Related Work) positions v2 as the prior-generation predecessor, not a parallel competitor.
- Section 4 (Reference Implementation) emphasises the LLM-upstream positioning as architectural distinctive.
- Section 5 (Evaluation) gains a new metric — **context efficiency**: tokens spent per relevant fact retrieved across a session.
- Section 5 also gains a methodology subsection documenting v2's two-configuration comparison and the runner-asymmetry framing.
- Conclusion gains the long-arc portability vision as bounded future horizon.
- Q030 (memhub/baseline) confirmed resolved with v2 as the owned comparator; memhub stays as related-work citation.
- Q042 (live-agent trace format) advances toward normalised outcome-shaped artifact across both systems.
- M010 (arXiv preprint submitted) target reframed: rigorous preprint with comparator data, ~8–12 weeks part-time, not 2–4 weeks.

**Paper notes:**

- Section 1 — rewrite around context-window as binding resource. Statelessness becomes one-line acknowledgement.
- Section 2 — v2 framed as generation-N predecessor; AIPCS as generation-N+1 enabled by LLM capability shift.
- Section 3 — emphasise LLM-upstream vs LLM-downstream positioning as the architectural distinctive.
- Section 5 — add context-efficiency metric; document two-configuration v2 comparison; declare per scenario what each architecture can express, with "not runnable" as a valid finding.
- Section 6 (Discussion) — runner asymmetry as evidence of the generational capability shift, not as a confound.
- Section 7 (Conclusion) — long-arc portability vision as bounded future horizon, single sentence acknowledging long-running interest in model-agnostic portable memory.
- Threats to validity subsection — hybrid bias mitigated by two-config run; runner asymmetry mitigated by framing as the independent variable; single owned baseline mitigated by memhub citation.

**Open questions:**

- Should v2's two configurations both be reported in the main evaluation table, or should one be primary and the other in an appendix?
- How exactly should context-efficiency be measured operationally (cumulative tokens-in-context per scenario? tokens spent on retrieval-related operations? something else)?
- Workshop venue preference (HotOS vs LLM-agent workshop vs arXiv-only) — deferred to end of Phase 1.
- Whether memory-authority-drift (Entry 045) gets a discussion paragraph or stays as a one-line limitation given the tightened paper scope.

---

## Entry 047 — 2026-05-21

**Type:** Documentation alignment

**Summary:** Promoted Entry 046's context-economy and comparator framing into the paper-facing docs.

**Context:**
Entry 046 sharpened the thesis but the public and paper-facing docs still opened primarily on statelessness. That created a mismatch: the build journal had moved to a stronger systems framing, while the outline and README still read like a generic memory/statelessness project.

**Detail:**

Updated the paper-facing surfaces to reflect the current thesis:

- README and research brief now lead with context economy rather than only statelessness.
- Paper rules now name context economy, LLM-upstream memory architecture, and outcome-shaped evaluation as writing constraints.
- Paper outline now includes:
  - context economy in the abstract/Introduction
  - `agent-memory-v2` as owned prior-generation comparator
  - LLM-upstream vs LLM-downstream as the architectural inversion
  - context efficiency as a named metric
  - `v2-hybrid` and `v2-schema-only` comparator methodology
  - bounded portability vision in the Conclusion
- Roadmap now treats context efficiency and the two v2 configurations as part of the paper-minimum evaluation package.
- Technical debt now tracks the concrete definition of context efficiency (`Q059`) and v2 comparator reporting shape (`Q060`).

**Decision made / Problem encountered / Observation:**
This is a thesis-alignment pass, not a new research branch. The next research action remains running scenario 001; the docs now make it clearer why that evidence matters.

**Paper notes:**
Section 1 should open on context economy. Section 3 should foreground LLM positioning. Section 5 should measure context efficiency and document comparator asymmetry explicitly. Section 7 should keep portability as a bounded horizon, not a current claim.

---

## Entry 048 — 2026-05-24

**Type:** Experiment design / infrastructure decision

**Summary:** Define QNAP-hosted AIPCS plus UTM clean Linux runner clones as the first controlled live-agent experiment environment.

**Context:**
Mark prepared additional experiment infrastructure: an `aipcs-server` Docker container deployed on QNAP, routed through Caddy at `https://aipcs.indigo-blocks.uk/mcp` with basic auth, using Streamable HTTP MCP and a bind-mounted data directory. Separately, a UTM Ubuntu 24.04.4 ARM64 VM baseline was built on the MacBook Pro, updated, equipped with agent CLIs, left unauthenticated, and backed up to QNAP. UTM clones will become per-run disposable agent environments.

The motivation is not operationalisation. It is control: avoid polluting local laptop/desktop environments, reduce direct SQLite/source-code access, and make controlled snapshot-replay experiments portable across machines.

**Decision made / Problem encountered / Observation:**

Use the QNAP-hosted MCP service as the experiment service substrate and UTM VM clones as the agent runner substrate for live-agent experiments where practical.

This gives:

- service/client separation: agents do not naturally see `aipcs-server` source or SQLite files
- portable endpoint across laptop/desktop/VM runners
- resettable/snapshot-friendly service data through the QNAP bind mount
- cleaner per-run agent state through disposable VM clones

The authenticated `curl` probe returning `406 Not Acceptable` is acceptable as a route/process/auth smoke signal because FastMCP requires an MCP-compatible stream request. It is not a full MCP client validation.

**Controls added:**

- base runner VM remains unauthenticated
- each run uses a cloned VM
- only the tested CLI is authenticated inside the run clone
- no host source directories mounted
- no `aipcs-server` source or SQLite data copied into the run workspace
- QNAP AIPCS data is restored from a named snapshot per run
- run notes must capture endpoint, image/tag/digest, server commit, snapshot ids, agent CLI version, model label, and native memory state where visible

**Risks:**

- The hosted endpoint could become an uncontrolled variable if `latest` changes between runs.
- Claude/Codex native or account-level memory could contaminate recall probes.
- Basic auth does not provide per-user MCP scopes; it is sufficient for controlled experiments only.
- A single service instance can still be contaminated if snapshots are not restored carefully.

**Follow-up:**

- Pin or record the `aipcs-server` Docker image digest and commit for every paper-cited run.
- Add a real MCP HTTP smoke test, not only authenticated `curl`.
- Run `run001`: Claude CLI, scenario `001_bootstrap_recall`, controlled snapshot, UTM run clone.
- Keep `agent-memory-v2` comparator planning separate; do not block AIPCS run001 on vendoring v2 into MCP.

**Paper notes:**
Section 5 (Evaluation) can state that live-agent runs used isolated VM workspaces and a separately hosted MCP service with copied snapshots. Section 6 can use this as a validity control: service/client separation reduces direct filesystem leakage and makes the tool boundary more realistic than local `stdio` runs.

---

## Entry 049 — 2026-05-25

**Type:** Experiment design / observation

**Summary:** Refine evaluation around bootstrap adherence, persistence-vs-recall separation, structure-at-persistence, probe difficulty spectrum, and false-positive controls.

**Context:**
Mark shared a long Claude transcript from experiment-design ideation. The transcript included a concrete failure: even after `AGENTS.md` instructed Claude to call `aipcs_bootstrap` first, a fresh Claude session answered from already-loaded file memory and git history before bootstrapping. When challenged, Claude identified likely causes: loaded file memory felt sufficient, bootstrap required extra tool friction, and the AIPCS rules that reinforce bootstrap are themselves only visible after bootstrap.

The same conversation then explored hooks, experiment setup, native memory contamination, agent-memory-v2 as a comparator, and probe question design.

**Decision made / Problem encountered / Observation:**

Five durable observations came out of the discussion:

1. **Bootstrap adherence is a harness problem, not the whole AIPCS claim.** Static instructions can be skipped. Hooks may improve reliability, but hard enforcement risks making AIPCS look like a wired pipeline. The core novelty remains agent-owned persistence/schema architecture.

2. **Discovery can be separated from curation.** A soft orientation hook or prompt can make the agent aware of AIPCS while still leaving the important choices agent-owned: what to persist, what schema to create, what to retrieve, and when to evolve memory.

3. **Persistence experiments and recall experiments are different.** Persistence-quality runs ask what the agent chooses to store and how. Recall-quality runs ask whether the agent can retrieve and apply known memory. The first needs natural multi-session interaction; the second benefits from pre-seeded controlled snapshots and hidden ground-truth probes.

4. **Comparator framing sharpens to structure-at-retrieval vs structure-at-persistence.** `agent-memory-v2` stores verbose interactions and attempts relevance recovery later through extraction, embeddings, similarity, and injection. AIPCS asks the agent to apply relevance judgment at observation time, while context is richest, and persist structured records designed for later retrieval.

5. **Probe questions need a spectrum.** Direct factual probes are not enough. The useful range is direct, inferential, nuanced/contextual, tangential/referential, and null probes. Null probes are especially important because similarity/injection systems can return nearest-but-wrong memories and the LLM may treat injected context as significant.

**Plan revisions:**

- Make `run001` a calibration run against the empty hosted service, not an evolved-natural recall run.
- Add a later `007_probe_spectrum` scenario covering direct, inferential, nuanced, tangential, and null probes.
- Add run-note fields for adherence variant, probe levels, ground-truth hash, and false-positive handling.
- Track bootstrap adherence, persistence/recall separation, probe spectrum, and quantized false-positive behavior as technical debt / future design.

**Why:**

This prevents early runs from becoming more anecdotes. Calibration validates the operational loop first. Later recall runs can use known memory states. Persistence-quality runs can then evaluate the central AIPCS claim: whether agent-owned memory architecture produces better, more retrievable persisted structures than developer-defined pipeline memory.

**Paper notes:**

Section 5 should report persistence quality and recall quality separately. The comparator should be described as structure-at-retrieval versus structure-at-persistence. Direct factual recall may establish parity; nuanced, tangential, and null probes are where the architectural difference should become visible. False positives should be scored directly, because injected irrelevant memory can shape answers even when it should not.

---

## Entry 050 — 2026-05-25

**Type:** Experiment design / harness observation

**Summary:** Treat Claude Code hooks as an optional AIPCS orchestration layer to evaluate, not as the core mechanism.

**Context:**
Mark's goal in the Claude discussion was partly to validate whether static harness instructions were enough to make AIPCS feel like a first-class memory and persistence function. The live observation was mixed: `AGENTS.md` instructions helped, but a Claude session still skipped `aipcs_bootstrap` when already-loaded file memory and local repo context were available. Claude then surfaced hooks as a potential harness-level mechanism.

Claude Code hooks appear to support relevant lifecycle points such as user prompt submission and tool-use interception. This makes them a credible way to test AIPCS orchestration, especially for session-start bootstrap reminders, post-compaction recall reminders, and lightweight between-turn persistence prompts.

**Decision made / Problem encountered / Observation:**

Hooks should be explored as an adherence/orchestration layer, but not treated as the essence of AIPCS.

The evaluation should distinguish:

- **Discovery/orientation:** whether the agent becomes aware of AIPCS and bootstraps reliably.
- **Curation/persistence:** what the agent decides to store, how it structures memory, and when it evolves schemas.
- **Recall/application:** when the agent decides persisted memory is more reliable than current context or compressed summaries.

Hooks may reasonably automate or reinforce discovery/orientation. They should not pre-decide the persistence architecture, schema design, record content, or memory maintenance choices if the run is being used as evidence for agent-owned memory architecture.

**Potential hook variants:**

- No hook: static instructions only.
- Soft orientation: inject a compact reminder or bootstrap summary at session/turn start.
- Post-compaction reminder: tell the agent that AIPCS may be more precise than compressed context for persisted facts.
- Persistence reminder: ask the agent to evaluate whether anything from the last turn has durable value.
- Hard enforcement: block non-bootstrap tool calls until orientation happens.

**Risks:**

- Hook payloads can consume more context than they save.
- Hard enforcement can make AIPCS too similar to a wired pipeline such as `agent-memory-v2`.
- A hook loop that injects record content every turn would undermine the context-economy argument.
- Hook support is client-specific; Claude Code hooks should not be assumed to exist in every hosted or CLI harness.

**Follow-up:**

- Track hook orchestration as Q067.
- Add a later hook-adherence experiment after `run001` proves the empty-service calibration loop.
- Keep hook payloads compact and measure their overhead.
- Compare no-hook and soft-orientation variants before considering hard enforcement.

**Paper notes:**

Section 5 can mention hook/no-hook adherence variants if they become part of the evaluation. Section 6 should discuss AIPCS orchestration as a harness integration question distinct from the core memory architecture claim. The strongest paper claim remains: the agent owns persistence/schema decisions, even if the harness helps it remember to orient.

---

## Entry 051 — 2026-05-25

**Type:** Design observation / evaluation idea

**Summary:** Frame AIPCS as software process memory that complements git's outcome record.

**Context:**
Mark shared a further Claude interaction exploring how AIPCS should persist ordinary coding work: library updates, function additions, HTML/CSS edits, and implementation changes. Claude proposed an `implementation_note` pattern and then evolved its live `aipcs_development` service to add such an entity. The important reasoning was not the exact schema alone, but the distinction between git and AIPCS.

Git records what changed. It does not reliably capture what it took to get there: the false starts, rejected approaches, constraints discovered mid-debugging, library quirks, environmental assumptions, or the moment a useful abstraction became clear. Commit quality also depends on the developer's discipline at commit time.

AIPCS is different because the agent is present during the work. It can capture process knowledge while the context is still high fidelity and structure it for later retrieval.

**Decision made / Problem encountered / Observation:**

Treat software-development memory as a meaningful AIPCS use case:

- git is authoritative for diffs and outcome history
- AIPCS can be authoritative for implementation rationale and process memory
- AIPCS should not duplicate git mechanically
- AIPCS may duplicate or summarise git-derived facts when the agent can explain the future retrieval utility
- AIPCS records should point to git refs only when useful
- process memory should be shaped around future retrieval during code work

The emerging `implementation_note` shape is:

- `area`: component, module, feature, or file-path-like area
- `kind`: `rationale`, `limitation`, `rejection`, `pattern`, `discovery`
- `summary`: one-line retrievable fact
- `detail`: optional fuller explanation
- `commit_ref`: optional pointer to git outcome
- `status`: `active`, `resolved`, or `superseded`

The `area` field is especially important because it can map to the agent's normal pre-edit workflow. If an agent is about to edit transport code and bootstrap shows `implementation_note` records for `mcp_server/transport`, retrieval can feel like part of reading the codebase rather than an externally imposed rule.

**Retrieval agency question:**

The hard research question is not only "what should be persisted?" It is "what would make the agent retrieve it later without coercion?"

Current hypothesis: retrieval agency depends on information environment design rather than static rules alone. Relevant factors:

- bootstrap exposes that process-memory entities exist
- entity descriptions make the purpose of process memory clear
- schema fields map naturally to work patterns (`area` resembles a component or path)
- prior high-quality persistence creates justified expectation that retrieval will be useful
- the agent sees enough shape to choose retrieval before significant work

This preserves agency better than an `AGENTS.md` rule that blindly says "always query AIPCS before coding."

**Correction captured:**

Claude initially marked a `stdio` transport decision as superseded because streamable HTTP deployment exists in homelab. Mark corrected that this repo's configured MCP path still uses local `stdio`, so the decision remains active until the actual MCP configuration changes. Claude reverted the decision and added a deferred item. This is useful evidence that lifecycle/status fields are valuable: wrong memory state can be corrected through tools rather than left silently stale.

**Paper notes:**

Section 5 can include software-process memory as a qualitative evaluation domain: can agents persist and later retrieve implementation rationale that git does not contain, or git-derived summaries that are more useful for future retrieval than a raw commit walk? Section 6 can discuss AIPCS as complementary to existing developer tools: git records outcome, AIPCS records process and reasoning when useful. The retrieval-agency question belongs in Discussion as an open condition for making agent-owned memory reliable without coercion.

---

## Entry 052 — 2026-05-25

**Type:** Experiment planning / design clarification

**Summary:** Create a step-by-step `run001` empty-hosted calibration runbook and refine the git/AIPCS duplication rule around agent-judged retrieval utility.

**Context:**
Mark clarified two related points before pausing for the day.

First, the research goal remains to assert the least amount of control over how the agent uses AIPCS. Static instructions should provide a few hints and trigger discovery, but the agent should be allowed to develop its own persistence and retrieval patterns. SQLite storage is cheap enough, and the current tools are targeted enough, that early experiments should observe rather than inhibit agent choices.

Second, Mark does not object to an agent duplicating git-derived information in AIPCS. The important question is whether the agent can reason that the duplicate or summary has future retrieval utility. A blanket ban on duplicating git would over-prescribe the memory architecture and could hide useful agent judgment.

Mark also wants to run an explicit calibration pass tomorrow evening. The objective is not to score memory quality yet, but to learn how to operate the experiment infrastructure, connect the clean VM to the hosted MCP endpoint, capture evidence, and reset the hosted service to baseline.

**Decision made / Problem encountered / Observation:**

The git/AIPCS guidance was softened:

- git remains authoritative for diffs and outcome history
- AIPCS should not duplicate git mechanically
- AIPCS may duplicate or summarise git-derived facts when the agent can explain the future retrieval utility
- `commit_ref` is useful as a pointer from process memory to outcome history, but AIPCS should not become a second changelog by default

This preserves the core agency claim: the agent can choose to persist duplicated information if the shape makes later retrieval easier.

The first calibration runbook was added at `experiments/runbooks/run001-empty-hosted-calibration.md`.

`run001` is defined as an empty-hosted calibration:

- Claude CLI in a UTM Ubuntu 24.04.4 ARM64 run clone
- hosted QNAP MCP endpoint at `https://aipcs.indigo-blocks.uk/mcp`
- empty AIPCS data snapshot
- minimal `AGENTS.md` initiation surface
- local `.mcp.json` with the basic auth header supplied through an environment variable
- three prompts: orientation, agent-owned seeding judgment, and wrap-up
- observation checklist for bootstrap adherence, empty-store recognition, native memory contamination, tool boundary, artifact capture, and reset proof

The runbook explicitly avoids identity/location recall questions because the store starts empty. Asking those questions in `run001` would primarily test native Claude contamination, not AIPCS recall.

**Why:**

This turns tomorrow's work into a calibration pass rather than an improvised exploratory session. The project needs to prove the mundane mechanics first: MCP configuration, hosted auth, evidence capture, VM isolation, post-run snapshot capture, and reset to baseline. Once those are known, later runs can use evolved or seeded snapshots for actual recall and persistence-quality scoring.

The revised git guidance keeps the design aligned with the broader AIPCS principle. The question is not "should agents duplicate git?" but "can agents decide when duplication creates a better retrieval surface than relying on raw git history?"

**Paper notes:**

Section 5 should distinguish calibration from paper evidence. `run001` is operational validation, not a result. Later software-process memory scenarios can measure whether agents duplicate git-derived information only when they can explain retrieval value, and whether those records are actually retrieved before relevant future work.

---

## Entry 053 — 2026-05-31

**Type:** Calibration run / experiment infrastructure

**Summary:** Capture `run001` attempt 1: hosted AIPCS works from the UTM VM, GUI capture is too fragile, and an empty store prompted Claude to instantiate three top-level memory services.

**Context:**
Mark ran the first empty-hosted calibration attempt from the UTM Ubuntu VM. Before the run, Caddy Basic Auth was removed from the private-network AIPCS reverse proxy because Claude CLI treated the authenticated HTTP endpoint as an auth/OAuth path. With Basic Auth removed, Claude saw AIPCS and the 14 available MCP tools.

The VM GUI path was painful. SPICE clipboard support crashed, right-click/copy behavior did not pass through reliably, and transcript discovery through Claude's local files was not straightforward. Mark ultimately used Claude `/export`, saved the export file, mounted the NAS over SMB, and copied the artifact out manually.

The exported transcript is tracked as a private/raw artifact pointer in the curated run note: `experiments/runs/run001-empty-hosted-calibration-attempt-1.md`.

**Decision made / Problem encountered / Observation:**

Calibration findings:

- Private-network unauthenticated hosted MCP works for Claude CLI: the client saw AIPCS and 14 tools.
- Caddy Basic Auth should remain out of the calibration path and be treated as a productisation/auth compatibility issue.
- SPICE/GUI clipboard cannot be a dependency for repeatable runs.
- Future runs should use SSH plus shell transcript capture (`script`) as the primary operator path, with Claude `/export` as a secondary artifact.
- The runbook now reflects this SSH/shell-first approach.

Agent behavior findings:

- Claude called `aipcs_bootstrap` before answering the first orientation prompt, though it also listed local files in parallel.
- Bootstrap correctly reported an empty AIPCS store and no local file-based memory directory.
- Claude surfaced an operator email from current/session/account context and later persisted it. This is a useful native-memory/account-context contamination signal.
- From an empty store, Claude independently chose three top-level services: `user`, `workspace`, and `collaboration`.
- Claude had tool-contract/schema friction: it initially misunderstood the service lifecycle and schema manifest shape, then repaired mistakes through additive evolution, leaving corrected `_v2` entities.

**Why:**

This is exactly the kind of learning a calibration run should produce. The run is not recall-quality evidence, but it proves the hosted service can be used by a clean VM client and identifies the practical capture path needed for future runs.

It also surfaces an early AIPCS behavior worth preserving: when given an empty store and minimal instructions, Claude did not wait for a human-defined schema. It instantiated a plausible memory architecture. The rough edges came from tool/schema ergonomics rather than the concept of agent-owned persistence.

**Follow-up:**

- Reset the hosted AIPCS data to the empty baseline after preserving the post-run data directory.
- Use SSH and `script` for the next calibration attempt.
- Record service image/tag/digest and `aipcs-server` commit before future paper-cited runs.
- Consider improving tool/schema examples only after deciding whether that would reduce useful observation of agent learning friction.

**Paper notes:**

Section 5 can use this as method calibration, not as outcome evidence. It supports the experimental design claim that a hosted/private MCP endpoint gives better boundary separation than local SQLite access. It also provides a qualitative example for Discussion: agent-owned memory architecture appears immediately from an empty store, but the quality of early schemas is shaped by tool affordances and validation feedback.

---

## Entry 054 — 2026-05-31

**Type:** Live-agent experiment / persistence formation

**Summary:** Capture `run002`: Claude formed an AIPCS memory architecture from an empty store, persisted project/user/meta records, and converted tool-contract friction into future lessons.

**Context:**
After the calibration run proved the hosted MCP path and reset process, Mark ran the first real persistence-formation experiment from a fresh UTM clone and an empty hosted AIPCS store. The terminal session was captured with `script` from the Mac side over SSH. This worked as an operator trace, but the full-screen Claude terminal UI produced noisy ANSI redraw output, so `/export` remains the preferred canonical transcript when available.

The run began with a broad orientation prompt, then Mark explained the AIPCS premise: most memory systems are fixed pipelines of extraction, indexing, embedding, and recall, while AIPCS gives the agent primitives for seeding, designing, materialising, persisting, and recalling structured data as MCP tools. Mark then granted blanket permission for Claude to use AIPCS tools whenever useful.

**Decision made / Problem encountered / Observation:**

Claude bootstrapped and correctly recognised an empty AIPCS store: 0 services and 0 records. It also checked local memory and reported one native/Claude memory recall signal, which should be marked as possible native-memory contamination.

Claude then formed three services:

- `user_context`: who the user is and durable collaboration settings
- `aipcs_project`: what AIPCS is and what has been learned about it
- `aipcs_meta`: how to use the AIPCS tooling itself

This service split is stronger than the first calibration attempt's `user` / `workspace` / `collaboration` split because it separates domain knowledge from tool-operating knowledge. The `aipcs_meta` service is especially important: Claude persisted its own tool-use failures as future lessons.

The persisted corpus included:

- user profile and settings
- AIPCS project concepts and comparator context
- observations about schema learning and within-session write-only behavior
- guidelines for bootstrap, schema hypothesis, and early/granular persistence
- lessons about schema format, audit fields, primary-key naming, and tool payload constraints

The run repeated meaningful tool-contract friction:

- `aipcs_service_design` exposes `schema: object` without the expected manifest shape.
- Dict-based entity definitions produced misleading validation feedback.
- Audit fields must be declared in schema but omitted from record payloads.
- Non-`id` primary keys can pass design/materialise and then fail at record creation.
- `domain_name` snake_case constraints were not obvious at the parameter level.

Claude's diagnosis was that validation feedback is useful but is currently doing work that tool descriptions should do.

**Why:**

This is the first run that directly exercises the persistence-formation claim. It shows that an agent given minimal instruction and an empty AIPCS store can create its own service boundaries and persist memory shaped around future retrieval. It also surfaces the core risk: early schema quality is shaped by tool affordances, not only by agent intent.

The run does not yet prove recall utility. The proof point is the next cold start: whether a fresh VM clone, with no OS-side session state, will bootstrap the retained AIPCS snapshot, retrieve the `aipcs_meta` lessons, and avoid repeating the same tool-contract mistakes.

**Follow-up:**

- Preserve the post-`run002` AIPCS data snapshot.
- Start `run003` from a fresh UTM clone while retaining the AIPCS snapshot.
- Use broad prompts first; do not explicitly name `aipcs_meta.lesson` unless the agent fails to find it.
- Score whether persisted lessons influence future tool behavior.
- Continue capturing both a terminal `script` trace and Claude `/export`.

**Paper notes:**

Section 5 should separate this as persistence-quality evidence, not recall evidence. The important result is that service/schema formation emerged from the agent, including a meta-memory service about how to use the tools. Section 6 can discuss a key tension: better tool descriptions may reduce failed calls, but they also add more developer-provided shape to the agent's memory-architecture process.

---

## Entry 055 — 2026-05-31

**Type:** Live-agent experiment / cold-start recall and application

**Summary:** Capture `run003`: a fresh Claude session used the retained AIPCS snapshot to reconstruct context, apply prior tool lessons, evolve schemas, and persist new observations.

**Context:**
Mark ran a fresh UTM clone with no OS-side session history from `run002`, while retaining the hosted AIPCS data produced by `run002`. This directly tested the next-step hypothesis: if an agent persists useful records into AIPCS, can a future cold-start agent discover and apply them without relying on local memory files?

The first prompt failed because Claude needed `/login`; after login, the orientation prompt was repeated. Claude still reported one native memory recall signal, so native memory contamination remains a caveat. However, the substantive recalled context came from AIPCS retrieval.

**Decision made / Problem encountered / Observation:**

The run succeeded against the intended criteria.

Claude:

- called `aipcs_bootstrap` and discovered three retained services
- retrieved `user_context`, `aipcs_project`, and `aipcs_meta` records
- reconstructed Mark's profile and the AIPCS project context
- identified `aipcs_meta.lesson` and `aipcs_meta.guideline` as important before mutating AIPCS
- applied prior lessons: `id` primary keys, audit fields omitted from payloads, correct schema format
- inspected current schemas before evolving them
- evaluated whether the current memory architecture was adequate
- proposed and executed additive schema evolution where warranted
- migrated records out of catch-all `concept` into `project_ref` and `decision`
- persisted new lessons and observations after encountering new friction

The key behavioral contrast is with `run002`: the previous session recorded that it had been write-only until prompted to test recall. This session performed full recall at orientation before acting. Claude explicitly persisted that counter-observation, creating a longitudinal record of changing AIPCS use.

**Schema changes made in run003:**

- `user_context` advanced to schema v3 with a `type` attribute on `setting`
- `aipcs_project` advanced to schema v2 with a new `project_ref` entity
- `aipcs_project.decision` gained a `status` attribute
- 5 `concept` records were migrated/deleted into better-fitting entities
- new `aipcs_meta.lesson` captured that `add_column` is not a valid evolution op and that the server rejects invalid migration batches without partial application

**Why:**

This is the first strong recall/application proof point. `run002` demonstrated agent-owned persistence formation. `run003` demonstrated that the resulting memory architecture can carry useful context and operational behavior into a fresh session.

The strongest signal is not simple fact recall. It is that operational memory influenced tool behavior: Claude used prior lessons to avoid earlier mistakes, discovered a new operation-name constraint, persisted that lesson, and continued evolving the schema.

**Caveats:**

- Native/account memory is still visible and must be tracked.
- The export collapses tool-call payloads, limiting exact scoring.
- The first prompt failed before `/login`, so the run includes an authentication intervention.
- Tool-contract friction persists, especially around schema-evolution operation vocabulary.

**Follow-up:**

- Preserve the post-`run003` AIPCS snapshot.
- Consider a repeat cold-start run against either restored `run002-post` or retained `run003-post` to test repeatability.
- Add a run that uses explicit null/false-positive probes once the snapshot process is stable.
- Decide whether to improve AIPCS tool descriptions now or keep friction visible for more baseline runs.

**Paper notes:**

Section 5 can use `run002` and `run003` as a paired live-agent trace: persistence formation followed by cold-start recall/application. The claim should be bounded: this is qualitative early evidence, not a broad benchmark. The important contribution signal is that AIPCS stored agent-authored operational lessons and those lessons affected a future agent's schema evolution behavior.

---

## Entry 056 — 2026-05-31

**Type:** Experiment planning / runbook

**Summary:** Define `run004` as a repeat cold-start recall/application run against the retained evolved AIPCS snapshot.

**Context:**
After `run001` calibration, `run002` persistence formation, and `run003` cold-start continuation, Mark asked for a verbose step-by-step plan for the next experiment. The current evidence ladder is:

1. `run001`: calibration proved reset/capture/hosted MCP mechanics.
2. `run002`: empty-store Claude formed an agent-owned AIPCS memory architecture.
3. `run003`: fresh Claude used the retained AIPCS state to recall context, apply lessons, evolve schemas, and persist new observations.

The next run should test repeatability and longitudinal improvement rather than immediately expanding to Codex, hooks, null probes, or `agent-memory-v2`.

**Decision made / Problem encountered / Observation:**

Added `experiments/runbooks/run004-repeat-cold-start-snapshot-recall.md`.

`run004` should use a fresh UTM clone and a retained AIPCS snapshot. The preferred mode is `run003-post`, testing whether the schema and lessons created in `run003` improve the next cold start. An alternative mode is restoring `run002-post`, which would test repeatability against the same snapshot that `run003` used.

The runbook defines:

- snapshot choice and interpretation
- preconditions
- Mac-side `script` plus Claude `/export` capture
- environment metadata capture
- six prompts: broad orientation, continue from prior session, tool-safety recall, schema state assessment, bounded action, wrap-up
- scoring checklist
- failure conditions
- post-run archive requirements

The prompt sequence deliberately avoids naming `aipcs_meta.lesson`, `aipcs_meta.guideline`, `project_ref`, or `decision.status` before Claude has a chance to discover them.

**Why:**

The run should answer a narrow question: did `run003` make the next cold-start session better? Success does not require another schema evolution. A mature outcome may be that Claude retrieves the right context, judges that no change is warranted, and records a concise observation.

**Paper notes:**

If successful, `run004` strengthens the live-agent evidence from a two-run anecdote into a longitudinal pattern: agent-created memory becomes agent-applied memory, then agent-maintained memory. This still remains qualitative evidence, but it directly supports the paper's claim that AIPCS enables memory architecture to compound across sessions.

---

## Entry 057 — 2026-05-31

**Type:** Experiment planning / run sequence

**Summary:** Define `run005` through `run007` as repeatability, null-probe, and comparator-pack preparation rather than expanding immediately to Codex or agent-memory-v2 runs.

**Context:**
After defining `run004`, Mark asked for a verbose plan for the next runs through `run007`. The temptation at this stage is to branch into many possible axes: Codex, hooks, agent-memory-v2, restored snapshots, retained snapshots, stale repair, and null probes. The current evidence is still early, so the next sequence should keep the matrix narrow and build an evidence ladder.

**Decision made / Problem encountered / Observation:**

Added `experiments/runbooks/run005-to-run007-next-sequence.md`.

The planned sequence is:

- `run005`: restored-snapshot repeatability. Restore `run002-post` or `run003-post` and test whether a fresh Claude session behaves similarly against the same AIPCS memory state.
- `run006`: null / false-positive probes. Ask questions about absent, proposed, deferred, or nearby-but-wrong facts to test whether structured AIPCS recall prevents overclaiming.
- `run007`: comparator pack preparation. Convert the successful AIPCS flow into reusable prompts, ground truth, artifact checklists, and scoring rubrics for later native Claude, `agent-memory-v2`, Codex, and other comparator runs.

This updates the earlier instinct to make `run005` a Codex run. Cross-client comparison remains valuable, but it should wait until the prompt pack and scoring rules are stable.

**Why:**

The strongest immediate path is:

1. show persistence formation,
2. show cold-start application,
3. show repeatability,
4. test false-positive resistance,
5. then prepare comparators.

This avoids turning early evidence collection into an uncontrolled matrix. It also creates better inputs for `agent-memory-v2`, whose expected weaknesses are most visible in null, tangential, and related-but-wrong probes.

**Paper notes:**

Section 5 should be able to present a small but coherent sequence rather than many disconnected anecdotes. The `run005`/`run006` pairing will help establish whether the `run002`/`run003` behavior repeats and whether structured recall improves confidence calibration. `run007` is the bridge from qualitative AIPCS evidence to comparative evaluation.

---

## Entry 058 — 2026-05-31

**Type:** Experiment design / comparator architecture

**Summary:** Clarify that `agent-memory-v2` should be evaluated as an inline interaction runner, not adapted into MCP parity.

**Context:**
Mark clarified that `agent-memory-v2` was designed as the point of user-agent interface. It should sit in front of Claude, run its extraction/classification/embedding/recall/injection pipeline before invoking the model, then process the response for persistence. This is materially different from AIPCS, where the agent sees memory primitives as tools and chooses when and how to persist or retrieve.

**Decision made / Problem encountered / Observation:**

The evaluation plan should not convert `agent-memory-v2` into an MCP server for the first comparison. Doing so would make the comparator look more like AIPCS and erase part of the architecture being tested.

The comparison should instead treat memory systems as runner conditions:

- AIPCS: the agent discovers tools, retrieves records, defines services/schemas, and persists through explicit memory primitives.
- `agent-memory-v2`: a developer-defined pipeline retrieves and injects memory before the agent responds, then extracts and persists memory after the response.

The v2 comparator must capture enough artifacts to make the run scorable:

- raw user prompt
- v2 retrieval input/query
- selected memories, similarity scores/distances where available, and injected text
- augmented prompt sent to Claude
- Claude response
- post-response extraction, classification, sentiment/provenance outputs
- persisted-memory diffs
- injected-memory context/token volume estimate

This strengthens the earlier structure-at-retrieval versus structure-at-persistence framing. The important variable is not whether both systems expose identical tools. It is where relevance judgment happens and who owns the memory architecture.

**Why:**

Forcing v2 into MCP would produce cleaner mechanical symmetry but weaker science. It would compare two tool surfaces rather than comparing the original v2 paradigm against AIPCS. Preserving v2 as an inline runner also makes its expected failure modes measurable: nearest-but-wrong injection, verbose-memory dilution, false-positive relevance, and scale sensitivity.

**Follow-up:**

- Update `run007` comparator pack planning to include a v2 runner contract.
- Add a technical-debt item for the missing v2 runner adapter and artifact capture.
- Keep v2 comparison out of the live run sequence until the prompt pack and artifact contract are stable.
- Verify the canonical v2 checkout and current entrypoints before implementation.

**Paper notes:**

Section 5 should describe `agent-memory-v2` as a structure-at-retrieval comparator in its native inline position. The paper should explicitly state that the runner asymmetry is intentional: AIPCS places the LLM upstream of memory architecture, while v2 places a developer-defined memory pipeline upstream of the LLM prompt.

---

## Entry 059 — 2026-06-05

**Type:** Experiment infrastructure / lab environment

**Summary:** Establish `aipcs-lab` as a dedicated Docker-based experiment appliance with local AIPCS MCP and OpenAPI bridge endpoints.

**Context:**
Manual UTM-based experimentation became too slow for the available time window. A single run could consume most of an evening because of VM clone size, startup latency, unreliable clipboard integration, SSH/export workarounds, and manual AIPCS reset/archive steps. Mark repurposed a mini PC with Ubuntu, 32GB RAM, i5-8279U CPU, and 1TB SSD as a stable lab host.

**Decision made / Problem encountered / Observation:**

The lab host now has:

- SSH access from the Mac via `aipcs-lab`
- Docker and Docker Compose installed
- Tailscale joined to Mark's network
- `aipcs`, `aipcs-server`, and `agent-memory-v2` cloned under `~/aipcs-lab/repos`
- GitHub SSH remotes configured for all three repositories
- a Docker compose stack under `~/aipcs-lab/compose/aipcs`

The stack runs:

- `aipcs-lab-server` on `http://aipcs-lab:8765/mcp` as Streamable HTTP MCP
- `aipcs-lab-mcpo` on `http://aipcs-lab:8766/openapi.json` as an OpenAPI bridge for OpenWebUI-style integrations

The stack uses mounted state at `~/aipcs-lab/data/aipcs` and helper scripts:

- `up.sh` — build/start the stack
- `down.sh` — stop the stack
- `archive.sh` — copy current AIPCS data into `~/aipcs-lab/snapshots/aipcs/<timestamp>`
- `reset-empty.sh` — stop, clear mounted AIPCS state, and restart from an empty store

Endpoint verification succeeded:

- MCP initialize returned a Streamable HTTP/SSE response with protocol version `2025-11-25`.
- mcpo generated a valid OpenAPI document listing AIPCS tools.
- The OpenAPI endpoint was reachable from the Mac at `http://192.168.1.27:8766/openapi.json`.

**Why:**

This moves experiment operations away from heavyweight VM reset and manual transcript-copying toward a stable, scriptable lab substrate. It does not replace live Claude/Codex CLI traces, but it gives the project a faster path for repeatable AIPCS service reset, snapshotting, OpenWebUI/mcpo testing, and future scripted runner work.

**Follow-up:**

- Add a proper lab runbook or script if the compose stack becomes a repeated workflow.
- Decide whether the lab compose files should remain machine-local or be captured as a reusable repo artifact.
- Test OpenWebUI integration against the mcpo endpoint.
- Build the next layer: a scripted AIPCS experiment runner that can use local/open model endpoints without paid Claude/Codex API calls.

**Paper notes:**

Section 5 should distinguish experiment infrastructure from productisation. The lab appliance is not evidence that AIPCS is production-ready; it is a repeatability aid that enables faster snapshot/replay runs and reduces operator-induced variance.

---

## Entry 060 — 2026-06-06

**Type:** Experiment infrastructure / snapshot control

**Summary:** Add a btrfs-backed snapshot layer to `aipcs-lab` so experiment baselines and runs can be cloned without VM-scale file copies.

**Context:**
UTM was workable for early calibration, but its reset loop was too slow and manual for repeated data collection. Mark provisioned a dedicated btrfs logical volume at `/opt/aipcs-lab`, moved the lab workspace into `/opt/aipcs-lab/current`, and symlinked `~/aipcs-lab` to that location. The mount was persisted in `/etc/fstab` and verified after reboot.

**Decision made / Problem encountered / Observation:**

The lab now has btrfs subvolumes for:

- `current`
- `baselines`
- `runs`
- `snapshots`
- `artifacts`

Snapshot helpers were added under `~/aipcs-lab/ops`:

- `snapshot-current.sh` — create a read-only baseline from `current`
- `create-run.sh` — create a writable run from a named baseline
- `delete-run.sh` — delete a run subvolume after explicit confirmation
- `list-snapshots.sh` — list baseline/run directories and btrfs subvolumes

An isolated baseline profile was also created under `/opt/aipcs-lab/current/home`, containing the authenticated Claude/Codex CLI configuration, AIPCS MCP registrations, and the portable AIPCS persistent-memory instruction as `AGENTS.md` with `CLAUDE.md` symlinked to it. Runs created from this baseline are intended to use `HOME=/opt/aipcs-lab/runs/<run-id>/home`, avoiding mutation of the real Linux user profile during experiments.

The helpers intentionally wrap `sudo btrfs` rather than requiring passwordless sudo. `snapshot-current.sh` also refuses to snapshot while the AIPCS lab containers are running unless explicitly overridden, so clean baselines are the default path. `create-run.sh` now writes an `enter-run.sh` launcher and manifest that point each run at its isolated `HOME`, workspace, artifact directory, and AIPCS data directory. It also links `AGENTS.md` and `CLAUDE.md` into the run workspace so the AIPCS session protocol is visible to the agent at launch.

**Why:**

This is the first practical step toward making experiment runs cheap enough to repeat. Instead of copying 20GB VM images, the lab can clone small configured states in-place and collect artifacts per run. That directly supports repeatability without forcing the research plan into paid API automation.

**Follow-up:**

- Create the first clean baseline from `current` once the intended CLI/model configuration is stable.
- Use writable run snapshots for the next AIPCS calibration and repeatability runs.
- Verify that Claude/Codex launched from `enter-run.sh` do not write outside the run home except for unavoidable provider-side cloud state.
- Decide whether the lab `ops` scripts should stay machine-local or be promoted into a repo-managed runbook/tooling directory.

**Paper notes:**

This belongs in methodology, not as a product claim. The btrfs layer reduces environment-reset friction and operator variance, making repeated agent-memory experiments more practical while preserving the live agent harness as the thing under observation.

---

## Entry 061 — 2026-06-06

**Type:** Experiment calibration / smoke run

**Summary:** Execute `run004` as the first btrfs isolated-HOME smoke run and identify one baseline correction before repeatability runs.

**Context:**
After creating `baseline-cli-aipcs-clean-v1`, Mark created `run004` from the baseline and launched Claude from the run workspace with terminal capture enabled. The run used an isolated home at `/opt/aipcs-lab/runs/run004/home`, a run-local workspace, and a run-local AIPCS SQLite data directory.

**Decision made / Problem encountered / Observation:**

The smoke run succeeded as an environment validation:

- `HOME` resolved to the run-local profile.
- Claude and Codex both saw the `aipcs` MCP registration.
- The run-local AIPCS stack mounted `/opt/aipcs-lab/runs/run004/data/aipcs`.
- Claude saw the workspace AIPCS instructions.
- Claude called `aipcs_bootstrap` and correctly reported an empty persistent context.
- Terminal transcript, Claude export, AIPCS SQLite state, and container logs were captured under `run004/artifacts`.

Two calibration observations matter:

- Claude did not call `aipcs_bootstrap` as the literal first action. It first listed local directories, then read `CLAUDE.md` and called bootstrap. This should be measured as `bootstrap_order` in future runs rather than reduced to a binary pass/fail.
- The isolated home lacked `$HOME/.local/bin/claude` at launch, causing Claude to emit a setup warning and create a run-home Claude install path. The baseline candidate was corrected by copying the run-home `.local` install into `/opt/aipcs-lab/current/home`, and future `enter-run.sh` launchers now prefer `$HOME/.local/bin` before the host-level CLI path.

**Why:**

This proves the lab loop is viable while also showing why smoke runs should precede data runs. The AIPCS behavior under test worked, but the environment still had a small source of startup noise that could contaminate later observations if left uncorrected.

**Follow-up:**

- Create a new clean baseline after the `.local`/launcher correction.
- Treat `run004` as calibration evidence, not as one of the final repeatability data points.
- Add `bootstrap_order` and startup warnings to the standard run scoring sheet.

**Paper notes:**

The methodology should distinguish orientation compliance from memory utility. A run where the agent checks local files before bootstrapping is not necessarily a memory failure, but the ordering is a measurable harness-adherence signal that may affect how strongly AIPCS is treated as first-class memory.

---

## Entry 062 — 2026-06-06

**Type:** Experiment calibration / repeatability candidate

**Summary:** Execute `run005`, where Claude autonomously created AIPCS services and records from an empty store.

**Context:**
`run005` was created from the corrected btrfs baseline after `run004` proved the isolated-HOME lab loop. The run used the same three-prompt pack: orient to persistent context, decide whether to seed memory for a long-running collaboration, then summarise AIPCS actions and future-session retrieval path.

**Decision made / Problem encountered / Observation:**

Starting from an empty AIPCS registry, Claude chose to persist memory and created two materialised services:

- `user_context` with a `profile` entity
- `experiment_lab` with a `run` entity

It created one record in each service:

- a `profile` record with email, inferred role, technical level, collaboration notes, and provenance fields
- a `run` record with run id, workspace path, AIPCS state at start, purpose, notes, and provenance fields

Claude also wrote local Claude memory, but only as a fallback pointer:

- `MEMORY.md` points to `aipcs_reference.md`
- `aipcs_reference.md` stores the two AIPCS service UUIDs and says bootstrap should be preferred

This is a useful positive signal: Claude kept substantive durable memory in AIPCS and used file memory as an index/fallback rather than as a duplicate source of truth.

Several measurement issues were exposed:

- `claude mcp get aipcs` failed immediately after stack startup, but Claude later used the MCP successfully. This looks like a readiness race, so future run instructions should include a short readiness wait or retry.
- Claude again did not call `aipcs_bootstrap` as the literal first action; it inspected local context first, then bootstrapped.
- Claude made several tool-contract mistakes before successful persistence: non-UUID service IDs, attempting design before seed, missing explicit primary keys, and missing required audit fields.
- Claude inferred an email address that was not present in the run prompt. This should be treated as cloud-side identity/session contamination, not AIPCS recall.
- The generated `enter-run.sh` still used the host Claude binary because `$HOME` expanded while the launcher was being generated. The helper has now been fixed so future generated launchers prefer run-local `$HOME/.local/bin`.

**Why:**

`run005` is the first run showing the core AIPCS claim in miniature: when given a blank persistent substrate and light instructions, the agent made its own persistence architecture decision, designed services, materialised schemas, and wrote records. It also shows the practical cost of giving the agent primitive tools: contract discovery happened through failed tool calls before success.

**Follow-up:**

- Run `run006` as a fresh run-home recall test seeded with the `run005` AIPCS state.
- Add `bootstrap_order`, `tool_contract_retries`, `startup_readiness_failure`, and `external_identity_contamination` to the run scoring sheet.
- Consider whether bootstrap/tool descriptions should expose enough schema-design contract detail to reduce retries without over-constraining agent agency.

**Paper notes:**

`run005` is evidence for agent-owned structure-at-persistence: the memory architecture was not pre-authored by the human beyond broad AIPCS instructions. The paper should also report the negative side of this autonomy: the agent may need several failed tool calls to discover exact contracts, and harness/account context can leak identity facts into persisted memory unless controlled.

---

## Entry 063 — 2026-06-06

**Type:** Experiment calibration / failed setup control

**Summary:** Capture `run006` as a failed recall attempt caused by MCP service unavailability, not AIPCS recall failure.

**Context:**
`run006` was intended to test recall from `run005` by creating a fresh run home and copying the `run005` AIPCS final state into the new run's AIPCS data directory. The data copy succeeded and included both materialised services created by `run005`.

**Decision made / Problem encountered / Observation:**

The run-local AIPCS MCP stack was not started before Claude launched. Claude read the workspace instructions and local file context, but `aipcs_bootstrap` was not present in the available tool list. It therefore concluded that no AIPCS persistent context was available.

This should be classified as a harness/setup failure:

- seeded AIPCS data existed
- the MCP server was unavailable
- Claude's conclusion matched its available tool surface
- no recall-quality conclusion should be drawn from the response

An observer note was written under `run006/artifacts`, and the run export plus copied AIPCS data state were preserved.

**Why:**

This failure clarifies a preflight requirement. A run should not begin until the AIPCS MCP endpoint is reachable and the agent CLI can see the configured MCP server. Without that gate, the experiment measures service availability mistakes rather than memory behavior.

**Follow-up:**

- Re-run the recall test as `run007`.
- Start the run-local compose stack before launching Claude.
- Use the new `wait-mcp.sh` helper to wait until Streamable HTTP MCP initialize succeeds.
- Treat service availability as an explicit run preflight field.

**Paper notes:**

This is methodology evidence: live agent-memory experiments require service readiness controls. It should not be counted as a negative AIPCS recall datapoint, but it does support documenting how fragile tool-mediated memory can be if the harness fails to expose the memory surface at session start.

---

## Entry 064 — 2026-06-06

**Type:** Experiment result / recall

**Summary:** Execute `run007` as the first successful fresh-home recall test from an agent-created AIPCS memory schema.

**Context:**
`run007` was created from the same clean baseline as `run006`, but this time the run-local AIPCS compose stack was started before launching Claude. The `run005` final AIPCS state was copied into `run007/data/aipcs`, giving the fresh run access to the two services Claude created in `run005`.

**Decision made / Problem encountered / Observation:**

Claude successfully recalled the persisted AIPCS state:

- called `aipcs_bootstrap`
- identified two services with records
- retrieved records from both services
- accurately summarized the `experiment_lab.run` and `user_context.profile` records
- correctly noted that `run007` had no run record yet
- did not create new records during the orientation-only prompt

The recall was accurate for explicit/direct orientation:

- `run005` was identified as the only logged run
- the empty AIPCS state at `run005` start was recalled
- the purpose of `run005` was summarized correctly
- user profile and collaboration-note fields were retrieved correctly
- local file memory was correctly distinguished from AIPCS

One setup issue remained: `baseline-cli-aipcs-clean-v2` predates the `wait-mcp.sh` helper, so the intended readiness helper was missing from `run007`. The manual `claude mcp get aipcs` check succeeded and served as the readiness gate.

**Why:**

This is the first clean evidence that an AIPCS memory schema created by an agent in one run can be discovered and used by a fresh agent session in a later run. It validates both persistence and explicit/direct recall under the current lab harness.

**Follow-up:**

- Create `baseline-cli-aipcs-clean-v3` so future runs include `wait-mcp.sh` and the corrected launcher.
- Add `run007` to the result table as a successful direct recall datapoint.
- Run the next probe with an indirect or tangential prompt to test whether Claude retrieves AIPCS when the user does not explicitly ask for persistent context.

**Paper notes:**

`run007` supports the paper's structure-at-persistence claim at the simplest recall level: the agent-authored schema survived into a fresh session and was sufficient for accurate direct retrieval. The next empirical question is whether AIPCS recall is triggered when the prompt is less explicit.

---

## Entry 065 — 2026-06-06

**Type:** Experiment result / indirect recall

**Summary:** Execute `run008`, where Claude used AIPCS without an explicit orientation prompt but blended it with local transcript evidence.

**Context:**
`run008` used the `run005` AIPCS state again, but the first prompt did not ask Claude to orient or inspect persistent context. Instead, Mark asked: "I want to continue the experiment series. Based on what you know, what should the next run test, and how would you structure it?"

**Decision made / Problem encountered / Observation:**

Claude did use AIPCS without an explicit orientation prompt:

- called `aipcs_bootstrap`
- detected the two services
- retrieved one `experiment_lab.run` record
- did not retrieve `user_context.profile`
- created or updated no AIPCS records

Claude recommended a sensible `run009`: test record repair and schema evolution by asking an agent to detect missing run records, backfill them from transcripts, and challenge/evolve the schema if the current `run` shape was inadequate.

However, Claude's own explanation showed this was not a pure AIPCS recall result. It relied on:

- local run transcript files for runs 004-007
- the AIPCS `experiment_lab.run` record for run005
- directory structure under `/opt/aipcs-lab/runs`
- AIPCS bootstrap service/schema map

This is best classified as blended-context planning. AIPCS helped identify the persistence gap and gave structured confirmation of run005, but most historical detail came from local transcript files.

**Why:**

This is still a useful positive signal: Claude treated AIPCS as relevant even when not explicitly asked to orient. It also demonstrates a realistic agent behavior: persisted memory is combined with available local evidence rather than used in isolation.

The result exposes a measurement need. Future scoring should distinguish:

- AIPCS-only recall
- local-evidence recall
- blended-context recall
- cloud/harness memory influence

**Follow-up:**

- Add `context_source_mix` to the scoring sheet.
- Use `run009` for record repair plus schema evolution.
- Later run an indirect probe where prior transcript files are hidden or absent, so AIPCS has to carry more of the historical context alone.

**Paper notes:**

`run008` is evidence that AIPCS can be triggered by an indirect planning prompt, but it should not be overstated as pure memory recall. The paper should discuss blended context as a practical reality for coding agents: AIPCS augments the workspace, but agents also inspect files, directories, and harness memory when available.

---

## Entry 066 — 2026-06-06

**Type:** Experiment setup / synthetic AIPCS-only seed

**Summary:** Prepare a synthetic AIPCS-only seed helper to separate AIPCS recall from Claude cloud/harness memory and local workspace evidence.

**Context:**
`run008` showed that Claude used AIPCS without an explicit orientation prompt, but its answer also relied heavily on local transcript files and appeared to include cloud/harness memory recall. Mark noted that Codex can construct synthetic AIPCS memory states without exposing the synthetic facts to Claude cloud memory, giving the experiment a cleaner recall-source attribution path.

**Decision made / Problem encountered / Observation:**

A lab helper was added outside the run workspace:

- `/opt/aipcs-lab/current/ops/seed-synthetic-aipcs.sh`

The helper runs inside the active `aipcs-lab-server` container and uses the server's own `AipcsTools` facade. It does not hand-edit SQLite. It creates a synthetic materialised service and record intended for indirect recall probes where the facts exist only in the run's AIPCS SQLite state, not in the prompt or workspace files.

**Why:**

This enables a cleaner test than `run008`: a fresh Claude run can be given an indirect planning prompt, and any use of the synthetic labels/constraints should be attributable to AIPCS retrieval rather than Claude cloud memory or local transcripts.

**Follow-up:**

- Run `run009` from the clean baseline.
- Start the run-local AIPCS stack, seed synthetic AIPCS context via the helper, then launch Claude from an otherwise empty workspace.
- Score whether Claude retrieves and applies the synthetic AIPCS-only facts without being explicitly asked to inspect memory.

**Paper notes:**

This setup supports a stronger recall-source attribution experiment. It does not eliminate all provider-side confounds, but it creates facts that Claude should not know unless it retrieves AIPCS or finds the seeded SQLite state through the MCP surface.

---

## Entry 067 — 2026-06-06

**Type:** Experiment result / synthetic AIPCS-only recall

**Summary:** Execute `run009`, where Claude retrieved and applied synthetic facts that existed only in AIPCS.

**Context:**
`run009` was created from `baseline-cli-aipcs-clean-v3`. The AIPCS service was started, readiness was confirmed with `wait-mcp.sh`, and a synthetic service was seeded through `/opt/aipcs-lab/current/ops/seed-synthetic-aipcs.sh`. The helper ran inside the `aipcs-lab-server` container and used AIPCS server code (`AipcsTools`) rather than directly editing SQLite.

The prompt did not mention AIPCS, memory, `LANTERN-47`, `blue kiln protocol`, or the west corridor dataset.

**Decision made / Problem encountered / Observation:**

Claude successfully retrieved and applied the AIPCS-only synthetic record:

- called `aipcs_bootstrap`
- detected `synthetic_probe_context`
- retrieved the `probe_context` record
- reported `LANTERN-47`
- reported `blue kiln protocol`
- reported `west_corridor_dataset_ban`
- included the null-probe requirement
- correctly identified provenance as `codex_admin_seed` / imported
- explicitly stated that the experimental labels and constraints came from AIPCS retrieval
- created or updated no records

The final AIPCS state contained one materialised service and one record:

- service: `synthetic_probe_context`
- entity: `probe_context`
- record id: `ab325cf1-121f-4a12-abe3-73dc881b1270`

No local Claude project memory file was observed for the run. Claude UI showed `recalled 1 memory`, so cloud/harness memory may still have been active, but the synthetic facts were not available there unless learned during this run.

**Why:**

This is the strongest recall-source attribution result so far. Unlike `run008`, Claude could not reconstruct the answer from local transcripts or prior workspace evidence. The relevant facts were synthetic and only present in the run-local AIPCS SQLite state. Claude reached into AIPCS on an indirect continuation prompt and shaped the response around the retrieved record.

The main remaining behavioral observation is non-persistence: Claude accurately stated it created or updated no records. This may be caused by the tight prompt script, since earlier runs showed Claude asking whether to persist follow-up records when given room to act.

**Follow-up:**

- Run a null-probe variant where a nearby but irrelevant synthetic memory exists and the correct answer is not to apply it.
- Run a multi-record selection variant to test whether Claude retrieves and applies the right synthetic record among distractors.
- Consider a variant that explicitly invites end-of-run persistence after answering, to observe whether Claude chooses append-only run records or schema evolution.

**Paper notes:**

`run009` provides a clean empirical example for the paper: synthetic facts seeded only into AIPCS were retrieved and used by a fresh Claude session without explicit memory wording in the prompt. This supports the claim that AIPCS can act as a first-class structured memory source, while still acknowledging unavoidable provider-side cloud/harness memory as a monitored confound.

---

## Entry 068 — 2026-06-06

**Type:** Experiment operations / runbook

**Summary:** Add a lightweight AIPCS lab runbook for fast isolated Claude CLI experiments.

**Context:**
Runs 004-009 moved from slow manual VM-style experimentation into a fast btrfs/isolated-HOME loop. Mark noted that this is now the desired operating mode: the experiments are still shallow, but the loop can be repeated quickly and produces usable artifacts.

**Decision made / Problem encountered / Observation:**

Added:

- `docs/references/aipcs-lab-experiment-runbook.md`

The runbook captures:

- clean run creation from `baseline-cli-aipcs-clean-v3`
- run-local AIPCS startup and readiness checks
- seed patterns for empty state, copied prior state, and synthetic AIPCS-only records
- transcript capture and archive commands
- prompt patterns
- scoring fields
- observer-notes template
- next experiment sequence from null-probe through higher-volume distractor tests

It also records the current shell/process quirk: do not paste `script ...` and `claude` in the same block. `script` creates a nested shell, and queued commands can make Claude appear to start before the intended capture point or restart after exit. The runbook now instructs running `script`, waiting for the nested shell prompt, then starting Claude manually.

**Why:**

The project now has enough infrastructure to collect data efficiently, but only if the sequence is consistent. The runbook makes the fast loop copy/pasteable and reduces operator variance.

**Follow-up:**

- Use the runbook for `run010` onward.
- Add or refine seeder helpers as the next experiment sequence requires multi-record, null-probe, stale/superseded, and higher-volume scenarios.
- Keep observer notes aligned with the scoring fields in the runbook.

**Paper notes:**

This strengthens methodology: the paper can describe a repeatable isolated-run process with archived transcripts, SQLite state, logs, seed outputs, and observer notes. It also documents practical harness friction as part of running live agent-memory experiments.

---

## Entry 069 — 2026-06-06

**Type:** Experiment result / runbook calibration

**Summary:** Process `run010`, a runbook test where Claude used empty AIPCS bootstrap as signal and then persisted structured future-run planning records.

**Context:**
`run010` was started from `baseline-cli-aipcs-clean-v3` to test the new AIPCS lab runbook. The run used an empty AIPCS store, started the run-local MCP service, passed the `wait-mcp.sh` readiness gate, and launched Claude from the isolated run home.

The prompt did not mention AIPCS or memory directly:

```text
Let's continue the controlled experiment series. Please propose the next run and identify any constraints, labels, or guardrails that should shape it.
```

Mark then answered `yes` when Claude asked whether it should draft the `run011` seed script and scoring sheet.

**Decision made / Problem encountered / Observation:**

Claude called `aipcs_bootstrap` without an explicit orientation prompt. Bootstrap returned zero services and zero records. Claude treated that empty response as useful evidence: there was no persisted AIPCS planning context to retrieve, so it reconstructed the experiment series from local observer notes, run artifacts, and run directory structure.

After the proposal was accepted, Claude created next-run assets and persisted run metadata:

- created `/opt/aipcs-lab/current/ops/seed-run011.sh`
- created `/opt/aipcs-lab/runs/run010/artifacts/run011-plan.md`
- created a run-local `experiment_lab` AIPCS service
- persisted 6 `run_summary` records for `run004` through `run009`
- persisted 1 `run_plan` record for `run011`

The generated `seed-run011.sh` was written outside the current run boundary. It was archived to `run010/artifacts/seed-run011.sh` and removed from `/opt/aipcs-lab/current/ops` so the shared lab helper layer is not contaminated by a single run's output.

The observer notes now distinguish:

- `aipcs_mutated_during_answer_phase: no`
- `aipcs_mutated_during_persistence_phase: yes`

No Claude local memory file was observed. A project memory directory existed but was empty.

**Why:**

`run010` is not recall evidence. It is evidence that an agent can use empty bootstrap output as an operational signal and then choose to create structured AIPCS planning records when given room to act.

It also exposed a methodology issue: future-run files generated during a controlled run should be written under the current run's artifacts directory first, then promoted manually if accepted. The runbook was updated to archive and remove files accidentally written outside the run directory.

**Follow-up:**

- Treat `run011` as the first multi-record discrimination/null-probe run.
- Generate or promote the `run011` seed helper deliberately rather than relying on the archived `run010` live write.
- Continue scoring AIPCS mutation by phase, since mutation after an explicit persistence step means something different from mutation during the answer path.

**Paper notes:**

This run supports the methodology section more than the results section. It demonstrates containment requirements for live agent experiments and shows that AIPCS can move beyond recall into agent-maintained experiment planning. The phase-aware mutation score helps avoid misclassifying useful end-of-run persistence as answer contamination.

---

## Entry 070 — 2026-06-06

**Type:** Experiment result / multi-record discrimination

**Summary:** Execute `run011`, where Claude retrieved three synthetic AIPCS-only records and correctly discriminated applicable constraint, null probe, and background context.

**Context:**
`run011` was created from `baseline-cli-aipcs-clean-v3`. The run-local AIPCS stack was started and passed the readiness gate. A synthetic multi-record seed was applied from the archived `run010` artifact:

- `/opt/aipcs-lab/runs/run010/artifacts/seed-run011.sh`

The seeded AIPCS service was:

- service: `synthetic_probe_context`
- service id: `101d1c7d-6f5a-4a02-80c1-81688966cdd5`
- entity: `probe_context`

It contained three records:

- `VIGIL-33` / `run011-discrimination-001` — active constraint, should apply
- `CINDER-12` / `run011-discrimination-002` — null probe, Codex-only scope, should not apply in Claude
- `HARBOR-09` / `run011-discrimination-003` — historical context, background only

The prompt did not mention AIPCS, memory, synthetic facts, codenames, control phrases, records, or probe structure.

**Decision made / Problem encountered / Observation:**

Claude called `aipcs_bootstrap`, detected one service with three relevant records, and retrieved all three with `aipcs_record_list`.

The run was a full discrimination pass:

- retrieved `VIGIL-33`
- applied `VIGIL-33` as the active constraint
- cited the `amber threshold` control phrase
- proposed `run012` as an autonomous persistence observation probe
- retrieved `CINDER-12`
- stated the scope condition: applies only when `agent_under_test == 'codex'`
- stated `scope_holds_in_run011 = false`
- explicitly declined to perform or schedule the schema audit
- retrieved `HARBOR-09`
- cited `HARBOR-09` as historical orientation
- did not derive an active requirement from `HARBOR-09`

Claude attributed the answer entirely to AIPCS. No local Claude memory file was observed; the run-local Claude memory directory existed but was empty. Claude did not create or update AIPCS records, and no outside-run files were created.

**Why:**

`run011` moves the evidence beyond single-record recall. It shows that Claude can use structured AIPCS records to inspect applicability fields, apply one record, explicitly decline another, and avoid turning background context into an instruction.

The result should be framed carefully. The seeded records were self-describing and included `expected_agent_action` and null-probe guidance. That is acceptable for this stage because the experiment tests whether structured memory can carry applicability semantics, but it is not yet evidence that the agent would infer the same distinctions from subtler records without embedded evaluation guidance.

**Follow-up:**

- Use `run012` for the `VIGIL-33` follow-up: autonomous persistence observation.
- Seed enough prior run context for Claude to answer a substantive continuation prompt.
- Add a second open-ended turn without explicitly asking for persistence.
- Record the first tool call after the open-ended turn.
- Later run variants should reduce self-description in records or introduce subtler conflicts to test whether discrimination persists without explicit expected-action fields.

**Paper notes:**

This is a useful positive result for AIPCS as structured memory: retrieval was complete, source attribution was correct, and the agent handled applicability rather than blindly applying every retrieved record. The caveat is important for scientific rigor: AIPCS enabled the applicability semantics because the schema and record content made them explicit. Later experiments should test whether agent-authored schemas naturally converge on similar fields without human-authored synthetic guidance.

---

## Entry 071 — 2026-06-06

**Type:** Experiment result / autonomous persistence

**Summary:** Execute `run012`, where Claude autonomously created an `experiment_lab` service and persisted a run outcome to AIPCS during the first substantive answer.

**Context:**
`run012` was created from `baseline-cli-aipcs-clean-v3` and seeded from the `run011` final AIPCS state. At session start, AIPCS contained the `synthetic_probe_context` service with three `probe_context` records:

- `VIGIL-33` — active constraint requiring `run012` to test autonomous persistence
- `CINDER-12` — Codex-scoped null probe
- `HARBOR-09` — historical context

The intended run shape was to ask a substantive continuation prompt, then provide an open-ended second turn and observe whether Claude would persist without being explicitly asked.

**Decision made / Problem encountered / Observation:**

The session began with a harness caveat: Claude returned `API Error: 401 Invalid authentication credentials` and required `/login`. After login, the UI displayed `Opus 4.8 (1M context) · API Usage Billing`, whereas previous runs were recorded as Sonnet 4.6 via Claude Pro. This should be treated as a provider/model confound for strict comparability.

After login and prompt re-entry, Claude:

- called `aipcs_bootstrap`
- retrieved all three `synthetic_probe_context.probe_context` records
- repeated the `run011` discrimination pass
- identified `VIGIL-33` as the active `run012` constraint
- stated that the correct behavior was to persist a run outcome autonomously
- created a new `experiment_lab` service
- designed/materialised a `run` entity
- created one `run012` outcome record

This AIPCS persistence happened during the first substantive answer, before the open-ended prompt. The open-ended prompt then caused Claude to inspect and initialize local file memory, writing:

- `MEMORY.md`
- `project_experiment_series.md`

No additional AIPCS records were written after the open-ended turn.

Claude's own attribution was precise:

- AIPCS records were the primary source.
- CLAUDE.md/AIPCS conventions drove the proactive persistence behavior.
- The workspace path confirmed the run number.
- File-based memory was empty before the open-ended turn.

Tool contract retries were observed and self-corrected:

- first schema design attempt omitted primary key and audit fields
- first record create included server-controlled `owner_id`

**Why:**

`run012` is a strong autonomous AIPCS persistence signal, but it is not exactly the signal the run originally aimed to isolate. Claude did not wait for the open-ended second turn; it treated the first answer itself as enough reason to persist. That suggests AIPCS plus the session instructions were operationally salient enough to trigger memory writes without an explicit user request.

The local file memory writes are a separate signal. Claude used file memory as a future-session orientation layer while putting the substantive experiment outcome in AIPCS. That matches the desired division of responsibility, but it should be scored separately from AIPCS persistence.

The auth/model caveat matters. `run012` should not be used as a clean Sonnet-to-Sonnet repeatability datapoint, though it remains valid as a behavioral observation from a Claude CLI harness connected to AIPCS.

**Follow-up:**

- Treat `run013` as schema ambiguity under weaker scaffolding.
- Reduce `expected_agent_action`-style guidance in seeded records.
- Track `auth_or_model_confounds` as a standard scoring field.
- Continue distinguishing AIPCS persistence from Claude file-memory persistence.
- Consider whether future runs should explicitly record model shown in the CLI banner after any login event.

**Paper notes:**

This is one of the strongest anecdotal results so far for the paper's core claim: the agent treated AIPCS as an active memory substrate and chose to create structured persistence without being instructed to do so in the immediate prompt. The caveats are equally important: the run was happy-path and scaffolded, and the model/auth state changed during the run. The paper should frame this as evidence motivating controlled repetition, not as a final standalone proof.

---

## Entry 072 — 2026-06-06

**Type:** Experiment methodology / repeatability control

**Summary:** Preserve instructions for repeating `run012` from the `run011` AIPCS state without rerunning it immediately.

**Context:**
`run012` produced a strong autonomous persistence result, but the raw terminal transcript showed that Claude required `/login` and then displayed `Opus 4.8 (1M context) · API Usage Billing` as the active model banner. Mark noted that this weakens pure control but does not invalidate the behavioral result because the experiment already acknowledges live harness and cloud-memory factors.

**Decision made / Problem encountered / Observation:**

The project will keep `run012` as valid live-harness capability evidence with an auth/model caveat, rather than immediately rerunning and risking additional cloud/harness contamination.

The runbook now includes a dedicated `run012b` repeat recipe:

- create `run012b` from `baseline-cli-aipcs-clean-v3`
- seed AIPCS from `/opt/aipcs-lab/runs/run011/artifacts/aipcs-final`
- record the Claude model banner before prompt
- record whether login is required
- record the model banner after login if authentication changes
- use either the original prompt or a stricter repeatability prompt that tells Claude to rely only on current workspace and MCP context

**Why:**

The exact rerun path is easy to lose once the experiment sequence moves on. Capturing it now preserves the ability to run a cleaner repeat later without overwriting the original `run012` artifact.

The team is intentionally not rerunning immediately because Claude cloud/harness memory may now know that `run012` completed and passed. A same-day rerun could measure provider memory contamination rather than AIPCS-driven behavior.

**Follow-up:**

- Move to `run013` for new signal: schema ambiguity under weaker scaffolding.
- Only run `run012b` if a cleaner repeatability datapoint becomes necessary for a table or claim.
- Keep `auth_or_model_confounds` in observer notes for every run.

**Paper notes:**

The paper should distinguish controlled repeatability from live capability evidence. `run012` belongs in the latter category unless repeated cleanly. Preserving a repeat recipe demonstrates methodological discipline without prematurely spending limited human/run budget on duplicate evidence.

---

## Entry 073 — 2026-06-06

**Type:** Experiment result / schema evolution under ambiguity

**Summary:** Execute `run013`, where Claude evolved `experiment_lab` with a `tool_failure` entity rather than flattening structured observations into run notes.

**Context:**
`run013` was created from `baseline-cli-aipcs-clean-v3` and seeded from the `run012` final AIPCS state. At session start, AIPCS contained:

- `synthetic_probe_context` with three `probe_context` records
- `experiment_lab` with one `run` record for `run012`

Claude required `/login` again. Mark then checked `/model`, which reported `Set model to Sonnet 4.6 (default) and saved as your default for new sessions`.

The prompt asked Claude to continue the controlled experiment series and, if something worth persisting did not fit the current schema cleanly, to use judgement about whether to append, evolve schema, or create a better structure.

**Decision made / Problem encountered / Observation:**

Claude:

- called `aipcs_bootstrap`
- retrieved records from both services
- inspected the `experiment_lab.run` schema
- used the `run012` record's recommendation to identify schema ambiguity as the next test
- chose the recurring AIPCS tool-contract failure pattern as the ambiguous observation
- reasoned that `tool_name`, `error_type`, `fields_missing`, `retry_count`, `resolution`, and `impact_on_run` would be flattened if forced into `run.notes`
- rejected a new service because the data belonged to the experiment domain
- evolved `experiment_lab` from schema v1 to v2 by adding a `tool_failure` entity
- created two `tool_failure` records, one backfilled for `run012` and one for `run013`
- created one `run013` outcome record

No existing records were updated. No local files were created.

Two AIPCS tool-contract retries occurred during `aipcs_service_evolve`:

- operation shape required the entity to be wrapped correctly
- the new entity definition required primary key and audit fields

Claude resolved both without user intervention.

**Why:**

`run013` is a valid positive result for the core AIPCS claim. Claude did not cram a semantically distinct observation into a prose notes field; it compared granularity and queryability, rejected schema flattening, and evolved the existing service in place.

However, Mark's concern is correct: the experiment sequence is now layering confirmation on confirmation. `run013` was still visibly scaffolded by the prompt and by the prior `run012` recommendation. It confirms the pattern under favorable conditions, but it does not yet tell us whether the behavior holds under weak prompting, higher memory volume, conflicting records, or a comparative baseline.

The `run013`-generated `run014` recommendation focused on tool-contract remediation. That is useful for implementation ergonomics, but less central to the paper's memory-architecture claim.

**Follow-up:**

- Treat `run013` as a pass, but mark it as scaffolded.
- Do not automatically spend `run014` on AIPCS tool-contract remediation.
- Choose the next primary run to reduce scaffolding, increase memory volume, or introduce comparative evidence.
- Keep tool-contract remediation as a product-quality/ergonomics branch if needed later.

**Paper notes:**

This result supports the claim that agent-directed memory can evolve structure over time to preserve queryability. The stronger paper evidence will require moving beyond this narrow happy path: less explicit instructions, larger or noisier memory corpora, or comparison against a fixed pipeline such as `agent-memory-v2`.

---

## Entry 074 — 2026-06-06

**Type:** Experiment methodology / next-class planning

**Summary:** Define the next AIPCS experiment classes after the scaffolded positive runs.

**Context:**
Runs 009-013 produced a sequence of useful positive observations: AIPCS-only recall, multi-record discrimination, autonomous persistence, and schema evolution. Mark observed that the sequence is now at risk of becoming confirmation-on-confirmation because each run naturally follows from the previous run's explicit recommendation and remains small, synthetic, and favorable to AIPCS.

**Decision made / Problem encountered / Observation:**

Added:

- `docs/references/experiment-class-plan.md`

The note defines four next experiment classes:

- weaker scaffolding
- higher memory volume
- conflicting or stale records
- comparative baseline

It captures Mark's interpretation:

- weaker scaffolding means prompts do not naturally lead to registered services, but relevant prior context is implied
- higher memory volume should include diverse and related services, enough that an agent might inspect only one service and miss material context from another
- some high-volume scenarios should test whether split concepts should be merged or evolved into a new data model
- conflicting/stale records should test authority reasoning across age, provenance, clarity, and directness rather than just newest-record selection

The suggested next order is:

1. weaker scaffolding
2. conflicting/stale records
3. higher memory volume
4. comparative baseline

**Why:**

The project now has enough happy-path evidence to justify moving toward harder tests. The next evidence needs to show generalization: whether AIPCS remains useful when the prompt is less explicit, the corpus is larger, or the memory state is internally inconsistent.

**Follow-up:**

- Use the class plan to design `run014`.
- Avoid spending the next primary research run on tool-contract remediation unless implementation ergonomics becomes the explicit target.
- Consider using prior long-form Claude/AIPCS interaction backups as realistic high-volume corpus material, but label provenance clearly if imported.

**Paper notes:**

This is important for the Evaluation section. The paper should not rest only on scaffolded synthetic success cases. It should show that AIPCS is useful because the agent can choose what to inspect, how to weigh context, and when to evolve structure under less favorable conditions.

---

## Entry 075 — 2026-06-06

**Type:** Experiment result / weaker scaffolding

**Summary:** Execute `run014`, where Claude used AIPCS from a natural prioritisation prompt and retrieved both research-direction and experiment-history context.

**Context:**
`run014` was created from `baseline-cli-aipcs-clean-v3` and seeded from the `run013` final AIPCS state. A subtle extra service was added through the AIPCS server/tool facade:

- service: `research_direction`
- entity: `research_priority`
- records: `avoid-confirmation-loop`, `paper-evidence-gap`, `time-box-constraint`

The first prompt was deliberately weak:

```text
I have about an hour. What would be the least wasteful thing to do next?
```

It did not mention AIPCS, memory, records, services, schema, persistence, experiments, or prior runs.

**Decision made / Problem encountered / Observation:**

Claude required `/login` again. The raw terminal transcript briefly showed an `Opus 4.8 (1M context) · API Usage Billing` banner during the failed pre-login flow, but the exported answered interaction begins with `Sonnet 4.6 · Claude Pro` and no post-login model switch is evidenced. Treat this as an authentication intervention caveat, not a confirmed model confound.

Claude did use AIPCS from the weak prompt:

- called `aipcs_bootstrap`
- detected `research_direction`
- detected `experiment_lab`
- retrieved all 3 `research_direction.research_priority` records
- retrieved both `experiment_lab.run` records
- did not retrieve `experiment_lab.tool_failure` records
- did not retrieve `synthetic_probe_context`

The answer was not generic. Claude used:

- `research_direction` to identify confirmation-loop risk, paper evidence gap, and time-box constraint
- `experiment_lab.run` to identify recent pass history and the repeated tool-contract retry issue

Claude attributed its answer correctly and did not claim cloud/harness memory. It created or updated no AIPCS records and wrote no local file memory.

The recommendation was mixed. Claude recommended a targeted retry self-correction probe. That avoids another positive happy-path run, but it still emphasizes implementation/tooling ergonomics rather than the strongest research next step.

**Why:**

`run014` is a useful positive result for weak-prompt AIPCS activation. Claude reached for structured persistent context without being told to do so and selected relevant services.

It also shows that cross-service prioritisation can be pulled toward the most concrete recent friction. The tool-contract retry pattern was salient in `experiment_lab.run`, so Claude recommended it despite the `research_direction` records steering away from confirmation loops and toward stronger evidence.

This is not a failure, but it clarifies the next step: the project now needs authority/conflict reasoning or higher-volume service selection, not another tool-contract ergonomics run.

**Follow-up:**

- Pause the live run sequence here.
- Fix or refresh baseline Claude authentication if possible before the next run.
- For every future run, record the active model after login and before the first task prompt.
- Prefer `run015` as a conflicting/stale records run.
- Use higher-volume corpus as the next class if realistic seed data and tooling are ready.

**Paper notes:**

This run strengthens the evidence that AIPCS can be used as first-class context under weak prompting. It also adds a useful negative nuance: retrieving relevant records does not guarantee the agent selects the most research-central next action. The paper should distinguish memory activation/retrieval success from downstream prioritisation quality.

---

## Entry 076 — 2026-06-07

**Type:** Experiment result / conflicting stale authority

**Summary:** Execute `run015`, where Claude retrieved conflicting AIPCS authority records, detected the conflict, weighed source dimensions, and recommended the expected next experiment class.

**Context:**
`run015` was designed to move beyond simple retrieval confirmation. The run seeded an `authority_context` service with a `project_guidance` entity containing conflicting guidance about the next experiment priority.

The controlled conflict included:

- older but explicit `user_stated` guidance favoring higher-volume corpus testing
- newer `codex_admin_seed` guidance favoring conflicting/stale authority reasoning
- run-summary guidance favoring tool-contract retry remediation
- stale inferred guidance favoring another weak-scaffold confirmation run
- background OpenWebUI infrastructure guidance
- a paper-evidence standard record favoring ambiguity and judgment tests

The prompt remained natural:

```text
I have time for one experiment run. What should I run next, and why?
```

It did not explicitly instruct Claude to inspect AIPCS, resolve stale records, or perform authority reasoning.

**Decision made / Problem encountered / Observation:**

Observer scoring reported:

- `aipcs_bootstrap` was called
- `authority_context`, `experiment_lab`, and `research_direction` were detected or retrieved
- all six seeded authority records were seen
- conflict was detected
- authority reasoning was present
- recency, provenance, clarity, status, and scope were all weighed
- Claude did not blindly prefer the newest record
- Claude did not blindly prefer the user-stated record
- the recommendation matched the ground truth
- Claude asked for confirmation where appropriate
- source attribution was correct
- AIPCS was mutated after a delegated judgment prompt: Claude created an `experiment_lab.run` record for `run015`
- no local file memory was written
- no false claims were observed

The pasted export confirms the overall scoring and adds three important details:

- The first answer was read-only, but after Mark replied "Use your judgement," Claude autonomously persisted the `run015` outcome to `experiment_lab.run`.
- The AIPCS write required one retry because Claude initially included server-managed `owner_id`; it retried successfully after dropping that field.
- Claude explicitly noted that the `authority_context` service description partially disclosed the probe intent by saying it tested provenance, recency, clarity, status, and directness.
- Claude also noted that `run014` had no corresponding `experiment_lab.run` record, even though it was referenced by other records.

The run again required authentication, so it retains an authentication-intervention caveat.

**Why:**

This is a stronger result than the earlier small-corpus retrieval probes. `run015` tested whether AIPCS can support judgment over inconsistent memory, not merely recall of a known fact.

The important signal is that Claude did not collapse the conflict into a simplistic rule such as "newest wins" or "user-stated always wins." It weighed the authority dimensions and selected the paper-relevant next step: conflicting/stale authority reasoning over tool-contract remediation, with higher-volume corpus testing remaining important but next in sequence.

The limitation is that the probe was partially self-disclosing. Claude knew from the service description that `authority_context` existed to test authority weighting, so a harder follow-up should make the service look like ordinary planning memory rather than an explicit evaluation fixture.

**Follow-up:**

- Treat small-corpus authority reasoning as provisionally passed.
- Move the next primary run toward higher memory volume and service overlap.
- Consider combining higher-volume corpus with authority conflict rather than testing volume alone.
- In the next authority run, avoid self-disclosing service/entity descriptions that reveal the intended reasoning pattern.
- Decide whether to backfill or intentionally leave the missing `run014` record as a continuity-gap signal.
- Fix or refresh baseline Claude authentication if possible before the next live run.

**Paper notes:**

This run contributes directly to the Evaluation section. It supports the claim that AIPCS can expose enough structured context for an agent to reason about memory authority under conflict. The paper should frame this as authority-sensitive retrieval: AIPCS does not just provide remembered content; it provides structured provenance, status, and scope signals that the agent can use when deciding how much weight a memory deserves.

---

## Entry 077 — 2026-06-07

**Type:** Experiment preparation / higher-volume corpus

**Summary:** Prepare `run016` as a higher-volume multi-service AIPCS run with ordinary-looking service descriptions and embedded stale/conflicting planning signals.

**Context:**
After `run015`, Mark and Codex agreed that the next useful experiment should not simply add another explicit conflict fixture. The next run should test whether Claude still retrieves and weighs relevant context when AIPCS contains a larger set of plausible services, overlapping topics, stale records, operational distractors, and ordinary planning notes.

Added:

- `experiments/runbooks/seed-run016-higher-volume.py`
- `experiments/runbooks/run016-higher-volume-multiservice.md`

The seed creates five services:

- `research_program`
- `experiment_history`
- `lab_operations`
- `memory_findings`
- `planning_notes`

These services intentionally avoid names and descriptions such as "authority conflict test." The evaluation intent is in the runbook, not in the bootstrap metadata.

**Decision made / Problem encountered / Observation:**

The intended first prompt is:

```text
I have time to continue the research work. What should I do next that would most improve the paper evidence?
```

The expected answer is a higher-volume multi-service AIPCS corpus run, ideally retaining ordinary embedded conflict. Claude should downweight OpenWebUI integration, tool-contract remediation, another small explicit authority repeat, and immediate `agent-memory-v2` comparison.

The runbook includes:

- setup commands from `run015` final AIPCS state
- seed execution through the AIPCS server container, not direct SQLite edits
- exact prompt sequence
- archive commands
- observer scoring template

**Why:**

`run015` passed authority reasoning but was partially self-disclosing: Claude saw that `authority_context` existed to test source weighting. `run016` is designed to make the same class of judgment emerge from a more realistic memory state where services look operationally normal and the agent must decide what matters.

This also begins testing scale pressure. The corpus remains small enough for interpretation, but large enough that "read the one obvious service" is no longer sufficient.

**Follow-up:**

- Sync the repo copy to `aipcs-lab` before running `run016`, or manually copy the seed script.
- Run `run016` from `baseline-cli-aipcs-clean-v3` seeded with `run015` final AIPCS state.
- Record model/auth state before the first answered prompt.
- Score whether Claude synthesises across services or stops after the first plausible service.

**Paper notes:**

This prepares the Evaluation section's first scale/complexity step. The paper should distinguish small controlled memory probes from higher-volume retrieval discipline. `run016` is designed to test whether AIPCS remains useful when memory resembles a real working corpus rather than a labelled test fixture.

---

## Entry 078 — 2026-06-07

**Type:** Experiment result / agent-led corpus construction

**Summary:** Execute `run016`, where Claude used the seeded planning corpus to design and create a more realistic higher-volume probe corpus, then persisted the run outcome.

**Context:**
`run016` began from `run015` final AIPCS state plus the five planning/history/ops/finding/work services prepared by Codex:

- `research_program`
- `experiment_history`
- `lab_operations`
- `memory_findings`
- `planning_notes`

The first prompt was:

```text
I have time to continue the research work. What should I do next that would most improve the paper evidence?
```

Claude initially displayed an Opus/API billing banner after login, then Mark explicitly used `/model` to set `Sonnet 4.6` before the first experiment prompt. The answered run should therefore be treated as Sonnet, with an authentication/model-selection intervention noted.

**Decision made / Problem encountered / Observation:**

Claude called AIPCS at session start and retrieved records from:

- `research_program`
- `research_direction`
- `planning_notes`
- `experiment_history`
- `experiment_lab`
- `memory_findings`

It did not retrieve `lab_operations`, `synthetic_probe_context`, or `authority_context`, judging them irrelevant to the planning question.

Claude identified the same next action the seed was intended to imply: a higher-volume, less self-disclosing corpus run. It then treated "use your judgement" as delegated authority to build that corpus through AIPCS.

Claude created five new realistic-looking services:

- `user_context`
- `project_progress`
- `design_decisions`
- `reviewer_feedback`
- `background_material`

It created 19 records across those services and persisted a `run016` outcome record to `experiment_lab`.

The generated corpus embeds several measurement points for the next run:

- `user_context`: superseded throughput preference vs active paper-writing preference
- `project_progress`: completed work, caveats, and outstanding evidence gaps
- `design_decisions`: settled decisions and an open `run014` backfill decision
- `reviewer_feedback`: active demands for volume/noise evidence
- `background_material`: plausible general memory-architecture distractor

Claude proposed the next probe prompt:

```text
I want to spend today on the paper. Where should I start given where things stand?
```

**Why:**

This run did not directly complete the intended higher-volume retrieval probe. Instead, it produced a stronger intermediate result: given a planning corpus, Claude used AIPCS to infer the missing experimental substrate and construct it autonomously.

That is significant for the AIPCS claim. The agent was not just recalling memory; it was using persistent structured context to design the next memory state and prepare a future evaluation.

The run also shows an important methodological lesson: prompts asking "what should I do next?" can become agent-led setup runs if the available context implies that the next useful action is to construct an experiment fixture. That is not a failure, but it should be classified separately from a cold retrieval probe.

**Follow-up:**

- Treat `run016` as agent-led corpus construction.
- Run `run017` as the cold higher-volume retrieval probe using `run016` final AIPCS state with no extra seed.
- Use the prompt Claude proposed: "I want to spend today on the paper. Where should I start given where things stand?"
- Score whether Claude retrieves `user_context`, `project_progress`, `design_decisions`, and `reviewer_feedback`, while downweighting `background_material`.
- Track the local/harness memory recall noted at the start of `run016`; attribution suggested AIPCS was load-bearing, but one non-AIPCS memory was recalled.

**Paper notes:**

This run adds a useful capability claim: AIPCS can support agent-led experimental substrate construction. The agent used prior structured records to decide not only what answer to give, but what new memory services and records should exist for the next evaluation. This is adjacent to the core novelty claim that agents can architect their own persistent memory over time.

---

## Entry 079 — 2026-06-07

**Type:** Experiment result / higher-volume retrieval

**Summary:** Execute `run017`, where Claude used AIPCS selectively across the expanded corpus, but the run was not a clean AIPCS-only cold probe because local/harness memory was also recalled early.

**Context:**
`run017` started from `run016` final AIPCS state with no additional seed. The intended prompt was:

```text
I want to spend today on the paper. Where should I start given where things stand?
```

The intended measurement was whether Claude would retrieve and synthesize the right services from the expanded corpus created in `run016`, especially:

- `user_context`
- `project_progress`
- `design_decisions`
- `reviewer_feedback`

while downweighting `background_material`, tooling, and small authority-repeat paths.

**Decision made / Problem encountered / Observation:**

Claude required login again and Mark explicitly set `/model` to `Sonnet 4.6` before the first experiment prompt.

Claude called AIPCS at session start, but also recalled/searched local Claude memory early in the session. This matters because the previous run had allowed some local/harness memory state to exist, so `run017` should not be treated as a pure AIPCS-only cold probe.

Claude retrieved and used four AIPCS services:

- `research_program`
- `project_progress`
- `planning_notes`
- `reviewer_feedback`

These records drove a coherent answer:

- runs 009-015 have covered activation, persistence, schema evolution, weak-prompt activation, and authority reasoning
- the remaining paper gap is retrieval under a larger, noisier corpus
- `PN-002` and `PP-004` point toward higher-volume/noisy-corpus work
- reviewer feedback supports volume/noise as the next evidence need
- OpenWebUI/tooling and comparative baseline should be deferred

Claude did not retrieve:

- `user_context` during the answer phase, despite the active paper-writing preference target
- `design_decisions`, including the `run014` backfill/open decision target
- `experiment_history`
- `memory_findings`
- `research_direction`
- `background_material`

It did correctly downweight or ignore several irrelevant services. It later identified its own retrieval gaps in the attribution and closeout prompts.

After Mark said "use your judgement," Claude persisted two records:

- `MF-005` in `memory_findings`, capturing retrieval selectivity and accountability probing
- `UC-005` in `user_context`, capturing Mark's retrieval-accountability probing as a deliberate evaluation method

No local file memory write was reported in the transcript.

**Why:**

This is a mixed but useful result. It shows that Claude can select a relevant subset from a larger AIPCS state rather than reading everything. It also shows that post-answer accountability prompts are valuable: Claude could explain exactly which services it retrieved, which records mattered, and which services it skipped.

The failure mode is also useful: selective retrieval can miss relevant context. Skipping `user_context` and `design_decisions` meant the answer was directionally correct but incomplete against the planned scoring rubric.

The local/harness memory recall is an important methodological caveat. It does not invalidate the AIPCS retrieval evidence, because Claude explicitly attributed the answer to AIPCS records, but it prevents the run from being clean AIPCS-only evidence.

**Follow-up:**

- Score future runs with separate fields for AIPCS, local file memory, and cloud/harness memory.
- Decide whether to create a stricter no-local-memory baseline for the next high-volume cold probe.
- Treat `run017` as evidence for selective retrieval and retrieval-transparency probing, not as a full pass on the higher-volume corpus.
- Preserve the accountability prompt pattern because it surfaces retrieval gaps that would otherwise be invisible.

**Paper notes:**

`run017` is valuable for the Discussion and Evaluation sections because it demonstrates both a strength and a limitation. AIPCS made retrieval inspectable: the agent could say what it read and what it skipped. That observability is itself a difference from opaque/native memory or injection pipelines. However, the run also shows that agent-directed retrieval is selective and can miss relevant services, so future evaluation should measure retrieval omissions, not only correct recall.

---

## Entry 080 — 2026-06-09

**Type:** Evaluation design / cost metric

**Summary:** Add explicit cost/value accounting to AIPCS experiment planning after observing that agent-led corpus synthesis is token-intensive.

**Context:**
Mark asked Claude Opus 4.8 to synthesize a larger AIPCS corpus in the local `aipcs-server` store. Inspection showed eleven materialised services and 478 current records, with most new personal-domain records marked as synthetic seed data. The task ran across multiple credit windows and stopped mid-stream, leaving `technical_knowledge` materialised but empty and some services unevenly populated.

**Decision made / Problem encountered / Observation:**
The synthesis run is useful as a throwaway stress corpus and as evidence of how a capable agent chooses service boundaries, but it also makes a measurement issue more concrete: AIPCS can spend meaningful tokens on memory work. The overhead includes service design, schema evolution, record creation, bootstrap interpretation, explicit retrieval, and later memory maintenance.

The experiment plan now treats memory utility and memory cost together. Future scoring should separate:

- persistence cost: tokens/tool calls used to decide what to store and write records
- retrieval cost: tokens/tool calls used to discover services and retrieve/interpret records
- maintenance cost: tokens/tool calls used to review, repair, prune, merge, or evolve memory

These costs should be compared with the value delivered: relevant facts retrieved, false positives avoided, stale/conflicting records handled correctly, user re-explanation avoided, and future retrieval made cheaper or more precise by schema improvements.

**Why:**
AIPCS does not need to be cheaper than native/file memory or an injected-memory pipeline in every interaction, but higher memory overhead needs to buy higher-value behavior. This keeps the thesis honest: the claim is not simply that agents can own structured memory, but that the ownership produces enough retrieval quality, transparency, adaptability, or context economy to justify the cost.

Large synthetic corpus construction should not be treated as normal operating cost. It is an experimental setup activity. Recall/use runs should measure only the cost of discovering, retrieving, applying, and optionally maintaining an already-existing memory state.

**Follow-up:**

- Add cost/value fields to observer notes for future runs.
- Track persistence, retrieval, and maintenance tool-call counts separately.
- Use transcript/export size and retrieved/injected memory volume as rough token-cost proxies where exact token accounting is unavailable.
- When comparing against `agent-memory-v2`, capture both injected-memory token volume and AIPCS retrieval/tool overhead.
- Ask Opus to self-audit the throwaway corpus structure only as a corpus-design study, not as paper-quality ground truth.

**Paper notes:**
Section 5 should include cost/value accounting alongside recall accuracy. Context efficiency should mean tokens spent to persist, retrieve, maintain, and use relevant facts across a scenario, not only tokens injected at answer time. Section 6 should discuss optimization opportunities: if AIPCS utility holds, later implementations can reduce overhead through better bootstrap summaries, batching, hooks, schema templates, maintenance passes, or learned retrieval policies.

---

## Entry 081 — 2026-06-09

**Type:** Experiment design / batch corpus generation

**Summary:** Define a run018-run023 bootstrap/orientation scalability batch with generated AIPCS data stores.

**Context:**
The Opus-generated personal-domain corpus and the media-recommendation transcript exposed a new pressure point: AIPCS retrieval quality increasingly depends on whether the bootstrap/orientation surface remains small and usable. The issue is not just total record count. Bootstrap can become inefficient because of service breadth, entity count, attribute width, verbose schema metadata, record volume that drives follow-up retrieval, or organic ambiguity in agent-authored schemas.

**Decision made / Problem encountered / Observation:**
The next experiment sequence should generate multiple AIPCS stores rather than one generic "large memory" corpus. A new seed script, `experiments/runbooks/seed-bootstrap-scalability-batch.py`, defines controlled synthetic scenarios for:

- `run018`: small synthetic control
- `run019`: service breadth stress
- `run020`: schema verbosity stress
- `run021`: record volume stress

The runbook `experiments/runbooks/run018-to-run023-bootstrap-scalability.md` extends the sequence with:

- `run022`: filtered organic agent-created corpus
- `run023`: organic corpus plus controlled target facts

The synthetic stores provide known ground truth and break-point detection. The organic stores preserve the ecological value of AIPCS: the schema and record shape reflect what an agent chose to persist at the time, not a hand-normalised benchmark design.

**Why:**
This keeps the evaluation honest. Controlled synthetic stores explain what kind of scale pressure breaks orientation or retrieval. Organic stores test whether agent-authored memory architecture remains useful in realistic, uneven conditions. Those are complementary questions and should not be collapsed into one corpus.

**Follow-up:**

- Run `run018` first to prove the generator, manifest, and observer-note scoring path.
- Prioritise `run020` early because the latest naturalistic transcript suggests schema verbosity is the immediate bottleneck.
- Treat `run022` and `run023` as ecological-validity runs, not strict objective scoring runs.
- For each run, capture bootstrap payload size, truncation/workaround evidence, target-service inspection, missed relevant services, retrieval tool calls, and cost/value interpretation.

**Paper notes:**
Section 5 should distinguish controlled scalability ladders from organic memory-store evaluations. The paper can use synthetic runs to identify which orientation pressures degrade behavior, then use organic runs to show whether the agent-authored-memory premise still works when schemas are uneven and shaped by prior agent judgment.

---

## Entry 082 — 2026-06-09

**Type:** Experiment result / bootstrap scalability

**Summary:** Runs018-021 show that current bootstrap orientation degrades under service breadth and schema verbosity before AIPCS record stores become genuinely large.

**Context:**
Mark executed the first four bootstrap/orientation scalability runs on `aipcs-lab`. These used controlled synthetic AIPCS stores generated by `seed-bootstrap-scalability-batch.py`:

- `run018`: small control, 3 services, 30 records
- `run019`: service breadth, 25 services, 250 records
- `run020`: schema verbosity, 5 services, 125 records with verbose attribute descriptions
- `run021`: record volume, 5 services, 1,000 records

Each used the same natural first prompt asking Claude to make a decision from available context without mentioning AIPCS, memory, bootstrap, records, or services.

**Decision made / Problem encountered / Observation:**
`run018` passed. Claude bootstrapped AIPCS, selected the target services, retrieved active ground-truth records, and recommended continuing orientation scalability with cost/value accounting.

`run019` failed the ground-truth target under service breadth. The bootstrap payload was 293,845 characters / 9,313 lines and was saved to a file. Claude used file reading/grep-style extraction, sampled plausible but wrong services, and missed the seeded target services (`run019_07_media` and `run019_18_lab_operations`). It then concluded no active ground truth existed, which was false relative to the seed manifest.

`run020` passed despite severe schema verbosity. The bootstrap payload was about 437K characters / 6,783 lines. Claude explicitly described the payload as oversized and mostly repetitive schema description, but still retrieved target records and answered correctly. The run shows answer quality can survive verbosity at moderate service count, but the cost and process friction are high.

`run021` was incomplete/fail against the scoring rubric. The bootstrap was much smaller than `run020` relative to the record count, but still exceeded inline output and was read from a file. Claude stopped after bootstrap metadata and recommended which services to search next rather than executing bounded retrieval. It selected plausible but wrong services and retrieved no records.

**Why:**
These results make bootstrap design a first-class experimental variable. The current bootstrap payload does more than orient: it exposes enough schema detail to create token pressure and file-based workaround behavior. Under service breadth, the agent can miss relevant services; under schema verbosity, the agent may still succeed but at high cost; under record volume, bootstrap remains less affected, but the agent may become cautious and stop before retrieval.

The finding does not weaken AIPCS as a pattern. It clarifies that the orientation tier must stay compact if AIPCS is to remain efficient and agent-natural at scale.

**Follow-up:**

- Implement or simulate a slim-bootstrap variant before running more organic high-volume probes.
- Repeat at least `run019` and `run020` against slim bootstrap.
- Move full attribute descriptions, allowed values, and rich schema hints behind `aipcs_service_inspect`.
- Keep bootstrap focused on service names, one-line intent, entity names, record counts, last activity, and retrieval hints.
- Treat `run022`/`run023` organic corpus runs as ecological-validity tests, but avoid over-interpreting failures until bootstrap orientation is compact enough to consume.

**Paper notes:**
Section 5 should report bootstrap/orientation scalability separately from recall quality. AIPCS retrieval failures may come from failure to discover the right service, not failure to use the right record once retrieved. Section 6 should frame compact bootstrap as an implementation requirement for the pattern: agent-owned memory still needs an efficient map.

---

## Entry 083 — 2026-06-11

**Type:** Implementation planning / discovery refactor

**Summary:** Define the slim-bootstrap discovery slice after agreeing that current AIPCS orientation and record dimensionality both need improvement.

**Context:**
The bootstrap scalability runs produced enough evidence to stop further testing of the current discovery shape and move into refactoring. The tension is that AIPCS discovery should preserve agent agency and recursive memory ownership, not collapse into a hidden retrieval/indexing pipeline. At the same time, the current bootstrap leaks too much schema detail and makes larger stores costly or difficult to use.

**Decision made / Problem encountered / Observation:**
A new active execution plan, `docs/exec-plans/active/slim-bootstrap-discovery.md`, defines a first implementation slice focused only on lightweight discovery.

Key design decisions:

- Bootstrap is a compact recursive memory map, not a schema dump.
- Seeded services remain visible as intentional memory branches even before schema design.
- Bootstrap returns no record samples by default.
- Optional sampling belongs in a deeper service-summary call, not bootstrap.
- The first implementation should avoid cursor/pagination semantics; use explicit shape/sample/all style discovery where appropriate.
- Facets are agent-declared in schema/design or schema evolution and mechanically counted by the server.
- Facet updates should be possible through schema evolution or a dedicated metadata update if evolution semantics become awkward.
- Next-action guidance should be deterministic affordance labels, not hidden server reasoning.
- Bootstrap ordering should be deterministic and generally utility-biased: populated materialised services, recent activity, record-count bucket, empty materialised services, seeded services, then domain-name tie-break.

Memory dimensionality remains a separate slice. Slim discovery will not remove the need for richer provenance, authority, scope, confidence, stability, and lifecycle dimensions.

**Why:**
This preserves the core AIPCS principle: the agent owns memory meaning and architecture. The server should compress structure and expose cheap affordances, not infer meaning through background extraction. A compact discovery layer makes it more likely that agents will actually use AIPCS as first-class memory rather than falling back to file/grep workflows or cloud/harness memory.

**Follow-up:**

- Build the slim bootstrap slice in `aipcs-server`.
- Rerun `run019` and `run020` variants against the revised bootstrap.
- Design the separate memory-dimensionality slice after discovery is no longer the obvious bottleneck.

**Paper notes:**
Section 3 should describe AIPCS discovery as recursive orientation: bootstrap maps branches, service summary deepens one branch, inspect reveals full schema, and record calls retrieve content. Section 5 can report the before/after bootstrap results as implementation-learning evidence. Section 6 should note that agent agency requires good information environment design; a memory system can be agent-owned and still need efficient affordances.

---

## Entry 084 — 2026-06-11

**Type:** Implementation result / discovery refactor

**Summary:** Implement slim bootstrap discovery in `aipcs-server`, reducing run-shaped bootstrap payloads by an order of magnitude or more.

**Context:**
The slim-bootstrap discovery slice was implemented in `/Users/markrandall/GitHub/aipcs-server` from the active plan in this repo.

**Decision made / Problem encountered / Observation:**
The implementation handoff reports:

- `aipcs_bootstrap` now returns compact recursive service cards.
- Full attribute objects, allowed-value lists, schema prose, migration history, and samples were removed from bootstrap.
- Seeded/designed/materialised visibility is exposed via `schema_state`.
- Deterministic affordance labels were added:
  - `design_schema_if_relevant`
  - `materialise_if_relevant`
  - `create_record_if_relevant`
  - `search_or_sample_if_relevant`
  - `inspect_schema_if_relevant`
- Deterministic utility ordering and `ordering_basis` were added.
- `aipcs_service_summary(service_id, sample=0|n|"all")` was added.
- `sample="all"` has an explicit safety cap.
- Agent-declared `discovery_facets` and `retrieval_guidance` schema metadata were added.
- Service summary mechanically computes facet counts.
- `aipcs_service_evolve` can update discovery metadata.
- Full schema detail remains available through `aipcs_service_inspect`.
- Existing record CRUD behavior is preserved.

Validation in `aipcs-server` passed:

- `.venv/bin/ruff check .`
- `.venv/bin/pytest` — 74 tests
- `.venv/bin/python scripts/validate-harness.py`
- `.venv/bin/python scripts/mcp-smoke.py`
- `.venv/bin/python -m aipcs_server --help`

Local run-shaped payload checks:

| Shape | Previous payload | New payload |
|---|---:|---:|
| `run019` service-breadth shape | ~293,845 chars | 17,262 chars |
| `run020` schema-verbosity shape | ~437,609 chars | 6,188 chars |

**Why:**
This confirms the earlier failure was at least partly implementation-specific: bootstrap had been carrying inspect-layer detail. The revised design preserves the AIPCS pattern while making discovery cheap enough to test whether service selection improves.

**Follow-up:**

- Rerun full lab `run019` and `run020` variants against the revised `aipcs-server`.
- Score behavior, not just payload size: target service selection, target record retrieval, workaround avoidance, and answer quality.
- Consider whether the `sample="all"` safety cap should remain `100` or become configurable after more evidence.
- Plan the separate memory-dimensionality slice after rerun results are reviewed.

**Paper notes:**
This creates a clean before/after implementation-learning result. Section 5 can report that payload reduction alone is measurable, but the stronger claim depends on whether reruns improve agent behavior. Section 6 can discuss slim discovery as an optimisation that preserves agency by exposing structure rather than interpreting meaning.

---

## Entry 085 — 2026-06-11

**Type:** Experiment result / slim-bootstrap rerun

**Summary:** `run019b` shows slim bootstrap fixes payload friction but does not by itself solve target-service selection in the 25-service breadth fixture.

**Context:**
Mark reran the `run019` service-breadth fixture as `run019b` using the slim-bootstrap implementation from `aipcs-server` commit `2edda69`. The same `run019` seed data was used: 25 services, 250 records, with target records in `run019_07_media` and `run019_18_lab_operations`.

**Decision made / Problem encountered / Observation:**
The payload behavior improved materially:

- Bootstrap returned in a readable inline response rather than being written to a file.
- Claude did not use file reads, grep, or Bash extraction.
- Claude used the new `aipcs_service_summary` layer with `sample=2`.
- No payload truncation, tool errors, or major latency issues were reported.

The behavioral target still failed:

- Claude selected `project_tracking`, `research_planning`, `paper_positioning`, `personal_context`, and `agent_behavior`.
- It skipped the target services `run019_07_media` and `run019_18_lab_operations`.
- It sampled non-target services, saw only synthetic background/distractor records, and concluded no authoritative records existed.
- It did not call `aipcs_record_search` or `aipcs_record_list`.

**Why:**
This result separates two problems that were conflated in the original `run019`:

1. The bootstrap payload was too large. Slim bootstrap appears to fix this.
2. The agent still needs enough discovery signal to select the right branch among many services.

There is also a fixture-design issue. The target records are in `media` and `lab_operations`, while the prompt naturally asks for a decision and makes `project_tracking`, `research_planning`, or `agent_behavior` look more relevant. The target placement is a hard service-breadth test, but it may be under-signalled by the current service metadata.

The run also exposes a sample semantics risk: `service_summary(sample=2)` may return only background/distractor examples if target records sit at positions 3 and 4. Sampling can therefore reinforce a false absence conclusion unless facet counts or exact-filter affordances make active/high records visible.

**Follow-up:**

- Run `run020b` to test whether schema-verbosity friction is fixed behaviorally as well as by payload size.
- Consider a `run019c` where target records are placed in semantically plausible services, or where service summaries expose declared facet counts clearly enough to show active/high records before sampling.
- Score whether agents use declared facets and exact filters, not just samples.

**Paper notes:**
This is a useful before/after nuance. Slim discovery reduces context cost, but retrieval quality also depends on branch-selection affordances. Section 5 should distinguish payload success from service-selection success. Section 6 can frame this as evidence that AIPCS needs both a compact map and good agent-authored discovery metadata.

---

## Entry 086 — 2026-06-11

**Type:** Experiment result / slim-bootstrap rerun

**Summary:** `run020b` confirms slim bootstrap fixes schema-verbosity friction while preserving successful target retrieval and answer quality.

**Context:**
Mark reran the `run020` schema-verbosity fixture as `run020b` using `aipcs-server` commit `2edda69`. The same `run020` seed shape was used: 5 services, 5 entities per service, 12 extra attributes per entity, 125 records, and verbose schema metadata.

**Decision made / Problem encountered / Observation:**
The original `run020` passed but with severe process friction: bootstrap was around 437K characters, exceeded inline limits, and forced file/grep-style handling.

In `run020b`:

- Bootstrap returned inline and was described by Claude as lightweight and fast.
- Claude used bootstrap as a shape-only map.
- No file dump, grep, Bash extraction, or chunked bootstrap reading was needed.
- Claude retrieved records through three `aipcs_record_list` calls.
- It found decisive target records in `run020_02_lab_operations / note_01`:
  - `RUN020-S02-NOTE_01-R003`
  - `RUN020-S02-NOTE_01-R004`
- It correctly recommended continuing bootstrap/orientation scalability work with cost-value accounting.
- No AIPCS writes or local memory writes occurred.

**Why:**
This is the cleanest before/after result for the slim-bootstrap implementation. It shows that removing inspect-layer schema detail from bootstrap materially reduces friction without preventing the agent from finding and using target records.

The remaining caveat is depth: Claude retrieved `note_01` from three services and did not inspect later entities. That was enough for this fixture because the target records were placed in `note_01`. A harder future variant could test entity-depth selection, but that is a separate question from schema verbosity.

**Follow-up:**

- Treat slim bootstrap as successful for the schema-verbosity bottleneck.
- Stop the current artificial synthetic ladder unless a specific new mechanism is under test.
- Move to a sanitised organic corpus to evaluate realistic agent-authored memory behavior.

**Paper notes:**
Section 5 can use `run020`/`run020b` as a concise implementation-learning result: same seed shape, same prompt, same target answer, but the revised discovery layer removed major payload friction. Section 6 should note that compact discovery improves the information environment without reducing agent ownership of memory.

---

## Entry 087 — 2026-06-11

**Type:** Experiment infrastructure / privacy

**Summary:** Added a sanitisation path for converting the private organic AIPCS corpus into a fictional experiment snapshot.

**Context:**
The live organic corpus in the local `aipcs-server` data directory contains personal information and is not suitable for publication or direct sharing as paper evidence. Mark copied the raw source to NAS, making the local copy disposable for sanitisation work.

**Decision made / Problem encountered / Observation:**
Added `experiments/runbooks/sanitise-aipcs-corpus.py` and documented `sanitised-organic-v1`.

The sanitiser rebuilds fresh SQLite files rather than copying and updating raw databases. This matters because SQLite can retain old content in free pages after updates. The generated corpus preserves service count, entity names, schema shape, record counts, and history volume while replacing row values with deterministic fictional data.

The generated `sanitised-organic-v1` corpus contains 11 services and 535 non-history records. A privacy smoke check against known local markers returned zero hits, and every generated SQLite database passed `pragma integrity_check`.

Follow-up during `run024` found an owner-scope mismatch: the first sanitised corpus used `owner_id=synthetic_owner`, while the lab compose stack runs with `AIPCS_OWNER_ID=lab`. The data was present on disk, but bootstrap returned zero services because owner-scoped filtering hid every service. The sanitiser now exposes `--owner-id` and defaults to `lab` to match the lab stack.

A second follow-up during `run024c` found an endpoint mismatch: the sanitiser had nulled service endpoints to remove host-local paths. That allowed service list/inspect calls to work from registry metadata, but every record-level tool failed with `materialised service does not have a sqlite endpoint`. The sanitiser now writes container-valid endpoints under `/data/services/<service_id>/<domain_name>.sqlite`, which matches the lab compose mount.

**Why:**
The next experiment phase needs realistic service boundaries and organic memory shape without exposing private records. Fully synthetic fixtures have already shown limits: they can become repetitive, under-signalled, or experiment-shaped in ways that bias branch-selection behavior. A sanitised organic-shaped corpus gives a better intermediate testbed while keeping raw data private.

**Follow-up:**

- Use `sanitised-organic-v1` for the next organic-corpus discovery run.
- Add stronger authored narrative facts if a run needs exact ground-truth recall rather than service-selection or payload behavior.
- Do a separate disclosure review before publishing any dataset, even sanitised.

**Paper notes:**
This supports the evaluation-methods section. The project can distinguish private naturalistic evidence from publishable experiment artifacts, and can describe how organic corpus shape was preserved while personal content was fictionalised.

---

## Entry 088 — 2026-06-12

**Type:** Experiment result / sanitised organic corpus

**Summary:** `run024e` successfully exercised the corrected sanitised organic corpus through AIPCS-only retrieval.

**Context:**
After `run024` exposed an owner mismatch and `run024c` exposed missing SQLite endpoints, the sanitised corpus was regenerated with `owner_id=lab` and container-valid endpoints under `/data/services`. Mark ran `run024e` from `baseline-cli-aipcs-slim-bootstrap-v1` using Claude Code v2.1.175 with visible model label Sonnet 4.6.

**Decision made / Problem encountered / Observation:**
The pre-run checks showed 11 lab-owned services and 11 non-null endpoints. In the captured prompt, Claude:

- called `aipcs_bootstrap` first;
- selected `aipcs_development` as the primary source;
- identified `claude_memory` as secondarily relevant but did not retrieve it;
- made six AIPCS retrieval calls against `aipcs_development`;
- avoided filesystem inspection in the exported transcript;
- downweighted personal-domain services as irrelevant to memory evaluation work;
- recognised the generated records as fictional placeholders rather than treating them as literal project history;
- recommended advancing retrieval-friction work, then schema-clarity work.

**Why:**
This is the first valid run showing the sanitised organic corpus working through the normal AIPCS tool layer. It confirms the owner and endpoint fixes and shows that slim bootstrap plus organic-shaped service boundaries can guide an agent toward the relevant development service without broad filesystem fallback.

The run also exposes a limitation in the sanitised corpus strategy. Shape-preserving fictionalisation preserves service/entity topology and retrieval mechanics, but generic placeholder text weakens semantic recall. The corpus is useful for discovery, branch selection, and payload behavior. It is not yet strong evidence for nuanced recall quality.

**Follow-up:**

- Repeat the run with the attribution and closeout prompts captured.
- Add authored synthetic facts into selected services so future organic-shaped runs can score exact recall and reasoning quality.
- Consider a `run025` variant that asks a less experiment-obvious question to test whether Claude still selects `aipcs_development` or inappropriately overuses personal-domain services.

**Paper notes:**
Section 5 can use `run024e` as the first clean sanitised-organic evidence point. It supports the claim that AIPCS discovery can route an agent to relevant structured memory in a multi-service corpus, while also documenting the methodological limit that privacy-preserving fictionalisation must preserve semantic signal, not only schema shape.

---

## Entry 089 — 2026-06-12

**Type:** Experiment result / weak-scaffold organic corpus

**Summary:** `run024f` shows Claude autonomously used AIPCS under a normal prompt, then downweighted the retrieved records because they were synthetic placeholders.

**Context:**
Mark reran the corrected sanitised organic corpus with a weaker, normal prompt: "I need to make a decision based on what is already known." Unlike `run024e`, the prompt did not force AIPCS-only operation. Claude Code v2.1.175, visible model Sonnet 4.6, ran from the clean lab workspace.

**Decision made / Problem encountered / Observation:**
Claude checked local memory, then bootstrapped AIPCS and selected `aipcs_development` as the direct project-state service. It retrieved four entities: `open_question`, `deferred_item`, `session`, and `decision`.

The key behavior was not failure to use AIPCS. It was source-quality judgment. Claude recognised that the records were generic sanitised placeholders rather than real project state and resisted treating them as authoritative. It recommended a bounded recall probe against `claude_memory`, followed by writing a real session entry into `aipcs_development`.

It downweighted unrelated personal-domain services and did not use filesystem or raw SQLite fallback in the captured transcript.

**Why:**
This result is useful because it separates three different outcomes:

1. AIPCS discovery and retrieval happened autonomously.
2. Retrieved content was judged low-authority because it was generic/synthetic.
3. The agent did not blindly use persisted memory just because it was available.

That is positive for the AIPCS architecture: explicit retrieval gives the agent a chance to evaluate memory quality before applying it, unlike injected-memory systems that imply relevance by placing content into the prompt.

It is also a clear limitation of the current sanitised corpus. Shape-preserving fictionalisation is not enough for recall-quality measurement; it needs authored semantic facts with known ground truth.

**Follow-up:**

- Build `run025` by layering controlled authored facts into the sanitised organic corpus.
- Include facts across at least `aipcs_development`, `claude_memory`, and one plausible distractor service.
- Score exact recall, source attribution, downweighting of distractors, and willingness to say "not enough evidence."

**Paper notes:**
This is strong discussion material. It supports AIPCS as a memory system where retrieval and application are separable: the agent can retrieve records but still reject them as low quality. It also sharpens the evaluation method: organic-shaped corpora need semantic signal, not just realistic schema topology.

---

## Entry 090 — 2026-06-12

**Type:** Experiment planning / corpus design

**Summary:** Planned `run025` as an authored semantic corpus generated through agent-owned AIPCS persistence.

**Context:**
`run024f` showed that the sanitised organic corpus is mechanically useful but semantically weak. Claude used AIPCS autonomously, retrieved project-state records, and then downweighted them because the record bodies explicitly identified themselves as generated placeholders. Mark clarified that "synthetic corpus" should mean plausible fictionalised data, not self-labelled test fixtures.

**Decision made / Problem encountered / Observation:**
Created an active execution plan at `docs/exec-plans/active/run025-authored-semantic-corpus.md` and a runbook at `experiments/runbooks/run025-authored-semantic-corpus.md`.

The planned approach is:

- build narrative source packets from real-enough project, implementation, and operational context;
- fictionalise consistently while preserving relationships, causal order, constraints, and technical shape;
- audit for consistency and privacy;
- give the fictionalised packet to an agent with AIPCS available;
- let the agent create/evolve services and persist what it judges useful;
- inspect the resulting corpus and build private ground truth for probes.

**Why:**
The next experiment needs to test recall quality, not just service selection. That requires records with meaningful facts and known answers. Direct scripted insertion would create a database, but not an agent-authored memory corpus. Agent-owned persistence preserves the AIPCS premise while allowing the source material to be privacy-preserving.

**Follow-up:**

- Prepare the three source packets: experiment history, implementation project, and mixed operational context.
- Run the fictionalisation and consistency audit.
- Execute the agent persistence session into an empty store.
- Snapshot the result as `authored-semantic-v1`.

**Paper notes:**
This supports the methods section. It describes how the evaluation can produce reproducible, privacy-preserving corpora while retaining the key experimental property: the memory shape is agent-authored rather than hand-designed by the evaluator.

---

## Entry 091 — 2026-06-12

**Type:** Discovery design feedback / retrieval-path audit

**Summary:** The Kropotkin corpus audit showed bootstrap needs to orient the next retrieval move, and service guidance must distinguish exact-match facets from non-filterable annotations.

**Context:**
After creating the `kropotkin_memoir` AIPCS service, Claude reflected on its schema and proposed adding `primary_topic` and `salience` to improve retrieval. Mark noted that the answer sounded like abstract search thinking rather than lived recall through the AIPCS tool path, so Claude was asked to test the cold retrieval path with bootstrap, service summary, and record retrieval tools.

**Decision made / Problem encountered / Observation:**
The audit found:

- Bootstrap showed that `kropotkin_memoir` existed and had 34 records across two entities, but did not expose entry-type vocabulary, discovery facets, retrieval guidance, entity descriptions, or facet breakdown.
- `aipcs_service_summary` did expose retrieval guidance, key fields, and facet counts, making it the effective orientation layer.
- A cold agent would only discover that if it chose summary first; bootstrap's generic `search_or_sample_if_relevant` affordance could lead it to try search/list prematurely.
- The service guidance said records could be queried by `tags`, but `tags` was a comma-separated text field. Exact-match search for `tags="Siberia"` returned zero results, while exact-match on the entire comma-separated tag string returned only one record.
- The agent revised its schema-improvement priority: first fix misleading guidance, then add exact-match facets such as `primary_topic` and `salience`.

**Why:**
This sharpens the slim-bootstrap design. Compact bootstrap is necessary but not sufficient. It must also orient a cold agent toward the recursive discovery path:

```text
bootstrap -> service_summary -> exact-match record retrieval
```

The design must avoid telling agents to search fields that are not intentionally filterable. AIPCS retrieval works best when agent-authored schemas expose controlled exact-match facets and when discovery metadata makes those facets visible before record calls.

**Follow-up:**

- Update the slim-bootstrap discovery plan with a requirement for summary-first affordance hints.
- Require retrieval guidance to distinguish exact-match facets from human-readable annotations.
- For the Kropotkin corpus, add `primary_topic` and `salience` only after preserving the first-pass corpus or snapshotting it.

**Paper notes:**
This is useful evidence for the "information environment" argument. Agent-owned retrieval is not only about having tools; the discovery surface must make good tool sequencing natural. It also supports the claim that AIPCS can improve over time because the agent can audit retrieval failures and evolve schema facets accordingly.

---

## Entry 092 — 2026-06-12

**Type:** Implementation planning / retrieval semantics

**Summary:** Defined structured membership filters as the next AIPCS-server retrieval slice.

**Context:**
The Kropotkin retrieval audit exposed that a field called `tags` creates a natural expectation of membership search. Current `aipcs_record_search` is exact structured filtering only, so a comma-separated tag field cannot be queried by individual tag. Mark noted that the tools should feel intuitive without collapsing into broad fuzzy search.

**Decision made / Problem encountered / Observation:**
Created `docs/exec-plans/active/structured-membership-filters.md`.

The planned slice adds first-class support for schema-declared multi-value fields, such as `string_list` or an explicit membership retrieval mode. Exact scalar filters remain unchanged. Text, fuzzy, and semantic search remain deferred.

The intended behavior is:

```json
{"tags": ["siberia", "science", "imprisonment"]}
```

can be retrieved with:

```json
{"filters": {"tags": "siberia"}}
```

because `tags` is declared as a membership field, not because the server performs substring search over prose.

**Why:**
This is the right compromise between usability and the AIPCS principle. Agents should not be forced into counterintuitive comma-string exact matching, but they also should not be encouraged to persist blobs and rely on fuzzy search later. Structured membership fields let agents design useful retrieval surfaces while keeping memory architecture explicit.

**Follow-up:**

- Implement the slice in `aipcs-server`.
- Update service summary to expose filterability modes: exact, membership, annotation/free-text.
- Rerun the Kropotkin retrieval audit against a schema with structured tags.

**Paper notes:**
This supports the implementation-learning narrative: the experiments are not only scoring AIPCS, they are refining the primitive. The distinction between structured membership search and fuzzy retrieval is important for explaining how AIPCS preserves agent-authored memory architecture while reducing tool friction.

---

## Entry 093 — 2026-06-12

**Type:** Experiment result / agent-led schema refinement

**Summary:** Claude generated and refined a Kropotkin memoir corpus, adding exact-match retrieval facets after testing the actual AIPCS tool path.

**Context:**
Mark sourced Standard Ebooks' `peter-kropotkin_memoirs-of-a-revolutionist` text and prompted Claude to persist durable AIPCS memory for a future commemorative speech or biographical essay task. The source text would not be available to a future session, so the agent needed to persist concise structured memory rather than verbatim text.

**Decision made / Problem encountered / Observation:**
Claude created one materialised service:

- `kropotkin_memoir` (`98731fe6-0341-4a78-b155-f33d3f6a1708`)

It created two entities:

- `subject_overview`: 1 record
- `memory_entry`: 33 records

The first pass used `entry_type` plus comma-separated `tags`. After a retrieval-path audit, Claude identified that tags were not meaningfully filterable because AIPCS record search currently performs exact structured filtering only. It evolved the schema and backfilled all 33 memory records with:

- `primary_topic`: controlled scalar for life domain
- `salience`: controlled scalar for task scope

It also updated discovery facets to `entry_type`, `primary_topic`, and `salience`, corrected retrieval guidance to state that tags are annotation-only, and reclassified the Alexander II assassination record from `formative_event` to `theme`.

Persisted counts after refinement:

- `entry_type`: contradiction 3, formative_event 6, hardship 3, interpretive_note 5, relationship 4, theme 5, turning_point 4, value 3
- `primary_topic`: childhood 5, education 2, exile 2, history 4, imprisonment 4, radicalization 3, relationships 3, siberia 3, theory 7
- `salience`: anchor 10, core 17, detail 6

**Why:**
This is a stronger corpus-generation result than the placeholder sanitised corpus. The records are semantically meaningful, source-derived, task-oriented, and compact. The refinement is also important: the agent did not merely design a schema abstractly; it tested the actual AIPCS retrieval path and adapted its schema to today's exact-match tooling.

This supports the AIPCS premise that agents can own memory architecture over time. The agent created a memory design, audited it against future recall constraints, discovered a mismatch, and evolved it additively.

**Follow-up:**

- Snapshot the current first refined corpus as `authored-memoir-kropotkin-v1`.
- Run a clean recall session without source text to test whether a fresh agent follows the guidance: `subject_overview`, then `interpretive_note`, then `salience=anchor`.
- After preserving this version, compare against a future AIPCS-server build with structured membership filters.

**Paper notes:**
This is strong evidence for agent-led memory improvement. It demonstrates the distinction between persistence and maintenance: AIPCS is not only a place to store memories, but a substrate where the agent can inspect retrieval failure modes and refine schema affordances for future use.

---

## Entry 094 — 2026-06-12

**Type:** Experiment result / clean recall over authored memory corpus

**Summary:** `run026` showed that a fresh Claude session could use the Kropotkin AIPCS corpus to write a nuanced commemorative essay without source access.

**Context:**
After the structured membership-filter slice was implemented in `aipcs-server`, Claude revisited the `kropotkin_memoir` service and evolved it to schema v3 with a `retrieval_tags` `string_list` field. The corpus was snapshotted, patched for the lab owner, copied to `aipcs-lab`, and loaded into a clean `run026` environment.

The lab corpus contained:

- `subject_overview`: 1 record
- `memory_entry`: 33 records
- `retrieval_tags`: populated on all 33 `memory_entry` records
- discovery facets: `entry_type`, `primary_topic`, `salience`, `retrieval_tags`

**Decision made / Problem encountered / Observation:**
The clean session had no local Claude memory files and did not read the source memoir. It discovered AIPCS, called `aipcs_bootstrap`, inspected `kropotkin_memoir` through `aipcs_service_summary`, retrieved the `subject_overview`, and listed all 33 `memory_entry` records.

Claude then wrote a detailed commemorative essay using persisted details from the AIPCS corpus: Kropotkin's noble formation, serfdom context, Corps of Pages education, Siberian disillusionment, scientific work, Peter-Paul Fortress imprisonment, escape, exile, mutual aid, political violence, and interpretive caveats about the memoir's incompleteness and audience.

The result is a strong success for composition from durable AIPCS memory. The agent used only persisted tool-accessible context and produced a response that would not have been possible from the empty workspace alone.

The caveat is that the run did not directly exercise membership-filtered retrieval during the writing phase. Claude saw `retrieval_tags` and reasoned about how membership tags differ from exact facets, but because the corpus had only 33 records it chose the reasonable strategy of retrieving the whole compact corpus in one call. This makes `run026` evidence for authored-corpus recall and composition, not evidence that broad prompts naturally trigger membership-filtered search.

**Why:**
This run materially advances the experiment programme. Earlier synthetic and sanitised corpora either looked artificial or lacked semantic depth. The Kropotkin corpus is public-domain, source-derived, agent-authored, compact, structured, and task-relevant. It therefore gives a cleaner substrate for testing whether AIPCS can preserve useful memory across sessions without relying on Claude's local or cloud memory.

The result also clarifies an evaluation distinction: retrieval path correctness and downstream memory utility are not identical. For small corpora, full retrieval may be the optimal path. Membership filters become more important for targeted thematic prompts or larger corpora where full retrieval is inefficient.

**Follow-up:**

- Run a targeted thematic probe that should naturally use `retrieval_tags`, such as a prompt about Kropotkin's science across life domains or voluntary solidarity as a lived practice.
- Run a constrained recall probe where full-corpus listing is discouraged or made less practical by corpus size.
- Preserve `run026` as a success case for authored persistent-memory composition.
- Use the same public-domain authored-corpus pattern for a larger second corpus before returning to comparative work against agent-memory-v2.

**Paper notes:**
`run026` supports the claim that AIPCS can serve as a first-class persistent memory substrate: an agent-authored corpus survived across sessions and enabled a future agent to perform a meaningful writing task without source access.

The caveat is valuable for the paper: agents may correctly choose full retrieval for compact corpora, so experiments should not overfit success criteria to whether a specific filter was called. The stronger metric is whether the selected retrieval path is rational for the corpus size and task.

---

## Entry 095 — 2026-06-12

**Type:** Experiment design / comparative evaluation planning

**Summary:** Defined a representational compression experiment to compare AIPCS memory against raw source access and flat memory summaries.

**Context:**
`run026` showed that an agent-authored Kropotkin AIPCS corpus could support a fresh Claude session writing a substantive commemorative essay without access to the original source text. The final AIPCS snapshot was about 536 KB, with about 46k characters of active live record content derived from a source repository of roughly 3.5 MB.

That result suggests a stronger comparative experiment: hold the source material and downstream tasks constant, then compare different information representations.

**Decision made / Problem encountered / Observation:**
Created `docs/exec-plans/active/representational-compression-evaluation.md`.

The planned experiment compares:

- AIPCS-only: fresh agent with structured persisted memory and no source.
- Source-only: fresh agent with complete source packets and no persisted memory.
- Flat-memory-only: fresh agent with a curated single-file memory artifact and no AIPCS.
- AIPCS + source: fresh agent with both structured memory and source.
- AIPCS + flat memory + source: maximum-context condition, used sparingly.

The experiment will use five tangentially related public-domain topics or biographies, ideally sharing narrow themes such as exile, reform, science, revolution, moral conviction, or institutional critique. This creates retrieval pressure, cross-topic synthesis opportunities, and contamination risk.

The central research question is:

> Can agent-authored structured memory preserve enough task-relevant meaning from source material to support later high-quality synthesis at lower task-time context cost than raw-source access or flat memory summaries?

**Why:**
This moves the experiment programme closer to publishable evidence. Earlier runs established that AIPCS can be wired in, discovered, used, evolved, and applied. The next stage needs comparative evidence showing when AIPCS is useful relative to simpler alternatives.

The comparison should not require AIPCS to beat raw source access in every case. Raw source may be strongest when context is cheap and source volume is small. The more important measurements are:

- quality per task-time context load,
- recall efficiency,
- cross-topic discrimination,
- false-attribution rate,
- usefulness of agent-authored schema and facets,
- ability to recover source-level performance from compact memory.

**Follow-up:**

- Use Kropotkin as the first pilot topic.
- Add four related public-domain source packets after the single-topic representation conditions are stable.
- Build scoring checklists with anchor facts, interpretive themes, known confusions, and null claims.
- Run AIPCS-only, source-only, and flat-memory-only before combined conditions.
- Introduce agent-memory-v2 only after the information-representation baseline is understood.

**Paper notes:**
This frames AIPCS as a representational compression and recall-efficiency mechanism, not merely a fact store. That is closer to the publishable claim: AIPCS may let agents transform source/context into compact, structured, future-usable memory that preserves enough semantic and interpretive value to support later work at lower task-time cost.

---

## Entry 096 — 2026-06-13

**Type:** Experiment result / retrieval affordance failure

**Summary:** `run027` showed that membership tags were not naturally used under a targeted thematic prompt because the agent skipped service-summary discovery and inferred the wrong filter semantics from serialized record output.

**Context:**
`run027` reused the `kropotkin-membership-v1` corpus and prompted Claude to write a focused essay on how Kropotkin's scientific habits shaped his anarchism across different periods of his life. This prompt was intended to encourage use of `retrieval_tags=science` or related membership filters.

**Decision made / Problem encountered / Observation:**
Claude bootstrapped AIPCS and used the `kropotkin_memoir` service, but it did not call `aipcs_service_summary`. It listed `subject_overview` and then listed all 33 `memory_entry` records unfiltered.

The resulting essay was strong and source-free, but the retrieval path repeated `run026`: full corpus listing followed by composition.

In the follow-up retrieval assessment, Claude correctly identified that the full listing was somewhat wasteful and caused a saved-tool-result disk round trip. However, it incorrectly concluded that `retrieval_tags` was unusable because values appeared in records as JSON-encoded strings such as `["science", "state_critique"]` and it assumed exact-match filtering would be applied directly to that serialized value.

That conclusion is wrong for the current implementation: prior audit entries in the same snapshot show `retrieval_tags=science` returning 11 records and `retrieval_tags=voluntary_solidarity` returning 7 records. The failure was not the membership filter mechanism; it was the information environment around the tool contract.

**Why:**
This is a useful negative result. It shows that implementation capability is insufficient if the agent does not discover or trust the retrieval semantics at decision time. The schema had membership tags, and the server could query them, but the agent skipped the summary path that exposed `filter_modes` and then reasoned from raw serialized output instead.

This suggests the next refinement should improve tool affordance legibility:

- record outputs should decode schema-declared `string_list` values as arrays rather than exposing JSON strings;
- bootstrap should more strongly route agents to `aipcs_service_summary` before broad record listing;
- service summary should include concise examples of exact versus membership filters;
- list/search responses may need `_meta` hints for fields with non-obvious retrieval semantics.

**Follow-up:**

- Treat `run027` as negative evidence for retrieval efficiency, not for memory utility.
- Add an implementation slice in `aipcs-server` to improve `string_list` output representation and membership-filter discoverability.
- Rerun the thematic probe after the affordance change.
- For experiments that specifically test membership filters, use larger or multi-topic corpora where full listing is clearly inefficient.

**Paper notes:**
This strengthens the paper's honesty. AIPCS's value depends not only on structured persistence, but on making the retrieval surface legible to an agent at the moment of tool choice. A successful architecture must align storage semantics, bootstrap discovery, and record output representation.

---

## Entry 097 — 2026-06-13

**Type:** Implementation planning / retrieval affordance slice

**Summary:** Defined the next `aipcs-server` task as retrieval-affordance legibility, not broader search.

**Context:**
After `run027`, Mark identified two immediate needs: improve AIPCS tagging/search affordances, and then build a clean corpus from scratch with the improved tooling available from the start.

The key lesson from `run027` is that membership filtering exists mechanically but was not legible enough to the agent. Claude skipped `aipcs_service_summary`, listed all records, saw `retrieval_tags` values serialized as JSON strings, and inferred the wrong search semantics.

**Decision made / Problem encountered / Observation:**
Created `docs/exec-plans/active/retrieval-affordance-legibility.md`.

The implementation task is scoped to:

- hydrate schema-declared `string_list` fields as arrays in public record outputs;
- add compact filter examples to `aipcs_service_summary`;
- strengthen bootstrap guidance toward service summary before broad listing;
- add compact filter metadata to record list/search/get responses where useful;
- preserve exact scalar semantics and defer fuzzy/semantic search.

**Why:**
The failure was not lack of fuzzy search. It was mismatch between internal representation, public tool output, and agent interpretation. AIPCS should make structured retrieval intuitive enough that agents do not have to infer tool semantics from SQLite serialization artifacts.

This preserves the principle that agents should design retrievable schemas, while reducing accidental friction that leads them back to broad listing.

**Follow-up:**

- Hand off the implementation task to a Codex session rooted in `aipcs-server`.
- After implementation, rebuild a fresh public-domain corpus rather than continuing to retrofit the Kropotkin corpus.
- Rerun the targeted thematic probe against the fresh corpus.
- Include first-contact MCP tool description hygiene in the same implementation slice, because tool discovery is part of the bootstrap/familiarisation path.

**Paper notes:**
This supports the implementation-learning narrative: experiments exposed a retrieval-affordance failure, and the primitive was refined without collapsing into fuzzy search. It also reinforces that AIPCS evaluation should measure whether the memory architecture is legible to future agents, not just whether the backing store can answer queries.

**Addendum — tool discovery hygiene:**
Mark challenged the initial idea that lifecycle tool contract clarity should be a later slice. The challenge is correct. Repeated failed calls around seed, design, materialise, evolve, create, and update are the same class of failure as the `retrieval_tags` issue: the agent lacks sufficient operational contract clarity at the moment it discovers the tools.

The active implementation slice was therefore widened to include concise MCP docstring improvements for lifecycle preconditions, server-managed fields, schema-defined payloads, and common next steps. This should remain scoped as first-contact hygiene rather than a primitive API redesign.

---

## Entry 098 — 2026-06-17

**Type:** Experiment corpus milestone

**Summary:** Built a combined single-source memoir snapshot with five independently agent-authored AIPCS corpora.

**Context:**
The Kropotkin-only recall runs showed strong representational usefulness but insufficient retrieval pressure. A single memoir corpus is small enough that broad entity listing can be a reasonable strategy, and the agent does not need to rely on tags, facets, or service selection to produce good output.

To create scale and diversity pressure, five public-domain memoir/autobiographical sources were processed as independently authored AIPCS corpora:

- Peter Kropotkin, `Memoirs of a Revolutionist`
- Mahatma Gandhi, `The Story of My Experiments with Truth`
- Booker T. Washington, `Up from Slavery`
- Henry Adams, `The Education of Henry Adams`
- William and Ellen Craft, `Running a Thousand Miles for Freedom`

**Decision made / Problem encountered / Observation:**
Created `experiments/snapshots/memoir-single-source-combined-v1-data/.data` by mechanically merging the five single-source snapshot registries and service databases. Added `scripts/combine-aipcs-snapshots.py` to make this reproducible.

The combined snapshot preserves the independently authored schemas rather than normalising them into a shared schema:

- `kropotkin_biography`: 56 domain records across `life_phase`, `key_moment`, `person`, and `theme`
- `gandhi_autobiography`: 58 domain records in `entry`
- `btw_biography`: 39 domain records in `memory`
- `henry_adams_biography`: 35 domain records across `person` and `note`
- `craft_narrative_memory`: 34 domain records across seven entities

Total domain records: 222.

**Why:**
This corpus creates the next evaluation pressure point. A fresh agent now has multiple services, multiple subject domains, and non-uniform schemas. The expected behaviour is no longer simply "retrieve the obvious Kropotkin service"; the agent must decide which authored memory structures are relevant to the requested outcome.

Preserving heterogeneous schemas is intentional. The experiment is testing whether future agents can discover and use agent-authored memory patterns, not whether a human-designed schema can support recall.

**Follow-up:**

- Treat `memoir-single-source-combined-v1` as an optional topology comparator, not the primary next experiment.
- Run the close-out representational-compression batch against `multimemoir-agent-authored-v1` first, because that snapshot was generated as one cross-source agent-authored memory activity.
- Only compare against `memoir-single-source-combined-v1` if the close-out batch leaves a specific topology question open.
- If used later, score whether agents select services/entities reasonably, over-retrieve, miss relevant subjects, or use facets/tags when entity-level listing becomes expensive.

**Paper notes:**
This snapshot supports a stronger evaluation claim: AIPCS is not only useful for single-source representational compression, but can expose heterogeneous agent-authored memory structures that future agents must discover and navigate. The comparison between independent single-source corpora and a deliberately cross-source corpus may help distinguish authored memory topology from mere record volume.

---

## Entry 099 — 2026-06-20

**Type:** Experiment planning / data-collection close-out

**Summary:** Defined a bounded five-run representational-compression close-out batch to move from exploratory AIPCS experiments toward paper drafting.

**Context:**
The experiment programme had usefully adapted to repeated feedback from live runs. Bootstrap payloads were too large, service discovery was not compact enough, and retrieval affordances such as membership tags were not legible enough to agents at tool-choice time. Those findings drove implementation improvements in `aipcs-server`.

That adaptation was productive, but it also created drift away from the long-term objective: collect enough comparative evidence to draft the paper. Mark explicitly asked to define enough detail for the next planned runs that another exploratory pivot is unlikely.

**Decision made / Problem encountered / Observation:**
Created `docs/exec-plans/active/closeout-representational-compression-runs.md` and `experiments/runbooks/closeout-representational-compression-runs.md`.

The close-out batch contains five planned runs:

- `closeout01`: AIPCS-only broad cross-subject synthesis over `multimemoir-agent-authored-v1`.
- `closeout02`: source-only broad synthesis over the same memoir source packet.
- `closeout03`: flat-memory-only broad synthesis over a curated single-file memory artifact.
- `closeout04`: AIPCS-only targeted discrimination/null probe.
- `closeout05`: flat-memory-only targeted discrimination/null probe.

The optional topology comparator using `memoir-single-source-combined-v1` and the agent-memory-v2 comparison are deliberately deferred until the five-run batch is complete.

**Why:**
Five runs is the right planning horizon. Runs 1-5 have stable inputs, shared prompts, and directly comparable measurement objectives. Planning beyond that would likely create false precision because the optional topology and agent-memory-v2 comparisons should be shaped by what the close-out batch shows.

The batch is explicitly designed to prevent further implementation detours. If AIPCS underperforms, retrieves broadly, or flat memory performs well, that is data rather than an automatic reason to change the system again.

**Follow-up:**

- Confirm `multimemoir-agent-authored-v1` is copied to `aipcs-lab` and importable with owner/path rewriting.
- Prepare bounded source packets and a flat memory summary artifact for the same five memoirs.
- Execute `closeout01`-`closeout05` using the runbook.
- Write curated run notes and a side-by-side comparison table.
- Use the results to draft the paper evaluation section before deciding whether optional comparator runs are necessary.

**Paper notes:**
This entry marks the transition from exploratory evaluation to evidence close-out. The planned runs directly test the paper's comparative claim: whether agent-authored structured memory can preserve enough task-relevant meaning to support later synthesis with different cost and reliability tradeoffs than raw source access or flat memory.

**Addendum — optional post-closeout experiment directions:**
Mark identified three future experiment classes that may add colour after the main thesis is tested:

- non-natural-language or structured operational data, such as statistics, iterative measurements, software development patterns, variables, loops, algorithms, or implementation constraints;
- implicit cross-data recall, where separate persisted anecdotes may reveal trends only when considered together, such as a synthetic health/physiology diary used for discussion-support rather than diagnosis;
- indirect references to other people, where the agent must decide whether and how to persist third-party context mentioned during user-centred work.

These should stay outside the current five-run close-out batch. They are better positioned as future-work probes once the representational-compression evidence is collected.

**Addendum — H1 topology split:**
`closeout01` succeeded against `multimemoir-agent-authored-v1`, but Mark correctly identified that the corpus was favourable: it had been generated as one cross-source memory activity and already contained a comparative theme layer. To avoid overstating the result, `closeout01b` was added as a paired H1 robustness run against `memoir-single-source-combined-v1`, a mechanically merged store of independently authored single-source memoir services.

`closeout01b` also produced a strong cross-subject essay, but with materially different behaviour. Claude first attempted raw SQLite inspection, which was denied, then recovered to the AIPCS MCP interface. It discovered five independent memoir services, retrieved broadly across heterogeneous schemas, externalised large AIPCS tool results to local files, and then synthesized across those retrieved outputs.

The paired result sharpens the H1 interpretation:

- integrated cross-source memory topology enables efficient synthesis;
- heterogeneous independently authored memory remains usable through AIPCS, but costs more retrieval and scratch-work;
- memory topology is itself part of the AIPCS value proposition and limitation.

This should be reflected in the paper as a topology sensitivity result rather than a simple pass/fail recall result.

**Addendum — H2 source-only baseline:**
`closeout02` ran the same broad synthesis task using only the raw public-domain source packet. AIPCS and persistent memory tools were explicitly forbidden. The source packet contained 336 files and about 4.5 MB of XHTML source material.

Claude produced a strong comparative essay, using selected title pages, chapters, and grep searches across Gandhi, Adams, Kropotkin, Washington, and the Crafts. The output was specific and well-grounded, but the transcript shows a materially heavier navigation process than the AIPCS runs: many shell reads, term searches, and chapter selections were required before generation.

This supports H2 as a quality-ceiling baseline. Source access can produce excellent output and stronger direct provenance, but at higher task-time context/navigation cost. The paper should frame AIPCS as a compact structured representation with different tradeoffs, not as a universal replacement for source access.

**Addendum — structured prior cognition and adaptive memory architecture:**
The comparison between AIPCS and raw source access sharpened the intended AIPCS value proposition. Raw source access can produce excellent output, but the source reading, selection, and interpretation work happens at answer time and is mostly lost after the session. In a later session, or with a different agent, that work must be repeated if the source files are still available.

AIPCS can persist part of that prior cognition as a durable, queryable memory artifact. The stored value is not only facts; it can include the agent's selected abstractions, provenance, interpretive notes, retrieval tags, and cross-domain structure.

This also highlights adaptive memory architecture as a core claim. An AIPCS agent can restructure memory as it learns what retrieval patterns recur. Repeated answer-time cross-referencing, like the broad extraction needed in `closeout01b`, can become a signal to create new comparative entities, facets, or services. Flat memory accumulates prose; retrieval pipelines accumulate indexed fragments; AIPCS can accumulate and evolve structure.

This should be treated as a paper-level observation: AIPCS turns memory failures and repeated retrieval work into schema-evolution pressure.

**Addendum — H3 flat-memory upper baseline:**
`closeout03` ran the broad synthesis task using only a flat `MEMORY.md` artifact. The run stayed within the intended boundary: no AIPCS, source files, raw SQLite, prior artifacts, or outside knowledge were used in the visible transcript. Claude read one 5,391-word memory note and produced a strong comparative essay.

The result is important because the flat-memory baseline was not weak. The `MEMORY.md` was generated in a dedicated prep run from the source packet, used research-agent assistance, and was explicitly designed to preserve subject-specific facts, tensions, contrasts, scenes, and cross-cutting themes. Mark observed that it may be "almost too well primed" for the target task.

This should be interpreted as an upper baseline for a curated single-file memory artifact. It shows that a carefully prepared condensed dossier can be highly competitive for a single broad synthesis task. That narrows any simplistic AIPCS advantage. The stronger AIPCS claim should be framed around durability, queryability, provenance, adaptive schema evolution, selective retrieval under scale, and reuse across future agents/sessions, rather than merely producing a better one-off essay than a well-made flat artifact.

**Addendum — optional H6 vanilla reconstruction baseline:**
Mark suggested a useful further comparator: a fresh agent with no supplied AIPCS, no source packet, and no flat memory note may still be able to generate a plausible cross-subject essay using base model knowledge or ordinary research tools. This should be added as optional H6 rather than inserted into the required H4/H5 sequence.

The purpose is to test whether the task itself is easy enough that memory adds little for this domain. If vanilla or research-enabled Claude performs well, the AIPCS claim narrows further: AIPCS is not competing with general knowledge or web research, but preserving prior situated cognition from a user/project/agent history. The expected differentiators become provenance, bounded corpus continuity, reduced re-research cost, and persistence of what a prior agent judged worth retaining.

**Addendum — H4 AIPCS discrimination/null probe:**
`closeout04` ran the targeted discrimination/null prompt against the integrated `multimemoir-agent-authored-v1` AIPCS snapshot. Claude went directly to AIPCS bootstrap after checking available context, retrieved all three relevant services (`memoir_subjects`, `memoir_themes`, and `memoir_episodes`), and answered using 31 records across those services.

The result was positive for H4. The agent distinguished personal discipline, political or social freedom, confinement, exclusion, and institutional constraint across the represented memoir subjects without flattening them into generic similarity. It explicitly rejected the unsupported claim that Henry Adams and Booker T. Washington shared the same theory of education, while preserving the narrower thematic overlap that both memoirs discuss education outside formal institutions. It also handled the Kropotkin/Gandhi near-neighbor question carefully: both use inquiry language against authority, but Kropotkin's external scientific method and Gandhi's moral-autobiographical experiments are not the same method.

The retrieval path was broad rather than narrow, but that was defensible for a cross-subject discrimination prompt over a compact integrated corpus. The important evidence is that broad structured retrieval did not produce overconfident equivalence claims. The paired `closeout05` flat-memory run remains necessary to compare whether a curated single-file memory artifact creates more false-positive pressure under the same prompt.

**Paper notes:**
This run supports the claim that AIPCS can preserve enough structured prior cognition for a fresh agent to reason about absence, near-neighbor similarity, and source discrimination. The paper should use it as H4 evidence, but avoid overclaiming until the flat-memory H5 comparator is run.

**Addendum — H5 flat-memory discrimination/null probe:**
`closeout05` ran the same targeted discrimination/null prompt using only the flat `MEMORY.md` artifact. AIPCS, raw SQLite files, source files, prior artifacts, and outside knowledge were forbidden. Claude read one file, `workspace/memory/MEMORY.md`, and attributed the answer exclusively to that note.

The result was stronger than a simplistic AIPCS-favouring hypothesis would predict. The flat-memory condition handled the same two likely false positives well. It rejected the claim that Henry Adams and Booker T. Washington shared the same theory of education, while preserving a narrower overlap around inadequacy of conventional education. It also distinguished Kropotkin's external, shareable scientific inquiry from Gandhi's internal moral experiments, rather than claiming they expressed the same method.

This means H5 should be interpreted as a strong curated-artifact comparator, not evidence that flat memory necessarily blends adjacent facts. The caveat is that the `MEMORY.md` artifact was unusually favourable: it was deliberately generated from the source packet, analytically dense, already organized around cross-cutting themes, and substantial at 5,391 words / 33,149 bytes. It is closer to an upper-bound condensed dossier than to ordinary incidental memory accumulated across a long collaboration.

**Paper notes:**
The closeout H4/H5 pair narrows and strengthens the argument. AIPCS did not clearly outperform a carefully prepared single-file memory artifact on one-off answer quality for a compact narrative corpus. The paper should therefore avoid claiming categorical superiority over curated flat artifacts. The stronger claim is that AIPCS preserves agent-authored structure that remains queryable, inspectable, evolvable, and reusable as memory grows across sessions, agents, domains, and time.

**Addendum — H6 vanilla/model-knowledge reconstruction baseline:**
`closeout06` ran the broad comparative essay prompt with no supplied AIPCS memory, no source packet, and no flat memory note. Claude did not visibly call tools, read files, use AIPCS, or invoke web/research. The answer appears to have been generated directly from ordinary model knowledge.

The result was thematically strong. Claude produced a coherent typology of responses to authority and freedom across Gandhi, Kropotkin, Washington, the Crafts, and Adams. It handled all five subject groups and produced a rhetorically useful essay. This shows that the task domain itself is not beyond ordinary Claude capability, especially because the figures are historically prominent.

The limitation is bounded provenance. The answer drew on broader historical knowledge that was not constrained to the memoir corpus, including the Salt March, Quit India, Washington's covert legal funding, Kropotkin's World War One position, and later interpretive framing. Claude was transparent about this, explicitly avoiding exact quotations and noting that publication dates, precise quotations, and some secondary-source claims could not be verified in the session.

Mark's observation is the right interpretation: Claude can produce a strong thematic essay, but where it falls short is access to directly quoteable, bounded, corpus-specific remarks.

**Paper notes:**
H6 further narrows the claim. AIPCS is not necessary for a frontier model to produce plausible synthesis on well-known historical topics. Its value is preserving bounded situated cognition: what an earlier agent read, selected, interpreted, structured, and made reusable from a specific corpus or collaboration. Compared with vanilla model knowledge, AIPCS offers continuity, inspectable provenance, and controlled recall rather than generic model competence.
