# AIPCS Paper Outline

**Working title:** Agent-Instantiated Persistent Context Services: A Pattern for Autonomous Domain-Adaptive Memory via MCP

**Author:** Randall Mark
**Target venue:** arXiv preprint (→ optionally HotOS / SOSP / AI systems workshop)
**Target length:** 6–10 pages (systems paper style)
**Status:** Outline — sections seeded from BUILD_JOURNAL running notes

**Detailed drafting wireframe:** [wireframe.md](wireframe.md)

---

## Abstract

*Draft when all other sections are complete.*

AIPCS is a pattern for autonomous, domain-adaptive memory infrastructure in which an AI agent defines and evolves its own persistent memory architecture through a small set of primitive tools. Unlike prior work — which either pre-defines memory schemas, provides generic semantic stores, or organises existing data — AIPCS makes the agent responsible for deciding the object model, schema, persistence boundaries, and later schema adaptation. We present the pattern, a local MCP-native reference implementation, and early evaluation evidence showing bootstrap, retrieval, stale-memory repair, schema self-audit, and schema-rationale recall.

Core framing: AIPCS addresses the context economy of long-running agent work. The scarce resource is not only persistence across sessions, but the agent's ability to retrieve precise, structured context without repeatedly re-reading prose summaries or semantic recall blobs.

---

## 1. Introduction

**Key points:**
- Context economy: long sessions degrade when relevant context is compacted away, over-reinserted, ignored, or retrieved as prose the agent must re-read
- Statelessness is a visible symptom, but the stronger systems problem is efficient use of scarce context window
- Existing markdown side files and semantic recall stores often act as copy/paste transport into context; AIPCS aims for targeted structured recall
- The inversion: AIPCS flips the model — the agent is upstream of memory architecture, not only downstream of a developer-defined schema
- Consumer access equity: the pattern emerged from solving API key friction for job seekers (OAuth 2.0 + DCR as a design constraint, not an afterthought)
- The AIPCS irony: we built AIPCS without AIPCS — manually managing context that the pattern would structure automatically. This is the pattern's clearest illustration of its own value.
- Paper structure overview

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
| agent-memory-v2 | Owned prior-generation memory layer: developer-defined taxonomy, extraction/classification pipeline, semantic/vector recall safety net, profile injection | Good fixed-schema/pipeline comparator; LLM is downstream of memory architecture rather than architect of it |
| memhub (kninetimmy, 2026) | Local per-repo coding memory with SQLite, MCP, predefined facts/decisions/tasks/docs, staged writes, and FTS/hybrid recall | Strong fixed-domain pipeline baseline; classifier/index/retrieval architecture is developer-defined, not agent-instantiated domain services |
| mcp-memory-service | Knowledge graph via MCP | Fixed developer-defined schema |
| Hindsight (Vectorize, 2026) | Semantic memory retrieval via MCP | Semantic search; developer-defined structure |
| SchemaAgent (2025) | LLM-driven schema generation for existing data | Schema generation for existing problems, not persistent memory primitive |
| Graph/vector database memory systems | Rich storage/retrieval substrates over facts, relationships, or embeddings | Storage substrate differs, but the core architecture is still usually externally chosen; AIPCS asks who decides and evolves the memory architecture |

**Standards to cite:**
- MCP specification (Anthropic, 2024)
- RFC 7591 — OAuth 2.0 Dynamic Client Registration

---

## 3. The AIPCS Pattern

**Key points:**
- 10 core principles (P1–P10) from pattern spec — distil to paper length
- The full lifecycle: Recognition → Seed → Design → Materialise → Operate → Evolve
- The architectural inversion: developer-defined systems place the LLM downstream of memory architecture; AIPCS places the LLM upstream of memory architecture

**Two-state lifecycle (from Entry 002 / D004, D005):**
- SEEDED: domain marker planted, schema forming, not yet deployed. First-class primitive — queryable immediately. Agent resumes domain modelling across sessions via seed inspection.
- MATERIALISED: schema deployed, tools active, queryable. Progression from hint → seed → accumulated knowledge → schema design → materialisation.
- The seed is not a placeholder — it is the pattern's earliest observable state of persistence intent.

**Compaction hook as Model B trigger (from Entry 003 / D006):**
- Novel contribution: no prior art explicitly connects context compaction with structured memory instantiation
- Before compacting context, the agent evaluates all active knowledge domains for AIPCS persistence candidacy
- Key insight: persistence at compaction time should be closer to the source than a compressed summary — structured data does not degrade the way summaries do
- Worth a dedicated paragraph

**Self-referential MCP-native mechanism (from Entry 004 / D007):**
- Option 3: AIPCS is an MCP server. Primitive MCP tools create, materialise, operate, and evolve persistent context services.
- Architecturally distinctive — worth emphasising
- Options rejected: Option 1 (too weak), Option 2 (CLI friction), Option 4 (sidecar HTTP — environment-dependent)
- Later dynamic domain-specific tool generation is an optional interface layer, not the conceptual minimum. Current evidence suggests the stable primitive tool surface is sufficient to test the research hypothesis.

