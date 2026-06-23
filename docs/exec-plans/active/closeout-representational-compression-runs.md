# Execution Plan: Close-Out Representational Compression Runs

**Status:** Evidence collected
**Owner:** Agent + Randall Mark
**Created:** 2026-06-20
**Last updated:** 2026-06-20
**BUILD_JOURNAL entries:** 099

---

## Goal

Execute a bounded experiment series that gives enough comparative evidence to move from exploratory AIPCS data collection into paper drafting.

## Non-Goals

- Do not continue broad exploratory calibration during this series.
- Do not include agent-memory-v2 in this close-out batch.
- Do not compare the mechanically merged single-source snapshot unless the five planned runs complete and leave a specific topology question open.
- Do not revise AIPCS implementation during this batch unless the run is invalidated by a clear harness failure, data import failure, or server bug.
- Do not require AIPCS to outperform raw source access on every dimension.

## Context

Relevant project evidence:

- `run001`-`run003` established cold-start discovery, agent-authored persistence, and future-session recall/application.
- `run018`-`run021` established bootstrap payload and orientation scalability limits.
- `run019b` and `run020b` showed slim bootstrap fixed the concrete payload problem, while harsh service-selection cases can still fail.
- `run024e` and `run024f` showed agents can autonomously use AIPCS over an organic-shaped corpus but will downweight semantically hollow data.
- `run026` showed a fresh agent could write a nuanced source-free Kropotkin essay from an AIPCS corpus.
- `run027` showed membership/filter capability must be legible at tool-choice time, leading to retrieval-affordance improvements.

Relevant docs:

- `docs/exec-plans/active/representational-compression-evaluation.md`
- `docs/exec-plans/active/retrieval-affordance-legibility.md`
- `experiments/snapshots/multimemoir-agent-authored-v1.md`
- `experiments/runbooks/closeout-representational-compression-runs.md`

## Core Claim Under Test

AIPCS can act as an agent-authored structured memory representation that preserves enough task-relevant meaning from source material to support later high-quality synthesis at lower task-time context cost than raw source access or flat memory summaries.

The claim is not that AIPCS always beats source access. The sharper claim is about the tradeoff between quality, retrieval efficiency, source discrimination, and cost.

## Planned Runs

| Run | Representation | Prompt class | Primary question |
|---|---|---|---|
| `closeout01` | AIPCS-only | Broad cross-subject synthesis | Can a fresh agent discover and use an agent-authored multi-memoir AIPCS corpus without source access? |
| `closeout01b` | AIPCS-only, alternate topology | Same broad synthesis | Can a fresh agent synthesize across independently authored single-source AIPCS services without a pre-integrated comparative memory layer? |
| `closeout02` | Source-only | Same broad synthesis | What quality and cost does direct source access provide as the strongest obvious baseline? |
| `closeout03` | Flat-memory-only | Same broad synthesis | Does a curated single-file memory artifact achieve comparable quality at lower operational complexity? |
| `closeout04` | AIPCS-only | Targeted discrimination + null probe | Does structured memory reduce cross-subject misattribution and unsupported claims? |
| `closeout05` | Flat-memory-only | Same discrimination + null probe | Does flat memory over-apply nearby facts or lose source discrimination under the same probe? |
| `closeout06` | Vanilla / research-enabled optional | Same broad synthesis | Can a fresh agent reconstruct comparable synthesis without supplied AIPCS, source packet, or flat memory, using only model priors and any ordinary research tools available? |

## Optional Post-Closeout Experiments

These are deliberately outside the five-run batch. They should be considered after the main representational-compression evidence is collected and paper drafting has started.

| Direction | Question | Why it matters | Suggested first probe |
|---|---|---|---|
| Non-natural-language data | How does an agent-authored AIPCS service handle statistical, iterative, or code-structured data? | The current corpus is human-centric narrative memory. AIPCS should also be evaluated where schemas may contain measurements, variables, loops, algorithms, experiment results, or software design constraints. | Give an agent a small longitudinal dataset or software module history and ask it to persist future-useful memory, then test whether a fresh agent can retrieve trends, variables, algorithms, or implementation constraints. |
| Implicit cross-data recall | Can AIPCS surface correlations that were not explicit in one interaction but emerge across many persisted records? | Long-running memory is especially valuable when separate anecdotes become meaningful together, such as health or physiology trends. This is high-stakes and should be framed as decision support, not diagnosis. | Use a synthetic longitudinal health-style diary with known hidden correlations, then ask a fresh agent to identify factors worth discussing with a medical professional while avoiding medical claims beyond the evidence. |
| Indirect references to others | Does an agent persist and later retrieve information about people mentioned indirectly during user-centred tasks? | Real conversations include family, colleagues, collaborators, and third parties. AIPCS may need to distinguish user facts, third-party facts, inferred relationships, consent/sensitivity, and authority. | Use a synthetic personal/project interaction stream containing references to several people, then test whether the agent records third-party context appropriately and avoids overclaiming or exposing irrelevant personal details. |

