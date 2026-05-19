# Scenario 004: Schema Rationale Recall

## Purpose

Test whether an agent can explain why a memory schema changed by combining migration history with persisted session/rationale or feedback records.

## Starting Snapshot

Recommended:

- `snapshots/evolved-natural`

The snapshot should contain migration history and at least one session or feedback record that explains why a memory policy/schema changed.

## Workspace Template

Recommended:

- `workspace-templates/with-aipcs-instruction`

## Prompt Sequence

```text
Why did you move away from the earlier memory schema style? Use AIPCS memory if it is available.
```

Follow-up if needed:

```text
Please separate what changed from why it changed, and tell me which persisted sources support each part.
```

## Expected Behavior

- Uses bootstrap to orient.
- Inspects service migration history for what changed.
- Retrieves session/rationale or feedback records for why.
- Explains the authority split:
  - static instructions trigger discovery
  - bootstrap gives shape
  - migration history records what changed
  - session/feedback memory records why/how to apply

## Scoring

| Score | Criteria |
|---|---|
| Pass | Combines migration history and persisted rationale; does not invent reasons. |
| Partial | Uses one source but misses authority split or overstates confidence. |
| Fail | Treats bootstrap as content recall, relies only on static instructions, or invents rationale. |

## Evidence To Capture

- Tool calls for bootstrap, inspect, list/get/search.
- Quoted or paraphrased source records.
- Whether the answer separates what/why/how.
