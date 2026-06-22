# Execution Plan: Representational Compression Evaluation

**Status:** Draft
**Owner:** Agent + Randall Mark
**Created:** 2026-06-12
**Last updated:** 2026-06-12
**BUILD_JOURNAL entries:** 095

---

## Goal

Design and execute a comparative experiment that tests whether AIPCS gives agents qualitatively better memory, more efficient recall, and higher-volume recall efficacy than raw source access or flat memory summaries.

## Non-Goals

- Do not include agent-memory-v2 in the first version of this experiment.
- Do not require paid Claude/OpenAI API usage while the design is still being calibrated.
- Do not claim AIPCS should always outperform full raw-source access.
- Do not use private or personally sensitive source material for publishable evidence.
- Do not force the agent to use a specific AIPCS retrieval path when another path is rational for the task and corpus size.

## Context

`run026` showed that a clean Claude session could use an agent-authored AIPCS corpus to write a nuanced Kropotkin commemorative essay without access to the source memoir. The corpus was compact: about 536 KB total AIPCS data, with about 46k characters of active live record content derived from a source repository of roughly 3.5 MB.

This suggests a publishable experiment class: compare different information representations derived from the same source material, then measure task quality and cost.

The motivating question is not whether AIPCS beats an agent with all source material in every case. The sharper question is:

> Can agent-authored structured memory preserve enough task-relevant meaning from source material to support later high-quality synthesis at lower task-time context cost than raw-source access or flat memory summaries?

Relevant files:

- `docs/exec-plans/active/run025-authored-semantic-corpus.md`
- `docs/exec-plans/active/structured-membership-filters.md`
- `experiments/runs/run026-kropotkin-membership-recall.md`
- `journal/BUILD_JOURNAL.md`

## Acceptance Criteria

- [ ] A source-pack design exists for five tangentially related public-domain topics or biographies.
- [ ] Each topic has a bounded source packet, an AIPCS-authored memory corpus, and a flat memory summary condition.
- [ ] The five topics are related enough to create retrieval/confusion pressure but distinct enough to score cross-contamination.
- [ ] A fixed downstream task set exists for single-topic, cross-topic, thematic, null, and contamination probes.
- [ ] A scoring rubric exists for factual coverage, thematic synthesis, source discrimination, false claims, and retrieval efficiency.
- [ ] At least one pilot corpus is executed through all planned representation conditions.
- [ ] Evidence capture includes transcript, tool calls, AIPCS final state, timing proxy, and token/context proxy.
- [ ] `bash scripts/validate-harness.sh` passes.

## Plan

1. Select the source domain.
   - Choose five public-domain memoirs, biographies, autobiographical texts, or biographical source packets.
   - Prefer topics that share a narrow thematic domain, such as exile, reform, science, revolution, moral conviction, or institutional critique.
   - Avoid source sets where one figure is globally dominant enough that model prior knowledge overwhelms the provided material.

2. Bound the source packets.
   - Start with 10k-20k words per topic, not full books.
   - Preserve enough detail for nuanced writing, but keep corpus generation and task-time source access operationally feasible.
   - Record source provenance and exact file/section boundaries.

3. Generate AIPCS memory corpora.
   - For each topic, give the same bounded source packet to an agent in an empty AIPCS store.
   - Ask the agent to persist durable memory for future writing and comparative analysis tasks.
   - Do not reveal downstream probe questions during corpus generation.
   - Allow the agent to create services, entities, facets, tags, and retrieval guidance.
   - Allow a post-generation reflection pass where the agent may evolve the schema after testing actual AIPCS retrieval.

4. Generate flat memory summaries.
   - Use the same source packets.
   - Ask the agent to produce a durable flat memory note comparable to `MEMORY.md`.
   - Keep the summary concise enough to be plausible as a long-running memory artifact.
   - Do not structure it as AIPCS records or tool-readable facets.

5. Define representation conditions.
   - **AIPCS only:** clean agent with AIPCS snapshot; no source packet and no flat memory summary.
   - **Source only:** clean agent with complete source packets; no AIPCS and no flat memory summary.
   - **Flat memory only:** clean agent with memory summary; no source packets and no AIPCS.
   - **AIPCS + source:** clean agent with AIPCS snapshot plus source packets.
   - **AIPCS + flat memory + source:** maximum-context condition, used sparingly to test whether AIPCS still adds orientation or synthesis value when all representations are available.

