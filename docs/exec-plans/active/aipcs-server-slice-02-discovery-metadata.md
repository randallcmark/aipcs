# Execution Plan: aipcs-server Slice 02 - Better Discovery Metadata

**Status:** Draft
**Owner:** Agent
**Created:** 2026-06-24
**Last updated:** 2026-06-24
**Target repo:** `/Users/markrandall/GitHub/aipcs-server`
**BUILD_JOURNAL entries:** Add one when this slice is accepted or implemented

---

## Goal

Improve AIPCS discovery metadata so a cold agent can decide which service or branch to inspect next without making bootstrap large again.

The outcome should be a compact recursive discovery path:

```text
bootstrap -> service_summary -> branch_list / branch-scoped record retrieval
```

Bootstrap remains a portfolio map. `aipcs_service_summary` and branch tools provide the next layer of selective detail.

## Non-Goals

- Do not return record content from bootstrap.
- Do not restore full schema detail, attribute descriptions, allowed-value lists, samples, or migration history to bootstrap.
- Do not add fuzzy search, semantic search, embeddings, or cross-service search.
- Do not infer hidden semantic facets from prose.
- Do not force a global taxonomy of service or branch types.
- Do not replace agent-authored schema/branch design with server-authored recommendations.
- Do not solve long-term ranking or learning from usage in this slice.

## Context

The experiment programme showed that discovery quality is part of the memory system, not UI polish.

Key findings:

- `run018`-`run021` showed bootstrap payload and orientation failures under service breadth, schema verbosity, and record volume.
- `run019b` showed slim bootstrap fixed payload friction but did not fully solve harsh service-selection cases.
- `run020b` showed schema verbosity was fixed enough for clean target retrieval.
- `run027` showed retrieval affordances can exist but still not be discovered or trusted by the agent.
- `closeout01b` showed heterogeneous service topology can work, but requires more broad retrieval and scratch-work when branch/service selection is weak.
- Slice 01 adds `memory_branch` topology. Slice 02 should make that topology discoverable without turning bootstrap into a content dump.

Relevant existing plans:

- `docs/exec-plans/active/slim-bootstrap-discovery.md`
- `docs/exec-plans/active/retrieval-affordance-legibility.md`
- `docs/exec-plans/active/aipcs-server-slice-01-memory-dimensionality.md`

Relevant current implementation position in `aipcs-server`:

- `aipcs_bootstrap` returns compact service cards.
- `aipcs_service_summary` returns middle-tier service discovery with entity cards, branch cards, facets, filter modes, examples, and optional samples.
- `aipcs_branch_list` returns branch cards and counts.
- Branch metadata is service-local retrieval topology.

## Design Principle

Discovery metadata should expose **selection cues**, not retrieved knowledge.

Selection cues help an agent decide:

- Is this service relevant?
- Is this branch likely relevant?
- Is there enough memory here to justify a follow-up call?
- Which tool should I call next?
- Which filter or branch scope should bound retrieval?

Selection cues must not become summaries of the underlying records. They should describe shape, purpose, scale, freshness, topology, and retrieval affordances.

## Discovery Tiers

### Tier 1: `aipcs_bootstrap`

Purpose: orient the agent to available memory services.

Bootstrap should answer:

- what services exist;
- what each service is for;
- whether each service is seeded, designed, materialised, empty, or populated;
- whether branch topology exists;
- whether facets/guidance exist;
- whether the service has recent activity;
- which follow-up tool is appropriate.

Bootstrap should not answer:

- what records say;
- full schema shape;
- full branch list;
- all facet counts;
- all retrieval examples;
- migration history.

### Tier 2: `aipcs_service_summary`

Purpose: inspect one candidate service before retrieval.

Service summary should answer:

- what branches exist in this service;
- what branches are active/archived/superseded;
- what entities exist and how many records they contain;
- what discovery facets and filter modes are available;
- what branch-level retrieval scopes are likely useful;
- what exact or membership filters are safe to use;
- whether broad listing is probably rational for the service size.

### Tier 3: Branch-Scoped Retrieval

Purpose: retrieve bounded records once the agent has selected a branch/entity/filter.

This tier uses existing branch-scoped record list/search calls. A separate `aipcs_branch_summary` may be considered if service summaries become too large, but it is not required for the first implementation unless branch cards are insufficient.

## Proposed Bootstrap Service Card Additions

Keep additions compact and bounded.

Suggested fields:

```text
summary_available: bool
selection_cues:
  schema_state: seeded | designed | materialised
  has_records: bool
  has_branches: bool
  has_active_branches: bool
  has_discovery_facets: bool
  has_retrieval_guidance: bool
  unbranched_record_count_bucket: none | low | medium | high
  record_count_bucket: none | low | medium | high
  freshness_label: empty | recent | warm | stale
next_tools:
  - aipcs_service_summary
  - aipcs_branch_list
  - aipcs_record_search
  - aipcs_record_list
  - aipcs_service_inspect
```

Notes:

- Buckets are preferable to exact high-cardinality detail in bootstrap.
- Existing exact `record_count` and `entity_count` can remain if already present, but avoid adding unbounded lists.
- `recent_branches` should remain tiny and deterministic if included.
- `selection_cues` should be machine-readable booleans/labels, not prose paragraphs.

## Proposed Service Summary Improvements

`aipcs_service_summary` should become the main branch-selection surface.

For each branch card, include:

```text
id
slug
title
intent
branch_type
status
retrieval_summary
entity_counts
record_count
updated_at
selection_cues:
  has_records
  record_count_bucket
  freshness_label
  primary_entities
```

At service level, include:

```text
branch_count
active_branch_count
archived_branch_count
superseded_branch_count
unbranched_record_count
branch_type_counts
entity_count
record_count
retrieval_guidance
discovery_facets
filter_modes
filter_examples
```

Add a compact `retrieval_plan_hints` section:

```text
retrieval_plan_hints:
  - if branch seems relevant, prefer branch-scoped list/search over whole-service listing
  - use exact filters for scalar fields shown in filter_examples
  - use membership filters for string_list fields shown as membership
  - use inspect only when full schema detail is needed
```

These hints should be generic and deterministic, not generated reasoning about record content.

## Branch Selection And Branch Summaries

First implementation should try to make `aipcs_service_summary` plus `aipcs_branch_list` sufficient.

Add `aipcs_branch_summary` only if implementation review finds that branch cards in service summary become too large or agents still lack enough detail.

If added later, `aipcs_branch_summary(service_id, branch_id|branch_slug, sample=0|n|"all")` should mirror service summary at a branch scope:

- entity counts within one branch;
- filter modes/examples within branch;
- optional samples only when explicitly requested;
- no bootstrap bloat.

## Metadata Ownership

Prefer agent-authored metadata where meaning matters:

- service intent;
- retrieval guidance;
- discovery facets;
- branch title;
- branch intent;
- branch type;
- branch retrieval summary.

Prefer server-computed metadata where shape matters:

- record counts;
- entity counts;
- branch counts;
- freshness labels;
- count buckets;
- available filter modes;
- filter examples from observed facet values or allowed values;
- whether records are branched/unbranched.

The server should not infer hidden themes from prose. It should expose the structure the agent has already authored.

## Payload Budget Rules

This slice must preserve the slim-bootstrap lesson.

Bootstrap:

- no record samples;
- no full branch lists beyond a tiny bounded recent-branch signal;
- no full entity attribute objects;
- no allowed-values expansion;
- no prose-heavy guidance;
- no migration history.

Service summary:

- bounded branch cards;
- bounded facet counts;
- bounded filter examples;
- optional samples only via `sample`;
- clear cap for `sample="all"`.

## Implementation Plan

Each step should be feasible as a focused implementation session in `aipcs-server`.

1. **Audit current bootstrap/service summary payloads**
   - Capture representative JSON sizes for no services, one service, many services, one service with many branches, and one service with many records.
   - Use existing run-shaped fixtures if available.

2. **Define selection cue models**
   - Add model fields for compact `selection_cues` on bootstrap service cards.
   - Add model fields for branch-level `selection_cues` on service summary branch cards.
   - Prefer enums/booleans over prose.

3. **Add count and freshness buckets**
   - Implement deterministic bucket helpers.
   - Suggested record-count buckets:
     - `none`: 0
     - `low`: 1-10
     - `medium`: 11-100
     - `high`: 101+
   - Suggested freshness labels should be deterministic and based on `last_activity_at`/`updated_at`, with no hidden semantic interpretation.

4. **Expose compact bootstrap selection cues**
   - Add booleans for branches, facets, guidance, and summary availability.
   - Add `next_tools` or refine existing affordance labels to make the recursive path explicit.
   - Keep existing bootstrap contract backward-compatible where practical.

5. **Improve service summary branch cards**
   - Add branch status counts and branch type counts.
   - Add branch-level selection cues.
   - Add unbranched counts prominently.
   - Ensure inactive branches are visible but clearly marked.