These directions may add colour to the paper's future-work section. They should not block the five close-out runs.

## Evidence Standard

This batch is not trying to prove that AIPCS is universally superior to every memory approach. The publishable standard is narrower and more defensible:

- AIPCS supports an agent-authored memory topology that can be discovered by a later clean agent without bespoke human schema knowledge.
- The memory topology can span multiple source domains and still support cross-domain synthesis, not only single-service recall.
- Structured memory can preserve enough task-relevant meaning to support later generation without the original source material.
- AIPCS can preserve prior interpretive work across sessions as a durable cognitive artifact, rather than requiring future agents to re-source files and reconstruct reasoning from scratch.
- AIPCS memory architecture can adapt over time: repeated retrieval work, recurring concepts, or cross-domain patterns can become pressure for schema evolution, new entities, facets, or services.
- The representation has measurable tradeoffs against raw source access and flat memory summaries.
- Limitations and failure modes are treated as evidence, not as reasons to keep moving the goalposts.

Within that standard, H1 is the primary feasibility-and-transfer test. H2-H5 are the comparative and discrimination tests that make the evidence more than a successful anecdote.

## Emerging Interpretation

The first close-out runs suggest a useful distinction:

- Source-only runs perform source-time cognition: the agent reads source files, builds an argument, and loses most of that work after the session.
- Flat memory is expected to preserve a prose residue, but risks collapsing detail, provenance, and structure over time.
- AIPCS can preserve structured prior cognition: facts, interpretations, retrieval facets, and cross-domain abstractions remain available to future sessions or agents.

The contrast between `closeout01` and `closeout01b` adds a topology point. Integrated memory made synthesis efficient because the earlier agent had already persisted cross-cutting abstractions. Independently authored services were still usable, but required broader extraction and answer-time cross-referencing. A mature AIPCS workflow should be able to turn that repeated retrieval work into schema evolution pressure: for example, creating or evolving comparative theme services when the agent repeatedly needs cross-domain synthesis.

## Hypotheses

| Hypothesis | Expected evidence |
|---|---|
| H1: A later clean agent can discover and use an agent-authored cross-domain AIPCS memory topology for synthesis without source access. | `closeout01` tests an integrated cross-source memory topology with explicit comparative services. `closeout01b` tests a harder alternate topology made from independently authored single-source services. Together they show whether success depends on a pre-integrated comparative layer or whether a future agent can reconstitute synthesis across heterogeneous authored schemas. |
| H2: Raw source access is the quality ceiling but should carry higher task-time context and navigation cost. | `closeout02` may achieve equal or better factual coverage than AIPCS, but should require reading materially more source text, spend more effort locating relevant passages, and expose whether source access alone gives better synthesis per unit of context consumed. |
| H3: A curated single-file memory artifact is a plausible low-cost baseline, but should lose some retrievability, provenance, or source discrimination under cross-subject pressure. | `closeout03` may produce coherent prose from a prepared condensed dossier, but scoring should test whether it drops anchor facts, substitutes generic summaries, blends subjects, or lacks enough structure to explain why particular facts were selected. |
| H4: AIPCS structured memory should support better discrimination under near-neighbor and null probes than flat memory, if the agent uses the memory topology rationally. | `closeout04` should show whether service/entity/record selection helps the agent distinguish similar subjects, decline unsupported claims, and cite absence or uncertainty from the available structured memory. Failure is still meaningful if the agent over-retrieves, misses relevant branches, or treats weak records as authoritative. |
| H5: A curated single-file memory artifact should reveal whether dense summary representations increase false-positive pressure when adjacent but non-equivalent facts are present. | `closeout05` should test whether the prepared flat artifact causes blending, overconfident analogies, or unsupported equivalence claims in the same discrimination/null task used for `closeout04`. A strong flat-memory result would narrow AIPCS's claimed advantage and should be treated as real evidence. |
| H6: A vanilla or research-enabled fresh agent may reconstruct a plausible synthesis without supplied memory, but should pay re-research cost, show weaker bounded-corpus provenance, or rely unevenly on model priors. | `closeout06` is optional and can run later without sequencing dependency. It tests whether the task itself is easy enough for ordinary model knowledge or live research, and reframes AIPCS as preserving prior situated cognition rather than competing with general knowledge. |

