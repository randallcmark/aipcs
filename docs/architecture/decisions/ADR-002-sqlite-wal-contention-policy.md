# ADR-002: Version and Secure the SQLite WAL Contention Policy

**Status:** Accepted
**Date:** 2026-07-23
**Implemented:** `aipcs-mcp` commit
`c7e3752cc77898984b192721f0af56f2cd1b603c`
**BUILD_JOURNAL entry:** 103

---

## Context

The public-v1 SQLite adapters still use rollback-journal DELETE mode, fixed connection timeouts,
and categorical rejection of WAL sidecars. V1-08 lifecycle recovery requires independent
processes to coordinate through durable storage rather than process-local locks, and it requires
busy, crash, inspection, and retry behavior to be explicit before the cross-store coordinator is
implemented.

WAL mode is persistent database state, not a per-connection preference. Its `-wal` file is part of
the durable database state, and SQLite may create or retain `-wal` and `-shm` files while opening a
read-only database. WAL also requires same-host shared memory and does not support a network
filesystem. SQLite versions 3.7.0 through 3.51.2 have a documented multi-connection WAL-reset
corruption bug that is fixed in 3.51.3.

Changing journal mode without versioned evidence would leave crashes and competing migrators
unable to distinguish an intended partial conversion from an incompatible database. Treating
sidecars as either forbidden or trusted by pathname would also weaken the existing contained,
same-owner storage boundary.

## Decision

SQLite public v1 supports WAL only on Linux/macOS POSIX, on one host, on an operator-owned local
filesystem, with cooperating processes running as the same effective user. Python remains 3.12 or
newer and SQLite must be 3.51.3 or newer. Network filesystems, Windows, multi-host access, and a
hostile same-user peer are outside the supported v1 boundary.

WAL adoption is a versioned split-phase physical-policy migration:

- registry revision 3 uses migration `registry-0003-wal-policy`;
- service-store revision 2 uses migration `service-store-0002-wal-policy`;
- each database has one permanent strict policy table containing the singleton policy
  `aipcs.sqlite.wal.v1`, its compiled migration checksum, and phase `prepared | ready`; and
- historical descriptors, checksums, and history rows remain immutable.

A migration first commits the exact `prepared` marker and dirty predecessor in DELETE mode, then
switches the persistent journal mode, then commits the `ready` marker and target ledger revision
under `BEGIN IMMEDIATE`. It can resume only exact prepared/DELETE or prepared/WAL states. A clean
predecessor/DELETE and exact ready target/WAL are valid; every other ledger, marker, header, or
history combination fails closed. Fresh creation uses the same sequence so a crash cannot leave
an unmarked empty WAL database. Competing migrators re-inspect under the writer lock and may adopt
only an exact successor state produced by the finite migration.

Logical inspection remains application-read-only and observes one explicit read snapshot. It
does not create a missing database, change journal mode or schema, checkpoint, recover a legacy
rollback journal, or repair storage. SQLite may nevertheless create, rebuild, retain, replace, or
remove WAL/SHM operational files as part of opening and closing a valid WAL database.

The main database and every accepted `-wal`, `-shm`, or temporarily authorized `-journal` sibling
remain contained, regular, same-owner, mode `0600`, single-link files. The adapter validates them
through descriptor-relative no-follow operations. Full `openat`/`fstat` validation occurs before
SQLite opens and after it closes. Live checks use descriptor-relative no-follow metadata lookup
without opening and closing another descriptor, because POSIX `close()` can cancel SQLite
advisory locks on the same inode. The root and main database retain pinned identities. A
cooperating peer may legitimately unlink a checkpointed WAL/SHM pathname while another process
retains SQLite's internal descriptor, then recreate it for a later connection. Python does not
expose those SQLite descriptors, so every current sidecar pathname is revalidated without
claiming cross-process inode continuity. The adapter never manually edits, copies, renames,
truncates, repairs, or deletes a sidecar. A rollback journal is authorized only during exact
DELETE preparation or explicit migration-owned hot-journal recovery.

Every connection applies and verifies one immutable SQLite policy: WAL-ready state for ordinary
access, `locking_mode=NORMAL`, `synchronous=FULL`, foreign keys on, trusted schema off, recursive
triggers off, the appropriate query-only setting, `wal_autocheckpoint=1000`, and one configured
busy timeout. Registry and domain writers use `BEGIN IMMEDIATE`; inspections use one deferred read
transaction. A registry unit of work retains its anchored location for its entire connection
lifetime.

The public configuration field is `sqlite_busy_timeout_ms`, exposed as TOML
`[sqlite].busy_timeout_ms`, environment `AIPCS_SQLITE_BUSY_TIMEOUT_MS`, and CLI
`--sqlite-busy-timeout-ms`. Its range is 1 through 30000 milliseconds and its default is 5000.
Text forms are canonical unsigned decimal; TOML requires an integer rather than a boolean or
string. The same value configures both Python's connection timeout and SQLite's busy handler.

