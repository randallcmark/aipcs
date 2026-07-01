# Execution Plan: aipcs-server Slice 04 - Authority, Provenance, And Staleness

**Status:** Draft
**Owner:** Agent
**Created:** 2026-06-24
**Last updated:** 2026-06-24
**Target repo:** `/Users/markrandall/GitHub/aipcs-server`
**BUILD_JOURNAL entries:** Add one when this slice is accepted or implemented

---

## Goal

Make authority, provenance, staleness, lifecycle status, scope, and supersession normal first-class memory conventions so agents can reason about conflicting or stale records without each schema inventing the same pattern from scratch.

The outcome should be:

- agents receive a clear convention for authority-related fields during bootstrap and schema design;
- service summaries identify which entities support authority/provenance/staleness semantics;
- record responses enrich convention fields into compact `_meta.authority` and `_meta.staleness` objects;
- conflict and stale-memory reasoning becomes a normal retrieval pattern, not an optional ad hoc schema trick.

## Non-Goals

- Do not make one global mandatory record schema.
- Do not force every entity to include every authority field.
- Do not hard-code a universal weighting policy such as "newest always wins" or "user-stated always wins."
- Do not infer provenance or authority from prose.
- Do not silently rewrite agent-authored status, confidence, or source fields.
- Do not add destructive schema migration.
- Do not add semantic deduplication, embeddings, or automated conflict resolution.
- Do not require hosted/product compliance features such as legal hold, policy deletion, or immutable audit ledgers in this slice.

## Context

The authority/conflict experiment runs were among the strongest evidence for AIPCS. Agents retrieved conflicting records and weighed recency, provenance, status, scope, and clarity instead of blindly preferring the newest record or the most confident-looking one.

This behavior is central to dogfooding. Long-lived memory will accumulate:

- stale project plans;
- superseded decisions;
- duplicate summaries;
- imported material with different authority than user-stated facts;
- inferred preferences that should be weaker than explicit corrections;
- narrow-scope facts that should not generalise globally;
- records that were once valid but now expired.

Earlier work already established partial conventions:

- provenance fields are durable data, not server inference;
- relative age should be computed at retrieval time rather than stored;
- stale-memory repair is a first-class evaluation behavior;
- authority boundaries between services matter because duplicate summaries can drift.

Slice 04 turns those lessons into a normal server-supported convention surface.

Relevant prior evidence:

- authority/conflict runs: agents correctly reasoned over provenance, recency, clarity, status, and scope;
- live stale-memory repair: agents detected and updated/deleted stale persisted records;
- schema self-audit runs: agents identified duplicate-authority and lifecycle gaps;
- close-out evidence review: authority/provenance/staleness are part of durable memory quality.

Relevant earlier journal decisions:

- D015: provenance is schema convention; recency is retrieval-time metadata.
- D023: stale-memory repair is first-class evaluation behavior.
- D027: keep provenance/staleness weighting as conventions and hints, not fixed policy.

## Design Principle

Authority metadata should be **conventional and enriched**, not globally mandatory.

AIPCS should provide:

- stable recommended field names;
- stable value vocabularies where useful;
- detection of convention fields in service schemas;
- retrieval-time metadata enrichment;
- discovery cues that authority fields are available;
- validation only where the schema explicitly declares constraints.

AIPCS should not decide the truth for the agent. It should make the basis for judgment visible.

Authority metadata must also obey a strict payload discipline. The purpose is to make retrieval more useful, not to make every record heavy enough that agents avoid AIPCS.

Use three layers:

1. Bootstrap exposes authority **cues only**.
   - Show booleans and counts.
   - Do not enumerate every field or value.
   - Do not include record-level authority examples.

2. Service summary exposes the authority **contract once**.
   - Show which fields exist, which group they belong to, and how they can be filtered.
   - Put reusable explanation and retrieval guidance here rather than repeating it per record.

3. Record responses expose compact authority **values and computed enrichment only**.
   - Keep raw schema fields on the record as usual.
   - Avoid duplicating every convention field inside `_meta`.
   - Use `_meta.authority` and `_meta.staleness` for compact normalized signals and computed context such as expiry or relative age.

The design target is selective retrieval first. If agents can filter by `status`, `scope`, `provenance_type`, or supersession fields before listing, fewer records need to be returned and less authority metadata must be repeated.

## Recommended Convention Fields

These fields should be treated as a reusable authority profile for memory-like entities.

### Core Provenance

```text
provenance_type
provenance_source
provenance_note
```

Recommended `provenance_type` values:

```text
user_stated
agent_inferred
agent_observed
imported
derived
system_generated
```

