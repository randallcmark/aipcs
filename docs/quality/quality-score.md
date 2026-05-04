# Quality Score

A recurring snapshot of project health. Review monthly or after major milestones.

## Scorecard

| Area | Grade | Evidence | Next Action |
|---|---|---|---|
| Pattern clarity | A | Invention disclosure + pattern spec published; 10 principles defined; v1 architecture decisions made | Write Introduction and Background paper sections |
| Architecture legibility | B | `docs/architecture/index.md` covers trigger/mechanism/registration; boundaries defined | Resolve Q001-Q006 as design matures; create ADRs for major decisions |
| Validation reliability | C | No automated tests yet; validate-harness.sh covers harness completeness only | Build test suite alongside reference implementation |
| Reference implementation | D | Not yet started in this repo; Application Tracker is the proving ground | Complete M004-M008 milestones |
| Paper progress | B | Structure defined; Introduction and Background seeded; Evaluation and Implementation empty | Populate as build progresses |
| Harness integrity | A | Full harness in place from day one | Run validate-harness.sh after each session |

## Review Cadence

Default: after each milestone (M004, M005, ...) and monthly.

## Notes

Grades are evidence-based — link to failures, gaps, and milestones rather than vibes.

*Last reviewed: 2026-05-04 (initial harness setup)*
