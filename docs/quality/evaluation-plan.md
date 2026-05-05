# Evaluation Plan

> **Author:** Randall Mark — May 2026
> **Status:** v1 — framework adopted; results to be populated during build
> **BUILD_JOURNAL:** Entry 011
> **ADR:** [ADR-003-evaluation-framework.md](../architecture/decisions/ADR-003-evaluation-framework.md)

---

## Purpose

This document establishes the research questions, baselines, metrics, success criteria, and sequencing for evaluating AIPCS. It is the authoritative input to paper §5 (Evaluation).

The goal is not to show that AIPCS can work. It is to identify where it works well, where it breaks, what it costs, and whether it is measurably better than simpler alternatives in bounded domains.

---

## Research Questions

| ID | Research Question | Type |
|---|---|---|
| RQ1 | **Recognition** — does an agent reliably recognise AIPCS-appropriate situations and initiate the pattern correctly, without requiring an explicit prompt every time? | Behavioural |
| RQ2 | **Initial Design Quality** — does the agent produce a schema that adequately covers the domain at first attempt? | Quality |
| RQ3 | **Evolution Quality** — does the agent propose appropriate additive evolutions as domain knowledge grows, without breaking earlier queries? | Quality |
| RQ4 | **Retrieval and Continuity Utility** — does AIPCS-backed memory produce measurably better task continuation than baseline memory approaches? | Comparative |
| RQ5 | **Governance Effectiveness** — does the constraint model prevent harmful or low-quality schema proposals in practice? | Safety |
| RQ6 | **Runtime Portability** — can an AIPCS-instantiated service be exported and re-materialised in a different runtime context? | Portability |

---

## Baselines

Three baselines isolate the specific contributions of AIPCS.

### Baseline A — Harness Memory (markdown/index)

State tracked through markdown notes, index files, routing rules, and summarised state. This is the status quo pattern — the same approach this repo's own development uses.

**What it isolates:** Whether any form of structured persistence improves on the status quo. This is the most important baseline because it reflects the most common practical workaround.

**Setup:** Standard Claude.ai session with a CLAUDE.md harness. No AIPCS components.

### Baseline B — Developer-Defined Structured Memory

State tracked through a fixed, developer-authored relational schema covering the same domain as the AIPCS-designed schema. Agent populates the schema but does not design it.

**What it isolates:** Whether agent-directed schema design adds value over developer-defined structure. If Baseline B performs as well as AIPCS, the agent-design element is not contributing.

**Setup:** Hand-written SQLite schema with equivalent entity coverage to the agent-designed AIPCS schema. Same MCP tool surface, fixed schema.

### Baseline C — Minimal Generic KV/Document Store

State tracked through flexible JSON document storage with no domain schema. Agent stores and retrieves arbitrary documents via MCP.

**What it isolates:** Whether schema quality matters, or whether flexible storage is sufficient. If Baseline C performs comparably to AIPCS, structured schema design is not necessary.

**Setup:** Simple key-value MCP server with no domain structure. Agent stores JSON blobs.

---

## Evaluation Scenarios

### Suitable Scenarios

Good AIPCS candidates — multi-entity, relational, cross-session persistence valuable:

- **Career tracking** — job applications, companies, contacts, interview stages, outcomes (the reference implementation domain)
- **Research project tracking** — papers, ideas, experiments, hypotheses, status
- **Medical self-management** — symptoms, medications, appointments, providers, observations
- **Legal case tracking** — matters, parties, documents, key dates, actions

### Less Suitable Scenarios

Poor AIPCS candidates — use these to calibrate RQ1 (false positive rate):

- Simple single-entity tasks (a grocery list, a one-off reminder)
- Tasks already well served by the host application's own persistence
- Domains where the structure is entirely unknown — no repeating entities to model
- Short-horizon tasks where cross-session continuity has no value

---

## Metrics

### RQ1 — Recognition

- **Recognition rate:** Fraction of AIPCS-appropriate scenarios in which the agent voluntarily initiates the pattern without an explicit user prompt
- **False positive rate:** Fraction of non-AIPCS scenarios in which the agent mistakenly initiates the pattern
- **Measurement:** Scenario walkthroughs with and without explicit user hints; human rater judges appropriateness of trigger

### RQ2 — Initial Design Quality

- **Schema coverage:** Fraction of domain use cases the first-attempt schema can support (human rating against a domain rubric — see Q016)
- **Schema soundness:** Fraction of columns and entities that are semantically valid and non-redundant for the domain (human rating)
- **Validator pass rate:** Fraction of first-attempt schemas that pass the structural validator without requiring revision
- **Measurement:** Human qualitative review against domain rubric; comparative review against Baseline B schema

### RQ3 — Evolution Quality

- **Evolution appropriateness:** Are proposed evolutions additive, domain-coherent, and non-redundant? (human rating)
- **Breakage rate:** Fraction of proposed evolutions that would break existing query patterns if applied (automated check against prior tool definitions)
- **Evolution count:** Descriptive — how many evolutions occur in a typical domain lifecycle?
- **Measurement:** BUILD_JOURNAL running log of every evolution during the reference implementation build; adversarial test for break-inducing proposals

### RQ4 — Retrieval and Continuity Utility

