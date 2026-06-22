# Execution Plan: Structured Membership Filters

**Status:** Draft
**Owner:** Agent
**Created:** 2026-06-12
**Last updated:** 2026-06-12
**BUILD_JOURNAL entries:** 092

---

## Goal

Add intuitive structured membership filtering to AIPCS so fields such as tags can be queried as individual values without falling back to fuzzy or substring search.

## Non-Goals

- Do not add semantic/vector search.
- Do not add fuzzy matching.
- Do not make broad text search the primary retrieval path.
- Do not require agents to abandon structured schema design.
- Do not change existing exact scalar filter semantics for current text/integer fields.

## Context

The Kropotkin memoir corpus exposed a mismatch between agent expectations and current AIPCS record retrieval. The agent created a comma-separated `tags` field and then discovered that `aipcs_record_search` only supports exact scalar equality. A query such as `tags="Siberia"` returned zero records even though records had human-readable tag strings containing "Siberia".

This is not a case for fuzzy search. It is a case for first-class structured list/tag fields. AIPCS should make intentionally structured multi-value attributes retrievable by membership while keeping ordinary prose fields out of broad search.

## Acceptance Criteria

- [ ] Schema validation supports a list/tag-like attribute type or metadata marker.
- [ ] Records can persist multi-value fields in a structured representation, not comma-separated prose.
- [ ] Record search/list supports membership filtering on declared multi-value fields.
- [ ] Existing exact-match filters remain unchanged for scalar fields.
- [ ] Service summary exposes filterability mode per key field: exact, membership, or annotation/free-text.
- [ ] Retrieval guidance can distinguish filterable tags from human-readable annotation fields.
- [ ] Tests cover positive membership match, no match, invalid membership filter, and backward compatibility.
- [ ] README/docs state that text/fuzzy/semantic search remain deferred.

## Proposed Semantics

### Schema

Prefer an explicit attribute type if the current validator can accommodate it cleanly:

```json
{
  "name": "tags",
  "type": "string_list",
  "description": "Controlled retrieval tags for cross-cutting topics."
}
```

If a new type is too disruptive for the first slice, use explicit metadata on a text field:

```json
{
  "name": "tags",
  "type": "text",
  "retrieval_mode": "membership"
}
```

The first option is cleaner because it prevents comma-separated strings from masquerading as structured data.

### Record Values

Preferred record shape:

```json
{
  "tags": ["siberia", "science", "imprisonment"]
}
```

The storage representation can be SQLite JSON text if that is the smallest safe implementation.

### Filtering

Scalar fields keep exact equality:

```json
{
  "filters": {
    "entry_type": "contradiction"
  }
}
```

List/tag fields support membership:

```json
{
  "filters": {
    "tags": "siberia"
  }
}
```

The tool can interpret this as membership only because `tags` is schema-declared as a list/membership field.

An explicit operator form can be added if ambiguity becomes a problem:

```json
{
  "filters": {
    "tags": {"contains": "siberia"}
  }
}
```

Start with the simpler shape if validation can keep it unambiguous.

## Plan

1. Inspect current schema validator, materializer, and record store type handling.
2. Decide whether to implement `string_list` as a first-class type or as field metadata.
3. Add validation for list values on create/update.
4. Store list values safely in SQLite, likely as JSON text.
5. Update record hydration so returned records expose lists as lists, not raw JSON strings.
6. Add membership filter handling for declared list fields in `record_list` and `record_search`.
7. Update service summary to expose filterability modes.
8. Update README/tool docs to distinguish exact, membership, and deferred text search.
9. Add tests and run `aipcs-server` validation.
10. Rerun a small Kropotkin-style membership retrieval test.

## Progress Log

| Date | What happened |
|---|---|
| 2026-06-12 | Slice created after Kropotkin retrieval audit showed comma-separated tags were misleading with exact-match-only search. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Membership filtering before text search | Solves the intuitive tags problem while preserving structured retrieval as the primary AIPCS pattern. |
| Keep fuzzy/semantic search deferred | Avoids encouraging blob storage followed by broad retrieval. |

## Validation

Planning repo:

```bash
bash scripts/validate-harness.sh
```

Implementation repo:

```bash
.venv/bin/ruff check .
.venv/bin/pytest
.venv/bin/python scripts/validate-harness.py
.venv/bin/python scripts/mcp-smoke.py
```

Behavioral smoke:

```text
Create a test service with memory_entry.tags=["siberia", "science"].
Search tags="siberia".
Expect the record to return.
Search tags="exile".
Expect no match unless another record declares that tag.
```

## Risks

| Risk | Mitigation |
|---|---|
| Agents stop designing good facets and overuse tags | Keep tags structured and exact; service summary should still prefer typed facets such as entry_type, primary_topic, status, and salience. |
| JSON-in-SQLite complicates filtering | Keep implementation small; use JSON1 if available or normalised side table if JSON1 is unavailable. |
| Backward compatibility with existing comma-separated tags is unclear | Do not silently reinterpret existing text fields. Require schema evolution or explicit migration to a membership field. |
| Tool contract becomes confusing | Service summary must expose field filter modes clearly. |

---