6. **Add retrieval plan hints to service summary**
   - Keep hints static and deterministic.
   - Make branch-scoped retrieval the natural path when branch topology exists.
   - Keep exact/membership filter semantics visible.

7. **Update docs and smoke/eval scripts**
   - Update README and architecture docs.
   - Update `scripts/mcp-smoke.py` to print/assert selection cues.
   - Update any eval fixtures that expect exact bootstrap/service summary shapes.

8. **Add tests**
   - Bootstrap service cards expose compact selection cues.
   - Bootstrap does not include branch lists beyond the bounded signal.
   - Service summary exposes branch status/type counts.
   - Service summary exposes unbranched count and branch selection cues.
   - Service summary hints recommend branch-scoped retrieval when branches exist.
   - Payload remains bounded in a synthetic many-branch/many-record fixture.

9. **Validate**
   - Run formatter/linter/tests.
   - Run harness validation.
   - Run MCP smoke.

## Acceptance Criteria

- [ ] Bootstrap remains compact and contains no record samples or full schema detail.
- [ ] Bootstrap service cards expose machine-readable selection cues for branches, facets, guidance, record scale, and freshness.
- [ ] Bootstrap makes the next discovery step explicit without prose bloat.
- [ ] Service summary exposes branch status counts, branch type counts, branch record counts, and unbranched record count.
- [ ] Service summary branch cards include compact selection cues.
- [ ] Service summary distinguishes exact, membership, and annotation/non-filter fields.
- [ ] Service summary gives branch-aware retrieval hints without inventing semantic recommendations.
- [ ] Inactive branches are visible as inactive and not hidden from discovery.
- [ ] Tests verify payload boundaries and compactness.
- [ ] Existing no-branch services still discover cleanly.
- [ ] Existing branch-enabled services discover cleanly.

## Validation

Expected commands in `aipcs-server`:

```bash
.venv/bin/ruff check .
.venv/bin/pytest
.venv/bin/python scripts/validate-harness.py
.venv/bin/python scripts/mcp-smoke.py
```

Optional payload checks should compare representative JSON character counts before/after this slice. Do not require exact byte equality in tests unless the project already has stable fixtures for it.

## Risks

| Risk | Mitigation |
|---|---|
| Bootstrap becomes heavy again | Enforce payload budget rules and put detail in service summary. |
| Selection cues become server reasoning | Keep cues mechanical: booleans, buckets, counts, freshness labels. Agent-authored meaning stays in intent/guidance/branch summaries. |
| Agents over-trust count/freshness buckets | Present buckets as retrieval-cost cues, not relevance scores. |
| Branch cards become too large | Add `aipcs_branch_summary` later if needed; do not overload bootstrap. |
| Tool surface becomes confusing | Keep recursive path explicit: bootstrap -> service_summary -> branch/list/search -> inspect only if needed. |
| Tests become brittle around payload shape | Test key fields and absence of prohibited content, not exact full JSON. |

## Open Questions For Implementation Session

1. Should bootstrap use a nested `selection_cues` object or flat fields?
   - Recommendation: nested object for clarity, while preserving existing flat fields for compatibility.

2. Should branch type counts include inactive branches?
   - Recommendation: include all by default, with separate status counts so agents can tell active from archived/superseded.

3. Should `next_tools` be a new field or should existing `affordances` be extended?
   - Recommendation: keep `affordances` for state labels and add `next_tools` for concrete tool names if this does not bloat output.

4. Should `aipcs_branch_summary` be added now?
   - Recommendation: no unless service summaries become too large in implementation. First try richer service summary branch cards.

5. Should freshness thresholds be configurable?
   - Recommendation: no for this slice. Use deterministic fixed thresholds and revisit after dogfooding.

## Handoff Prompt For aipcs-server

Use this prompt when opening a fresh implementation session in `/Users/markrandall/GitHub/aipcs-server`:

```text
Implement the AIPCS Slice 02 better discovery metadata plan from:
/Users/markrandall/GitHub/aipcs/docs/exec-plans/active/aipcs-server-slice-02-discovery-metadata.md

Follow the aipcs-server AGENTS.md instructions. Convert the slice into an active repo-local execution plan if appropriate, then implement the smallest coherent version that satisfies the acceptance criteria. Preserve the slim-bootstrap payload boundary: bootstrap should expose selection cues and next-step metadata, not records, full schemas, samples, or full branch lists.
```

## Progress Log

| Date | What happened |
|---|---|
| 2026-06-24 | Draft handoff slice created from bootstrap scalability and service-selection findings. |

