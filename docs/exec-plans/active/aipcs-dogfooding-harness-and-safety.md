# Execution Plan: Dogfooding Harness And Safety Baseline

**Status:** Draft
**Owner:** Randall Mark / Agent
**Created:** 2026-06-24
**Last updated:** 2026-06-24
**Target repos:** `/Users/markrandall/GitHub/aipcs`, `/Users/markrandall/GitHub/aipcs-server`, homelab/private lab host
**BUILD_JOURNAL entries:** Entry added 2026-06-24

---

## Goal

Create a practical, reversible AIPCS dogfooding setup so Claude/Codex can use AIPCS during real work without risking private-data leakage, uncontrolled state drift, or unrecoverable memory corruption.

## Non-Goals

- Do not build production authentication or public internet exposure.
- Do not create a publishable corpus from private dogfooding data.
- Do not require every repo to use AIPCS immediately.
- Do not solve automated maintenance in this slice.
- Do not use direct SQLite writes as the normal operating path.

## Context

Dogfooding was deliberately postponed while controlled experiments were active. That constraint is now relaxing: the paper evidence is sufficiently bounded, and the project needs real-use pressure to find the next set of design flaws.

The lab work already established useful practices:

- snapshot or archive the AIPCS data directory before experiments;
- keep run artifacts separate from working repo state;
- record visible model/client/date/tool surface;
- avoid direct database mutation in scored runs;
- prefer private local/homelab endpoints until hardening exists.

## Acceptance Criteria

- [ ] A private AIPCS endpoint is available for day-to-day local/homelab work.
- [ ] The dogfooding data directory can be backed up with one copy/pasteable command.
- [ ] The dogfooding data directory can be restored or moved aside without losing the last good state.
- [ ] Claude and Codex can both see the AIPCS MCP server where feasible.
- [ ] A simple bootstrap -> service summary -> record create -> retrieval loop works.
- [ ] Private dogfooding data is clearly excluded from publishable experiment snapshots.
- [ ] A lightweight dogfooding note template is available.

## Plan

1. Pick the first dogfooding store.
   - Prefer a private local or homelab `.data` directory.
   - Use a distinct owner id from experiment owners if possible.
   - Keep it separate from `experiments/snapshots/`.
2. Create backup conventions.
   - Before first use, archive the empty or initial `.data`.
   - Before significant schema changes, archive again.
   - Store private backups outside git.
3. Wire the endpoint into one harness.
   - Start with the harness you will actually use first.
   - Confirm `aipcs_bootstrap` is callable.
   - Confirm the tool list reflects the current server version.
4. Run a one-task dogfood pilot.
   - Choose a real but low-risk task, such as planning the next paper section or reviewing implementation notes.
   - Let the agent decide what to persist.
   - Ask the agent at the end what it persisted and why.
5. Review the AIPCS state.
   - Check whether it used branches, authority fields, and retrieval affordances.
   - Note any blobs, duplicated facts, missing provenance, or awkward schemas.
6. Decide whether to widen.
   - Add `aipcs-server` coding work only after one low-risk pilot.
   - Add personal or sensitive topics only after backup/export and maintenance are comfortable.

## Copy-Paste Dogfooding Note Template

```text
## AIPCS Dogfooding Note

Date:
Client:
Visible model:
Repo/task:
AIPCS endpoint:
AIPCS owner id:
aipcs-server commit/version:

Prompt/task summary:

Services inspected:
Records retrieved:
Records created:
Records updated:
Branches created/used:

Useful memory behavior:
Friction or failed tool calls:
Potential maintenance needed:
Privacy concerns:
Paper/design notes:
```

## Validation

```bash
bash scripts/validate-harness.sh
```

Manual dogfood validation:

```text
1. Agent calls aipcs_bootstrap.
2. Agent can inspect or summarise a service.
3. Agent can create a low-risk record.
4. A fresh session can retrieve that record.
5. Backup/restore path is documented before sensitive data is stored.
```

## Risks

| Risk | Mitigation |
|---|---|
| Private memory leaks into git artifacts | Keep private `.data` paths out of repo snapshots and add explicit notes when exporting. |
| Agent bypasses MCP and edits SQLite directly | Treat direct DB access as out-of-contract; use hosted/private endpoint or file permissions where useful. |
| Claude/Codex cloud memory contaminates observations | Treat dogfooding as qualitative design evidence unless run under frozen controlled conditions. |
| Store grows before maintenance tools exist | Start with low-risk domains and schedule early self-audit. |
