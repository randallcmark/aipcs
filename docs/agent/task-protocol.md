# Task Protocol

## When to create an execution plan

Create a plan in `docs/exec-plans/active/` when the task:
- Spans more than one subsystem or file area
- Requires decisions that will be hard to reverse
- Is likely to take more than one session
- Has unclear acceptance criteria

Use the [template](../exec-plans/template.md).

## Intake

Before starting any non-trivial task:
- What is the concrete outcome? (not "improve X" — "X now does Y")
- Which files or subsystems are involved?
- What does the BUILD_JOURNAL say about related decisions?
- What validation commands will confirm success?
- Does this need an execution plan?

## Implementation

- Prefer existing patterns — check the journal and architecture docs before inventing
- Keep changes scoped — don't fix things you weren't asked to fix
- Add a BUILD_JOURNAL entry for any decision made during implementation
- Update architecture docs if the pattern or system design changes
- Don't leave the harness in a broken state

## Completion

- Run `bash scripts/validate-harness.sh`
- Report: what changed, what was decided, what's next
- Move the execution plan from `active/` to `completed/` if applicable
- Check [docs/quality/technical-debt.md](../quality/technical-debt.md) — did you resolve or reveal any debt?
