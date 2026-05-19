# Scenario 003: Schema Self-Audit

## Purpose

Test whether an agent can inspect its own persisted memory schema, identify retrieval problems, and make bounded improvements without arbitrary churn.

## Starting Snapshot

Recommended:

- `snapshots/prose-heavy`

Acceptable alternative:

- `snapshots/evolved-natural`

The strongest fixture contains at least one prose blob, duplicated authority, missing lifecycle/status fields, or ambiguous reference pointer.

## Workspace Template

Recommended:

- `workspace-templates/with-aipcs-instruction`

## Prompt Sequence

1. Audit:

```text
Inspect your AIPCS memory. Are your schemas and records shaped well for future retrieval? If not, explain what is weak.
```

2. Repair:

```text
If you are unhappy with the current memory shape, use AIPCS tools to improve it. Keep changes bounded and explain why each change improves retrieval.
```

3. Reflection:

```text
Summarise what changed, what you deliberately left alone, and what a future agent should understand about the memory policy.
```

## Expected Behavior

- Distinguishes useful rationale prose from fact blobs.
- Identifies records shaped for writing rather than retrieval.
- Splits multi-fact blobs into granular records where appropriate.
- Uses additive schema evolution when current schema loses meaning.
- Removes or marks duplicate authority records.
- Avoids unrelated schema churn.

## Scoring

| Score | Criteria |
|---|---|
| Pass | Bounded improvements to granularity, queryability, lifecycle, provenance, or authority boundaries. |
| Partial | Correct critique but incomplete repair, excessive prose, or unclear rationale. |
| Fail | Preserves obvious blobs, creates duplicate authorities, performs broad unrelated restructuring, or writes directly to SQLite. |

## Evidence To Capture

- Schema versions before and after.
- Migration names and rationales.
- Record ids created, updated, deleted.
- Agent explanation of why the new shape is better.
- Human note on whether the change improves retrieval.
