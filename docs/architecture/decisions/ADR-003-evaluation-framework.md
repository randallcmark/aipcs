# ADR-003: Adopt a Formal Evaluation Framework

**Status:** Accepted
**Date:** 2026-05-04
**BUILD_JOURNAL entry:** 011

---

## Context

The paper outline §5 (Evaluation) was seeded with informal metrics drawn from BUILD_JOURNAL running notes. There was no structured research question set, no defined baselines, and no pre-specified success or failure criteria.

Without these, evaluation results cannot be compared across runs or sessions, the paper's evaluation section cannot meet the standard of a systems paper, and results risk being post-hoc rationalisations of whatever happened to work rather than evidence against pre-committed criteria.

An external evaluation plan (May 2026) provided a full framework. Adopting it is required before evaluation work begins.

## Decision

Adopt `docs/quality/evaluation-plan.md` as the authoritative evaluation specification. The framework establishes:

- **6 research questions** (RQ1–RQ6): Recognition, Initial Design Quality, Evolution Quality, Retrieval/Continuity Utility, Governance Effectiveness, Runtime Portability
- **3 baselines**: A (harness/markdown memory), B (developer-defined structured memory), C (minimal generic KV/document store)
- **Per-RQ metrics** with measurement methods
- **Evaluation methods mix**: scenario walkthroughs, adversarial prompting, comparative task tests, human qualitative review, failure analysis, BUILD_JOURNAL running metrics
- **Required artefacts per run**: transcript, schema manifest, audit log, journal entry, token cost, baseline comparison notes
- **5 early success criteria**
- **5 early failure conditions** (pre-committed — must be resolved before paper submission if triggered)
- **4-phase evaluation sequencing** aligned to implementation phases

## Consequences

**Benefits:**
- Evaluation is repeatable and comparable across runs and sessions
- Failure conditions are pre-committed — no post-hoc rationalisation of negative results
- The 3 baselines allow comparative claims in the paper, not just descriptive ones; they isolate the specific contributions (RQ4 vs Baseline A, B, C)
- The 4-phase sequencing starts evaluation at M007 — earlier than previously planned — ensuring evaluation data accumulates during the build rather than as a final step

**Costs / tradeoffs:**
- The formal framework constrains what counts as evaluation evidence — informal observations still belong in the BUILD_JOURNAL but only structured evaluation runs feed paper §5
- The adversarial prompting suite (RQ5) is new work not previously planned; it must be designed before Phase 5 begins
- Human qualitative review for RQ2 and RQ3 requires a rubric (Q016) — added to technical-debt.md

**Follow-up actions:**
- Update `docs/roadmap/implementation-sequencing.md` Phase 5 to align with evaluation phases
- Update `paper/outline.md` §5 with RQ1–RQ6 and baselines A–C structure
- Design adversarial prompting suite before Phase 5 work begins (see Q015)
- Add Q015 and Q016 to `docs/quality/technical-debt.md`

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Informal journalling only (current approach) | Cannot produce comparable results; insufficient for a systems paper evaluation section that makes comparative claims |
| Fully automated evaluation only | Schema quality (RQ2, RQ3) and utility (RQ4) require human judgement; automated-only evaluation would miss the most important quality dimensions |
| Single baseline (Baseline A only) | A single baseline cannot isolate whether structure matters (Baselines B and C address this) or whether agent-design adds value (Baseline B specifically isolates this). The comparative value of the work requires all three. |
| Delay evaluation framework until after initial build | Risk: evaluation data collected without a framework cannot be retroactively structured into RQs with pre-defined metrics. The framework must exist before data collection begins. |

## Validation

- `docs/quality/evaluation-plan.md` exists with all 6 RQs, 3 baselines, metrics, success criteria, and failure conditions
- `docs/roadmap/implementation-sequencing.md` phases 4–7 align with evaluation phases 1–4
- `paper/outline.md` §5 references the 6 RQs and 3 baselines
- Before Phase 4 evaluation begins: adversarial prompting suite draft exists
- Before Phase 5 begins: human review rubric for schema quality (Q016) drafted
