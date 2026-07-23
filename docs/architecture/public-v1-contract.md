# Public-v1 Primitive Server Contract

**Status:** Canonical implementation-contract update
**Date:** 2026-07-23
**Evidence:** BUILD_JOURNAL Entries 100, 102, 103, 104, and 105

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

The frozen V1-08A lifecycle contract adds three further independent per-service values. This is a
planned contract, not a statement that the current server exposes materialisation or evolution:

- `schema_version` is the agent-authored evolution counter. An evolution names the exact current
  value and supplies an adjacent target manifest; it is not the manifest-document version.
- `service_revision` is a server-owned positive compare-and-swap revision for lifecycle state. A
  seed starts at 1; each successful design, materialisation, evolution, or later operational
  transition increments it once, while an exact replay never increments it.
- `record_version` is a later server-owned per-record mutation revision. It is reserved by V1-08A
  and becomes a record-runtime concern only in V1-08F.

Adapter migration revisions remain private physical-layout revisions. None of these values can
substitute for another.

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

### Frozen V1-08 lifecycle contract

The following future semantics are frozen by V1-08A without registering a tool or changing the
current five-tool SQLite surface. A future materialise request requires `service_id`, exact
`expected_service_revision`, exact `expected_schema_version`, and `idempotency_key`. A future
evolve request requires the same values plus a complete, deeply validated manifest-v2 target
document. It does not accept agent SQL, a migration delta, or migration-history prose. Materialise
is limited to an active designed seed at schema version 1; evolve is limited to an active
materialised service whose target schema version is exactly one greater than the stored current
manifest.

Lifecycle admission first validates and detaches the request, then computes its canonical
principal-scoped fingerprint and resolves an existing `(principal_id, idempotency_key)` claim
*before* loading current expected revisions. An exact completed claim replays even after its
successful operation incremented `service_revision`; a changed fingerprint conflicts; an exact
prepared claim resumes deterministic reconciliation; and an exact recovery-required claim returns
the same bounded terminal result. Only a new key checks current service/schema revisions and the
per-service blocker before it prepares durable intent.

For that new key, physical relational support is part of admission rather than a later surprise.
After the blocker check and before inserting prepared intent, materialise compiles the exact stored
manifest and evolve classifies the exact stored-current/admitted-target pair as one supported
additive transition. An unsupported relational target creates no lifecycle row. Existing-key
resolution retains precedence and never depends on current relational state.

For these future operations, malformed input, unsupported transition, stale expected revision,
changed-fingerprint reuse, recovery-required, storage-unavailable, and generic internal failure are
non-retryable as submitted. Storage-busy, a *different-key* operation-in-progress, and
operation-uncertain are retryable. An exact same-key prepared claim resumes reconciliation rather
than returning operation-in-progress.

The internal coordinator commits prepared intent and closes the registry transaction before any
service-store I/O. It discards every physical-action return and re-observes exact state through the
pure recovery planner. A pre-action unavailable observation is storage-unavailable. Numeric busy
remains storage-busy. An inspection-time migration error is operation-uncertain because no exact
state was returned; it is not inferred as incompatible. Once a physical action or registry commit
may have taken effect, a failure whose durable outcome cannot be proven is operation-uncertain; it
never becomes recovery-required from exception text or an assumed rollback. Every registry UoW is
closed on every path.

SQLite's exact crash-resumable foundation migration exposes committed `prepared` WAL states as
`dirty` between its bounded physical phases. A same-key coordinator therefore runs the existing
foundation migration action once for an observed dirty foundation, discards the return, and
re-observes. Exact prepared state converges to ready; generic historical dirt is not repaired and
remains dirty. Only that freshly re-observed dirt after a successful bounded migration attempt, an
exact incompatible/domain-unsafe observation, or the registry's exact final CAS refusal makes
recovery-required durable.

The registry-held manifest remains the sole current schema authority. A prepared lifecycle intent
may retain one immutable admitted target snapshot as operation evidence, but the service database
must not acquire a manifest, schema version, transition/provenance record, fingerprint, operation
ledger, or second migration ledger. The lifecycle intent has `prepared`, `completed`, and
`recovery_required` phases; it is the durable per-service transition authority, rather than a
process-local mutex or a progress flag.

