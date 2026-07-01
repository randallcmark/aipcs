# Execution Plan: Retrieval Affordance Legibility

**Status:** Superseded — merged into `aipcs-server-slice-03-first-class-retrieval-affordances.md`
**Owner:** Agent
**Created:** 2026-06-13
**Last updated:** 2026-06-24
**BUILD_JOURNAL entries:** 097

---

## Supersession Note

This plan has been merged into `docs/exec-plans/active/aipcs-server-slice-03-first-class-retrieval-affordances.md`.

The original plan bundled several concerns:

- `string_list` hydration and membership filtering;
- service-summary filter examples;
- bootstrap routing toward service summary;
- record `_meta` retrieval metadata;
- MCP tool docstring hygiene.

Those concerns have since split naturally:

- structured membership filtering and hydration were implemented in earlier `aipcs-server` work;
- slim bootstrap and service-summary discovery were improved through Slice 02;
- remaining work is the narrower Slice 03 problem: make retrieval affordances first-class structured response objects so agents can discover exact and membership query contracts without inferring them from prose, raw record values, or tool descriptions.

Keep this file as historical context for `run027`; use Slice 03 for implementation.

## Goal

Make AIPCS tool contracts and structured retrieval semantics legible to agents at the moment of tool choice, so agents can familiarise themselves with AIPCS, progress through service lifecycle operations, and use schema-declared membership fields correctly without relying on prompt coercion.

## Non-Goals

- Do not add fuzzy search.
- Do not add semantic/vector search.
- Do not reinterpret existing comma-separated string fields as structured tags.
- Do not require agents to use membership filters when full retrieval is rational for a small corpus.
- Do not remove exact scalar filtering or change existing scalar equality semantics.
- Do not redesign the primitive tool API in this slice.
- Do not add generated domain-specific tools.

## Context

The structured membership-filter slice added support for schema-declared `string_list` fields and membership filtering. The backend can already answer filters such as:

```json
{"retrieval_tags": "science"}
```

when `retrieval_tags` is declared as a `string_list`.

However, `run027` showed an affordance failure:

- Claude bootstrapped AIPCS.
- It skipped `aipcs_service_summary`.
- It listed all records.
- It saw `retrieval_tags` values in returned records as JSON-encoded strings such as `["science", "state_critique"]`.
- It inferred, incorrectly, that exact-match filtering would be applied directly against the serialized string.
- It therefore concluded membership filtering was unusable, despite prior audit evidence that membership filtering works.

The next implementation slice should align storage semantics, record output representation, bootstrap guidance, and service-summary examples.

The same class of issue has appeared earlier in the experiment programme across service lifecycle operations. Agents have often needed multiple failed attempts before successful seed, design, materialise, evolve, create, or update operations. These failures usually come from unclear tool preconditions, server-managed fields, schema-managed fields, or operation payload shape. Because MCP tool discovery exposes tool name, input schema, and docstring, the docstrings are part of the first-contact contract and should be improved in this slice.

Relevant files:

- `experiments/runs/run027-targeted-membership-probe.md`
- `journal/BUILD_JOURNAL.md` Entry 096
- `docs/exec-plans/active/structured-membership-filters.md`

## Acceptance Criteria

- [ ] Record list/search/get responses hydrate schema-declared `string_list` values as JSON arrays/lists, not serialized JSON strings.
- [ ] Returned records preserve backward compatibility for ordinary string fields, including legacy comma-separated annotation tags.
- [ ] `aipcs_service_summary` exposes concise filter examples for filterable fields, including membership fields.
- [ ] `aipcs_service_summary` distinguishes exact, membership, and annotation/non-filter guidance clearly enough that an agent need not infer semantics from raw record values.
- [ ] Bootstrap next-step guidance more strongly routes agents to `aipcs_service_summary` before broad record listing.
- [ ] Record list/search/get responses include `_meta` or equivalent tool-level retrieval metadata for the entity, including available filter modes and at least one membership example where applicable.
- [ ] MCP tool docstrings state the lifecycle precondition for each tool where relevant.
- [ ] MCP tool docstrings identify whether payload fields are agent-supplied, schema-defined, or server-managed where ambiguity has caused failed calls.
- [ ] `aipcs_service_evolve` discovery text gives the expected operation-payload shape at a high level.
- [ ] Record create/update discovery text tells agents to submit only schema-defined domain fields; server-managed fields such as id, owner_id, created_at, updated_at, and _meta should normally be omitted.
- [ ] Design/materialise discovery text makes the service lifecycle order explicit: seed -> design -> materialise -> record operations -> evolve.
- [ ] Tests cover hydrated `string_list` output from create/list/get/search.
- [ ] Tests cover service-summary membership examples.
- [ ] Tests cover bootstrap next-step text or structured affordance output.
- [ ] Existing tests and smoke scripts pass.

## Plan

