# AIPCS v1 Technical Design

**Version:** 0.1 — Working Draft
**Author:** Randall Mark
**Date:** 2026-05-04
**Status:** Design — pre-implementation

---

> **2026-05-19 implementation note:** The first local reference implementation has
> proven the core loop with stable primitive MCP tools and generic record operations.
> Dynamic generated domain-specific tools and FastAPI service generation remain useful
> future interface/productisation layers, but they are not required for the first
> research proof.

> **2026-07-21 public-v1 synchronisation note:** This document remains the historical
> pre-implementation working design. The public-v1 primitive-server contract is
> `docs/architecture/public-v1-contract.md`. It retains agent-authored schema and
> additive evolution as the pattern core, while making generic tools the public
> interface and adding explicit relational, lifecycle, portability, recovery, and
> administration boundaries. Generated tools, FastAPI services, public remote MCP,
> OAuth/DCR, hosted tenancy, and zero-knowledge storage are not public-v1 requirements.

---

## Purpose

This document defines the v1 technical architecture for the AIPCS reference implementation. It translates the pattern specification into concrete design decisions ready for implementation within Application Tracker.

It is the working design document — decisions recorded here should be reflected in the build journal and will feed into the arXiv paper's implementation section.

---

## Scope of v1

V1 establishes the core AIPCS runtime: the MCP-native primitive server, the two-state service lifecycle, the schema design and materialisation flow, and the schema evolution model.

This historical v1 design explicitly deferred Tier 3 elevated access,
multi-agent locking, the domain taxonomy registry, and CLI tooling. The later
public-v1 contract resolves local same-host, same-effective-user SQLite
coordination: WAL permits concurrent readers and SQLite serialises one writer.
Hosted, cross-user, and multi-host coordination remain deferred.

V1 must be sufficient to:
- Receive a user hint and plant a tool seed
- Design a schema from accumulated domain knowledge
- Materialise a persistent queryable service
- Operate records through stable primitive/generic MCP tools
- Evolve the schema additively
- Support user-mediated Tier 2 access

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Client                           │
│         (Claude, ChatGPT, or any MCP-compatible)        │
└──────────────────────────┬──────────────────────────────┘
                           │ MCP protocol
           ┌───────────────┴───────────────┐
           │                               │
┌──────────▼──────────┐       ┌────────────▼────────────┐
│   AIPCS Server      │       │  Domain Service(s)      │
│                     │       │                         │
│  Management tools:  │       │  Dynamically created    │
│  aipcs_service_seed │       │  per domain:            │
│  aipcs_service_*    │       │                         │
│                     │       │  SQLite schema          │
│  Service registry   │       │  FastAPI endpoints      │
│  Schema validator   │       │  MCP tool definitions   │
│  Migration engine   │       │  Schema manifest        │
└──────────┬──────────┘       └────────────┬────────────┘
           │                               │
           └───────────┬───────────────────┘
                       │
           ┌───────────▼───────────┐
           │   AIPCS Registry DB   │
           │                       │
           │  services             │
           │  seeds                │
           │  manifests            │
           │  migrations           │
           │  audit_log            │
           └───────────────────────┘
