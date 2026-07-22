# ADR-001: Use Immediate RESTRICT for Public-v1 Foreign Keys

**Status:** Accepted
**Date:** 2026-07-22
**BUILD_JOURNAL entry:** 101

---

## Context

The first relational-contract implementation combined `ON DELETE/UPDATE RESTRICT` with
`DEFERRABLE INITIALLY DEFERRED`. Adapter planning exposed that this is not one portable behavior.
SQLite applies `RESTRICT` immediately even when the foreign-key constraint is declared deferred,
and PostgreSQL distinguishes non-deferrable `RESTRICT` from deferrable `NO ACTION`.

Public v1 already rejects every cycle in the required relationship graph because its planned
single-record API could not create the first record. Nullable cycles are breakable without deferred
constraints: create records with null relationship values, then update the edges after targets
exist.

## Decision

Keep the manifest relationship policy `restrict` and use native immediate `ON DELETE RESTRICT` and
`ON UPDATE RESTRICT` in SQLite and PostgreSQL. The backend-neutral relational contract reports
constraint timing as `immediate`.

Do not silently render `NO ACTION` for a `restrict` declaration and do not add custom deferred
enforcement.

## Consequences

**Benefits:**

- one truthful behavior across both required reference adapters;
- no manifest wire-policy change;
- no triggers or adapter-specific emulation;
- relationship creation remains compatible with the planned single-record mutation boundary.

**Costs / tradeoffs:**

- callers cannot temporarily violate a relationship within a transaction and repair it before
  commit;
- nullable cycles require a staged create-then-update workflow;
- the pre-release V1-07A relational value and documentation require a corrective follow-up.

**Follow-up actions:**

- correct the canonical contract, public relational value, tests, documentation, and installed
  artifact smoke before SQLite materialisation;
- make V1-07B inspect the native immediate action exactly;
- require the PostgreSQL adapter to pass the same behavioral contract.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Deferred `NO ACTION` | It changes the declared policy and permits operation ordering that `RESTRICT` intentionally forbids. |
| Custom deferred `RESTRICT` enforcement | It adds disproportionate cross-adapter triggers/application logic and a second enforcement path. |
| Render `NO ACTION` while retaining the name `restrict` | The stored behavior would contradict the manifest contract. |

## Validation

- SQLite DDL and behavioral tests prove parent delete/update fails immediately.
- PostgreSQL conformance must prove the same behavior.
- Required-cycle validation and nullable-cycle materialisation tests remain green.
- Official behavior references: [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html) and
  [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html).
