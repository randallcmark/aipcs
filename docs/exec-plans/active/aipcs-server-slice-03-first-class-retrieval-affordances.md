# Execution Plan: aipcs-server Slice 03 - First-Class Retrieval Affordances

**Status:** Draft
**Owner:** Agent
**Created:** 2026-06-24
**Last updated:** 2026-06-24
**Target repo:** `/Users/markrandall/GitHub/aipcs-server`
**BUILD_JOURNAL entries:** Add one when this slice is accepted or implemented

---

## Goal

Make exact and membership retrieval affordances first-class discovery objects so a cold agent can see how to query a service without inferring semantics from prose, raw records, or individual tool descriptions.

The intended discovery path remains:

```text
aipcs_bootstrap -> aipcs_service_summary -> aipcs_record_search/list
```

Slice 03 should make the retrieval contract visible at the right tier:

- bootstrap says whether useful structured retrieval affordances exist;
- service summary shows the concrete queryable fields, filter modes, value shapes, and examples;
- record responses may reinforce the same contract in compact `_meta`, but should not be the primary discovery mechanism.

## Non-Goals

- Do not add fuzzy search, substring search, full-text search, semantic search, embeddings, or cross-service search.
- Do not make broad search the default retrieval strategy.
- Do not put observed record values or record samples into bootstrap.
- Do not restore full attribute objects or schema detail to bootstrap.
- Do not bloat individual MCP tool descriptions with large examples.
- Do not infer semantic tags or facets from prose.
- Do not require every service to use tags.
- Do not silently reinterpret legacy comma-separated string fields as membership fields.
- Do not replace agent-authored schema/facet design with server-authored domain recommendations.

## Context

`run027` showed a specific affordance failure. Membership filters existed and were implemented, but the agent did not reliably discover or use them. It reasoned from record values and apparent exact-match semantics rather than from an obvious retrieval contract.

This slice supersedes the remaining unresolved parts of `retrieval-affordance-legibility.md`. That older plan correctly identified the broad issue, but it bundled already-completed work with future work. Slice 03 narrows the remaining implementation target to first-class structured retrieval-affordance discovery.

Earlier slices addressed adjacent problems:

- `structured-membership-filters.md` added intentional `string_list` membership filtering.
- `retrieval-affordance-legibility.md` identified that record hydration, filter examples, and tool discovery all affect agent success.
- Slice 02 added compact discovery metadata and made `aipcs_service_summary` the middle discovery tier.

Slice 03 should now consolidate retrieval affordances as an explicit API concept rather than leaving them spread across `filter_modes`, `filter_examples`, entity cards, record `_meta`, docs, and tool prose.

Relevant plans:

- `docs/exec-plans/active/structured-membership-filters.md`
- `docs/exec-plans/active/retrieval-affordance-legibility.md`
- `docs/exec-plans/active/aipcs-server-slice-02-discovery-metadata.md`

Relevant experiment signal:

- `run027`: membership filters existed but were not reliably discovered or used.
- Kropotkin membership corpus runs: agents could retrieve with exact facets when prompted, but often needed stronger affordance visibility.
- Close-out mixed-corpus runs: agents fell back to broad extraction when memory topology and retrieval affordances were heterogeneous.

## Design Principle

Retrieval affordances should be explicit contracts, not hints the agent reconstructs from scattered evidence.

An affordance should answer:

- which entity can be queried;
- which field can be queried;
- whether the field uses scalar exact match, list membership, or annotation/free-text;
- what value shape the tool expects;
- whether examples are available;
- how to form a valid filter object;
- whether branch scoping can combine with the filter.

This is still not semantic search. It is making structured retrieval legible.

## Proposed Response Shape

Introduce a small reusable retrieval-affordance object in public discovery responses.

Suggested shape:

```json
{
  "entity_name": "memory_entry",
  "field_name": "retrieval_tags",
  "mode": "membership",
  "value_shape": "single_string_member",
  "filter_shape": {"retrieval_tags": "science"},
  "source": "schema_string_list",
  "facet": true,
  "example_available": true,
  "observed_value_count": 12
}
```

For exact scalar fields:

```json
{
  "entity_name": "memory_entry",
  "field_name": "entry_type",
  "mode": "exact",
  "value_shape": "scalar",
  "filter_shape": {"entry_type": "turning_point"},
  "source": "schema_scalar",
  "facet": true,
  "example_available": true,
  "observed_value_count": 8
}
```

For annotation/free-text fields:

```json
{
  "entity_name": "memory_entry",
  "field_name": "interpretive_note",
  "mode": "annotation",
  "value_shape": "free_text",
  "filter_shape": null,
  "source": "schema_text",
  "facet": false,
  "example_available": false,
  "observed_value_count": null
}
```

Names can differ during implementation, but the API should preserve the distinction between:

- filterable exact scalar fields;
- filterable membership fields;
- non-filter annotation/free-text fields.

## Bootstrap Requirements