```

The AIPCS Server is a single always-on MCP server. Domain services are created dynamically by it. Both are accessible to the MCP client via the same MCP connection.

---

## Service Lifecycle States

Every AIPCS domain service exists in one of two states:

### SEEDED
A domain marker has been planted. The agent has recognised a persistence need but has not yet accumulated sufficient domain knowledge to design a full schema.

A seed contains:
```json
{
  "service_id": "uuid",
  "domain_name": "string — human readable e.g. job_applications",
  "domain_class": "string — top-level taxonomy e.g. career",
  "intent_description": "string — what the agent intends to track",
  "confidence": "seeded",
  "created_at": "iso8601",
  "last_activity_at": "iso8601",
  "session_count": 0,
  "schema": null,
  "endpoint": null
}
```

A seeded service is immediately queryable via `aipcs_service_inspect`. The agent can ask "what domains am I tracking?" and receive seeded services in the response.

### MATERIALISED
A full schema has been designed, validated, and deployed. The service is running, its MCP tools are registered, and the agent can read and write domain data.

A materialised service adds to the seed:
```json
{
  "confidence": "materialised",
  "schema_version": "integer",
  "endpoint": "http://localhost:{port}",
  "tools": ["domain_object_action", ...],
  "materialised_at": "iso8601",
  "last_evolved_at": "iso8601"
}
```

---

## AIPCS Management Tools (the primitive set)

These are the tools exposed by the AIPCS Server itself — available to the agent from the moment AIPCS is connected.

### `aipcs_service_seed`

Plant a domain marker. Always the first action when a persistence need is recognised.

```json
{
  "name": "aipcs_service_seed",
  "description": "Plant a domain tracking marker. Use when a persistence need is recognised but the schema is not yet fully formed. Returns a service_id for future reference.",
  "parameters": {
    "domain_name": "string — short snake_case domain identifier",
    "domain_class": "string — top-level class from known taxonomy or proposed new class",
    "intent_description": "string — what the agent intends to track in this domain"
  }
}
```

### `aipcs_service_design`

Submit a full schema design for a seeded domain. The AIPCS server validates it before accepting.

```json
{
  "name": "aipcs_service_design",
  "description": "Submit a relational schema design for a seeded domain. Schema is validated before acceptance. Returns validation result and any required revisions.",
  "parameters": {
    "service_id": "uuid — from aipcs_service_seed",
    "schema": {
      "entities": [...],
      "relationships": [...],
      "indices": [...],
      "query_patterns": [...]
    },
    "tool_definitions": [...]
  }
}
```

### `aipcs_service_materialise`

Deploy a validated schema as a live queryable service.

```json
{
  "name": "aipcs_service_materialise",
  "description": "Deploy a validated schema as a live queryable service. In the first reference implementation, records are operated through stable generic MCP tools. Generated domain-specific MCP tools are optional and may require session reconnect in some clients.",
  "parameters": {
    "service_id": "uuid — with validated schema"
  }
}
```

### `aipcs_service_evolve`

Propose and apply a schema migration. Additive changes applied immediately after validation. Destructive changes require confirmation.

```json
{
  "name": "aipcs_service_evolve",
  "description": "Propose a schema migration for a materialised service. Additive changes (add column, add table) are applied after validation. Destructive changes require explicit confirmation.",
  "parameters": {
    "service_id": "uuid",
    "migration": {
      "type": "additive | destructive",
      "description": "string — human readable description of the change",
      "changes": [...]
    }
  }
}
```

### `aipcs_service_list`

Discover all seeded and materialised services for the current owner.

```json
{
  "name": "aipcs_service_list",
  "description": "List all AIPCS domain services — both seeded and materialised. Returns service_id, domain_name, domain_class, state, and tool names for materialised services.",
  "parameters": {
    "state_filter": "all | seeded | materialised — default all"
  }
}
```

### `aipcs_service_inspect`

Get the full schema manifest for a service.

```json
{
  "name": "aipcs_service_inspect",
  "description": "Get the schema manifest, migration history, and tool definitions for a domain service.",
  "parameters": {
    "service_id": "uuid"
  }
}
```

### `aipcs_service_suspend`

Pause a materialised service without deleting data.

```json
{
  "name": "aipcs_service_suspend",
  "description": "Suspend a materialised domain service. Data is preserved. MCP tools are deregistered. Service can be resumed.",
  "parameters": {
    "service_id": "uuid"
  }
}
```

### `aipcs_service_export`

Export schema and data for a service — the consent-gated sharing primitive.

```json
{
  "name": "aipcs_service_export",
  "description": "Export schema and data for a domain service. Output format: JSON or SQLite dump. Requires explicit owner confirmation.",
  "parameters": {
    "service_id": "uuid",
    "format": "json | sqlite",
    "scope": "schema_only | data_only | full"
  }
}
```

---

## Schema Design Requirements

When the agent calls `aipcs_service_design`, it submits a schema that must satisfy the following validation rules before acceptance:

### Structural requirements
- Minimum one entity with at least one non-id attribute
- All entity names in snake_case
- All attribute names in snake_case
- Primary key defined on every entity
- Foreign keys explicitly declared for all relationships

### Audit requirements
- Every entity must include: `created_at`, `updated_at`, `created_via`
- Top-level entities must include `owner_id`

### Taxonomy requirements
- `domain_class` must be set — either from the known taxonomy or as a proposed new class
- Tool definitions must follow `domain_object_action` naming convention
- Tool names maximum 60 characters
- Tool descriptions maximum 250 characters

### Evolution requirements
- Schema version initialised at 1
- Migration history initialised as empty array
- All fields documented in schema manifest

### Validation failure response
If validation fails, AIPCS returns a structured list of violations with remediation guidance. The agent must revise and resubmit. It does not materialise a schema that fails validation.

---

## Schema Manifest Format

The schema manifest is a human-readable JSON document that travels with every AIPCS service. It is the authoritative record of the service's data model.

```json
{
  "manifest_version": 1,
  "service_id": "uuid",
  "domain_name": "job_applications",
  "domain_class": "career",
  "intent_description": "Track job applications through their lifecycle stages",
  "schema_version": 3,
  "created_at": "iso8601",
  "last_evolved_at": "iso8601",
  "entities": [
    {
      "name": "job_application",
      "description": "A single job application and its current state",
      "attributes": [
        {"name": "id", "type": "uuid", "primary_key": true},
        {"name": "owner_id", "type": "string", "required": true},
        {"name": "company_name", "type": "string", "required": true},
        {"name": "role_title", "type": "string", "required": true},
        {"name": "status", "type": "string", "required": true},
        {"name": "applied_at", "type": "datetime"},
        {"name": "created_at", "type": "datetime", "required": true},
        {"name": "updated_at", "type": "datetime", "required": true},
        {"name": "created_via", "type": "string", "required": true}
      ]
    }
  ],
  "relationships": [],
  "indices": [
    {"entity": "job_application", "fields": ["owner_id", "status"]}
  ],
  "migration_history": [
    {
      "version": 1,
      "type": "initial",
      "description": "Initial schema — core job application tracking",
      "applied_at": "iso8601"
    },
    {
      "version": 2,
      "type": "additive",
      "description": "Added interview_date and recruiter_name fields",
      "applied_at": "iso8601"
    },
    {
      "version": 3,
      "type": "additive",
      "description": "Added salary_expectation and notes fields",
      "applied_at": "iso8601"
    }
  ],
  "tool_definitions": [
    {
      "name": "job_application_list",
      "description": "List job applications with status, dates, and key metadata.",
      "required_scope": "read",
      "type": "read"
    },
    {
      "name": "job_application_get",
      "description": "Get full detail for one job application by id.",
      "required_scope": "read",
      "type": "read"
    },
    {
      "name": "job_application_create",
      "description": "Create a new job application record.",
      "required_scope": "write",
      "type": "write"
    },
    {
      "name": "job_application_status_update",
      "description": "Update the status of a job application. Records change history.",
      "required_scope": "write",
      "type": "write"
    }
  ]
}
```

---

## Schema Evolution Rules

### Additive migrations (auto-applied after validation)
- Add a new column with a nullable or defaulted value
- Add a new table
- Add a new index
- Add a new tool definition

### Destructive migrations (require explicit confirmation)
- Drop a column
- Drop a table
- Rename a column or table
- Change a column type
- Remove a tool definition

### Migration validation
Before any migration is applied:
1. AIPCS validates the migration against the backward-compatibility rules
2. If additive — apply immediately, update manifest, increment schema_version
3. If destructive — return proposed migration to agent with impact summary, require `confirm: true` on resubmission
4. All migrations recorded in migration_history with type, description, and applied_at

---

## AIPCS Skill Definition (v1)

The AIPCS skill is the prompt/instruction set that teaches an agent to recognise persistence needs and use AIPCS correctly. It must be portable across different agent skill frameworks.

### Bootstrap model
Bootstrap is the combination of:

1. **Static agent instructions** — the agent must know AIPCS exists, what purpose it serves, when to seed, and when to persist data likely to be useful in a future session.
2. **Dynamic discovery map** — the current organisation of persisted services, exposed as a lightweight data-dictionary view rather than record content.
3. **Deferred procedural skills** — optional multi-step workflows that may later be packaged as skills when they are better represented as agent procedure than atomic MCP tools.

The dynamic bootstrap map should include enough description to reduce blind probing: service intent, domain class, entity names, record counts, recent activity, and schema/entity descriptions where available. It should help the agent understand what information is likely to be found under each domain branch and whether a new fact fits the current schematic approach or suggests schema evolution.

Bootstrap must remain lightweight. It should not dump record content, and it should not replace task-specific retrieval.

### Trigger conditions
The agent should evaluate AIPCS when:
- A user explicitly asks to track, remember, or persist something across sessions
- The agent judges that information from the current interaction is likely to be useful in a future session
- The agent identifies multiple related entities that need to be tracked together over time
- The agent starts a new session with AIPCS available — call bootstrap/discovery before making claims about persisted context
- The agent is about to perform context compaction — evaluate all active knowledge domains for persistence candidacy before compressing
- The agent recognises it is re-explaining domain context it has explained before (a signal that persistence would have helped)

### Behaviour on trigger
1. At session start, call bootstrap/discovery to load the current data-dictionary map.
2. For memory-like services, retrieve bounded content from low-cardinality identity, preference, feedback, behavioural-rule, and project-state entities before answering questions about the user or project.
3. For new persistence needs, check whether an existing service already covers the domain.
4. If yes — use it. Update it if new information warrants evolution.
5. If no — call `aipcs_service_seed` immediately with domain_name, domain_class, and intent_description.
6. Accumulate domain knowledge across interactions.
7. When sufficient domain knowledge exists, call `aipcs_service_design` with full schema.
8. Call `aipcs_service_materialise` to deploy.
9. Use stable generic record tools for reads and writes in this domain. Generated domain-specific tools may be added later as a convenience layer.

### Domain classes and common use cases
`domain_class` is not a closed taxonomy in v1. Agents should prefer common categories with stable definitions when they fit, and propose new classes when they do not.

The purpose of common categories is interoperability and discovery, not restriction. They should help an agent recognise that `job_applications` belongs under `career`, or that `project_memory` belongs under `project`, without preventing more precise domain names or later reclassification.

Common category definitions should be maintained as reference guidance alongside the implementation, not hard-coded validation gates in the first slice.

### Compaction hook
Before compacting context:
1. Call bootstrap/discovery to identify active domains
2. For each active domain, evaluate whether unsaved knowledge should be persisted
3. Write any new knowledge to the relevant domain service before compaction
4. Persist at the level of structured data, not summaries — compaction degrades; structured data does not
5. Proceed with compaction

### Constraints
- Always check for existing services before seeding a new one — avoid domain duplication
- Tool names must follow domain_object_action
- Never persist sensitive data (passwords, payment details, credentials) in AIPCS services
- Always record created_via in writes

---

## Authentication Model (v1)

V1 uses a simplified local trust model acceptable for the reference implementation proving ground. The production OAuth 2.0 + DCR model is designed for but deferred to v2.

### V1 local trust
- AIPCS server runs on localhost within the Docker Compose network
- Owner_id is set from the authenticated application session
- MCP connection is over the private Docker network — not exposed publicly
- All tools enforce owner_id scoping

### V2 target (OAuth 2.0 + DCR)
Per the pattern specification and Application Tracker's MCP_OAUTH_DCR_PLAN.md:
- Dynamic Client Registration
- Authorization Code with PKCE
- Scoped tokens per domain service
- Consent screen per domain
- Token revocation and audit

---

## Deployment (v1)

Docker Compose service alongside Application Tracker:

```yaml
services:
  app:
    # existing Application Tracker service

  mcp:
    # existing MCP sidecar

  aipcs:
    build: ./aipcs
    volumes:
      - aipcs_data:/data        # registry DB and service manifests
      - aipcs_services:/services # per-domain SQLite databases and FastAPI services
    environment:
      - AIPCS_HOST=0.0.0.0
      - AIPCS_PORT=8100
      - AIPCS_DATA_DIR=/data
      - AIPCS_SERVICES_DIR=/services
      - AIPCS_OWNER_ID=${APP_OWNER_ID}
    networks:
      - internal
    restart: unless-stopped