After V1-08E public composition, the service projection adds only `service_revision` and the
bounded aggregate `recovery_state: clear | pending | recovery_required`. It exposes no
idempotency key, fingerprint, operation id, target snapshot, phase timestamp, fault text, or repair
procedure. Exact target-first observation may finalise a prepared materialise or evolve operation:
inside the documented same-operating-system-owner, contained-store boundary, an exact target that
predates the intent cannot be distinguished from one committed before a crash. Partial,
incompatible, extra, altered, or unexpectedly deleted state is never adopted or repaired
automatically; it becomes `recovery_required`.

### Frozen V1-08C SQLite physical policy

Local SQLite v1 requires Python 3.12 or newer and SQLite 3.51.3 or newer on Linux/macOS POSIX, on
one host and one operator-owned local filesystem, with cooperating processes running as the same
effective user. Network filesystems, Windows, multi-host access, and a hostile same-user process
are outside this support boundary.

WAL adoption is a versioned, split-phase physical migration: registry revision 3 and service-store
revision 2 each add one exact singleton policy row for `aipcs.sqlite.wal.v1`, with compiled checksum
and `prepared | ready` phase. Migration commits the prepared dirty predecessor in DELETE mode,
switches the persistent journal mode, then commits ready target history under `BEGIN IMMEDIATE`.
Only an exact clean predecessor/DELETE, prepared/DELETE, prepared/WAL, or ready target/WAL is
accepted. Fresh creation uses the same state machine; every other marker, ledger, header, or
history combination fails closed. Competing migrators re-inspect under the SQLite writer lock.

Inspection observes one explicit read snapshot and never changes application/schema state,
journal mode, or checkpoint policy. SQLite may still create, rebuild, retain, replace, or remove
WAL/SHM operational siblings during a valid open/close. The database and accepted sidecars remain
contained regular same-owner mode-`0600` single-link files, validated by descriptor-relative
no-follow operations. Full `openat`/`fstat` validation occurs before SQLite opens and after it
closes. Live checks use descriptor-relative no-follow metadata lookup without opening and closing
another descriptor, because POSIX `close()` can cancel SQLite advisory locks on the same inode.
The root and main database retain pinned identities. A cooperating peer may legitimately unlink
or recreate a WAL/SHM pathname while another process retains SQLite's internal descriptor, which
Python does not expose, so each current sidecar pathname is revalidated without claiming
cross-process inode continuity. The adapter never edits or removes WAL/SHM itself. A rollback
journal is authorized only during exact DELETE preparation or explicit migration-owned
hot-journal recovery.

Connections verify WAL readiness, `locking_mode=NORMAL`, `synchronous=FULL`, foreign keys,
trusted-schema and recursive-trigger settings, query-only intent, `wal_autocheckpoint=1000`, and
one configured busy timeout. The public field `sqlite_busy_timeout_ms` has range `1..30000`,
default `5000`, and exact TOML/environment/CLI representations. It configures both Python connect
waiting and SQLite's busy handler; there is no adapter retry loop.

`StorageBusy` is a bounded condition created only from numeric SQLite BUSY-family result codes or
a PASSIVE checkpoint busy indicator. It is not inferred from driver text, elapsed time,
`SQLITE_LOCKED`, or an uncertain post-commit outcome. Every explicit migration that observes or
creates a ready WAL store performs one PASSIVE checkpoint and an independent final readiness
observation. A valid partial PASSIVE checkpoint is successful progress. Ordinary reads and writes
do not initiate explicit checkpoints.

These are private SQLite physical mechanics, not backend-neutral schema or lifecycle semantics.
The full decision, alternatives, and validation boundary are recorded in
[ADR-002](decisions/ADR-002-sqlite-wal-contention-policy.md).

V1-08D implements and proves the cross-store coordinator under this final policy. V1-08E then
composes generic lifecycle MCP operations, V1-08F establishes generic records, and V1-08G
establishes structured discovery and branch topology. PostgreSQL starts only after V1-08G, so it
proves this complete behavior rather than defining missing record, branch, or recovery semantics.

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
