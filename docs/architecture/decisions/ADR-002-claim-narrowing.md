# ADR-002: Narrow the AIPCS Claim and Establish a Claims Boundary Document

**Status:** Accepted
**Date:** 2026-05-04
**BUILD_JOURNAL entry:** 010

---

## Context

The v1 README and architecture documents used several overreach-prone phrases:

- **"Universal primitive"** — implies universal applicability before any generalisation evidence exists
- **"The agent is the architect of its own memory"** — accurate in spirit but could be read as implying unconstrained autonomy
- **MCP foregrounded as the primary novelty** — MCP is the chosen interface surface, not the novelty itself; over-positioning it makes the contribution look implementation-specific
- **Compaction as "primary Model B trigger"** — this is a design intent, not a field-validated claim

Additionally, the pattern documentation had no single authoritative claims document. Language could drift toward overclaim in different files independently, with no single source of truth to adjudicate.

An external critique (May 2026) identified four areas of claim risk and provided a safer external framing.

## Decision

1. Create `docs/architecture/claims-and-scope.md` as the authoritative claims boundary document. Where language elsewhere in the repo conflicts with this document, claims-and-scope.md takes precedence.

2. Adopt the following working core claim:
   > "AIPCS is a constrained runtime pattern for agent-directed creation and evolution of structured persistent memory services."

3. Adopt the following safer external framing for paper abstract, README, and presentations:
   > "AIPCS is an early pattern for governed agent-directed structured memory, where an agent can propose and evolve persistence schemas under runtime validation instead of relying solely on developer-defined memory models."

4. Retire "universal primitive" from README.md and all repo documents. Replace with "general-purpose pattern" pending demonstrated generalisation beyond the reference implementation.

5. Reframe compaction from "primary Model B trigger" to "a designed Model B trigger" — pending field evidence from evaluation.

6. Reduce MCP prominence in the Key Insight framing. MCP is the interface; the novelty is governed agent-directed persistence.

7. Add an explicit Non-Goals list to `docs/architecture/claims-and-scope.md` and update `docs/product/research-brief.md`.

## Consequences

**Benefits:**
- A single authoritative claims document prevents language drift across files
- Narrower claims are more defensible in peer review — they set a bar that the evaluation can actually clear
- Explicit non-goals reduce misinterpretation of the pattern's scope
- Softer framing on compaction avoids making an evaluable claim before the evaluation is run
- Reduced MCP prominence makes the contribution independent of MCP's continued relevance

**Costs / tradeoffs:**
- "Universal primitive" was memorable; "general-purpose pattern" is more accurate but less punchy — acceptable tradeoff for a research paper
- Some existing language in README.md and paper/outline.md requires targeted updates
- A single authoritative document adds a maintenance obligation — any future claims update must go through claims-and-scope.md

**Follow-up actions:**
- Update `README.md` §The Key Insight paragraph
- Update `paper/outline.md` §1 claim framing note and §3 compaction reframing
- Any future document additions must use the claims-and-scope.md framing as the reference

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Keep "universal primitive" — it is aspirational framing, not a factual claim | A claim in a research paper is evaluated, not aspirational. "Universal" cannot be defended before portability and multi-domain evaluation is complete. |
| Add qualifications inline per document | Inline qualifications drift and are inconsistently applied as the repo evolves. A single authoritative document is more maintainable. |
| Make no language changes — the nuance is understood | The critique was produced by an independent reviewer who did not understand the nuance from the existing language. If a motivated reader missed it, so will peer reviewers. |

## Validation

- `docs/architecture/claims-and-scope.md` exists with all 6 claims, 9 non-claims, and 6 non-goals
- `README.md` no longer uses the phrase "universal primitive"
- `paper/outline.md` §3 compaction framing matches the approved language from claims-and-scope.md
- No document in the repo makes a claim that is not covered by or consistent with claims-and-scope.md
