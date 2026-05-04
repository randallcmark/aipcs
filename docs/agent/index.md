# Agent Operating Index

This is the operating reference for agents working in this repository.

## Principles

- The BUILD_JOURNAL is the primary narrative record — every decision and milestone belongs there
- Harness docs are the reference layer — durable rules and context that don't change with every entry
- AIPCS is a pattern, not a product — don't apply consumer software thinking to a research project
- Paper first — every observation during the build is potential paper material; capture it
- Small coherent changes — prefer targeted edits over broad refactors
- Improve the harness when stuck — friction is signal that context is missing

## Task Routes

| Task type | Start with |
|---|---|
| Understand the project | [../product/research-brief.md](../product/research-brief.md) |
| Architecture / pattern work | [../architecture/index.md](../architecture/index.md) |
| AI pattern rules | [ai-feature-rules.md](ai-feature-rules.md) |
| Security | [security-rules.md](security-rules.md) |
| Complex task | [task-protocol.md](task-protocol.md) |
| Paper work | [paper-rules.md](paper-rules.md) |
| Journaling | [../../journal/BUILD_JOURNAL.md](../../journal/BUILD_JOURNAL.md) |
| Validation | [validation.md](validation.md) |
| Doc maintenance | [doc-maintenance.md](doc-maintenance.md) |
| Quality / debt | [../quality/technical-debt.md](../quality/technical-debt.md) |

## Default Workflow

1. Clarify the task by reading the smallest relevant docs
2. Check if an execution plan is needed (use [task-protocol.md](task-protocol.md) to decide)
3. Make the smallest coherent change
4. Add a BUILD_JOURNAL entry if a decision was made or milestone reached
5. Update harness docs if behaviour or architecture changed
6. Run `bash scripts/validate-harness.sh`
7. Summarise what changed and what's next