**Schema evolution as agent act (from Entry 005 / D008):**
- Additive migrations by default; destructive require explicit confirmation
- Agent proposes, AIPCS validates and applies
- Schema manifest travels with the service — versioned, human-readable JSON
- Every migration recorded in history — the schema's audit trail

**Tool taxonomy:**
- Stable primitive tools first; generated domain-specific tools later only if they improve usability without undermining portability
- Workflow-oriented tools, not database-oriented
- Naming convention: `domain_object_action` (e.g. `job_application_status_update` not `job_application_update`)
- Tool names maximum 60 characters; descriptions maximum 250

---

## 4. Reference Implementation

**Key points:**
- Standalone `aipcs-server` as the current proving ground for the pattern mechanics.
- Application Tracker and career management remain the motivating origin, but product integration is not required for the core research proof.
- The reference implementation is intentionally local-first so memory architecture, schema evolution, and retrieval behavior can be studied without hosting/auth/productisation confounds.

**Architecture (from technical design):**
- AIPCS Server (MCP-native) + Registry DB + Domain Services
- Primitive surface: seed/list/bootstrap/inspect/design/materialise/evolve plus generic record create/list/get/search/update/delete/history
- 8 original management primitives remain the broader design target; suspend/export are deferred
- Three-tier access: Tier 1 (agent MCP tools), Tier 2 (user via agent), Tier 3 (consent-gated read-only export)
- Docker/homelab/public MCP are productisation and deployment paths, not minimum evidence for the paper

**Impediments and resolutions (from Entry 004 — valuable "lessons learned" material):**

| Impediment | Resolution |
|---|---|
| Dynamic tool registration not universal | Session reconnect acceptable for v1 |
| Agent must know AIPCS exists | Always-on in the stack |
| Schema quality model-dependent | Validation layer — propose, validate, revise cycle |
| No domain tools before first seed | Skill: first action is always seed |
| Dynamic generated tools require client restart | Treat generated domain tools as optional UX; prove the concept through stable primitive tools first |

**Schema manifest format:**
- Versioned JSON, travels with the service
- Includes: entities, relationships, indices, migration history, tool definitions, domain_class
- Full example in `docs/AIPCS_v1_Technical_Design.md`

**Authentication:**
- V1: local trust within Docker network; owner_id from application session
- V2 target: OAuth 2.0 + DCR per pattern specification and Application Tracker's MCP_OAUTH_DCR_PLAN.md

*Populate with implementation detail as build progresses (M005–M008)*

Current implementation evidence to promote:
- Standalone `aipcs-server` repo now proves local MCP `stdio` operation with seed/list/bootstrap/inspect/design/materialise/evolve and generic record create/list/get/search/update/delete/history.
- `aipcs_bootstrap` is a lightweight data-dictionary map, not a content dump; Bootstrap V2 adds schema summaries, attribute metadata, retrieval hints, and non-binding domain-class guidance.
- Exact structured `aipcs_record_search` is intentionally narrow to preserve schema-quality pressure.
- Retrieval `_meta` computes updated-age dynamically and echoes provenance convention fields when records carry them.
- `aipcs_service_evolve` implements additive schema evolution with version increments, migration history, safe SQLite DDL, and existing-record preservation.
- Live Claude trace showed Bootstrap V2 driving cold-start orientation, bounded retrieval, stale-memory detection, and autonomous memory repair.
- First portable static instruction artifact exists at `docs/agent/examples/aipcs-persistent-memory-instruction.md`.

---

## 5. Evaluation

**Metrics to collect during build:**
- What workflows became possible that weren't before?
- Latency cost of agent schema design vs a hand-designed schema
- Token cost of the schema design step
- **Context efficiency:** tokens spent to persist, retrieve, maintain, and use each relevant fact across a scenario or longer session; this should capture whether structured query and agent-authored schema beat repeated prose re-insertion over time
- **Cost/value accounting:** distinguish expensive corpus-construction or schema-synthesis sessions from ordinary recall/use sessions. AIPCS can justify higher token/tool overhead only when it improves recall precision, false-positive resistance, stale/conflicting memory handling, or reduces user re-explanation.
- **Probe spectrum:** evaluate direct, inferential, nuanced/contextual, tangential/referential, and null/false-positive probes rather than only direct factual recall
- **Seed-to-materialisation speed**: how quickly do seeds materialise in practice? Average number of interactions before materialisation (from Entry 002)
- **Schema evolution frequency**: how many evolutions occur during a typical domain tracking lifecycle? (from Entry 005)
- **Stale-memory repair**: can an agent compare recalled records against current tool/schema state, identify stale facts, and correct them through AIPCS tools? (from Entry 033)
- **Schema self-audit**: can an agent inspect its own memory structure, identify prose blobs, duplicate authorities, missing lifecycle fields, and ambiguous references, then repair them through AIPCS tools? (from Entry 034)
- **Schema-rationale recall**: can an agent explain why a schema changed by combining manifest migration history with retrieved session records, without relying on static instruction files? (from Entry 035)
- **Prose leakage**: do broad open-text fields cause agents to persist readable explanations instead of retrievable facts, and do constrained fields reduce blob formation? (from Entry 036)
- **Software process memory:** git records outcomes, but AIPCS can record implementation rationale, rejected approaches, discoveries, constraints, limitations, and retrieval-useful summaries while the agent is present during the work.
- **Deterministic Agent-Led Evaluation V1**: `aipcs-server/scripts/eval-v1.py` now seeds representative services and checks bootstrap, bounded retrieval, persisted-fact recall, stale-memory repair, schema self-audit, schema-rationale recall, and direct-SQLite guardrail behavior. Live-agent scoring remains the next layer. (Entry 037)
- Schema quality: human assessment, coverage of domain use cases
- Which trigger phrasings worked best for Model A recognition?
- How did the compaction hook perform in practice — did it surface domains that would otherwise have been lost?
- What failed or surprised you?
- **Minimum research package**: local reference implementation, deterministic mechanics runner, live-agent traces, fixed-schema comparison, and clear limitations. Homelab, OAuth/DCR, public MCP, generated domain tools, and hardening are future/productisation work unless directly needed for the evaluation.

