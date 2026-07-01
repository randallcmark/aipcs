# Execution Plan: aipcs-server Slice 01 - Richer Memory Dimensionality

**Status:** Draft
**Owner:** Agent
**Created:** 2026-06-24
**Last updated:** 2026-06-24
**Target repo:** `/Users/markrandall/GitHub/aipcs-server`
**BUILD_JOURNAL entries:** Add one when this slice is accepted or implemented

---

## Goal

Add a generic intermediate memory-branch layer to `aipcs-server` so long-lived services can organise persisted records with more granularity than `service -> entity -> record`.

The intended topology becomes:

```text
service -> memory_branch -> entity -> record
```

This should reduce broad scans, reduce pressure toward large prose-blob records, and give future agents a more legible map of a service's internal memory shape.

The branch layer must also support **retroactive organisation**. An agent should be able to start with a simple service/entity shape and later insert branch topology above existing records when the memory has grown enough that retrieval pressure is visible.

## Non-Goals

- Do not build a graph database.
- Do not require every record to belong to a branch.
- Do not introduce a fixed global taxonomy of branch types.
- Do not solve full-text search, fuzzy search, embeddings, or cross-service search in this slice.
- Do not merge services automatically.
- Do not introduce destructive migrations.
- Do not literally transform an entity table into a branch. Branches are topology metadata layered above records, not replacements for entity schemas.
- Do not require existing materialised services to be manually migrated before they remain usable.

## Context

This slice comes from repeated live-agent experiment feedback:

- Flat memory shapes encouraged broad retrieval and large records.
- Heterogeneous service topologies remained usable but required scratch-work and broad extraction.
- Agents needed more discovery structure than entity names and record counts, but bootstrap still needed to remain compact.
- The older `aipcs-server/docs/design/user-memory-schema-dimensions.md` proposal identified useful topical, temporal, and relational axes, but only for one `user_memory` entity. This slice generalises that insight into a server-level topology primitive.

Relevant current implementation positions in `aipcs-server`:

- `aipcs_bootstrap` returns compact service cards and must remain slim.
- `aipcs_service_summary` is the middle-tier discovery tool and can expose richer service structure.
- `aipcs_service_inspect` remains the full schema/manifest inspection tool.
- Record tools are generic across arbitrary materialised service entities.
- Schema evolution is additive-only.
- Server-managed fields are protected from agent writes.

## Design Principle

Memory branches are **AIPCS topology metadata**, not ordinary domain schema attributes.

Agents should own the branch names, intent, summaries, and organisation, but branches should be managed by the server in a consistent way across all services. This avoids forcing each service schema to reinvent `topic`, `phase`, `collection`, `source`, `thread`, or `scope` fields differently.

The distinction to teach agents is:

```text
Entities describe record shape.
Branches describe retrieval scope, topic, phase, source, or collection.
```

For example, a service may start with one entity:

```text
service: project_memory
entity: implementation_note
```

Later, when the service contains many notes, the agent can add branches without rewriting the entity schema:

```text
branch: bootstrap-discovery
branch: schema-evolution
branch: experiment-harness
entity: implementation_note
```

Existing `implementation_note` records can then be assigned to branches. This is the preferred interpretation of "promoting" a flat concept into a richer memory shape: the entity table is not converted into a branch; branch topology is inserted above relevant records.

## Proposed Data Model

Create server-managed topology tables in each materialised service database.

Preferred table names:

```text
_aipcs_memory_branch
_aipcs_record_branch
```

These names should be reserved and rejected as normal agent-defined entity names.

### `_aipcs_memory_branch`

```text
id                text primary key
owner_id          text not null
slug              text not null
title             text not null
intent            text not null
branch_type       text null
parent_branch_id  text null
status            text not null default 'active'
retrieval_summary text null
created_at        text not null
updated_at        text not null
```

Constraints:

- Unique per owner/service: `(owner_id, slug)`.
- `status` should initially allow `active`, `archived`, and `superseded`.
- `parent_branch_id` is optional. The slice may store it without building deep traversal features.
- `branch_type` is free text in v1. Do not enforce a taxonomy.

