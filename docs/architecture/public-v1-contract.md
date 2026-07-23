# Public-v1 Primitive Server Contract

**Status:** Canonical implementation-contract update
**Date:** 2026-07-23
**Evidence:** BUILD_JOURNAL Entries 100, 102, 103, 104, 105, and 106

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

The following lifecycle semantics were frozen by V1-08A. V1-08D implements their private
coordinator without registering a tool or changing the current five-tool SQLite surface. A future
public materialise request requires `service_id`, exact
`expected_service_revision`, exact `expected_schema_version`, and `idempotency_key`. A future
public evolve request requires the same values plus a complete, deeply validated manifest-v2 target
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

SQLite's exact crash-resumable foundation migration exposes committed `prepared` states as
`dirty` and commits the exact clean R2 predecessor as `outdated` before R3 begins. A same-key
coordinator therefore runs the existing foundation migration action for either observation and
re-observes. The public `dirty` state deliberately does not distinguish live exact peer progress
from historical dirt, while `outdated` is explicitly resumable predecessor evidence. Repeated
non-convergence after the bounded reconciliation budget is operation-uncertain and leaves the
registry intent prepared; neither observation is sufficient by itself to make recovery-required
durable. Exact incompatible/domain-unsafe observations or the registry's exact final CAS refusal
remain terminal recovery evidence.

The completed coordinator and usable-memory runtime are implemented in `aipcs-mcp` commit
`a5f0f2a2538c771d00986857df2177c5de300370`. Deterministic, real-SQLite, spawned-process, and
real-stdio proof covers admission, cross-store fault boundaries, exact-target restart adoption,
persistent unsafe-state recovery, same-key cooperation, different-key exclusion, independent
services, exact R2-to-R3 migration, and post-action uncertainty. Separately installed wheel and
sdist workflows exercise the full 21-tool SQLite MCP surface, restart, migration, isolation, and
redaction from a clean exact commit tip.

The registry-held manifest remains the sole current schema authority. A prepared lifecycle intent
may retain one immutable admitted target snapshot as operation evidence, but the service database
must not acquire a manifest, schema version, lifecycle transition/provenance record, lifecycle
fingerprint, lifecycle operation ledger, or second migration ledger. This does not prohibit the
service-local completed-mutation replay evidence required to commit record and topology
idempotency atomically with their one-database mutations; that evidence is not a schema or
materialise/evolve transition authority and has no prepared phase. The lifecycle intent has
`prepared`, `completed`, and `recovery_required` phases; it is the durable per-service transition
authority, rather than a process-local mutex or a progress flag.

After V1-08E public composition, the service projection adds only `service_revision` and the
bounded aggregate `recovery_state: clear | pending | recovery_required`. It exposes no
idempotency key, fingerprint, operation id, target snapshot, phase timestamp, fault text, or repair
procedure. Exact target-first observation may finalise a prepared materialise or evolve operation:
inside the documented same-operating-system-owner, contained-store boundary, an exact target that
predates the intent cannot be distinguished from one committed before a crash. Partial,
incompatible, extra, altered, or unexpectedly deleted state is never adopted or repaired
automatically; it becomes `recovery_required`.

### Frozen V1-08E public composition contract

V1-08E registers exactly `aipcs_service_materialise` and `aipcs_service_evolve` in a ready SQLite
runtime. Stateless remains server-info only. `registry_lifecycle` retains its existing meaning for
seed/list/inspect/design; a separate `materialisation_lifecycle` feature is true only when both new
tools and their coordinator are fully bound. This additive public cut changes
`aipcs_mcp_contract` from the historical pre-release `1.0` identifier to the full SemVer value
`1.1.0`. It does not establish support windows, deprecation policy, or a general release-version
policy, which remain a later release-governance decision.

The materialise request is the strict flat object
`{service_id, expected_service_revision, expected_schema_version, idempotency_key}`. The evolve
request adds one field named `schema`, using the same complete manifest-v2 public document shape
as design without design's initial-schema restriction. `service_id` is a non-zero lowercase
canonical UUID; revisions are strict integers rather than booleans or coerced numbers;
`expected_service_revision` is positive and bounded by the signed-64-bit service-revision range;
materialise requires expected schema version 1; and evolve requires a positive current schema
version below the maximum so its complete target is exactly one version greater. Unknown fields,
caller-supplied principal/provenance, SQL, deltas, recovery choices, and physical-storage inputs are
rejected before registry or service-store work. MCP supplies the configured principal and fixed
`created_via="mcp"`.

The public lifecycle error-code mapping is exact and bounded:

| Coordinator category | Public error code | Retryable |
| --- | --- | --- |
| `malformed_input` | `validation_failed` | No |
| `unsupported_transition` | `unsupported_transition` | No |
| `stale_revision` | `stale_revision` | No |
| `changed_fingerprint` | `changed_fingerprint` | No |
| `operation_in_progress` | `operation_in_progress` | Yes |
| `recovery_required` | `recovery_required` | No |
| `storage_busy` | `storage_busy` | Yes |
| `operation_uncertain` | `operation_uncertain` | Yes |
| `storage_unavailable` | `storage_unavailable` | No |
| `internal_failure` | `internal_error` | No |

Messages remain generic and contain no principal, key, fingerprint, manifest, operation evidence,
locator, path, DSN, SQL, driver text, audit content, or repair instruction. Missing and
cross-principal services are indistinguishable from stale expected state at this lifecycle
boundary. A failure envelope retains `result: null`; after a retryable outcome callers use
inspect/list to observe the aggregate `recovery_state` rather than receiving an operation object.

Every public service projection obtains `recovery_state` from one principal/service-scoped,
read-only registry aggregate in the same short registry snapshot used for the service read:
no active lifecycle row is `clear`, a durable `prepared` row is `pending`, and a terminal
`recovery_required` row is `recovery_required`. Completed rows are clear. The aggregate never
inspects physical storage and exposes no lifecycle-row detail. Lifecycle success/replay projects
the completed terminal service as `clear`, including the existing safe logical
`storage {backend, namespace}` and `materialised_at` fields where applicable.

The ready SQLite composition root constructs the registry adapter, service-store catalog,
domain-schema store, and coordinator from the same resolved location and busy-timeout policy.
Startup migrates only the registry; it allocates or migrates no service store until a lifecycle
request has durably prepared. No configuration field, standalone lifecycle/admin/repair CLI,
retry loop, lease, mutex, PostgreSQL behavior, record operation, or repair workflow is added by
this slice.

V1-08E is implemented in `aipcs-mcp` commits
`6c3b6fb44e053968506f7b873ece0cb913afd3a5` and
`58b106ab84c58871e5af693e58d6dbe1f1d06c8e`. Its source suite, public-history hygiene gate, and
exact-tip release verifier pass. Independently installed wheel and sdist artifacts exercise the
seven-tool contract, materialise/evolve success and replay, process restart, principal isolation,
changed-fingerprint and stale-revision failures, terminal recovery-required behavior, aggregate
recovery projection, and response redaction through real MCP stdio. Separate real-stdio process
proof covers same-key cooperation, different-key exclusion before storage work, and one terminal
revision/effect/audit.

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

V1-08D implements and proves the cross-store coordinator under this final policy in
`aipcs-mcp` commit `7856338f0490343b2e126b3b5a0e845d65d9509f`. V1-08E then composes generic
lifecycle MCP operations, V1-08F establishes generic records, and V1-08G
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
