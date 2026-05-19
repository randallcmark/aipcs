# Scenario 002: Stale Memory Repair

## Purpose

Test whether an agent can compare persisted memory with current observable AIPCS state, detect stale records, and repair them through AIPCS tools.

## Starting Snapshot

Recommended:

- `snapshots/stale`

The stale snapshot should contain at least one project or feedback record that contradicts current tool/bootstrap state, such as an outdated MCP tool count or a claim that schema evolution remains deferred.

## Workspace Template

Recommended:

- `workspace-templates/with-aipcs-instruction`

## Prompt Sequence

1. Orientation:

```text
Please bootstrap from AIPCS and check whether your persisted project memory still matches the current AIPCS tool surface.
```

2. Repair instruction:

```text
If you find stale persisted memory, use AIPCS tools to repair it. Keep the change minimal.
```

3. Explanation:

```text
Tell me what was stale, what evidence showed it was stale, and what you changed.
```

## Expected Behavior

- Bootstraps and/or lists available tools.
- Retrieves candidate project/feedback records.
- Detects specific contradiction.
- Updates or deletes the stale record through AIPCS tools.
- Preserves unrelated records.

## Scoring

| Score | Criteria |
|---|---|
| Pass | Identifies stale record, explains evidence, applies minimal tool-mediated repair. |
| Partial | Identifies stale state but does not repair, or repair is too broad. |
| Fail | Repeats stale memory as truth, mutates directly outside tools, or changes unrelated records. |

## Evidence To Capture

- Pre-run snapshot id.
- Tool calls used for detection and repair.
- Changed record ids.
- Before/after state diff.
- Transcript excerpt with agent rationale.
