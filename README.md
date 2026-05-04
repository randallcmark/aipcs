# Agent-Instantiated Persistent Context Services (AIPCS)

**A pattern for autonomous, domain-adaptive memory infrastructure via MCP**

> *Conceived and authored by Randall Mark — May 2026*
> *Pre-publication claim of invention. See [licence](#licence) below.*

---

## What is AIPCS?

AI agents are stateless. Every session begins from zero. For simple tasks this is fine. For complex, evolving, multi-entity domains — job searching, medical management, project tracking, legal case management — it is a critical limitation.

Existing solutions ask developers to pre-define memory schemas. The agent populates them, but has no say in their structure. This works for fixed product features. It does not work as a general-purpose agent capability.

**AIPCS is the pattern by which an AI agent, upon recognising a complex stateful tracking need, autonomously:**

1. Designs a domain-appropriate relational schema
2. Scaffolds a persistent, queryable service around that schema
3. Registers that service as an MCP tool
4. Manages the evolution of that service as its understanding of the domain deepens

The result is memory infrastructure that is **structured and queryable** (not just semantically searchable), **domain-specific** (not generic), **agent-designed** (not developer-designed), **session-persistent** (survives between conversations), and **client-agnostic** (accessible by any MCP-compatible AI).

---

## The Key Insight

Most agent memory systems invert the right relationship. The developer designs the structure; the agent fills it in.

AIPCS inverts this: **the agent is the architect of its own memory**. The developer provides the scaffolding capability — the ability to instantiate a schema, wrap it in a service, and register it as an MCP tool. The agent decides what structure that memory should have, based on the domain it is helping with.

This makes AIPCS a **universal primitive** rather than a fixed application schema. Job tracking today. Medical history tomorrow. Research notes next week. The agent selects the appropriate structure at instantiation time.

---

## The Consumer Access Problem

AI-assisted features in productivity tools are typically locked behind developer API subscriptions — a separate paid tier on top of any consumer AI subscription a user already holds. For users who already pay for Claude or ChatGPT, this is unnecessary duplication. For lower-income users who need AI assistance most, it is a real barrier.

AIPCS incorporates **OAuth 2.0 with Dynamic Client Registration (DCR)** as a design constraint. Users connect their existing consumer AI client to a self-hosted AIPCS instance using a standards-based registration and consent flow — no separate API key required. This is not incidental to the pattern; it is part of the invention.

---

## Core Principles

| # | Principle | Summary |
|---|-----------|---------|
| P1 | Agent as architect | The agent designs the schema. Not the developer. |
| P2 | Structured over semantic | Relational schemas for precise queries, not just vector recall. |
| P3 | Service over store | Memory is wrapped in an API layer, not accessed as a raw database. |
| P4 | MCP as interface | Services exposed as MCP tools — composable and portable. |
| P5 | Workflow-oriented tools | Tools follow `domain_object_action`, not `get_record` / `update_field`. |
| P6 | Separation of concerns | Read ≠ write. Generation ≠ persistence. Agent reasons; service stores. |
| P7 | Consumer accessibility | OAuth 2.0 + DCR. No separate developer API key required. |
| P8 | Privacy-first deployment | Self-hosted, local-first. User data stays under user control. |
| P9 | Provenance and auditability | All agent-created outputs record full provenance. |
| P10 | MCP off by default | No ambient exposure. Must be explicitly enabled. |

---

## Pattern Lifecycle

```
Recognition  →  the agent identifies a complex stateful tracking need
     ↓
Design       →  the agent analyses the domain and designs a relational schema
     ↓
Scaffolding  →  database init script + API service layer + Docker config
     ↓
Registration →  service registered as MCP tool(s) with workflow-oriented names
     ↓
Operation    →  persistent across sessions, accessible by any MCP-compatible client
     ↓
Evolution    →  agent extends schema as domain understanding deepens
```

---

## Relation to Prior Art

AIPCS was developed following a review of related work. The following are acknowledged as related but distinct:

- **MemFabric** — LLM-managed self-organising markdown files. Related in spirit but produces flat files, not structured queryable schemas, and does not scaffold MCP-registered services.
- **PISA** — Piaget-inspired adaptive memory schema architecture. The closest academic antecedent, but an academic architecture rather than a deployable MCP-integrated service pattern.
- **Nemori** — Self-organising Memory-Augmented Generation. Addresses retrieval from conversational memory, not schema design or service scaffolding.
- **MemGPT / Letta** — OS-inspired memory paging. The external store schema is developer-defined, not agent-designed.
- **mcp-memory-service / Hindsight** — MCP-connected persistent memory backends with pre-defined developer schemas.
- **SchemaAgent** — LLM multi-agent framework for database schema generation from requirements. Generates schemas for existing data problems, not as a universal memory primitive with MCP integration and consumer DCR access.

No reviewed prior art combines agent-designed schemas, on-demand service scaffolding, MCP tool registration, workflow-oriented tool taxonomy, DCR-based consumer AI access, and domain-agnostic instantiation into a unified deployable pattern.

---

## Origin

AIPCS emerged from the development of [Application Tracker](https://github.com/randallcmark/application_tracker) — a self-hosted, Docker-deployable career management platform for job seekers. While designing the MCP integration for that application, and specifically while solving the API access friction problem for lower-income job seekers, the author recognised a generalised pattern that extends well beyond career management.

The career application is the first proving ground for AIPCS. The pattern is designed to be extracted from it and published as a general-purpose contribution.

The author also holds prior personal work: an earlier agent memory layer that was explicitly designed and defined by the developer rather than by the agent. That experience directly motivated this invention, which inverts that relationship.

---

## Documents

| Document | Description |
|----------|-------------|
| [`docs/AIPCS_Invention_Disclosure_v2.pdf`](docs/AIPCS_Invention_Disclosure_v2.pdf) | Timestamped invention disclosure establishing authorship and novelty claims |
| [`docs/AIPCS_Pattern_Specification_v0.1.docx`](docs/AIPCS_Pattern_Specification_v0.1.docx) | Implementation-agnostic pattern specification (v0.1 working draft) |

---

## Status and Roadmap

- [x] Invention disclosure — timestamped and documented
- [x] Pattern specification v0.1 — working draft
- [ ] Reference implementation — in progress within Application Tracker
- [ ] Pattern extraction — generalised framework extracted from reference implementation
- [ ] arXiv preprint — technical paper establishing public prior art
- [ ] Open-source release — reference implementation under attribution-friendly licence

---

## Licence

**Documents** (`docs/`): [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
You are free to share and adapt with attribution.

**Code** (when published): MIT Licence

The author does not seek to commercially restrict this invention. The intent is open attribution and contribution to the research and practitioner community.

---

## Author

**Randall Mark**
Conceived: May 2026
GitHub: [@randallcmark](https://github.com/randallcmark)

---

*This repository is a pre-publication claim of invention. The documents herein establish the author's conception of the AIPCS pattern prior to academic publication. All rights are reserved by the author pending that publication.*
