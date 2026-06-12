# Execution Plan: Slim Bootstrap Discovery

**Status:** Implemented — Awaiting Lab Rerun
**Owner:** Agent
**Created:** 2026-06-11
**Last updated:** 2026-06-11
**BUILD_JOURNAL entries:** 082, 083, 084

---

## Goal

Refactor AIPCS discovery so `aipcs_bootstrap` is a compact recursive memory map, with deeper schema and content discovery moved to explicit follow-up calls.

## Non-Goals

- Do not redesign record dimensionality in this slice.
- Do not add graph storage, semantic search, background extraction, or background facet generation.
- Do not make bootstrap return record content by default.
- Do not optimise every record retrieval path; this slice focuses on discovery/orientation.
- Do not remove `aipcs_service_inspect`; it remains the full-detail schema tool.

## Context

- `run018`-`run021` showed current bootstrap scales poorly as a discovery layer.
- `run019` missed target services under service breadth.
- `run020` showed schema verbosity can produce a bootstrap around 437K characters, forcing file/grep-style use.
- `run021` showed record volume can lead the agent to stop at orientation and propose retrieval rather than perform it.
- The organic media-recommendation transcript showed a similar failure: Claude used `media_learning` but missed `personal_preferences` because orientation was too heavy.

Relevant docs:

- [Architecture index](../../architecture/index.md)
- [Bootstrap scalability summary](../../../experiments/runs/run018-run021-bootstrap-scalability-summary.md)
- [Experiment class plan](../../references/experiment-class-plan.md)

## Requirements

### R001 — Bootstrap Is A Recursive Map

`aipcs_bootstrap` must answer:

- what memory branches exist
- why they exist
- how rich they are
- whether they are empty, seeded, materialised, or populated
- where an agent should inspect next if relevant

It must not try to make the agent fully understand every service.

### R002 — Seeded Services Remain Visible

Seeded-but-empty services are intentional memory branches. Bootstrap must include them with enough signal for future reflection:

```json
{
  "domain_name": "technical_knowledge",
  "state": "seeded",
  "intent": "Reusable technical knowledge and gotchas",
  "schema_state": "not_materialised",
  "record_count": 0,
  "next_action": "design_schema_if_relevant"
}
```

### R003 — No Full Attribute Objects In Bootstrap

Bootstrap must not include full attribute objects by default:

- no full field descriptions
- no full allowed-value lists
- no migration history
- no repeated schema prose
- no provenance field blocks

Full schema detail belongs in `aipcs_service_inspect`.

### R004 — No Record Samples In Bootstrap By Default

Bootstrap returns no record samples by default.

Sampling is an explicit follow-up discovery action, not part of base orientation.

### R005 — Add Service Summary Discovery

Add a middle-tier discovery call:

```text
aipcs_service_summary(service_id, sample=0 | n | "all")
```

Purpose:

- inspect one service more deeply than bootstrap
- expose entity cards, declared facets, key fields, counts, and retrieval affordances
- optionally include bounded samples when explicitly requested

This tool is the right home for optional samples. Bootstrap should remain cheap.

### R006 — Sample Semantics Are Explicit

For `aipcs_service_summary`:

- `sample=0`: shape only
- `sample=n`: return up to `n` representative records per entity
- `sample="all"`: return all records for the service, only when the agent explicitly asks

Avoid generic cursor/pagination in this slice. The discovery model is:

```text
bootstrap -> summary/sample -> deliberate record retrieval
```

If `sample="all"` would exceed a safety cap, the tool should return a clear error or require a separate explicit record retrieval call. Do not silently truncate.

### R007 — Agent-Declared Facets

Facets are agent-declared in schema/design or schema evolution, then mechanically counted by the server.

Example schema-level metadata:

```json
{
  "discovery_facets": ["category", "status", "source_type", "priority"]
}
```

The server may compute bounded counts over those declared fields:

```json
{
  "facets": {
    "status": {"active": 17, "stale": 2},
    "priority": {"high": 4, "medium": 12, "low": 3}
  }
}
```

The server should not infer semantic facets from prose. The agent owns meaning; the server aggregates declared structure.

### R008 — Facets Are Evolvable

Agents must be able to change discovery facets as memory patterns evolve.

Facet updates may be implemented as part of `aipcs_service_evolve` or as a dedicated metadata update tool if that is cleaner:

```text
aipcs_service_update_discovery(service_id, discovery_facets, retrieval_guidance)
```

The first implementation should prefer the smaller change surface unless evolution semantics become awkward.

### R009 — Deterministic Affordance Labels

Bootstrap and summary responses should include deterministic labels for obvious next actions:

| State | Suggested affordance |
|---|---|
| seeded, no schema | `design_schema_if_relevant` |
| materialised, zero records | `create_record_if_relevant` |
| materialised, records exist | `search_or_sample_if_relevant` |
| schema detail needed | `inspect_schema_if_relevant` |

These are not dynamic recommendations. They are stable affordance labels that make tool use easier.

### R010 — Retrieval Guidance Is Agent-Authored Or Schema-Derived

Retrieval guidance should come from:

- agent-authored schema/query patterns
- declared discovery facets
- indexed/filterable fields
- service intent

It should not be hidden server interpretation.

Example:

```json
{
  "retrieval_guidance": "Search preference.category and status before listing all preferences."
}
```

### R011 — Freshness, State, And Scale Are Always Visible

Bootstrap service cards must expose:

- service id
- domain name
- domain class
- state
- schema state
- one-line intent
- record count
- entity count
- last activity
- materialised time when available
- whether detail is available
- suggested affordance labels

### R012 — Deterministic Utility Ordering

Bootstrap ordering should be deterministic and generally utility-biased:

1. materialised services with records
2. more recent activity
3. record-count bucket
4. materialised zero-record services
5. seeded services without schema
6. domain name as final tie-break

The response should expose the ordering basis so the agent understands what the map is optimising for.

### R013 — Search Stays Available But Not Primary Discovery

Search remains available for deliberate retrieval.

The discovery path should make targeted inspect/search natural enough that the agent does not default to broad search or grep-like workflows.

## Proposed Response Shapes

### Bootstrap Service Card

```json
{
  "service_id": "uuid",
  "domain_name": "personal_preferences",
  "domain_class": "user",
  "state": "materialised",
  "schema_state": "materialised",
  "intent": "Durable user preferences and defaults",
  "record_count": 37,
  "entity_count": 1,
  "last_activity_at": "2026-06-09T20:15:44Z",
  "entities": [
    {
      "name": "preference",
      "record_count": 37
    }
  ],
  "affordances": [
    "search_or_sample_if_relevant",
    "inspect_schema_if_relevant"
  ],
  "detail_available": true
}
```

### Service Summary

```json
{
  "service_id": "uuid",
  "domain_name": "personal_preferences",
  "intent": "Durable user preferences and defaults",
  "entities": [
    {
      "name": "preference",
      "record_count": 37,
      "key_fields": ["category", "polarity", "strength", "status"],
      "discovery_facets": ["category", "status", "source"],
      "facets": {
        "category": {"entertainment": 12, "food": 8},
        "status": {"active": 17, "stale": 2}
      },
      "retrieval_guidance": "Search category/status before listing all preferences.",
      "sample": []
    }
  ]
}
```

## Acceptance Criteria

- [x] `aipcs_bootstrap` no longer includes full attribute objects by default.
- [x] Seeded, materialised-empty, and populated services all appear in bootstrap with correct state/affordance labels.
- [x] Bootstrap payload for `run019`-shape store is small enough to return inline rather than being written to a file by Claude Code in local measurement.
- [x] Bootstrap payload for `run020`-shape store is dramatically smaller than the observed ~437K payload.
- [x] A service-level summary tool exists or equivalent follow-up discovery path is implemented.
- [x] Service summary exposes declared facets and mechanical counts where configured.
- [x] Facets can be added or changed through service evolution or a metadata update tool.
- [x] Full schema detail remains available through `aipcs_service_inspect`.
- [x] Existing record CRUD behavior is unchanged.
- [ ] Rerun `run019` and `run020` variants show reduced payload friction and improved target-service selection.

## Plan

1. Inspect current `aipcs_bootstrap`, `aipcs_service_inspect`, service registry, and schema manifest code in `aipcs-server`.
2. Add a compact bootstrap serializer that emits service cards only.
3. Preserve full schema serialization under `aipcs_service_inspect`.
4. Add `aipcs_service_summary` or equivalent summary method.
5. Add schema metadata support for `discovery_facets` and optional retrieval guidance.
6. Add mechanical facet-count computation for declared fields.
7. Add affordance-label derivation from service state and counts.
8. Add or update deterministic tests for seeded/materialised/populated services.
9. Rerun synthetic bootstrap scalability fixtures, especially `run019` and `run020`.
10. Update docs and journal with before/after payload and behavior results.

## Progress Log

| Date | What happened |
|---|---|
| 2026-06-11 | Created slice from run018-run021 evidence and design discussion. |
| 2026-06-11 | Implemented in `aipcs-server`; local validation passed and run-shaped payload checks dropped to 17,262 chars for `run019` shape and 6,188 chars for `run020` shape. Awaiting full lab reruns. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| No record samples in bootstrap by default | Keeps bootstrap a cheap map rather than a content retrieval tool. |
| Samples belong in service summary | Lets agents deepen discovery deliberately without making every session pay the cost. |
| Facets are agent-declared and server-counted | Preserves agent ownership of meaning while avoiding drift-prone manual facet maintenance. |
| No pagination/cursor in first slice | The desired model is recursive discovery, not generic API pagination. |
| Stable utility ordering | Makes bootstrap deterministic while surfacing likely useful branches first. |

## Validation

```bash
bash scripts/validate-harness.sh
```

Implementation validation should also run in `aipcs-server`:

```bash
.venv/bin/ruff check .
.venv/bin/pytest
.venv/bin/python scripts/validate-harness.py
.venv/bin/python scripts/mcp-smoke.py
.venv/bin/python -m aipcs_server --help
```

Behavioral validation:

```bash
# rerun run019-shape and run020-shape stores after slim bootstrap lands
# using experiments/runbooks/run018-to-run023-bootstrap-scalability.md
```

## Risks

| Risk | Mitigation |
|---|---|
| Bootstrap becomes too thin and agents miss relevant services | Include one-line intent, entity names/counts, state, freshness, record counts, and declared facets in service summary. |
| Samples reintroduce content dumps | Keep samples out of bootstrap; make sample explicit in service summary. |
| Facet fields drift or become stale | Compute counts mechanically from agent-declared fields. |
| Over-prescribing next actions reduces agent agency | Use deterministic affordance labels, not server-inferred recommendations. |
| Slim bootstrap hides schema detail needed for tool calls | Keep `aipcs_service_inspect` as explicit full schema retrieval. |
