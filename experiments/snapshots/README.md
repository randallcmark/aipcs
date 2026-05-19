# Memory Snapshots

This directory records snapshot definitions for controlled AIPCS experiments.

Actual copied SQLite data should usually stay out of git. Use manifests to describe what the snapshot contains, where the raw artifact lives, and how it was produced.

## Snapshot Types

| Snapshot | Purpose |
|---|---|
| `empty` | No services or records. Tests whether the agent seeds memory from scratch. |
| `seeded` | Seeds exist but services are not materialised. Tests schema formation. |
| `evolved-natural` | Copy of a naturalistically evolved agent memory store. Tests recall and reuse. |
| `stale` | Evolved store with known stale or contradictory records. Tests repair. |
| `prose-heavy` | Store with blobs and weak schema shape. Tests schema self-audit. |
| `read-only` | Store used with read-only permission variants. Tests permission boundary behavior. |

## Snapshot Manifest

Use `SNAPSHOT_TEMPLATE.md` for each snapshot. Keep the manifest in git. Keep raw database copies private unless deliberately publishing sanitized fixtures.
