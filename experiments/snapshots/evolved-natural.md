# Snapshot: evolved-natural

## Purpose

Capture a naturalistically evolved agent memory store for recall, schema-rationale, and longitudinal comparison experiments.

## Source

- Source data directory: `/Users/markrandall/GitHub/aipcs-server/.data`
- Source date: 2026-05-19
- Created by: pending
- Sanitized: no

## Contents

| Service | State | Notes |
|---|---|---|
| `claude_memory` | materialised | Agent-created/evolved memory service with user, feedback, project, and reference entities. |
| `aipcs_development` | materialised | Project-state service with decisions, deferred items, implementation slices, open questions, and session records. |

## Expected Properties

- Contains agent-authored memory-policy records.
- Contains split user profile records after prose-blob cleanup.
- Contains mutation history showing memory schema and record evolution.
- Contains incomplete provenance backfill because provenance was added part-way through.

## Known Defects / Intended Stimuli

- Good for bootstrap/recall and schema-rationale scenarios.
- Not clean enough for objective baseline by itself; use as naturalistic corpus or copied fixture.

## Raw Artifact Location

```text
Not yet copied. Use a private per-run snapshot path outside git.
```

## Reproduction Notes

Copy the source data directory into a per-run `AIPCS_DATA_DIR`. Do not run experiments against the live source.