**Comparator methodology (from Entry 046):**
- Use `agent-memory-v2` as the owned fixed-schema/pipeline comparator.
- Evaluate `agent-memory-v2` in its native position as an inline interaction runner, not as an MCP tool/server. The flow is user input → v2 pre-processing/retrieval/injection → Claude invocation → v2 post-response extraction/persistence.
- Run `v2-hybrid` as the strong practical baseline: semantic router + structured extractor + taxonomy.
- Run `v2-schema-only` as the cleaner fixed-schema lower bound: taxonomy path without semantic/vector safety net where feasible.
- Hold scenario inputs and output artifacts comparable across systems; do not normalise internals because LLM upstream vs downstream is the independent variable.
- Capture comparator artifacts: raw prompt, retrieval input, selected/injected memories, similarity scores where available, augmented prompt, model response, post-response extraction/classification outputs, persisted-memory diffs, and injected context volume.
- Treat "not runnable on this architecture" as a legitimate result for scenarios that require agent-owned schema creation or evolution.
- Hold the LLM/harness family as close as possible, record date, model label, tool surface, transcript, and artifact pointers.
- Frame the architectural contrast as structure-at-retrieval (`agent-memory-v2`) versus structure-at-persistence (AIPCS).
- Separate persistence-quality experiments from recall-quality experiments so persistence failures are not confused with retrieval failures.

*Populate during build (M007–M008)*

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

**Broader questions:**
- How general is the pattern? Where does it break down?
- Security: schema as injection vector — how does the validation layer hold up in practice?
- Persisted memory can itself become a shadow instruction channel if recalled behavior-shaping records are allowed to compete with the static harness; this is a productisation/security risk, not the core novelty claim
- Does AIPCS improve as models improve? Schema design quality is model-dependent.
- Do larger volumes of persisted data create enough retrieval pressure for agents to improve schemas, or do agents fall back to broad listing/prose summaries unless prompted to self-audit?
- How should results be reported under opaque and changing hosted-agent harnesses? Record date/model label/tool surface/transcript and keep deterministic mechanics separate from live-agent behavior.
- Are richer stores such as graph databases useful later as substrates, or do they distract from the central question of agent-owned architecture?
- Runner asymmetry is not a confound to remove when the claim is about LLM positioning relative to memory architecture; it should be named and bounded as the independent variable.
- How should services avoid duplicate authority when one memory domain wants a convenience summary of facts owned by another domain?
- How should durable rationale be distributed across static instructions, bootstrap, migration history, session records, and behavioral memory?
- How much of memory quality is shaped by the agent harness's prose-writing defaults rather than by the storage system alone?
- How much bootstrap/discovery should be enforced by hooks or static instructions without weakening the claim that persistence architecture remains agent-owned?
- Under what information-environment conditions does agent-directed retrieval become reliable without coercion?
- How does AIPCS complement git for software development by preserving process knowledge and retrieval-useful summaries without becoming a second changelog?
- What would a mature AIPCS ecosystem look like — shared taxonomy, cross-deployment portability, multi-agent coordination?

---

## 7. Conclusion

*Draft last — after all other sections are complete.*

Bounded future horizon:
- AIPCS points toward portable, model-agnostic user memory that can move across clients and devices, but this paper only claims the local pattern and early evidence for agent-owned memory architecture.

---

## Appendix (if needed)

- Full schema design prompt (skill definition)
- Schema manifest format (reference)
- Tool taxonomy conventions
- Management tool primitive schemas

---

*This outline grows with the build. Promote BUILD_JOURNAL running notes here when they are substantive. See [docs/agent/paper-rules.md](../docs/agent/paper-rules.md) for the journal–paper pipeline.*
