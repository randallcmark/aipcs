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

**From BUILD_JOURNAL §1:**
> "The irony of manually journalling AIPCS's own development — without AIPCS — is noted and should appear in the paper introduction. It is a concrete illustration of the pattern's value."

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

**From BUILD_JOURNAL §2:**
> "Captured in invention disclosure. Refine during write-up."

---

## 3. The AIPCS Pattern

**Key points:**
- 10 core principles (P1–P10) from pattern spec — distil to paper length
- The lifecycle: Recognition → Design → Scaffolding → Registration → Operation → Evolution
- Three defining characteristics: agent as architect, structured queryable memory, MCP-native registration
- Tool taxonomy: workflow-oriented tools, not database-oriented (a design contribution in itself)
- Agent-managed schema evolution: the agent extends its own schema over time without developer intervention

**Source:** `docs/AIPCS_Pattern_Specification_v0.1.docx` — distil to ~2 pages

---

## 4. Reference Implementation

**Key points:**
- Application Tracker as the proving ground (career management for job seekers)
- Why this domain: multi-entity tracking (jobs, applications, stages, artefacts), relational dependencies, cross-session persistence — all strong AIPCS trigger conditions
- v1 architecture: Model A trigger, sidecar HTTP mechanism, dynamic MCP registration
- Schema design prompt: what the agent receives, what it must produce
- Tool taxonomy examples from the career domain
- OAuth/DCR implementation: consumer subscription as authentication
- Docker Compose structure: sidecar alongside main application
- Key implementation decisions (link to ADRs)

**From BUILD_JOURNAL §4:**
> "Record: architecture diagram, key technology choices and why, how the agent triggers instantiation, schema design examples (career domain), tool taxonomy examples, OAuth/DCR implementation notes, Docker Compose structure"

*Populate this section during the build (M005–M008)*

---

## 5. Evaluation

**Metrics to collect during build:**
- What workflows became possible that weren't before?
- Latency cost of agent schema design vs hand-designed schema
- Token cost of the schema design step
- Schema quality: human assessment, coverage of use cases
- Schema evolution: how did the agent handle adding fields in practice?
- Prompt patterns: which trigger phrasings worked best?
- Failure modes: what failed? What surprised?

**From BUILD_JOURNAL §5:**
> "Record: what workflows became possible, latency cost, token cost, schema evolution behaviour, prompt patterns, surprises and failures"

*Populate this section during the build (M007–M008)*

---

## 6. Discussion

**Seed questions (from BUILD_JOURNAL §6):**
- How general is the pattern really? Where does it break down?
- What are the security implications of agent-designed schemas? (schema as injection vector)
- Does AIPCS get better as models improve? (schema design quality is model-dependent)
- What would a mature AIPCS ecosystem look like? (service registry, schema sharing, multi-agent access)
- Open questions not resolved in v1: Q002 (schema versioning), Q003 (service registry), Q004 (multi-agent locking), Q005 (conflict resolution), Q006 (portability)

---

## 7. Conclusion

*Draft last — after all other sections are complete.*

---

## Appendix (if needed)

- Full schema design prompt
- Service manifest format
- Tool taxonomy conventions

---

*This outline grows with the build. Promote BUILD_JOURNAL running notes here when they are substantive. See [docs/agent/paper-rules.md](../docs/agent/paper-rules.md) for the journal–paper pipeline.*
