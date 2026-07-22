# Public-v1 Primitive Server Contract

**Status:** Canonical implementation-contract update
**Date:** 2026-07-21
**Evidence:** BUILD_JOURNAL Entry 100

This contract preserves the May 2026 technical design as historical working design and research
archaeology. It does not change the AIPCS pattern: the agent remains the architect of its persistent
memory schema and may evolve that schema as knowledge accumulates. It makes the public product
boundary explicit.

## Interface ownership

Public v1 is a local-first `stdio` MCP server with stable generic primitives for service lifecycle,
discovery, records, branches, maintenance, and planned portability/lifecycle operations. The server
owns MCP tool names, descriptions, and contracts. Agent-authored schemas own entities, attributes,
relationships, indices, and retrieval guidance; schemas do not define MCP tools.

Generated domain tools, per-domain FastAPI services, agent-authored `tool_definitions`, aliases,
registry classification confidence, `session_count`, and dedicated merge/split are retired from the
public model. Parent-service composition is deferred until independently managed services need a
clear composition contract. Fuzzy/semantic/cross-service retrieval, public remote MCP, OAuth/DCR,
hosted tenancy, and zero-knowledge storage are separate future work.

## Version layers

| Layer | Identifier | Responsibility |
| --- | --- | --- |
| Distribution | `aipcs-mcp` SemVer | Installed package, executable, dependencies, and admin CLI |
| MCP capability | `aipcs_mcp_contract` SemVer | Tool surface, fields, errors, lifecycle, capabilities |
| Manifest | `manifest_version` integer | Schema document interpretation; private v1 imports one-way to public v2 |
| Storage migration | Per-adapter revision | Physical registry/domain schema and repair state |
| Export bundle | `export_format_version` integer | Portable schema/data/history/branch envelope and importer semantics |

The layers are independent. `schema_version` remains a per-service evolution counter and an
optimistic-concurrency input, not an MCP compatibility version. Private `aipcs-server` 0.1 stores
are migration sources, not a permanent public runtime compatibility promise.

## Relational and storage boundary

Initial designs validate every relationship and index. Public v1 supports explicit single-service
foreign keys and explicitly named agent-declared indexes; adapters may generate deterministic
internal support indexes that are not manifest declarations. Materialisation creates every accepted
constraint and declared index. `add_index` is additive evolution. A new entity may reference an
existing entity. Changes requiring an existing-table rebuild are rejected with a structured
unsupported-migration response; the server never retains relational metadata it cannot enforce.

Foreign keys use native immediate `ON DELETE RESTRICT` and `ON UPDATE RESTRICT` semantics in both
reference adapters. Required relationship cycles are rejected before persistence; nullable cycles
remain constructible by inserting records with null relationship fields and updating those fields
after their targets exist. Public v1 does not claim a deferred `RESTRICT` combination: SQLite
executes `RESTRICT` immediately even on a deferred constraint, and PostgreSQL does not defer
`RESTRICT`. This preserves one honest cross-backend behavior without custom enforcement.

AIPCS exposes narrow registry and materialised-service storage ports. SQLite is the local default and
reference adapter. PostgreSQL is the only secondary reference adapter required for v1; no general
adapter plugin framework is promised. Backend locators/namespaces are non-secret; credentials and
filesystem paths never appear in MCP responses, audits, or portable exports.

## Lifecycle, portability, and recovery

```text
design_state:       seeded | materialised
operational_status: active | suspended | archived
```

Suspended and archived services remain inspectable and exportable but reject mutation. Seeds have no
automatic TTL. Maintenance can report a dormant candidate only. Purge is explicit, admin-only,
confirmed, and leaves an audit tombstone with verified export or explicit override.

Export/import uses a backend-neutral, versioned bundle containing service identity, manifest, state,
records, record history, branches, relevant audit metadata, and checksums. Import validates before
mutation, supports dry-run and collision policy, and records provenance.

Every mutation has an idempotency key and request fingerprint. Schema evolution and service
transitions use expected versions; record update/delete uses a server-managed revision. SQLite
WAL/busy handling and PostgreSQL transactions satisfy the same behavioural contract. Failed
cross-store work reconciles or exposes a deterministic repair state.

## Administration and release boundary

The `aipcs` admin CLI calls the same application services as MCP for configuration, status/doctor,
storage/service inspection, export/import, maintenance, archive/resume, and purge. It has no raw
SQL escape hatch. Public distribution is `aipcs-mcp`, verified through a clean-machine `uvx` smoke
test.

A late release slice decides supported releases, security fixes/backports, deprecation and end-of-
life windows, disclosure handling, and release ownership. It is intentionally deferred until the
compatibility and operating envelope are measured, but must be complete before general availability.

## Paper framing

The evidence supports a bounded architectural claim: AIPCS provides durable, inspectable, evolvable,
agent-authored memory structure. It does not establish benchmark superiority over curated flat
artifacts, raw source access, or model priors. This hardening programme is dogfooding-informed
implementation work, not retroactive experimental proof of production readiness.