## Controls

- Use the same clean lab baseline for all five runs.
- Use the same downstream prompt text for `closeout01`, `closeout01b`, `closeout02`, and `closeout03`, changing only the available representation/topology.
- Use the same discrimination/null prompt text for `closeout04`-`closeout05`, changing only the available representation.
- Do not provide downstream probe prompts during corpus or summary generation.
- Keep source files out of the workspace for AIPCS-only and flat-memory-only runs.
- Keep AIPCS unavailable or empty for source-only and flat-memory-only runs.
- Capture transcript, exported response, server logs where applicable, and observer notes for every run.
- Treat Claude cloud/native memory as an uncontrollable confound; score only facts grounded in the provided representation or explicitly attributed by the agent.

## Assumptions

- `multimemoir-agent-authored-v1` is the primary AIPCS snapshot for `closeout01`.
- `memoir-single-source-combined-v1` is the alternate AIPCS topology for `closeout01b`.
- The source-only condition uses the same five public-domain memoirs that generated the AIPCS corpus.
- The flat-memory-only condition uses a generated single-file memory artifact from the same bounded source packet set. This is a curated, task-prepared artifact rather than an ordinary organic `MEMORY.md` accumulation.
- The agent model may shift over time; visible model label and CLI version must be recorded but are not controlled.
- Claude login may be required in a run home; this is an operational nuisance, not automatically an invalidating condition.

## Measurement Objectives

Each run should capture:

- bootstrap/tool discovery path, if AIPCS is available;
- source files read, if source is available;
- flat memory file read, if flat memory is available;
- number of AIPCS tool calls, retrieval calls, and failed calls;
- transcript size and output length;
- wall-clock start/end times;
- subject-specific anchor facts used;
- cross-subject interpretive themes used;
- unsupported claims;
- cross-subject misattributions;
- appropriate uncertainty;
- whether the retrieval/read path was rational for the available representation.

## Scoring Rubric

Use additive/subtractive scoring after each run.

| Dimension | Scoring |
|---|---|
| Anchor fact coverage | +1 for each correct source-supported subject-specific fact, max 10. |
| Interpretive synthesis | +1 for each meaningful cross-subject theme, max 5. |
| Source discrimination | +1 for each correct distinction between similar subjects/events, max 5. |
| Appropriate uncertainty | +1 for each explicit refusal to overclaim unsupported memory/source, max 3. |
| Unsupported invention | -1 for each unsupported factual claim. |
| Generic substitution | -1 where a specific available fact should have been used but was replaced with vague prose. |
| Cross-subject misattribution | -2 for each fact assigned to the wrong subject. |
| Tool/source discipline | Qualitative 1-5 score. |
| Prose usefulness | Qualitative 1-5 score, separate from factual score. |

## Stop Conditions

Pause the batch only if:

- the AIPCS snapshot imports incorrectly and bootstrap shows the wrong owner/path or no expected services;
- the source-only or flat-memory conditions accidentally expose AIPCS data;
- the AIPCS-only runs expose source files in the workspace;
- Claude cannot complete a run because of authentication or client failure;
- server logs show tool errors that make the run uninterpretable.

Do not pause merely because:

- the agent chooses broad retrieval;
- AIPCS underperforms a baseline;
- flat memory performs better than expected;
- the agent retrieves fewer records than hoped;
- the answer exposes a limitation in the memory representation.

Those are data.

## Plan

1. Confirm the close-out artifacts exist:
   - `multimemoir-agent-authored-v1` AIPCS snapshot;
   - bounded source packet directory;
   - flat memory summary file;
   - scoring checklist.
2. Run `closeout01` AIPCS-only broad synthesis over the integrated cross-source corpus.
3. Run `closeout01b` AIPCS-only broad synthesis over the independently authored merged corpus.
4. Run `closeout02` source-only broad synthesis.
5. Run `closeout03` flat-memory-only broad synthesis.
6. Score `closeout01`, `closeout01b`, `closeout02`, and `closeout03` side by side before proceeding.
7. Run `closeout04` AIPCS-only discrimination/null probe.
8. Run `closeout05` flat-memory-only discrimination/null probe.
9. Write curated run notes for the close-out runs.
10. Update `representational-compression-evaluation.md` with results.
11. Decide whether optional follow-up is needed:
    - source+AIPCS combined condition;
    - mechanically merged single-source topology comparator;
    - vanilla/research-enabled reconstruction baseline;
    - agent-memory-v2 comparator.

## Acceptance Criteria

