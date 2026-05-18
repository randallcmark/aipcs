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
- The inversion: AIPCS flips the model — agent as architect, not consumer of pre-designed schema
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
| memhub (kninetimmy, 2026) | Local per-repo coding memory with SQLite, MCP, predefined facts/decisions/tasks/docs, staged writes, and FTS/hybrid recall | Strong fixed-domain pipeline baseline; classifier/index/retrieval architecture is developer-defined, not agent-instantiated domain services |
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

**Compaction hook as Model B trigger (from Entry 003 / D006):**
- Novel contribution: no prior art explicitly connects context compaction with structured memory instantiation
- Before compacting context, the agent evaluates all active knowledge domains for AIPCS persistence candidacy
- Key insight: persistence at compaction time should be closer to the source than a compressed summary — structured data does not degrade the way summaries do
- Worth a dedicated paragraph

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

Current implementation evidence to promote:
- Standalone `aipcs-server` repo now proves local MCP `stdio` operation with seed/list/bootstrap/inspect/design/materialise and generic record create/list/get/search/update/delete/history.
- `aipcs_bootstrap` is a lightweight data-dictionary map, not a content dump.
- Exact structured `aipcs_record_search` is intentionally narrow to preserve schema-quality pressure.
- Retrieval `_meta` computes updated-age dynamically and echoes provenance convention fields when records carry them.
- First portable static instruction artifact exists at `docs/agent/examples/aipcs-persistent-memory-instruction.md`.

---

## 5. Evaluation

**Metrics to collect during build:**
- What workflows became possible that weren't before?
- Latency cost of agent schema design vs a hand-designed schema
- Token cost of the schema design step
- **Seed-to-materialisation speed**: how quickly do seeds materialise in practice? Average number of interactions before materialisation (from Entry 002)
- **Schema evolution frequency**: how many evolutions occur during a typical domain tracking lifecycle? (from Entry 005)
- Schema quality: human assessment, coverage of domain use cases
- Which trigger phrasings worked best for Model A recognition?
- How did the compaction hook perform in practice — did it surface domains that would otherwise have been lost?
- What failed or surprised you?

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
- Does AIPCS improve as models improve? Schema design quality is model-dependent.
- What would a mature AIPCS ecosystem look like — shared taxonomy, cross-deployment portability, multi-agent coordination?

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
