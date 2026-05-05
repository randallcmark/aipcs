# ADR-001: Adopt a Formal Governance Model for Agent Schema Proposals

**Status:** Accepted
**Date:** 2026-05-04
**BUILD_JOURNAL entry:** 009

---

## Context

The v1 architecture described a Schema Validator enforcing structural rules before materialisation. However, the overall governance model — who has authority to do what, under what conditions, with what audit trail — was not formally specified.

An external critique (May 2026) identified this as the primary gap in the v1 design. Without a formal governance model, the claim "agent proposes, runtime governs" was asserted but not substantiated. The pattern could be misread as describing unconstrained agent persistence with some optional validation bolted on.

Without explicit governance, a prototype cannot be used with real users and cannot be presented as a reference implementation.

## Decision

Adopt `docs/architecture/governance.md` as the authoritative governance specification, effective immediately. The model covers:

- **Authority chain** (5 layers): Agent proposes → Validator constrains → User consents → Service persists → Audit log explains
- **Proposal constraint categories**: unilateral actions (seed, list, inspect), validator-gated actions (schema design, additive migration), user-consent-gated actions (destructive migration, Tier 3 access, sensitive column addition)
- **Structural constraints**: what the Schema Validator must enforce before materialisation
- **Semantic constraints**: what validation must guard against (even where automation is not yet complete)
- **Sensitive-data handling**: disallowed classes; heuristic detection patterns
- **User transparency requirements**: 7 items — what a user must be able to determine at any time
- **Auditability requirements**: 8 auditable actions; 6-field audit entry structure
- **Consent tier model**: 3 tiers
- **Correction and redress**: 8 operations
- **Minimum governance standard for early prototypes**: 7-point checklist

This is a v1 design requirement, not a v2 deferral.

## Consequences

**Benefits:**
- The claim "agent proposes, runtime governs" is now concrete and substantiated
- The minimum governance standard gives implementors a clear bar before any prototype is exposed to users
- The authority chain makes accountability explicit — there is a defined chain from agent action to audit record

**Costs / tradeoffs:**
- Audit log and consent surface requirements add implementation scope to Phase 2
- Semantic validation is partially deferred — the model describes it but automated enforcement of semantic correctness is Q012/Q013
- Sensitive-data column detection requires the Schema Validator to be extended with heuristic name patterns

**Follow-up actions:**
- Update `docs/architecture/boundaries.md` with Constraint Layer section (references governance.md)
- Update `docs/roadmap/implementation-sequencing.md` Phase 2 to include audit_log table (step 8a), sensitive-data heuristics (step 8b), consent surface (step 8c)
- Add Q012–Q014 to `docs/quality/technical-debt.md`

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Defer governance specification to v2 | Leaves the core claim unsubstantiated; prevents the prototype from being used for user evaluation; leaves open the "unsafe unconstrained persistence" mischaracterisation |
| Govern only via structural schema validation | Structural rules are necessary but not sufficient — they do not cover consent, audit, user transparency, sensitive data, or correction/redress |
| Capability-based access model (CBAC) | Over-engineered for a research pattern at this stage; the simpler authority chain achieves the same accountability with less complexity |

## Validation

- All 8 auditable actions produce audit entries in the Registry DB `audit_log` table
- The minimum governance standard 7-point checklist passes for the Phase 2 prototype
- An adversarial schema proposal (attempt to add a credentials column) is rejected by the Validator
- User can inspect, export, and delete a domain service without developer intervention
- No destructive migration is applied without user confirmation in the evaluation runs