### `_aipcs_record_branch`

```text
owner_id     text not null
entity_name  text not null
record_id    text not null
branch_id    text not null
role         text not null default 'primary'
created_at   text not null
```

Constraints:

- Unique mapping for primary assignment: `(owner_id, entity_name, record_id, role)` where `role = 'primary'`.
- Initial allowed roles: `primary`, `related`.
- V1 can implement only `primary` if that materially reduces complexity, but the schema should not block later related assignments.

## Tool Surface

### New Tools

#### `aipcs_branch_create`

Create a memory branch inside a materialised service.

Inputs:

```text
service_id
slug
title
intent
branch_type optional
parent_branch_id optional
parent_branch_slug optional
retrieval_summary optional
```

Rules:

- The service must be materialised.
- `slug` must be unique within the service for the owner.
- If both `parent_branch_id` and `parent_branch_slug` are supplied, they must resolve to the same branch.
- Branch creation writes an audit/history entry.

#### `aipcs_branch_list`

List branches for one materialised service.

Inputs:

```text
service_id
status optional
branch_type optional
parent_branch_id optional
parent_branch_slug optional
include_counts optional default true
```

Output should include compact cards:

```text
id
slug
title
intent
branch_type
parent_branch_id
status
retrieval_summary
entity_counts
record_count
created_at
updated_at
```

#### `aipcs_branch_update`

Update branch metadata.

Inputs:

```text
service_id
branch_id or branch_slug
title optional
intent optional
branch_type optional
parent_branch_id optional
parent_branch_slug optional
status optional
retrieval_summary optional
```

Rules:

- Do not delete branches in this slice.
- `status=archived` is the preferred removal/deprecation path.
- Updating a branch does not mutate the records attached to it.

#### `aipcs_branch_assign_records`

Attach existing records to a memory branch.

Inputs:

```text
service_id
branch_id or branch_slug
entity_name
record_ids optional
filters optional
role optional default primary
replace_existing_primary optional default true
```

Rules:

- The service must be materialised.
- The branch must exist and belong to the same owner/service.
- The entity must exist in the service manifest.
- Either `record_ids` or `filters` must be supplied.
- `filters` must use the same structured filter semantics as `aipcs_record_list`/`aipcs_record_search`.
- When `replace_existing_primary=true`, existing primary branch assignments for matching records are replaced.
- When `replace_existing_primary=false`, assignments should use `role=related` or return a validation error if multiple primary branches would result.
- The tool should return matched record count, assigned count, and skipped/error details.
- This operation writes an audit/history entry.

This tool is the key retroactive-organisation primitive. It lets agents start simple and later say: "these existing records now belong under this branch."

### Existing Record Tool Changes

Add optional branch arguments to record creation and retrieval tools.

Affected tools:

```text
aipcs_record_create
aipcs_record_update
aipcs_record_list
aipcs_record_search
```

Proposed optional inputs:

```text
branch_id optional
branch_slug optional
branch_role optional default primary
```

Rules:

- If both `branch_id` and `branch_slug` are supplied, they must resolve to the same branch.
- `aipcs_record_create` with a branch attaches the new record to that branch.
- `aipcs_record_update` may change branch assignment when a branch argument is supplied.
- `aipcs_record_list` and `aipcs_record_search` filter records by branch when a branch argument is supplied.
- Records without a branch remain valid and retrievable.
- Listing/searching without a branch must preserve current behaviour and return all matching records.

Branch assignment during record creation is the forward path. `aipcs_branch_assign_records` is the retrospective path.

### Existing Discovery Tool Changes

#### `aipcs_bootstrap`

Keep bootstrap compact. Add only branch signals to service cards:

```text
branch_count
active_branch_count
recent_branches: [slug, title, updated_at] limited to a small deterministic count
branch_detail_available: true
next_tools may include summarize_or_list_branches_if_relevant
```

Bootstrap must not include full branch lists, full branch summaries, or record samples.

Bootstrap should include a compact concept hint, not a long example:

```text
Branches organise retrieval scope; entities define record shape. Add branches when one service grows multiple topics, phases, sources, or retrieval scopes.
```