Notes:

- `user_stated`, `agent_inferred`, `agent_observed`, and `imported` already exist as established convention values.
- `derived` is useful for summaries, cross-service views, and transformations.
- `system_generated` is useful for fixture data, migration notes, and server-created metadata records.
- The server should expose the vocabulary but not reject other values unless the schema declares allowed values.

### Source And Scope

```text
source_ref
source_kind
scope
scope_ref
```

Suggested values:

```text
source_kind: user | document | conversation | tool_observation | import | generated_fixture | external_reference
scope: global | project | service | branch | session | document | experiment | user_profile
```

Notes:

- Prefer `source_ref` over bare `source` to avoid ambiguity with `provenance_source`.
- `scope` is the retrieval-time warning label: a record may be true only for one project, branch, document, session, experiment, or user-profile context.
- `scope_ref` can hold a project id, branch slug, source document id, run id, or other domain-specific pointer.

### Confidence And Lifecycle

```text
confidence
status
```

Suggested values:

```text
confidence: low | medium | high | confirmed
status: active | tentative | stale | superseded | retracted | archived
```

Notes:

- `confidence` is agent-authored and should not be treated as mathematical probability.
- `status` is lifecycle state, not truth by itself.
- The server can surface these fields and examples but should not interpret them as automatic exclusion rules unless a future explicit policy layer is added.

### Validity And Staleness

```text
valid_from
valid_until
staleness_hint
```

Suggested `staleness_hint` values:

```text
stable
review_periodically
time_sensitive
expires
volatile
```

Notes:

- `valid_until` can be enriched at retrieval time into `expired: true/false`.
- `staleness_hint` is agent-authored policy context, not computed fact.
- Relative age should continue to be computed from `created_at` / `updated_at` at retrieval time.

### Supersession

```text
supersedes
superseded_by
```

Suggested shapes:

- `supersedes`: `string_list` of record ids or stable external refs.
- `superseded_by`: `string_list` of record ids or stable external refs.

Notes:

- Start with convention fields rather than a new cross-record relationship table.
- If bidirectional maintenance becomes important, add helper behavior later.
- The first implementation should make supersession visible and queryable, not automatically consistent across arbitrary entities.

## Convention Profile

Add an authority convention profile to bootstrap-level conventions.

Example:

```json
"authority": {
  "purpose": "Expose provenance, status, scope, confidence, validity, and supersession signals for agent judgment.",
  "recommended_fields": {
    "provenance": ["provenance_type", "provenance_source", "provenance_note"],
    "source": ["source_ref", "source_kind"],
    "scope": ["scope", "scope_ref"],
    "confidence": ["confidence"],
    "lifecycle": ["status"],
    "validity": ["valid_from", "valid_until", "staleness_hint"],
    "supersession": ["supersedes", "superseded_by"]
  },
  "recommended_values": {
    "provenance_type": ["user_stated", "agent_inferred", "agent_observed", "imported", "derived", "system_generated"],
    "confidence": ["low", "medium", "high", "confirmed"],
    "status": ["active", "tentative", "stale", "superseded", "retracted", "archived"],
    "staleness_hint": ["stable", "review_periodically", "time_sensitive", "expires", "volatile"]
  },
  "policy": "Signals inform agent judgment; the server does not choose which record is authoritative."
}
```

Keep this compact enough for bootstrap. The convention object can be static; per-service support belongs in service cards and summaries.

## Bootstrap Requirements

Bootstrap service cards should include compact authority support cues when a schema is available.

Example:

```json
"authority_cues": {
  "has_provenance_fields": true,
  "has_source_fields": true,
  "has_scope_fields": true,
  "has_confidence_field": true,
  "has_status_field": true,
  "has_validity_fields": false,
  "has_supersession_fields": true,
  "authority_field_count": 8,
  "summary_has_authority_contract": true
}
```

Constraints:

- no record values in bootstrap;
- no per-record authority summaries;
- no conflict detection in bootstrap;
- no global ranking or weighting;
- no full attribute objects.

Purpose:

- help a cold agent decide whether to call `aipcs_service_summary` before answering conflict-sensitive questions;
- make authority support discoverable without requiring full schema inspection.

## Service Summary Requirements

`aipcs_service_summary` should identify authority support at service and entity levels.

At service level:

```json
"authority_profile": {
  "supported": true,
  "entities_with_authority_fields": ["decision", "memory_entry"],
  "field_groups": {
    "provenance": ["provenance_type", "provenance_source", "provenance_note"],
    "scope": ["scope", "scope_ref"],
    "confidence": ["confidence"],
    "lifecycle": ["status"],
    "validity": ["valid_until", "staleness_hint"],
    "supersession": ["supersedes", "superseded_by"]
  },
  "retrieval_guidance": [
    "Use status/scope/provenance filters before broad conflict-sensitive retrieval when available.",
    "Treat superseded/retracted/stale records as context unless the user asks for history.",
    "Use valid_until and updated-age metadata to judge whether a fact needs confirmation."
  ]
}
```

At entity level:

```json
"authority_fields": {
  "provenance_type": {"group": "provenance", "mode": "exact"},
  "scope": {"group": "scope", "mode": "exact"},
  "status": {"group": "lifecycle", "mode": "exact"},
  "valid_until": {"group": "validity", "mode": "exact"},
  "supersedes": {"group": "supersession", "mode": "membership"}
}
```

These fields should integrate with Slice 03 retrieval affordances:

- exact authority fields should appear as exact retrieval affordances;
- `supersedes` / `superseded_by` should appear as membership affordances when declared as `string_list`;
- annotation fields such as `provenance_note` should not be advertised as exact filters unless the schema makes them filterable.

## Record Response Enrichment

When convention fields are present, record retrieval responses should include compact `_meta` enrichment.

Example:

```json
"_meta": {
  "authority": {
    "provenance_type": "user_stated",
    "provenance_source": "conversation",
    "source_ref": "run015",
    "source_kind": "conversation",
    "scope": "experiment",
    "scope_ref": "run015",
    "confidence": "high",
    "status": "active",
    "supersedes": ["old-record-id"],
    "superseded_by": []
  },
  "staleness": {
    "updated_age_days": 14,
    "valid_until": "2026-07-01",
    "expired": false,
    "staleness_hint": "review_periodically"
  }
}
```

Notes:

- Existing relative age metadata should be reused or normalised rather than duplicated awkwardly.
- `expired` can be computed from `valid_until` at retrieval time.
- If `valid_until` is absent, do not invent expiry.
- If `status` is absent, do not invent status.
- If provenance fields are absent, omit or mark `authority.supported=false`.
- Do not mirror every authority convention field into `_meta` if the raw record already contains it.
- Prefer compact aliases or grouped signals in `_meta` when they save agent attention, for example `provenance`, `scope`, `status`, `confidence`, and `expired`.
- Put repeated explanations, vocabularies, and field inventories in service summary, not on every returned record.

## Schema Guidance Requirements

The server should make it easier for agents to include the authority profile in future schemas.

Possible implementation options:

1. Static convention guidance only.
   - Add the profile to bootstrap conventions and docs.
   - Lowest risk, but agents still manually copy fields.

2. Schema validation hints.
   - When a service appears memory-like and lacks authority fields, validation can emit non-blocking `schema_hints`.
   - Example: "Memory-like entities often benefit from provenance_type, status, scope, confidence, and supersession fields."

3. Optional schema template helper.
   - Add a helper in docs or a small function, not necessarily a new MCP tool.
   - The agent still chooses whether to apply it.

Recommended first implementation:

- implement static convention guidance;
- add non-blocking schema hints when memory-like schemas omit all authority fields;
- do not add a new MCP tool unless implementation pressure shows repeated contract confusion.

## Implementation Plan

1. Inspect existing provenance and metadata handling.
   - `src/aipcs_server/conventions.py`
   - `src/aipcs_server/bootstrap_dictionary.py`
   - `src/aipcs_server/record_store.py`
   - `src/aipcs_server/registry.py`
   - `src/aipcs_server/schema_validator.py`
   - `src/aipcs_server/models.py`

2. Define authority convention metadata.
   - Add recommended field names and value vocabularies.
   - Keep vocabulary non-binding unless schema declares enum/allowed values.
   - Prefer `source_ref` / `source_kind` over bare `source`.

3. Add schema-field detection helpers.
   - Detect authority fields by exact conventional names.
   - Group fields into provenance/source/scope/confidence/lifecycle/validity/supersession.
   - Detect filter mode for each field using existing exact/membership logic.

4. Add bootstrap authority cues.
   - Compute booleans/counts from schema only.
   - Do not inspect record values.
   - Add tests confirming values are not leaked.

5. Add service-summary authority profile.
   - Include service-level supported groups.
   - Include entity-level `authority_fields`.
   - Reuse Slice 03 retrieval affordance machinery where implemented.

6. Add record `_meta` enrichment.
   - Extract present convention fields from returned records.
   - Compute validity/expiry from `valid_until` when present.
   - Normalise relative age metadata into `staleness` if feasible without breaking compatibility.
   - Keep raw fields on the record unchanged.