Bootstrap should stay compact and should not include concrete observed filter values.

Add a bounded retrieval-affordance summary to each service card, for example:

```json
"retrieval_affordance_cues": {
  "has_exact_filters": true,
  "has_membership_filters": true,
  "has_annotation_fields": true,
  "filterable_entity_count": 2,
  "filterable_field_count": 7,
  "membership_field_count": 2,
  "facet_field_count": 4,
  "examples_available": true,
  "summary_has_filter_contract": true
}
```

Optionally include a very small bounded preview of field names only:

```json
"retrieval_affordance_preview": [
  {"entity_name": "memory_entry", "field_name": "entry_type", "mode": "exact"},
  {"entity_name": "memory_entry", "field_name": "retrieval_tags", "mode": "membership"}
]
```

Preview constraints:

- bounded, deterministic, and small;
- no observed values;
- prefer declared discovery facets first;
- include at least one membership field when present;
- include at most 3-5 entries.

The purpose is to make a cold agent think: "this service has structured filters; call `aipcs_service_summary` before listing."

## Service Summary Requirements

`aipcs_service_summary` should become the authoritative retrieval-contract surface for a selected service.

At service level, include:

```json
"retrieval_affordances": [
  {
    "entity_name": "memory_entry",
    "field_name": "retrieval_tags",
    "mode": "membership",
    "value_shape": "single_string_member",
    "filter_shape": {"retrieval_tags": "science"},
    "source": "schema_string_list",
    "facet": true,
    "example_available": true,
    "observed_value_count": 12
  }
]
```

Entity cards may continue to include `filter_modes`, `filter_examples`, and `facets`, but those should be treated as backward-compatible detail. The first-class affordance list should be the simplest thing for an agent to scan.

Ordering should be deterministic:

1. declared discovery facets;
2. membership fields;
3. exact scalar fields with observed examples;
4. exact scalar fields without examples;
5. annotation/free-text fields, if included at all.

Keep the list bounded if necessary. If bounded, include:

```json
"retrieval_affordances_truncated": true,
"retrieval_affordance_limit": 50
```

The first implementation can choose a high enough cap for practical service summaries while still preventing pathological payload growth.

## Record Response Reinforcement

Record list/get/search responses may continue to include compact `_meta.filter_modes` and `_meta.filter_examples`.

If this slice introduces `retrieval_affordances`, record `_meta` should not duplicate the full service-level contract for every record. Prefer a compact reference or entity-level subset, for example:

```json
"_meta": {
  "retrieval_affordance_ref": "call aipcs_service_summary for full filter contract",
  "entity_filter_modes": {
    "entry_type": "exact",
    "retrieval_tags": "membership"
  }
}
```

Do not allow record responses to become the main discovery surface. Agents should not need to list records first to learn how to search.

## Tool Discovery Requirements

Do not solve this by bloating every tool docstring.

Small hygiene updates are acceptable, especially for `aipcs_service_summary`, `aipcs_record_search`, and `aipcs_record_list`, but the durable contract should be in returned structured fields.

Suggested docstring emphasis:

- `aipcs_service_summary`: "Use after bootstrap to see retrieval affordances, filter examples, facets, and branch cues for one service."
- `aipcs_record_search`: "Requires one entity and at least one structured filter; scalar fields use exact match, `string_list` fields use single-member membership filters. Use service summary for valid filter shapes."
- `aipcs_record_list`: "Can be bounded and branch-scoped; filters follow the same exact/membership semantics as search."

## Implementation Plan

1. Inspect existing discovery fields.
   - `src/aipcs_server/models.py`
   - `src/aipcs_server/bootstrap_dictionary.py`
   - `src/aipcs_server/registry.py`
   - `src/aipcs_server/record_store.py`
   - `src/aipcs_server/schema_types.py`
   - `src/aipcs_server/server.py`

2. Add typed retrieval-affordance models.
   - Add a reusable model such as `RetrievalAffordance`.
   - Add a compact bootstrap cue model such as `RetrievalAffordanceCues`.
   - Keep `mode` vocabulary stable: `exact`, `membership`, `annotation`.

3. Implement affordance extraction from schema and service stats.
   - Use schema attribute type and retrieval mode to classify fields.
   - Treat `string_list` as membership.
   - Treat known scalar filterable fields as exact.
   - Treat annotation/free-text fields as non-filterable.
   - Mark declared discovery facets.
   - Reuse existing facet counts and examples where available.

4. Add bootstrap cues.
   - Compute counts and booleans without reading record content values into bootstrap.
   - Add bounded preview entries only if compact and deterministic.
   - Ensure bootstrap still omits record samples, full attribute objects, full allowed values, and full schema detail.

5. Add service-summary retrieval affordances.
   - Surface concrete filter shapes in `aipcs_service_summary`.
   - Include membership examples using observed facet counts or schema allowed values where available.
   - Preserve existing `filter_modes`, `filter_examples`, and `facets` for compatibility.
   - Bound the affordance list if needed and expose truncation metadata.

