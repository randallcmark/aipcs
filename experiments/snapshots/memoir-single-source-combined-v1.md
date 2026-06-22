# Snapshot: memoir-single-source-combined-v1

Date: 2026-06-17

Purpose: Combined AIPCS corpus made by merging five independently agent-authored single-source memoir corpora into one data store.

Inputs:
- `kropotkin-clean-affordance-v1`
- `gandhi-agent-authored-v1`
- `washington-agent-authored-v1`
- `henry-adams-agent-authored-v1`
- `craft-agent-authored-v1`

Generation rule:
Each input corpus was generated independently from a public-domain Standard Ebooks source. Agents were allowed to choose service, schema, entity, and retrieval structure for each source. This combined snapshot preserves those independently authored structures rather than normalising them into a shared schema.

Observed structure:
- `kropotkin_biography`: 56 domain records across `life_phase`, `key_moment`, `person`, and `theme`
- `gandhi_autobiography`: 58 domain records in `entry`
- `btw_biography`: 39 domain records in `memory`
- `henry_adams_biography`: 35 domain records across `person` and `note`
- `craft_narrative_memory`: 34 domain records across `person`, `formative_event`, `relationship`, `encounter`, `theme`, `interpretive_note`, and `source_note`

Total domain records: 222.

Expected use:
- Multi-service retrieval pressure tests.
- Cross-subject comparative essay tests.
- Service/entity selection tests.
- False-positive and near-miss memory probes.
- Evaluation of whether agents use authored schemas naturally when broad listing becomes less attractive.

Owner:
Generated locally as owner `mark`. Lab imports must rewrite `owner_id` to `lab` and registry endpoints to `/data/services/...`.

Implementation note:
Created with `scripts/combine-aipcs-snapshots.py`, which merges registry service rows and copies service databases without altering the per-service schemas.