#### `aipcs_service_summary`

Add a `branches` section with compact branch cards and counts.

Output should include:

```text
branches:
  - id
    slug
    title
    intent
    branch_type
    status
    retrieval_summary
    entity_counts
    record_count
    updated_at
```

The summary should also expose branch-aware filter examples, for example:

```text
record_list(entity_name="memory_entry", branch_slug="early-life")
record_search(entity_name="decision", filters={"status": "active"}, branch_slug="bootstrap-scalability")
```

`aipcs_service_summary` is the right place for richer branch examples because the agent has already selected one service and intentionally requested more detail. It may include a short multi-step example:

```text
1. Create a branch when a service outgrows one flat topic.
2. Assign existing records to the branch with aipcs_branch_assign_records.
3. Create future records with branch_slug so later retrieval can stay bounded.
```

#### `aipcs_service_inspect`

Inspect may include full topology metadata if useful, but the authoritative branch discovery path should be summary/list, not inspect.

## Implementation Plan

Each step should be feasible as a single implementation session in `aipcs-server`.

1. **Reserve topology table names**
   - Update schema validation so agent-defined entities cannot use `_aipcs_memory_branch` or `_aipcs_record_branch`.
   - Add tests for rejected entity names.

2. **Create topology table helpers**
   - Add idempotent helper(s) to ensure branch tables exist in a materialised service database.
   - Call this helper during materialisation for new services.
   - Also call lazily from branch and record operations so existing service databases remain backward compatible.

3. **Add branch models**
   - Add input/output models for branch create/list/update.
   - Keep required fields small: slug, title, intent.
   - Validate status values and slug format consistently with existing service/domain slugs.

4. **Add branch store logic**
   - Implement branch create/list/update in the persistence layer.
   - Include owner scoping on every query.
   - Include compact entity/record counts for list output.
   - Add audit/history entries using existing patterns.

5. **Expose branch MCP tools**
   - Add `aipcs_branch_create`, `aipcs_branch_list`, `aipcs_branch_update`, and `aipcs_branch_assign_records`.
   - Ensure descriptions are concise but explicit about branch purpose.
   - Add tool smoke coverage.

6. **Add retroactive branch assignment**
   - Implement `aipcs_branch_assign_records`.
   - Support assignment by explicit `record_ids`.
   - Support assignment by structured filters if the existing record-list/search path can be safely reused.
   - Return matched/assigned/skipped counts.
   - Preserve existing records and schemas; this is topology assignment, not record mutation.

7. **Add branch assignment to record create/update**
   - Resolve `branch_id` or `branch_slug` before mutation.
   - On create, attach the new record when a branch is supplied.
   - On update, change the primary branch assignment only when branch fields are supplied.
   - Preserve existing create/update behaviour when no branch is supplied.

8. **Add branch filters to record list/search**
   - Filter by branch without changing current scalar/list filter semantics.
   - Return branch metadata in response `_meta` where useful.
   - Ensure branch filtering composes with exact scalar filters and `string_list` membership filters.

9. **Update discovery output**
   - Add compact branch signals to bootstrap service cards.
   - Add branch cards, counts, and examples to `aipcs_service_summary`.
   - Avoid making bootstrap verbose again.

10. **Update docs and scripts**
   - Update README/tool list.
   - Update architecture retrieval position.
   - Add a short AGENTS/agent-rules note if the target repo has an appropriate agent guidance file: start simple, then add branches when a service develops multiple retrieval scopes.
   - Update any smoke/eval scripts that assert exact tool counts or bootstrap shape.

11. **Validation**
   - Run formatter/linter/tests.
   - Run MCP smoke script.
   - Run any deterministic harness validation.

## Acceptance Criteria

