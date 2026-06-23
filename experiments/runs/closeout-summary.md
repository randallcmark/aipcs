# Close-Out Experiment Summary

## Scope

This summary consolidates the close-out representational-compression runs only. For the broader publication-readiness assessment across calibration, persistence, recall, authority, scalability, corpus, and close-out runs, see `experiments/runs/full-programme-evidence-review.md`.

The close-out runs are:

- `closeout01`: AIPCS-only integrated cross-source corpus.
- `closeout01b`: AIPCS-only mechanically merged heterogeneous single-source services.
- `closeout02`: raw source packet only.
- `closeout03`: curated single-file memory artifact, broad synthesis.
- `closeout04`: AIPCS-only discrimination/null probe.
- `closeout05`: curated single-file memory artifact, discrimination/null probe.
- `closeout06`: vanilla/model-knowledge reconstruction baseline.

The runs are sufficient to move into paper drafting. They do not prove broad AIPCS superiority. They do support a narrower and stronger claim: AIPCS preserves bounded, agent-authored, structured prior cognition that can be discovered and reused by later agents, with clear tradeoffs against source access, curated flat artifacts, and model priors.

## Sufficiency Judgment

The data is sufficient for a first paper evaluation section because it covers:

- an AIPCS success case over an integrated multi-domain corpus;
- an AIPCS robustness case over heterogeneous independently authored services;
- a source-only quality ceiling;
- a strong curated flat-artifact baseline;
- a targeted AIPCS discrimination/null probe;
- a paired flat-artifact discrimination/null probe;
- a vanilla/model-knowledge baseline.

The evidence is not sufficient for claims about:

- agent-memory-v2 comparison;
- very large-scale AIPCS performance;
- non-natural-language data;
- medical/health-style implicit trend recall;
- long-running months-scale organic memory evolution.

Those are future-work or follow-up experiment classes, not blockers for drafting the current paper.

## Run Comparison

| Run | Condition | Main Result | Strength | Limitation |
|---|---|---|---|---|
| `closeout01` | AIPCS integrated corpus | Fresh Claude discovered AIPCS and produced a strong cross-subject essay from three integrated memoir services. | Demonstrates reusable agent-authored memory topology. | Favourable topology: cross-cutting themes were already persisted. |
| `closeout01b` | AIPCS heterogeneous corpus | Fresh Claude synthesized across five independently authored services. | Shows AIPCS can tolerate non-uniform memory architectures. | Required broad retrieval, scratch-work, and recovered from an initial raw SQLite attempt. |
| `closeout02` | Source-only | Strong source-grounded essay from 336 files / 4.5 MB source packet. | Quality and direct provenance ceiling. | Higher task-time navigation and source triage cost; prior cognition not preserved. |
| `closeout03` | Curated flat artifact | Strong broad essay from one 5,391-word / 33,149-byte `MEMORY.md`. | Efficient upper baseline for compact curated memory. | Artifact was deliberately prepared, task-aligned, and not ordinary incidental memory. |
| `closeout04` | AIPCS discrimination/null | Correctly rejected unsupported Adams/Washington and Kropotkin/Gandhi equivalence claims. | Shows structured memory can support source discrimination and absence reasoning. | Retrieved broadly rather than surgically; compact corpus made this rational. |
| `closeout05` | Curated flat artifact discrimination/null | Also handled unsupported equivalence claims well. | Prevents weak-baseline comparison; flat artifact is a serious comparator. | Again relies on an unusually strong curated dossier. |
| `closeout06` | Vanilla/model knowledge | Strong thematic essay without supplied memory or source. | Establishes Claude's generic synthesis capability. | Weak bounded provenance; no direct quote verification; used facts outside controlled memoir corpus. |

## Evidence by Hypothesis

| Hypothesis | Status | Evidence |
|---|---|---|
| H1: Later clean agents can discover and use agent-authored cross-domain AIPCS memory. | Supported | `closeout01` succeeded over integrated services; `closeout01b` succeeded over heterogeneous services. |
| H2: Raw source access is the quality ceiling but costs more at task time. | Supported | `closeout02` produced strong grounded output, but required extensive file navigation across 336 source files. |
| H3: A curated flat artifact is a plausible low-cost baseline. | Supported, stronger than expected | `closeout03` produced strong output from one file. This narrows AIPCS's one-off answer-quality claim. |
| H4: AIPCS structured memory supports discrimination/null handling. | Supported | `closeout04` avoided near-neighbor false positives and explicitly handled insufficient evidence. |
| H5: Dense flat artifacts may create false-positive pressure. | Not supported in this corpus | `closeout05` also handled the null/discrimination probe well. The flat artifact was a strong upper baseline. |
| H6: Vanilla Claude may reconstruct plausible synthesis without supplied memory. | Supported | `closeout06` produced strong thematic synthesis from model knowledge, but with weak bounded provenance. |