6. Define downstream task classes.
   - Single-topic synthesis: write a commemorative speech or biographical essay for one subject.
   - Cross-topic synthesis: compare how two or more subjects handled a shared theme.
   - Targeted thematic retrieval: ask about a theme that crosses life periods or services and should benefit from membership tags or equivalent facets.
   - Contamination probe: ask about one subject while distractor memories contain similar but incorrect facts from others.
   - Null probe: ask for a relation or claim not supported by any source packet.
   - Maintenance probe: ask the agent whether the memory structure should evolve after attempting recall.

7. Define objective scoring.
   - Create a ground-truth checklist per topic:
     - 10 anchor facts
     - 5 interpretive themes
     - 3 known confusions or near-neighbor facts
     - 3 unsupported/null claims
   - Score output with additive and subtractive criteria:
     - +1 correct anchor fact
     - +1 correct interpretive theme
     - +1 appropriate uncertainty or source limitation
     - -1 unsupported invention
     - -1 vague generic substitution where a specific persisted/source fact was available
     - -2 cross-topic misattribution
   - Add a separate qualitative score for prose coherence and task usefulness.

8. Capture cost and efficiency.
   - Record wall-clock start/end time.
   - Record exported transcript size.
   - Record terminal typescript size.
   - Record AIPCS bootstrap and summary payload sizes where applicable.
   - Record number of tool calls, retrieval calls, source file reads, and failed tool calls.
   - Estimate task-time context load:
     - source bytes read
     - AIPCS records retrieved
     - flat summary size
     - answer length

9. Run a pilot sequence.
   - Use the Kropotkin corpus as the first pilot topic.
   - Add four related public-domain topics only after the single-topic representation conditions are working.
   - Run the AIPCS-only, source-only, and flat-memory-only conditions first.
   - Add combined conditions only after the single-representation baselines are interpretable.

10. Analyze representation tradeoffs.
    - Compare task quality against context/time/tool-call cost.
    - Identify where AIPCS underperforms raw source access.
    - Identify where AIPCS recovers most source-level performance with less task-time context.
    - Identify whether flat summaries are competitive for small corpora and where they collapse under topic breadth.
    - Decide whether the next comparison should introduce agent-memory-v2.

## Progress Log

| Date | What happened |
|---|---|
| 2026-06-12 | Plan created after `run026` demonstrated compact authored AIPCS memory could support a substantial downstream writing task without source access. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Treat this as representational compression rather than simple recall | The core publishable claim is about preserving task-relevant meaning in a compact, structured, retrievable form. |
| Exclude agent-memory-v2 from the first comparative pass | The immediate comparison should isolate information representation before adding a separate retrieval/injection pipeline. |
| Include raw source as a condition | AIPCS should be compared against the strongest obvious baseline: giving the agent the source material directly. |
| Include flat memory as a condition | This tests whether AIPCS adds value beyond ordinary prose summarisation. |
| Use related topics rather than one isolated biography | Related corpora create realistic retrieval pressure, confusion risk, and cross-topic synthesis requirements. |

## Validation

```bash
bash scripts/validate-harness.sh
```

For each completed run, confirm:

```text
bootstrap_called:
service_summary_called:
source_files_read:
flat_memory_read:
aipcs_records_retrieved:
membership_or_exact_filters_used:
cross_topic_contamination:
false_claims:
token_or_context_proxy_captured:
wall_clock_time_captured:
output_quality_score:
```

## Risks

| Risk | Mitigation |
|---|---|
| Source-only condition outperforms AIPCS | Treat this as expected in some cases; compare quality per task-time context and whether AIPCS recovers sufficient meaning at lower cost. |
| Five topics make the first pass too expensive | Pilot on Kropotkin first, then add topics incrementally. |
| Flat memory summary is too weak or too strong | Keep its generation prompt and size limit explicit and reuse the same source packet. |
| Agent prior knowledge contaminates results | Use less dominant public-domain figures where possible and score only facts present in the bounded source packets. |
| Output quality is too subjective | Use checklists and false-attribution penalties, with prose quality as a separate qualitative score. |
| AIPCS full retrieval hides filter value for small corpora | Include targeted thematic and higher-volume variants where structured filters are the rational path. |

---