7. Add non-blocking schema hints.
   - If an entity appears memory-like and has none of the authority fields, return a hint during design/evolve validation.
   - Hints must not reject schemas.
   - Do not require every table to include authority fields.

8. Update docs.
   - README retrieval/provenance section.
   - Architecture discovery section.
   - AI feature rules for authority conventions.
   - Smoke script assertions.

9. Add tests.
   - Bootstrap authority cues for a schema with convention fields.
   - Bootstrap omits record values such as actual source refs or statuses.
   - Service summary groups authority fields correctly.
   - Record list/get/search `_meta.authority` appears when fields are present.
   - `valid_until` produces `expired=true/false`.
   - Supersession `string_list` fields are hydrated and can be membership-filtered.
   - Schema hints appear for memory-like entities lacking authority fields but do not block acceptance.

10. Validate.
   - Run lint, tests, harness validation, and MCP smoke.

## Acceptance Criteria

- [ ] Bootstrap conventions include a compact authority/provenance/staleness profile.
- [ ] Bootstrap service cards expose compact authority support cues without record values.
- [ ] `aipcs_service_summary` identifies authority field groups at service and entity levels.
- [ ] Authority fields integrate with retrieval affordances where Slice 03 support exists.
- [ ] Record responses include compact `_meta.authority` when convention fields are present.
- [ ] Record responses include compact `_meta.staleness` / validity enrichment when temporal validity fields are present.
- [ ] `valid_until` is evaluated at retrieval time; stored relative age is not introduced.
- [ ] Supersession fields can be modelled as `string_list` and retrieved by membership.
- [ ] Memory-like schemas receive non-blocking hints when they omit all authority fields.
- [ ] Existing schemas without authority fields continue to work unchanged.
- [ ] No universal authority ranking policy is hard-coded.
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
1. Create a memory-like service with an entity containing:
   - provenance_type
   - provenance_source
   - source_ref
   - scope
   - confidence
   - status
   - valid_until
   - staleness_hint
   - supersedes as string_list
   - superseded_by as string_list
2. Materialise the service and create:
   - one active user_stated record;
   - one stale/superseded agent_inferred record;
   - one expired imported record.
3. Call aipcs_bootstrap.
4. Confirm authority cues are present without record values.
5. Call aipcs_service_summary.
6. Confirm authority_profile and authority_fields identify field groups and filter modes.
7. Call aipcs_record_search/list using status, scope, provenance_type, and supersedes membership filters.
8. Confirm returned records include _meta.authority and _meta.staleness.
9. Confirm expired record has expired=true.
```

## Risks

| Risk | Mitigation |
|---|---|
| Authority profile becomes a mandatory global schema | Keep fields conventional and optional; use hints, not rejection. |
| Agents over-trust metadata mechanically | Expose policy text that signals inform judgment; do not hard-code ranking. |
| `source` naming conflicts with existing `provenance_source` | Prefer `source_ref` and `source_kind`; preserve existing provenance fields. |
| Bootstrap grows too much | Include booleans/counts only; no values or examples. |
| Supersession consistency becomes hard | Start with queryable convention fields; defer automatic bidirectional repair. |
| Expiry logic becomes policy-heavy | Only compute whether `valid_until` is past; leave interpretation to agent/user. |
| Backward compatibility breaks existing services | Detect fields when present; omit metadata when absent. |
| Too many vocabularies over-prescribe agent schemas | Mark values as recommended conventions, not closed taxonomy unless schema declares allowed values. |

## Open Questions

- Should `status` include both `stale` and `superseded`, or should `stale` be represented only through staleness metadata?
- Should `confidence=confirmed` be a confidence value, or should confirmation be represented by provenance/status?
- Should supersession eventually become a server-managed relationship table rather than convention fields?
- Should schema hints be limited to memory-like domain classes, or any entity with "memory", "decision", "preference", "profile", "note", or "context" names?
- Should `valid_until` accept date-only strings, datetime strings, or both?
- Should `provenance_source` and `source_ref` both be recommended, or is that too much surface area for agents?

## Progress Log

| Date | What happened |
|---|---|
| 2026-06-24 | Slice drafted after discussion of authority/conflict runs and dogfooding requirements. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Use conventions and enrichment rather than mandatory global fields | Preserves agent-authored schemas while making common memory-quality dimensions discoverable. |
| Prefer retrieval-time staleness computation | Stored relative age becomes stale immediately; `valid_until` can be evaluated when records are retrieved. |
| Start supersession as convention fields | Queryable fields are enough for dogfooding; automatic relationship maintenance can follow after evidence. |

---