## Key Findings

### AIPCS Works As First-Class Persistent Memory

Across `closeout01`, `closeout01b`, and `closeout04`, fresh Claude sessions could discover AIPCS, retrieve durable context, and generate meaningful answers without source files. This supports the basic feasibility claim: AIPCS can function as a first-class memory and persistence substrate for agents.

### Memory Topology Matters

`closeout01` was efficient because the corpus had an integrated cross-source topology with subject, theme, and episode services. `closeout01b` was still successful, but the heterogeneous merged corpus required broader retrieval and local scratch-work. This is a useful limitation: AIPCS does not magically normalize memory created in isolation. The quality of agent-authored schema and retrieval guidance matters.

### Raw Source Is A Strong Ceiling, Not A Strawman

`closeout02` shows that direct source access can produce excellent output. AIPCS should not be framed as a universal replacement for source access. The stronger comparison is between source-time cognition and persisted prior cognition: raw source requires the future agent to redo source triage and interpretation, while AIPCS can preserve selected structure and interpretation for later reuse.

### Curated Flat Artifacts Are Serious Baselines

`closeout03` and `closeout05` show that a deliberately prepared single-file memory artifact can perform extremely well for compact narrative corpora. The artifact was 5,391 words / 33,149 bytes, generated from five sources, analytically dense, and task-aligned. It is not ordinary prose memory. It is closer to a condensed dossier.

This narrows the AIPCS claim. AIPCS did not clearly outperform that artifact on one-off answer quality. Its advantage must be argued on structure, provenance, retrieval, inspectability, maintainability, and evolution.

### Vanilla Claude Is Already Good At Thematic Synthesis

`closeout06` shows that Claude can write a strong essay about well-known figures from model knowledge alone. This makes the experiment more honest. AIPCS is not valuable because the model cannot synthesize. It is valuable because it can preserve bounded, corpus-specific, prior situated cognition with inspectable provenance.

### The Core Paper Claim Should Be Narrowed

The runs do not justify:

> AIPCS makes agents produce better prose than other memory approaches.

They do justify:

> AIPCS enables agents to persist, discover, inspect, and reuse structured prior cognition across sessions, preserving bounded corpus-specific interpretation in a way that raw source access, curated flat artifacts, and model priors each handle differently.

## Comparative Interpretation

| Dimension | AIPCS | Raw Source | Curated Flat Artifact | Vanilla Model Knowledge |
|---|---|---|---|---|
| One-off prose quality | Strong | Strong | Strong | Strong |
| Bounded provenance | Strong if records carry source/provenance | Strongest | Medium: depends on note construction | Weak |
| Direct quotation support | Medium: depends on what was persisted | Strongest | Medium: if quotes were retained | Weak |
| Task-time navigation cost | Low-medium | High | Low | Lowest |
| Inspectable memory structure | Strong | Not memory | Weak | None |
| Evolvability | Strong: schema/services can evolve | Not memory | Weak/manual | None |
| Cross-agent/session continuity | Strong | Requires source availability | Medium if file persists | Weak/uncontrolled |
| Scale outlook | Promising but not fully tested | Source cost grows | Single file becomes unwieldy | Unbounded but uncontrolled |
| Failure mode | Poor topology, broad retrieval, tool friction | Re-reading cost, source overload | Over-curation, stale dossier, hard to query | Unsupported facts, weak provenance |

## Drafting Implications

The paper should lead with AIPCS as an architectural primitive, not a summarization method.

Use the close-out evidence to structure the evaluation section:

1. Feasibility: `closeout01` and `closeout04`.
2. Topology sensitivity: `closeout01b`.
3. Source ceiling: `closeout02`.
4. Curated flat-artifact baseline: `closeout03` and `closeout05`.
5. Model-prior baseline: `closeout06`.

The discussion should explicitly state:

- AIPCS performed well, but so did strong baselines.
- The experiment therefore refines the claim rather than simply validating an advantage.
- AIPCS's distinctive value is long-running structured memory, not generic generation quality.
- More work is needed to compare against agent-memory-v2, larger corpora, and non-narrative domains.

## Recommendation

Stop the close-out data-collection loop here and move to paper drafting.

Additional experiments may be useful later, but the current batch already provides enough evidence to write a balanced evaluation section. Running more close-out variants now risks diminishing returns unless a specific paper gap is identified during drafting.
