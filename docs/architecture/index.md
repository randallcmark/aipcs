# AIPCS Architecture

## Pattern Summary

AIPCS (Agent-Instantiated Persistent Context Services) is a pattern in which an AI agent, upon encountering a sufficiently complex stateful tracking problem:

1. **Recognises** the need for structured persistent memory (via user hint or compaction trigger)
2. **Seeds** a domain marker immediately — a first-class primitive, queryable before schema exists
3. **Designs** an appropriate data schema as domain knowledge accumulates
4. **Materialises** a live service (SQLite + FastAPI + MCP tools) around the validated schema
5. **Evolves** the schema additively as the agent's understanding grows

The agent is the schema architect — not a consumer of a pre-designed schema. Memory is structurally queryable, not just semantically searchable. The service is dynamically registered as MCP tools, composable and portable.

**Authoritative v1 design document:** [`docs/AIPCS_v1_Technical_Design.md`](../AIPCS_v1_Technical_Design.md)

---

## Two-State Service Lifecycle

Every AIPCS domain service exists in one of two states:

```
SEEDED       — marker planted, schema forming, not yet deployed
MATERIALISED — schema deployed, tools active, queryable
```

A seed is a first-class object. It is immediately queryable (`aipcs_service_list`, `aipcs_service_inspect`). The agent can resume domain modelling across sessions by inspecting seeds. This gives the system visibility into persistence intent before the schema is ready.

---

## Bootstrap Model

Bootstrap is not only a server response. It has three layers:

| Layer | Purpose |
|---|---|
| Static agent instruction | Teaches the agent that AIPCS exists, when to seed, when to persist, and how to use the primitive tools |
| Dynamic discovery map | Gives a lightweight data-dictionary view of current services, domain classes, entity names, descriptions, counts, and recent activity |
| Procedural skills (deferred) | Captures multi-step workflows that are better expressed as agent procedure than atomic tools |

The dynamic map should be descriptive enough that the agent can decide where to probe next and whether new information fits the current schema. It should not return record content by default.

Common top-level domain classes are reference guidance, not a closed taxonomy in v1. They support interoperability and discovery while preserving the agent's ability to propose new categories.

---

## v1 Design Decisions

Three questions define the v1 architecture. All resolved.

### Trigger (Q001 — partially resolved)

**v1: Model A — explicit user hint**  
The user hint is a *hint*, not a complete specification. The agent acts immediately by seeding the domain, then accumulates knowledge across interactions before designing the schema.

**Model B — proactive agent recognition (designed for, skill in v1)**  
Two concrete triggers:
- The agent identifies multi-entity tracking needs with cross-session persistence
- **Compaction hook**: before compacting context, the agent evaluates all active knowledge domains for AIPCS persistence candidacy. Captures structured knowledge before compression degrades it. (D006)

The AIPCS skill definition documents both triggers. Full proactive recognition beyond these two cases is future work.

### Mechanism (Q001 — resolved: D007)

**Option 3 — AIPCS as MCP-native primitive server**

AIPCS is itself an MCP server. All management operations are MCP tool calls. Self-referential: MCP tools that create MCP tools. No CLI, no sidecar HTTP management API.

Impediments resolved during design (Entry 004):

| Impediment | Resolution |
|---|---|
| Dynamic tool registration not universal in MCP clients | Session reconnect acceptable for v1 |
| Agent must know AIPCS exists | Always-on in the Docker Compose stack |
| Schema quality depends on model capability | AIPCS validation layer — agent proposes, system validates, agent revises |
| No domain tools before first seed | AIPCS skill: first action is always `aipcs_service_seed` |

Options rejected: Option 1 (pure prompt — too weak), Option 2 (CLI — friction), Option 4 (sidecar HTTP — environment-dependent, complexity).

### Registration (resolved)

**Dynamic MCP tool discovery** — new domain services register their tools dynamically. Session reconnect acceptable for v1 clients that don't support live discovery.

---

## Management Tool Primitives

The AIPCS Server exposes 8 management tools available from the moment AIPCS is connected:

| Tool | Purpose |
|---|---|
| `aipcs_service_seed` | Plant a domain marker — always the first action |
| `aipcs_service_design` | Submit a schema design for a seeded domain (validated before acceptance) |
| `aipcs_service_materialise` | Deploy a validated schema as a live service with MCP tools |
| `aipcs_service_evolve` | Propose and apply a schema migration (additive or destructive with confirmation) |
| `aipcs_service_list` | Discover all seeded and materialised services |
| `aipcs_service_inspect` | Get full schema manifest and migration history for a service |
| `aipcs_service_suspend` | Pause a service without deleting data |
| `aipcs_service_export` | Export schema and data (consent-gated portability primitive) |

---

## Subsystems

| Subsystem | Purpose | Owner doc |
|---|---|---|
| AIPCS Server | MCP-native server exposing all 8 management primitives | [decisions/](decisions/) |
| Registry DB | Internal SQLite tracking services, seeds, manifests, migrations, audit log | Technical design §Architecture |
| Schema Validator | Validates agent-submitted schemas before materialisation | Technical design §Schema Design Requirements |
| Schema Designer (skill) | Prompt/skill teaching the agent to recognise triggers and use AIPCS correctly | [../agent/ai-feature-rules.md](../agent/ai-feature-rules.md) |
| Domain Services | Dynamically created per-domain SQLite + FastAPI + MCP tools | Technical design §Service Lifecycle |
| Reference Implementation | Application Tracker — the proving ground | `randallcmark/application_tracker` |

---

## Architecture Routes

- Full v1 design → [`docs/AIPCS_v1_Technical_Design.md`](../AIPCS_v1_Technical_Design.md)
- Boundary definitions → [boundaries.md](boundaries.md)
- Formal decisions (ADRs) → [decisions/](decisions/)
- Pattern principles (P1–P10) → `docs/AIPCS_Pattern_Specification_v0.1.docx`
- Open design questions → [../quality/technical-debt.md](../quality/technical-debt.md)

## Change Rules

- No change to trigger/mechanism/registration decisions without a BUILD_JOURNAL entry and an ADR
- No new dependency without checking [boundaries.md](boundaries.md)
- Agent-generated outputs (schemas, API code) are always treated as untrusted input — validate before executing