6. Review record `_meta` duplication.
   - Keep `_meta` useful but compact.
   - Avoid repeating the full service-level affordance list per record.
   - Ensure returned `string_list` fields remain hydrated as lists.

7. Update docs and smoke checks.
   - README retrieval section.
   - Architecture index discovery section.
   - MCP smoke assertions for bootstrap cues and service-summary affordances.

8. Add tests.
   - Bootstrap exposes retrieval-affordance cues without record values.
   - Bootstrap preview, if implemented, is bounded and contains no observed values.
   - Service summary exposes exact and membership affordances with valid filter shapes.
   - Annotation/free-text fields are labelled non-filterable or excluded consistently.
   - Membership filter shape matches the actual accepted search/list payload.
   - Existing membership search/list tests still pass.
   - Payload boundary tests confirm bootstrap does not include full filter value inventories.

9. Validate.
   - Run lint, tests, harness validation, and MCP smoke.

## Acceptance Criteria

- [ ] Bootstrap exposes compact retrieval-affordance cues for each service.
- [ ] Bootstrap does not expose observed record values, samples, full schema details, or full filter value inventories.
- [ ] Materialised services with membership fields make that fact visible before record listing.
- [ ] `aipcs_service_summary` exposes first-class retrieval affordance objects with entity, field, mode, value shape, and valid filter shape.
- [ ] Membership fields show a filter shape such as `{"retrieval_tags": "science"}`, not serialized-list exact matching.
- [ ] Exact scalar fields show scalar exact filter shapes.
- [ ] Annotation/free-text fields are clearly non-filterable or omitted from query affordances.
- [ ] The service-summary affordance list is deterministic and bounded if necessary.
- [ ] Existing `filter_modes`, `filter_examples`, and `facets` remain backward-compatible unless intentionally deprecated.
- [ ] Record `_meta` remains compact and does not become the primary discovery path.
- [ ] Tests cover exact, membership, and annotation/free-text affordance classifications.
- [ ] Existing validation and MCP smoke pass.

## Validation

Run in `aipcs-server`:

```bash
.venv/bin/ruff check .
.venv/bin/pytest
.venv/bin/python scripts/validate-harness.py
.venv/bin/python scripts/mcp-smoke.py
```

Suggested behavioral smoke:

```text
1. Create a materialised service with:
   - entry_type: string scalar facet
   - retrieval_tags: string_list facet
   - interpretive_note: annotation/free-text
2. Create records with several entry_type and retrieval_tags values.
3. Call aipcs_bootstrap.
4. Confirm bootstrap says exact and membership filters exist, without exposing values such as "science".
5. Call aipcs_service_summary.
6. Confirm retrieval_affordances includes:
   - entry_type exact scalar filter shape
   - retrieval_tags membership filter shape
   - interpretive_note as annotation/free-text or omitted from query affordances
7. Call aipcs_record_search with the advertised exact filter shape.
8. Call aipcs_record_search with the advertised membership filter shape.
9. Confirm both return expected records.
```

## Risks

| Risk | Mitigation |
|---|---|
| Bootstrap grows again | Use booleans/counts and tiny field-name previews only; no values, samples, or full schema objects. |
| Affordance objects duplicate existing fields | Treat existing `filter_modes`/`filter_examples` as compatibility fields; use first-class affordances as the agent-facing contract. |
| Agents overuse tags | Present membership as one mode beside exact facets and branch scoping, not as universal search. |
| Server starts inferring domain semantics | Classify only from schema-declared types, facets, retrieval modes, and mechanical counts. |
| Examples leak content into bootstrap | Keep examples in service summary only; bootstrap may say examples are available. |
| Service summary becomes too large | Bound affordance entries and expose truncation; preserve `service_inspect` and record retrieval for deeper work. |
| Tool descriptions remain insufficient | Keep short docstring hygiene but rely on structured response fields as the real contract. |

## Open Questions

- Should bootstrap include a tiny field-name preview, or only booleans/counts?
- Should annotation/free-text fields appear in `retrieval_affordances` as `mode=annotation`, or should query affordances only include filterable fields?
- What cap is appropriate for service-level retrieval affordances: 25, 50, or all fields for a normal schema?
- Should `retrieval_affordances` eventually replace `filter_modes`/`filter_examples`, or remain an agent-facing wrapper around them?

## Progress Log

| Date | What happened |
|---|---|
| 2026-06-24 | Slice drafted after Slice 02 review and discussion of run027 membership-affordance failure. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Keep retrieval affordances structured rather than docstring-heavy | Agents need the contract at runtime, and tool descriptions are too small and static to carry service-specific query shapes. |
| Keep bootstrap value-free | The slim-bootstrap lesson remains valid; bootstrap should signal that query affordances exist, not return data. |
| Make service summary authoritative for query shapes | `aipcs_service_summary` is the right tier after bootstrap and before record retrieval. |

---