volumes:
  aipcs_data:
  aipcs_services:
```

The AIPCS service is not exposed on the host network by default. It is accessible only to the MCP client over the internal Docker network.

---

## Three-Tier Access Model (design input)

Tier 3 is not implemented in v1 but the architecture must accommodate it.

### Tier 1 — Agent access
Full read/write via MCP tools. Normal operating mode. No direct database access.

### Tier 2 — User access
Natural language queries mediated by the agent. The agent uses its domain MCP tools to answer. The user can request:
- "What have you stored about my job search?" → agent calls `job_application_list`
- "Delete everything about company X" → agent calls domain delete tool
- "Export my career data" → agent calls `aipcs_service_export`

### Tier 3 — Elevated access (designed for, deferred)
Direct read-only access to domain service query endpoints. Requires explicit user consent grant. Cannot write. Audit logged. Scoped export tools. Target use cases: compliance review, data portability, practitioner access (medical scenario), IT audit.

The schema manifest and `aipcs_service_export` tool provide the v1 foundations for Tier 3 without fully implementing it.

---

## Open Questions (v1 scope)

| # | Question | Impact |
|---|----------|--------|
| Q007 | Minimum viable seed payload | Defines `aipcs_service_seed` parameter schema |
| Q008 | Seed TTL — auto-expire if never materialised? | Affects registry DB design |
| Q009 | Domain taxonomy — open registry or curated set? | Affects `domain_class` validation rules |
| Q010 | Domain overlap handling in taxonomy | Affects schema validation |
| Q011 | Tier 3 — v1 or v2? | Affects authentication model scope |

---

## Implementation Sequence

Following Application Tracker's existing task map pattern:

1. **AIPCS registry DB** — the internal database tracking services, seeds, manifests, migrations, audit log
2. **AIPCS management tools** — the eight primitive MCP tools
3. **Schema validator** — validation rules for `aipcs_service_design`
4. **Service materialisation** — SQLite init and manifest-backed queryable service state
5. **Generic record operations** — create/list/get/search/update/delete/history over materialised schemas
6. **Migration engine** — additive and destructive migration support
7. **AIPCS skill definition** — portable skill document
8. **End-to-end validation** — seed → design → materialise → use → evolve flow within Application Tracker

---

*This document is the v1 design. Implementation should follow this design and record deviations in the build journal.*
