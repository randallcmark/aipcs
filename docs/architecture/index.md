# AIPCS Architecture

## Pattern Summary

AIPCS (Agent-Instantiated Persistent Context Services) is a pattern in which an AI agent, upon encountering a sufficiently complex stateful tracking problem:

1. **Recognises** the need for structured persistent memory (via user hint or compaction trigger)
2. **Seeds** a domain marker immediately — a first-class primitive, queryable before schema exists
3. **Designs** an appropriate data schema as domain knowledge accumulates
4. **Materialises** a persistent queryable service around the validated schema
5. **Evolves** the schema additively as the agent's understanding grows

The agent is the schema architect — not a consumer of a pre-designed schema. Memory is structurally queryable, not just semantically searchable. The current reference implementation proves the pattern through stable primitive MCP tools plus generic record operations. Dynamically generated domain-specific tools remain an optional interface layer, not the conceptual minimum.

**Historical v1 working design:** [`docs/AIPCS_v1_Technical_Design.md`](../AIPCS_v1_Technical_Design.md)

**Authoritative public-v1 implementation contract:** [public-v1-contract.md](public-v1-contract.md)

The historical design establishes the pattern and research archaeology. The public-v1 contract
reconciles it with dogfooded primitive-server evidence without changing the agent-authored-schema
core of AIPCS.

---

## Public-v1 Interface and Lifecycle Boundary

Stable generic AIPCS MCP tools are the public interface. The server owns tool definitions and MCP
contracts; the agent-authored schema owns entities, attributes, relationships, indices, and retrieval
guidance. Generated domain tools, per-domain FastAPI processes, `tool_definitions`, aliases,
registry classification confidence, `session_count`, and dedicated merge/split are retired from
public-v1 semantics. Parent-service composition is deferred pending a concrete independent-service
case. Public v1 is local `stdio`; remote MCP/auth/hosting remain separate future work.

A service has two independent axes:

```text
design_state:       seeded | materialised
operational_status: active | suspended | archived
```

No seed is automatically abandoned by age. Maintenance may identify a dormant candidate, but
archive and purge are explicit owner/admin actions.

Relational foreign keys use portable immediate `ON DELETE RESTRICT` and `ON UPDATE RESTRICT`.
Required cycles are rejected and nullable cycles are staged through null relationship values; see
[ADR-001](decisions/ADR-001-immediate-restrict.md).

SQLite local-v1 storage uses a versioned, crash-resumable WAL policy with secured operational
sidecars, numeric busy classification, bounded per-lock waiting, one-snapshot inspection, and
PASSIVE migration checkpoints. It requires SQLite 3.51.3 or newer on one same-host local POSIX
filesystem; see [ADR-002](decisions/ADR-002-sqlite-wal-contention-policy.md).

## Historical Two-State Service Lifecycle

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

After the bootstrap scalability runs (`run018`-`run021`), the dynamic discovery map has a stronger constraint: it must be a compact recursive map, not a full schema dictionary. Bootstrap should expose service intent, state, entity names, counts, recent activity, and deterministic affordance labels. Full attribute descriptions, allowed values, migration history, and rich schema detail belong behind explicit inspection tools.

Seeded services remain first-class in discovery even before schema design. A seed is an intentional memory branch, so bootstrap should show the branch, its intent, its schema/materialisation state, and whether the next useful action is schema design.

Optional record samples are not part of default bootstrap. Sampling belongs in a deeper service-summary or record-retrieval step so the agent chooses when to spend context.

Facets should be agent-declared and server-counted. The agent decides which schema fields help discovery; the server may mechanically aggregate counts over those declared fields, but should not infer semantic facets from prose.

Bootstrap affordances should orient the next retrieval step, not merely name available tools. For populated services with declared facets or retrieval guidance, the preferred path is recursive: bootstrap shows that a service summary is available; service summary exposes exact-match facets, facet counts, and filterability-aware guidance; record calls retrieve content. Guidance must not advertise comma-separated annotation fields or free-text fields as if they were exact-match query facets.

AIPCS retrieval should distinguish exact scalar filters from structured membership filters. Scalar fields such as status, entry type, salience, or primary topic remain exact-match retrieval keys. Multi-value fields such as tags should only be advertised as filterable when the schema declares them as structured membership fields; comma-separated prose tags are annotations, not reliable query surfaces. Broad substring, fuzzy, and semantic search remain deferred because the pattern should continue to reward thoughtful persistence structure.

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

AIPCS is itself an MCP server. All management and record operations are MCP tool calls. Self-referential in the current evidence means MCP tools that create, operate, and evolve persistent context services; generated domain-specific MCP tools are a later UX layer. No CLI, no sidecar HTTP management API is required for the first proof.

Impediments resolved during design (Entry 004):

| Impediment | Resolution |
|---|---|
| Dynamic tool registration not universal in MCP clients | Generated domain-specific tools are optional for the first proof; stable primitive tools avoid reconnect friction |
| Agent must know AIPCS exists | Always-on in the Docker Compose stack |
| Schema quality depends on model capability | AIPCS validation layer — agent proposes, system validates, agent revises |
| No domain tools before first seed | AIPCS skill: first action is always `aipcs_service_seed` |

Options rejected: Option 1 (pure prompt — too weak), Option 2 (CLI — friction), Option 4 (sidecar HTTP — environment-dependent, complexity).

### Registration (reframed by D026)

**Stable primitive MCP tools first** — the server exposes primitive tools for service lifecycle, bootstrap/discovery, generic records, and schema evolution. These are sufficient to evaluate agent-owned schema design and memory evolution.

**Dynamic MCP tool discovery** remains a future optional interface layer. Generated domain-specific tools may improve ergonomics, but Claude/Codex restart/reconnect requirements make them a productisation concern rather than the core research mechanism.

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
| Domain Services | Per-domain persisted SQLite stores operated through primitive/generic MCP tools; generated FastAPI/domain tools deferred | Technical design §Service Lifecycle |
| Reference Implementation | Standalone `aipcs-server`; Application Tracker remains the motivating origin | `/Users/markrandall/GitHub/aipcs-server` |

---

## Architecture Routes

- Full v1 design → [`docs/AIPCS_v1_Technical_Design.md`](../AIPCS_v1_Technical_Design.md)
- Architecture diagrams → [diagrams.md](diagrams.md)
- Boundary definitions → [boundaries.md](boundaries.md)
- Formal decisions (ADRs) → [decisions/](decisions/)
- Pattern principles (P1–P10) → `docs/AIPCS_Pattern_Specification_v0.1.docx`
- Open design questions → [../quality/technical-debt.md](../quality/technical-debt.md)

## Change Rules

- No change to trigger/mechanism/registration decisions without a BUILD_JOURNAL entry and, when it becomes durable architecture policy, an ADR
- No new dependency without checking [boundaries.md](boundaries.md)
- Agent-generated outputs (schemas, API code) are always treated as untrusted input — validate before executing
