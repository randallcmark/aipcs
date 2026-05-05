# EP-001: Integrate External Critique and Design Documents

**Status:** Complete
**Owner:** Randall Mark
**Created:** 2026-05-04
**Completed:** 2026-05-04
**BUILD_JOURNAL entries:** 009, 010, 011, 012

---

## Goal

All findings from four external critique/design documents are reflected in the repository through new documents and targeted updates to existing documents, with full journal entries and ADRs.

## Non-Goals

- No code changes
- No changes to the Application Tracker repo
- No changes to `docs/AIPCS_v1_Technical_Design.md` — that document is pre-existing and stable
- No redesign of the 8 management primitives or the two-state lifecycle — the mechanism is confirmed; the surrounding infrastructure is what was updated

## Source Documents

| Document | Nature |
|---|---|
| aipcs-formal-critique.md | Independent external critique — 5 findings, 5 steering recommendations |
| aipcs-constraints-and-governance.md | Full governance framework |
| aipcs-claims-and-boundaries.md | Authoritative claim scope, non-goals, safer external framing |
| aipcs-evaluation-plan.md | 6 research questions, 3 baselines, 4-phase evaluation framework |

## New Files Created

| File | Source |
|---|---|
| `docs/architecture/governance.md` | aipcs-constraints-and-governance.md |
| `docs/architecture/claims-and-scope.md` | aipcs-claims-and-boundaries.md |
| `docs/quality/evaluation-plan.md` | aipcs-evaluation-plan.md |
| `docs/quality/critique-response.md` | aipcs-formal-critique.md |
| `docs/architecture/decisions/ADR-001-governance-model.md` | Governance decision |
| `docs/architecture/decisions/ADR-002-claim-narrowing.md` | Claims narrowing decision |
| `docs/architecture/decisions/ADR-003-evaluation-framework.md` | Evaluation framework decision |

## Existing Files Modified

| File | Nature of change |
|---|---|
| `journal/BUILD_JOURNAL.md` | Entries 009–012; D011–D014; S002; Q012–Q016; M011; §5 Evaluation updated; §3 and §6 paper notes updated |
| `docs/architecture/index.md` | §Governance Model and §Claims and Scope sections; ADR links; Change Rules |
| `docs/architecture/boundaries.md` | §Constraint Layer section; enforcement table; gaps line |
| `docs/quality/technical-debt.md` | Q012–Q016 added |
| `docs/product/research-brief.md` | Non-Goals expanded; safer external framing added; 4th research goal added |
| `docs/roadmap/implementation-sequencing.md` | Phase 2 governance steps; Phase 5 evaluation alignment; Phase 5b portability; Phase 7 evaluation step |
| `paper/outline.md` | §1 claim framing note; §3 compaction reframing + governance; §5 RQ/baseline structure; §6 governance + limitations |
| `README.md` | "Universal primitive" retired; Key Insight reframed; P11 added |

## Completion Checklist

- [x] BUILD_JOURNAL entries 009–012 written
- [x] Decision Log D011–D014 added
- [x] Spec Change Log S002 added
- [x] Open Questions Q012–Q016 added
- [x] Milestone M011 added
- [x] docs/architecture/governance.md created
- [x] docs/architecture/claims-and-scope.md created
- [x] docs/quality/evaluation-plan.md created
- [x] docs/quality/critique-response.md created
- [x] ADR-001, ADR-002, ADR-003 filed
- [x] docs/architecture/index.md updated
- [x] docs/architecture/boundaries.md updated
- [x] docs/quality/technical-debt.md updated
- [x] docs/product/research-brief.md updated
- [x] docs/roadmap/implementation-sequencing.md updated
- [x] paper/outline.md updated
- [x] README.md updated
- [x] validate-harness.sh passes