- **Task continuation accuracy:** Fraction of cross-session continuation tasks completed correctly — AIPCS vs Baselines A, B, C
- **Retrieval precision:** Fraction of retrieved records relevant to the query (human rating for qualitative queries)
- **Latency overhead:** Additional wall-clock time for schema design step vs Baseline A/B
- **Token cost:** Additional tokens consumed by the schema design step
- **Measurement:** Comparative task tests with identical prompts across AIPCS and each baseline; BUILD_JOURNAL latency and token records

### RQ5 — Governance Effectiveness

- **Constraint enforcement rate:** Fraction of out-of-constraint schema proposals correctly rejected by the validator
- **Adversarial pass rate:** Fraction of adversarial prompts that bypass governance controls (lower is better; zero is the target)
- **Audit completeness:** Fraction of auditable actions that produce a correct, complete audit entry
- **Measurement:** Adversarial prompting suite (designed before Phase 2 evaluation); audit log inspection after each test run

### RQ6 — Runtime Portability

- **Export completeness:** Does the export artefact contain schema + data + migration history + tool definitions?
- **Re-materialisation success rate:** Fraction of export artefacts that can be re-materialised in a clean runtime environment with correct query behaviour
- **Measurement:** Export/import test in a clean Docker Compose environment; verify all tools register and queries return expected results

---

## Evaluation Methods

A mix of methods is required — no single method addresses all six RQs:

- **Scenario walkthroughs** — structured sessions working through specific domain scenarios; primary method for RQ1, RQ2
- **Adversarial prompting** — deliberate attempts to induce schema injection, credential column addition, governance bypass, destructive migration without confirmation; primary method for RQ5
- **Comparative task tests** — identical task sequences run against AIPCS and each baseline; primary method for RQ4
- **Human qualitative review** — schema quality, evolution quality, utility; primary method for RQ2, RQ3 (a rubric is required — Q016)
- **Failure analysis** — systematic logging and review of every validator rejection, governance trigger, and unexpected behaviour; required for all RQs
- **BUILD_JOURNAL running metrics** — token cost, latency, evolution frequency logged per session; feeds RQ3, RQ4

---

## Required Artefacts Per Evaluation Run

Each evaluation run must preserve:

- [ ] Full session transcript
- [ ] Schema manifest at end of session (JSON)
- [ ] Audit log dump (all entries from the session)
- [ ] BUILD_JOURNAL entry (new entry per evaluation run with metrics)
- [ ] Token cost record (input + output tokens for schema design step)
- [ ] Baseline comparison notes (for comparative runs)

This makes results inspectable and supports publication.

---

## Early Success Criteria

An early bounded prototype supports a positive result if all five are met:

1. An agent reliably recognises the career domain as AIPCS-appropriate without an explicit user instruction in at least 70% of scenario walkthroughs (RQ1)
2. The first-attempt agent-designed schema passes the structural validator and covers the core career tracking use cases as judged by a domain rubric (RQ2)
3. At least one additive schema evolution is proposed and applied during the reference implementation build, without breaking existing queries (RQ3)
4. Cross-session task continuation is measurably more accurate with AIPCS than with Baseline A for at least one scenario (RQ4)
5. The adversarial prompting suite produces zero governance bypasses — all harmful proposals are rejected before execution (RQ5)

These five criteria do not require RQ6 — portability can be validated after initial publication.

---

## Early Failure Conditions

The approach should be reconsidered or narrowed if any of the following occur:

1. Recognition rate below 70% on candidate scenarios — even with designed triggers (RQ1 failure)
2. First-attempt schema consistently passes the validator but is substantively wrong for the domain — indicates the validator is insufficient (RQ2/RQ5 combined failure)
3. Any destructive migration is applied without user confirmation — governance failure
4. Any auditable action produces no audit record — auditability failure
5. Export produces an artefact that cannot be re-materialised in a clean environment (RQ6 failure)

These are not bad outcomes. They are useful results that sharpen the claim.

---

## Evaluation Phases

| Eval Phase | Label | Maps to Impl Phase | Goal | Milestone |
|---|---|---|---|---|
| Phase 1 | Concept Validation | Phase 4 — First Agent-Designed Service | Validate RQ1 and RQ2 with career tracking scenario; establish Baselines A and B | M007 |
| Phase 2 | Governance Validation | Phase 5 — Validation and Evaluation | Validate RQ3 and RQ5; run adversarial suite; inspect audit log | M008 |
| Phase 3 | Portability Validation | Phase 5–6 overlap | Validate RQ6; export/import test in clean environment | M008–M009 |
| Phase 4 | Comparative | Phase 6–7 — Extraction + arXiv | Validate RQ4 across all three baselines; generate paper §5 data | M009–M010 |

---

## Open Questions

| Q | Question |
|---|---|
| Q015 | What does the evaluation harness look like? How are session transcripts, audit logs, and token costs captured systematically? |
| Q016 | What is the human review rubric for schema quality? What criteria define a schema as adequate for a domain? |

---

## References

- BUILD_JOURNAL Entry 011, D013
- [ADR-003-evaluation-framework.md](../architecture/decisions/ADR-003-evaluation-framework.md)
- [docs/roadmap/implementation-sequencing.md](../roadmap/implementation-sequencing.md)
- [docs/architecture/governance.md](../architecture/governance.md) (RQ5 depends on governance model)
