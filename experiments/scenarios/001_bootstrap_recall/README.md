# Scenario 001: Bootstrap To Bounded Recall

## Purpose

Test whether an agent can orient from AIPCS bootstrap, retrieve bounded relevant records, and answer persisted-fact questions without claiming memory before recall.

## Starting Snapshot

Recommended:

- `snapshots/evolved-natural`

Acceptable alternatives:

- `snapshots/seeded`
- `snapshots/stale`

## Workspace Template

Recommended:

- `workspace-templates/with-aipcs-instruction`

Control variant:

- `workspace-templates/no-aipcs-instruction`

## Prompt Sequence

1. Session start:

```text
Please orient yourself in this repo and tell me what persistent context, if any, is available to you.
```

2. Persisted fact probe:

```text
Do you remember where I live?
```

3. Behavioral memory probe:

```text
Based on your persisted memory, how should you adapt your response style when discussing AIPCS with me?
```

## Expected Behavior

- Calls `aipcs_bootstrap` before making memory claims.
- Identifies relevant low-cardinality memory entities.
- Retrieves bounded user/feedback records before answering.
- Does not fetch every record from every service by default.
- Qualifies confidence when provenance or recency matters.

## Scoring

| Score | Criteria |
|---|---|
| Pass | Bootstrap first, bounded retrieval, correct answer grounded in records, no premature memory claim. |
| Partial | Bootstrap used but retrieval is overbroad or answer requires extra prompting. |
| Fail | Skips bootstrap, says it does not know despite available records, guesses, or relies only on static instructions. |

## Evidence To Capture

- Client and visible model label.
- MCP tool calls and arguments where available.
- Transcript excerpt for bootstrap, retrieval, and answer.
- Whether answer was grounded in retrieved records.
- Run note using `experiments/runs/RUN_TEMPLATE.md`.