1. Inspect current implementation.
   - `src/aipcs_server/schema_types.py`
   - `src/aipcs_server/schema_validator.py`
   - `src/aipcs_server/record_store.py`
   - `src/aipcs_server/bootstrap_dictionary.py`
   - `src/aipcs_server/registry.py`
   - `src/aipcs_server/models.py`
   - `src/aipcs_server/tools.py`

2. Hydrate `string_list` outputs.
   - Keep SQLite storage as JSON text if that is the current implementation.
   - Decode schema-declared `string_list` fields when returning records through public tools.
   - Apply consistently to `record_create`, `record_get`, `record_list`, `record_search`, and `record_update` outputs.
   - Preserve raw storage and audit behavior unless changing audit output is necessary and tested.

3. Add filter examples to service summary.
   - Extend the service-summary entity metadata with per-field filter examples or a compact `filter_examples` map.
   - Example:

```json
{
  "filter_modes": {
    "primary_topic": "exact",
    "retrieval_tags": "membership"
  },
  "filter_examples": {
    "primary_topic": {"primary_topic": "theory"},
    "retrieval_tags": {"retrieval_tags": "science"}
  }
}
```

4. Strengthen bootstrap-to-summary affordance.
   - Keep bootstrap compact.
   - Make the next-step guidance explicit: use `aipcs_service_summary` before broad list/search when a service appears relevant.
   - If bootstrap service cards already include affordances, ensure relevant materialised services with records surface `summarize_before_listing_if_relevant` or equivalent wording.

5. Add record-response retrieval metadata.
   - Include entity-level `filter_modes` and concise `filter_examples` in response `_meta` where available.
   - This should help agents that skipped summary correct themselves after the first list/search/get call.
   - Keep metadata compact; do not duplicate full schema manifests.

6. Improve MCP tool discovery text.
   - Update Python docstrings in `server.py`; these are surfaced by MCP `list_tools`.
   - Keep descriptions concise, but include lifecycle preconditions and the most common repair hints.
   - Suggested direction:
     - `aipcs_service_seed`: first lifecycle step; creates a service marker, not a schema.
     - `aipcs_service_design`: requires a seeded service; schema should define domain entities/attributes and should not include server-managed record fields unless the manifest convention requires explicit declaration.
     - `aipcs_service_materialise`: requires an accepted schema; creates the local domain database.
     - `aipcs_service_evolve`: requires materialised service; additive operations only; use operation objects with the supported op names.
     - `aipcs_record_create`: requires materialised service/entity; send schema-defined domain fields; omit server-managed fields.
     - `aipcs_record_update`: update schema-defined mutable fields by record id; omit server-managed fields.
     - `aipcs_record_list/search`: filters are scalar exact or `string_list` membership; call summary first for filter examples.

7. Update docs.
   - README/tool docs should explain exact vs membership filtering.
   - Explicitly note that `string_list` values are returned as arrays even if stored internally as SQLite JSON text.
   - Keep fuzzy/text/semantic search deferred.

8. Add tests.
   - Existing membership positive/negative tests should remain.
   - Add tests asserting returned `string_list` values are lists, not strings.
   - Add tests for service-summary examples.
   - Add tests for `_meta` filter metadata on list/search/get responses if implemented.
   - Add lightweight tests or smoke assertions for docstring content if the project already tests tool registration metadata. If not, do not add brittle text tests solely for prose.

9. Validate.
   - Run lint, tests, harness validation, and MCP smoke.

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
1. Create a service with memory_entry.retrieval_tags as string_list.
2. Create record: retrieval_tags=["science", "state_critique"].
3. List/get the record and confirm retrieval_tags is returned as a JSON array/list, not a string.
4. Search/list with filters={"retrieval_tags": "science"} and confirm the record returns.
5. Call service_summary and confirm filter_modes shows retrieval_tags=membership and filter_examples includes {"retrieval_tags": "science"}.
```

## Risks

| Risk | Mitigation |
|---|---|
| Output hydration breaks audit or SQLite persistence assumptions | Keep storage unchanged; hydrate only at public tool boundary and test all public record outputs. |
| Metadata increases payload size too much | Keep examples compact and entity-level; avoid full schema duplication in record responses. |
| Agents overuse tags instead of better facets | Present membership as one mode alongside exact facets, not as the preferred universal mechanism. |
| Bootstrap becomes verbose again | Add stronger routing language, not record samples or full schema detail. |
| Backward compatibility ambiguity | Do not reinterpret legacy string fields; only schema-declared `string_list` fields receive membership semantics and list output. |
| Tool descriptions become too long for discovery | Keep docstrings short but operational: lifecycle precondition, payload ownership, and next-step hint. Put deeper examples in service summary or docs. |
| Docstring-only fixes fail to change behavior | Treat this as low-cost first-contact hygiene, then measure in the next clean corpus run. If failures persist, consider structured tool metadata or an explicit `aipcs_tool_guide` resource/tool later. |

---