- [ ] Existing services without branch tables remain usable without manual migration.
- [ ] New materialised services get branch topology tables automatically.
- [ ] `aipcs_branch_create` creates a branch with owner scoping.
- [ ] `aipcs_branch_list` returns branch cards with record/entity counts.
- [ ] `aipcs_branch_update` updates branch metadata and status.
- [ ] `aipcs_branch_assign_records` can attach existing records to a branch by explicit IDs.
- [ ] `aipcs_branch_assign_records` can attach existing records to a branch by structured filters, or the implementation explicitly documents why filter-based assignment is deferred.
- [ ] `aipcs_record_create` can attach a record to a branch.
- [ ] `aipcs_record_update` can move a record to a branch when explicitly requested.
- [ ] `aipcs_record_list` can filter by branch.
- [ ] `aipcs_record_search` can combine branch filtering with existing structured filters.
- [ ] Records without branches remain valid and visible in normal list/search calls.
- [ ] Bootstrap remains compact and does not emit all branch details.
- [ ] `aipcs_service_summary` exposes branch-level retrieval affordances.
- [ ] Tests cover backward compatibility, invalid branch references, branch-scoped list/search, and reserved table names.
- [ ] Docs describe branches as AIPCS topology metadata, not normal domain schema.

## Validation

Exact commands should follow the `aipcs-server` repo conventions. Expected baseline:

```bash
.venv/bin/ruff check .
.venv/bin/pytest
.venv/bin/python scripts/validate-harness.py
.venv/bin/python scripts/mcp-smoke.py
.venv/bin/python -m aipcs_server --help
```

If the implementation changes script names or available validations, update this section in the target repo.

## Risks

| Risk | Mitigation |
|---|---|
| Bootstrap becomes verbose again | Put full branch detail in `aipcs_service_summary` and expose only compact branch signals in bootstrap. |
| Branches become a rigid taxonomy | Keep `branch_type` free text and agent-authored. Do not enforce global allowed values. |
| Branch metadata duplicates domain schema fields | Treat branches as retrieval topology, not source-of-truth domain facts. Domain entities may still contain their own thematic fields. |
| Existing databases break | Use idempotent lazy topology-table creation for existing materialised services. |
| Record tools become confusing | Keep branch arguments optional and preserve all current no-branch behaviours. |
| Agents overuse branches instead of evolving schemas | Service summary should frame branches as retrieval organisation, not a replacement for good entities and attributes. |
| Hierarchy creates complexity | Store optional parent IDs now, but do not implement recursive traversal beyond list/filter support in this slice. |
| Agents misunderstand branch promotion as destructive schema rewrite | Tool and summary guidance should say branches are inserted above existing records; entity schemas remain intact. |

## Open Questions For Implementation Session

1. Should branch lookup accept both `branch_id` and `branch_slug` everywhere, or should mutating tools require IDs after discovery?
   - Recommendation: accept both for agent ergonomics; reject if both are supplied and disagree.

2. Should `record_update` move a record between branches or only add a related branch?
   - Recommendation: implement primary branch replacement only for v1. Related branches can be added later if needed.

3. Should `aipcs_branch_assign_records` support filter-based assignment in v1?
   - Recommendation: yes if it can reuse existing structured filter paths safely. If not, implement `record_ids` first and document filters as a near-term follow-up.

4. Should unbranched records be represented as a synthetic branch in summaries?
   - Recommendation: show `unbranched_record_count`, but do not create a synthetic branch row.

5. Should branch tables live in the registry instead of per-service databases?
   - Recommendation: per-service databases. Branches are service-local topology and need to filter service records efficiently.

6. Should branch metadata be included in schema manifests?
   - Recommendation: no for v1. Branches are runtime memory topology, not schema. They should appear in summary/inspect output, not as manifest entities.

## Handoff Prompt For aipcs-server

Use this prompt when opening a fresh implementation session in `/Users/markrandall/GitHub/aipcs-server`:

```text
Implement the AIPCS Slice 01 richer memory dimensionality plan from:
/Users/markrandall/GitHub/aipcs/docs/exec-plans/active/aipcs-server-slice-01-memory-dimensionality.md

Follow the aipcs-server AGENTS.md instructions. Convert the slice into an active repo-local execution plan if appropriate, then implement the smallest coherent version that satisfies the acceptance criteria. Preserve backward compatibility for existing materialised services.
```

## Progress Log

| Date | What happened |
|---|---|
| 2026-06-24 | Draft handoff slice created from experiment findings and dogfooding requirements. |