- [x] Close-out run artifacts exist under the lab run archive.
- [x] Seven curated run notes exist under `experiments/runs/`, covering `closeout01`, `closeout01b`, and `closeout02`-`closeout06`.
- [x] Each run note includes transcript pointer, representation condition, observed context sources, scoring, and paper relevance.
- [x] At least one side-by-side comparison table exists for `closeout01`-`closeout03`, including the `closeout01b` topology variant.
- [x] Null/false-positive comparison exists for `closeout04` and `closeout05`.
- [x] The batch produces enough evidence to draft the paper's evaluation section without adding a new implementation slice.

## Progress Log

| Date | What happened |
|---|---|
| 2026-06-20 | Plan created to bound the final data-collection stage and avoid further exploratory drift. |
| 2026-06-20 | `closeout01`, `closeout01b`, and `closeout02` completed. H1 now has integrated and heterogeneous topology evidence; H2 source-only baseline produced strong output with clear navigation/context cost. |
| 2026-06-22 | `closeout03` completed. Flat-memory-only produced a strong answer from one best-effort source-derived memory note, but the note was unusually rich and task-aligned, making it an upper baseline rather than casual memory. |
| 2026-06-22 | `closeout04` completed. Claude went directly to AIPCS bootstrap, retrieved the three relevant integrated memoir services, and handled the discrimination/null prompt without unsupported equivalence claims. |
| 2026-06-22 | `closeout05` completed. Flat-memory-only also handled the discrimination/null prompt well, showing that a deliberately prepared 5,391-word condensed memory artifact is a strong upper baseline rather than a strawman. |
| 2026-06-22 | `closeout06` completed. Vanilla/model-knowledge-only produced a strong thematic essay but lacked bounded corpus provenance and directly verifiable quotations. |
| 2026-06-23 | Close-out results consolidated in `experiments/runs/closeout-summary.md`. Evidence judged sufficient for paper drafting, with a narrowed AIPCS claim focused on structured, bounded, evolvable memory rather than one-off prose superiority. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Plan five runs, not seven | Runs 1-5 are directly comparable and already have enough known inputs. Optional topology and agent-memory-v2 comparisons depend on what these runs show. |
| Use `multimemoir-agent-authored-v1` as the primary AIPCS corpus | It was generated as a single cross-source agent-authored memory activity, matching the representational-compression claim. |
| Add `closeout01b` as a paired H1 topology check | `closeout01` succeeded against an integrated comparative corpus, but that may be favourable because cross-cutting themes were already persisted. `closeout01b` tests a harder heterogeneous topology using independently authored single-source services. |
| Treat `closeout03` as an upper flat-memory baseline | The flat memory artifact was generated deliberately from source and was highly aligned with the task, so strong performance narrows AIPCS's claim rather than invalidating it. |
| Add optional H6 vanilla/research-enabled baseline | This tests whether a fresh agent can reconstruct comparable synthesis without supplied memory. It does not require special sequencing and should not block H4/H5. |
| Treat `closeout04` as a positive H4 AIPCS discrimination result | The agent used AIPCS immediately, retrieved broadly but rationally, and explicitly declined unsupported near-neighbor claims. The paired `closeout05` flat-memory run is still needed before making comparative claims. |
| Treat `closeout05` as a strong H5 curated-artifact comparator, not a flat-memory failure | The flat memory artifact was analytically rich, highly task-aligned, and substantial: 5,391 words / 33,149 bytes distilled from five sources. It handled the same null/near-neighbor probes well, so the AIPCS claim should focus on structured durability, queryability, provenance, scale, and evolution rather than one-off output quality. |
| Treat `closeout06` as a model-capability baseline, not a memory baseline | Claude can synthesize well from general knowledge for these well-known figures. The AIPCS comparison should therefore emphasize bounded corpus continuity, provenance, and reusable prior interpretation rather than generic essay competence. |
| Avoid implementation changes during the batch | The batch is for evidence collection; new implementation changes would reset the baseline. |

## Validation

```bash
bash scripts/validate-harness.sh
```

## Risks

| Risk | Mitigation |
|---|---|
| Source-only dominates quality | Compare quality per context/time and use source-only as the ceiling, not as a strawman. |
| Flat memory performs well | Treat it as a real baseline; the paper should state where AIPCS is worth the extra machinery. |
| AIPCS retrieves broadly | Score whether broad retrieval was rational for corpus size; do not overfit to tag usage. |
| Native/cloud memory leaks context | Score only facts attributable to the active representation; record visible memory signals as confounds. |
| Planning becomes stale before completion | Only the five-run batch is planned in detail; optional later runs remain deliberately high-level. |

---
