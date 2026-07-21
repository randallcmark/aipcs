# Execution Plan: Public-v1 Contract Synchronisation

**Status:** In Progress
**Owner:** Randall Mark and implementation agents
**Created:** 2026-07-21
**Last updated:** 2026-07-21
**BUILD_JOURNAL entries:** Entry 100

---

## Goal

Synchronise the research record and implementation programme around a bounded public-v1 contract
while preserving original design and experiment archaeology.

## Non-Goals

- Rewrite historical experiments or claim they prove production readiness.
- Change the core agent-authored-schema pattern.
- Implement public-v1 code in this research repository.
- Decide support/deprecation windows before the late release slice.

## Context

- Historical working design: `docs/AIPCS_v1_Technical_Design.md`
- Public-v1 contract: `docs/architecture/public-v1-contract.md`
- Implementation programme: private `aipcs-server` repository
- Narrative record: BUILD_JOURNAL Entry 100

## Acceptance Criteria

- [x] Historical technical design, architecture, research brief, roadmap, task map, and journal link
  to the public-v1 boundary.
- [ ] Private research/dogfooding artifacts are archived and restore-verified before redistribution.
- [ ] A clean `aipcs-mcp` public target has no private data or operating material.
- [ ] SQLite and PostgreSQL pass the same storage contract suite.
- [ ] Clean-machine `uvx`, stdio MCP, CLI, export/import, and release rehearsal pass.

## Plan

1. Preserve private snapshots, databases, transcripts, and maintainer material outside the future
   public repository; verify an archive restore.
2. Create a clean public-target repository from an allowlist.
3. Implement compatibility/configuration, storage ports, relational fidelity, idempotency, and
   PostgreSQL reference coverage.
4. Implement lifecycle/export/import, admin CLI, packaging, public documentation, and agent examples.
5. Decide support/security/deprecation policy and run the clean-room release gate.

## Progress Log

| Date | What happened |
|---|---|
| 2026-07-21 | Contract synchronisation created from implementation audit and dogfooding decisions. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Preserve the technical design as history; add a public-v1 contract. | The original draft contains useful research archaeology but no longer fully describes the product. |
| Keep one PostgreSQL adapter, not a plugin ecosystem. | Portability must be proven without multiplying untested database promises. |
| Defer public remote MCP and maintenance policy. | Both require separate security/operating evidence. |

## Validation

```bash
bash scripts/validate-harness.sh
```

Review the contract against the actual primitive-server code before every public-v1 slice.

## Risks

| Risk | Mitigation |
|---|---|
| Product wording erases research archaeology. | Keep the historical design and add dated journal/contract records. |
| Private dogfood data reaches the public repository. | Archive and verify first; use an allowlist rather than history rewriting. |
| The public contract overpromises remote security or adapters. | Keep v1 stdio-only with SQLite and one PostgreSQL reference adapter. |

## Paper notes

This is a design-evolution and implementation-planning artifact, not a performance result. It helps
the paper distinguish evidence for the AIPCS pattern from later work needed for a consumable open-
source implementation.