`StorageBusy` is a bounded transport-neutral condition with a fixed safe message. It is created
only from a numeric SQLite BUSY-family primary result code or a PASSIVE checkpoint busy result.
It is never inferred from exception text, elapsed wall time, `SQLITE_LOCKED`, or an uncertain
post-commit outcome. There is no adapter retry loop; the timeout applies independently to each
SQLite lock-acquiring call.

Every explicit migration that observes or creates a ready WAL store runs one bounded PASSIVE
checkpoint and then independently re-observes exact readiness. A valid partial PASSIVE checkpoint
is progress, not corruption. Ordinary reads and writes do not initiate explicit checkpoints.

This policy changes SQLite mechanics, private migration revisions, and configuration only. It does
not change the MCP tool surface, manifest grammar, backend-neutral storage contract, or compose
materialise/evolve. PostgreSQL must later satisfy the same behavioral outcomes without copying
SQLite policy tables, revisions, sidecars, or PRAGMAs.

## Consequences

**Benefits:**

- local multi-process readers and writers have one explicit, durable contention model;
- interrupted creation and DELETE-to-WAL conversion are exactly classifiable and resumable;
- WAL/SHM operational behavior no longer contradicts the location-security contract;
- busy and uncertain outcomes remain distinct, bounded, and testable;
- V1-08D can prove cross-store coordination against the final SQLite policy.

**Costs / tradeoffs:**

- SQLite 3.51.2 and earlier are unsupported by default, including runtimes with an unidentified
  vendor backport;
- network filesystems and multi-host SQLite remain explicit operator precondition failures rather
  than heuristically detected cases;
- a migration can wait for more than one configured busy interval because its finite split phases
  acquire independent SQLite locks;
- safe inspection may have observable SQLite-managed sidecar effects;
- sidecar metadata checks secure containment and reject unsafe files, but pathname identity
  continuity cannot distinguish legitimate SQLite peer churn and does not defend against a
  malicious process with the same OS identity.

**Follow-up actions:**

- V1-08C implemented and adversarially tested registry R3 and service-store R2 in
  `aipcs-mcp` commit `c7e3752cc77898984b192721f0af56f2cd1b603c`;
- that slice proved real spawned-process contention, crash recovery, snapshots, checkpoint
  progress, and installed wheel/sdist behavior;
- implement V1-08D coordination only after the V1-08C gates pass;
- define WAL-aware backup/export and explicit checkpoint administration in their later slices.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Keep rollback-journal DELETE mode | It serializes readers behind writers and does not establish the intended local multi-process behavior. |
| Set WAL opportunistically on every connection | Journal mode is durable state; this leaves no exact crash or compatibility evidence. |
| Accept any old database already in WAL | It cannot distinguish intentional conversion from unmanaged or incompatible state. |
| Manage WAL/SHM contents in application code | SQLite owns their format, recovery, checkpointing, and lifecycle; manual intervention risks corruption. |
| Defend correctness with a process-local mutex or retry loop | Neither coordinates independent processes or survives restart; SQLite's writer lock and durable evidence are the authority. |
| Detect network filesystems by mount/type heuristics | Such probes are platform-specific and cannot reliably identify every remapped, FUSE, or container filesystem. |
| Support affected SQLite versions and serialize connections in application code | It creates a fragile second coordination model and does not reliably identify vendor backports. |

## Validation

- Exact frozen predecessor fixtures upgrade without changing application data or historical
  descriptors, and every prepared/ready crash point converges or fails closed.
- Spawned independent processes prove reader/writer coexistence, bounded writer contention,
  migration races, no lost update, crash/restart recovery, and independent-database progress.
- Sidecar tests cover safe creation/replacement/cleanup and hostile symlink, hard-link, type,
  ownership, mode, orphan, and replacement cases without touching outside sentinels.
- Configuration tests prove strict parsing, precedence, redacted reporting, runtime gating, and
  propagation of the single busy timeout.
- Both isolated wheel and sdist installations create, reopen, contend on, crash, recover, and
  upgrade exact WAL stores using their own interpreter.
- Official behavior references: [SQLite WAL](https://www.sqlite.org/wal.html),
  [SQLite PRAGMAs](https://www.sqlite.org/pragma.html),
  [SQLite result codes](https://www.sqlite.org/rescode.html), and
  [SQLite's POSIX `close()` advisory-lock warning](https://www.sqlite.org/howtocorrupt.html#_posix_advisory_locks_canceled_by_a_separate_thread_doing_close_),
  plus
  [Python `sqlite3`](https://docs.python.org/3/library/sqlite3.html).
