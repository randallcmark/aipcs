# Harness Engineering Notes

## Source

This harness is adapted from `randallcmark/template_harness`, which draws on principles from OpenAI's "Harness engineering" writing (February 2026) and practical experience with agent-led codebases.

## Principles Applied

- **Keep AGENTS.md short** — it's a routing map, not a manual. Long routing files get ignored.
- **Treat repo-local docs as the system of record** — agents should trust docs over their training; docs should be updated when training assumptions break.
- **Progressive disclosure** — AGENTS.md → index.md → deeper docs. Don't front-load everything.
- **Capture plans, decisions, and debt in versioned files** — this is especially important in a research project where decisions compound. The BUILD_JOURNAL is the narrative; harness docs are the reference layer.
- **Make validation legible** — `bash scripts/validate-harness.sh` should be the one command to check harness health. No guessing.
- **Enforce rules mechanically** — anything that can be checked by a script should be. Don't rely on future agents to remember.
- **Treat agent failure as signal** — when an agent gets stuck, it usually means context is missing or a doc is wrong. Improve the harness.
- **Maintain the harness continuously** — the harness is not set-and-forget. It grows with the project.

## AIPCS-Specific Adaptations

This harness departs from the template in several ways appropriate to a research project:

| Template concept | AIPCS adaptation |
|---|---|
| `product-brief.md` | `research-brief.md` — frames the pattern as the "product" |
| `user-journeys.md` | `research-journeys.md` — development and paper workflows |
| `docs/agent/ui-ux-rules.md` | Omitted — no UI surface in this repo |
| No paper concept | Added `paper/outline.md` and `docs/agent/paper-rules.md` |
| Exec plans for features | Exec plans for build phases (M004, M005...) |
| Technical debt | Technical + conceptual debt (Q001-Q006 open research questions) |
| BUILD_JOURNAL not in template | Primary narrative record, pre-existing; harness complements it |
