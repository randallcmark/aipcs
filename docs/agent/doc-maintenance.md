# Documentation Maintenance

## Layout

| File | Purpose |
|---|---|
| `CLAUDE.md` | Project overview and orientation |
| `AGENTS.md` | Routing map — stays short |
| `docs/agent/` | Repeated task rules |
| `docs/agent/examples/` | Portable prompt/skill instruction examples to evolve over time |
| `docs/architecture/` | Pattern and system design constraints |
| `docs/product/` | Research context and development journeys |
| `docs/exec-plans/` | Temporary working plans (active and completed) |
| `docs/quality/` | Health snapshots and debt tracking |
| `docs/roadmap/` | Implementation sequence and task map |
| `journal/BUILD_JOURNAL.md` | Primary narrative record — chronological entries |
| `paper/outline.md` | Living paper structure |

## When to update

- Same session as a behaviour, architecture, or spec change
- When a decision in the BUILD_JOURNAL should become a rule in a harness doc
- When a journal open question is resolved — close it in `technical-debt.md` too
- When an agent got stuck because a doc was missing or wrong

## Staleness checks

- Broken links in any markdown file
- `docs/architecture/index.md` out of sync with BUILD_JOURNAL decision log
- `technical-debt.md` open items that have actually been resolved
- `paper/outline.md` sections with no notes when the build has progressed past them
- Execution plans in `active/` older than 30 days

Run `bash scripts/validate-harness.sh` to catch the mechanical checks.

## Promotion rule

If an agent repeats the same mistake or asks the same question twice, that's signal that the doc is wrong or missing. Add the rule to the appropriate harness file rather than just answering again.
