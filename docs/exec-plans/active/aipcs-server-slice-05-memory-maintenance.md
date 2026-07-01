# Execution Plan: aipcs-server Slice 05 - Memory Maintenance Helpers

**Status:** Draft
**Owner:** Agent
**Created:** 2026-06-24
**Last updated:** 2026-06-24
**Target repo:** `/Users/markrandall/GitHub/aipcs-server`
**BUILD_JOURNAL entries:** Entry added 2026-06-24

---

## Goal

Add lightweight maintenance discovery helpers so agents can find stale, ageing, duplicate-authority, low-activity, and poorly organised memory without broad listing the entire store.

## Non-Goals

- Do not automatically delete, archive, merge, or rewrite records.
- Do not infer semantic duplicates with embeddings.
- Do not create a universal truth-ranking policy.
- Do not require every schema to include authority fields.
- Do not add compliance/legal expunge controls in this slice.
- Do not build a background maintenance daemon.

## Context

Dogfooding will create long-lived stores. Those stores will accumulate stale records, superseded decisions, old branches, duplicate summaries, low-confidence inferences, and records without authority metadata.

Earlier decisions already reject automatic TTL/expiry in the normal agent memory plane. The agent should be able to see maintenance candidates and decide what to do.

Slice 04 made authority, provenance, staleness, scope, and supersession visible. Slice 05 should use those signals to help the agent maintain memory quality.

## Candidate Tool Surface

Prefer one small tool before adding many specialised tools:

```text
aipcs_maintenance_scan
```

Inputs:

```text
service_id: optional string
entity_name: optional string
branch_id_or_slug: optional string
scan_types: optional list[string]
limit: optional integer
include_examples: optional boolean default false
```

Initial `scan_types`:

```text
stale_or_expired
old_active
low_confidence
superseded
missing_authority
unbranched
low_activity_branch
duplicate_authority_candidate
blob_candidate
```

Output should be compact and candidate-oriented:

```text
{
  "scan_id": "...",
  "computed_at": "...",
  "service_count": 1,
  "candidate_groups": [
    {
      "scan_type": "stale_or_expired",
      "service_id": "...",
      "entity_name": "decision",
      "count": 4,
      "next_tools": ["aipcs_record_search", "aipcs_record_get"],
      "example_refs": [{"record_id": "...", "reason": "valid_until expired"}]
    }
  ],
  "recommendation": "Inspect candidate groups before updating/deleting records."
}
```

## Design Rules

- Maintenance scan returns candidates, not decisions.
- Candidate examples should be bounded and optional.
- No record prose/content should appear unless `include_examples` is true, and even then keep examples compact.
- Prefer record ids, entity names, branches, counts, and reasons.
- Use existing `_meta.staleness`, authority fields, branch assignment state, and updated-age logic.
- Never mutate state from a scan.
- Leave archive/delete/update to existing tools.

## Acceptance Criteria

- [ ] Agent can discover expired/stale records without listing every record.
- [ ] Agent can discover records missing authority fields in memory-like entities.
- [ ] Agent can discover unbranched records when branches exist.
- [ ] Agent can discover superseded records.
- [ ] Agent can discover low-confidence records.
- [ ] Scan output is count/ref/reason based and does not dump full records by default.
- [ ] No maintenance scan mutates memory.
- [ ] Tests cover empty stores, services without authority fields, and services with mixed stale/active records.

## Plan

1. Implement internal scan helpers over existing registry/service stores.
2. Start with non-content scans:
   - expired/stale;
   - superseded;
   - missing authority;
   - unbranched;
   - old active.
3. Add blob-candidate heuristics only if cheap and mechanical:
   - unusually long string fields;
   - many records with same title/summary prefix;
   - entity has few fields and many long prose values.
4. Expose one MCP tool.
5. Add tests for bounded candidate output.
6. Add documentation describing maintenance as agent judgment.

## Validation

```bash
.venv/bin/ruff check .
.venv/bin/pytest
.venv/bin/python scripts/validate-harness.py
.venv/bin/python scripts/mcp-smoke.py
```

## Risks

| Risk | Mitigation |
|---|---|
| Maintenance becomes hidden policy | Return candidates and reasons only; leave updates to the agent. |
| Scan payload gets too large | Return counts and bounded refs; require follow-up retrieval. |
| Duplicate detection becomes semantic search by stealth | Keep duplicate-authority candidates mechanical in v1. |
| Agents over-prune useful old memory | Default to recommendations and archive/status changes, not deletion. |
