# Execution Plan: Run025 Authored Semantic Corpus

**Status:** Draft
**Owner:** Agent + Randall Mark
**Created:** 2026-06-12
**Last updated:** 2026-06-12
**BUILD_JOURNAL entries:** 090

---

## Goal

Create a privacy-preserving, agent-authored AIPCS corpus with plausible semantic facts and known ground truth, suitable for testing recall quality rather than only service selection.

## Non-Goals

- Do not publish raw personal source material.
- Do not build a full public dataset disclosure process in this slice.
- Do not compare against agent-memory-v2 in this slice.
- Do not optimise AIPCS implementation behavior unless corpus generation exposes a blocking bug.
- Do not make the generated corpus self-label as synthetic or fictional in agent-visible record fields.

## Context

- `run024e` proved the corrected sanitised organic corpus can be loaded and queried through AIPCS.
- `run024f` showed Claude autonomously used AIPCS under weak scaffolding, but downweighted the records because their values explicitly said they were generated fictional placeholders.
- The current `sanitised-organic-v1` corpus preserves service/entity shape, counts, timestamps, and retrieval mechanics, but does not preserve enough semantic signal for exact recall tests.
- The next corpus must be fictionalised but plausible: invented details should behave like real collaboration memory, not like labelled fixtures.

Relevant files:

- `experiments/runbooks/sanitised-organic-corpus.md`
- `experiments/snapshots/sanitised-organic-v1.md`
- `experiments/runs/run024e-sanitised-organic-corpus.md`
- `experiments/runs/run024f-normal-prompt-sanitised-organic.md`
- `journal/BUILD_JOURNAL.md`

## Acceptance Criteria

- [ ] A private source packet exists outside git or in a clearly non-sensitive draft location.
- [ ] A fictionalised source packet exists with stable substitutions for people, places, systems, dates, identifiers, and relationships.
- [ ] A consistency audit confirms substituted names, dates, relationships, and system references do not drift.
- [ ] An agent-owned AIPCS persistence session creates or evolves services from the fictionalised packet without direct scripted row insertion for the main memory content.
- [ ] The generated corpus contains enough known facts to score recall objectively.
- [ ] The corpus avoids agent-visible labels such as "synthetic", "fictional", "sanitised", or "generated for experiments" inside memory records.
- [ ] A private ground-truth file maps probe questions to expected answers and source records.
- [ ] A `run025` snapshot manifest and run note are created.
- [ ] `bash scripts/validate-harness.sh` passes.

## Plan

1. Define corpus requirements.
   - Decide target domains: experiment history, implementation project, lab operations, agent behavior, and one plausible distractor domain.
   - Decide minimum ground truth: 20-30 authored facts, including direct, inferential, stale/conflicting, and null-probe cases.
   - Decide which facts must be cross-service, so the agent has to choose between services or combine records.

2. Build private source packets.
   - Use real enough inputs to preserve natural complexity: AIPCS run history, implementation notes, lab setup, and selected prior conversation summaries.
   - Keep raw personal details private.
   - Write source packets as narrative material, not as database rows.

3. Fictionalise source packets.
   - Replace names, locations, domains, hostnames, repo names, IPs, exact dates, and sensitive personal details.
   - Preserve causal order, recurrence, constraints, relative age, and relationship structure.
   - Preserve technical shape where it matters: service names, schema names, command patterns, tool behavior, failure modes, and file/module analogues.
   - Keep a private transformation map if needed; do not publish it.

4. Audit fictionalisation consistency.
   - Check that each renamed person/system/place is used consistently.
   - Check that date ordering and "stale" semantics remain coherent.
   - Check that no record text announces itself as synthetic.
   - Check that no original personal identifiers remain.

5. Run agent-owned persistence into an empty AIPCS store.
   - Start from a clean lab run and empty AIPCS data directory.
   - Provide the fictionalised source packet to the agent.
   - Instruct the agent to use AIPCS as its memory system and persist what it believes will help future sessions.
   - Allow the agent to create/evolve services and choose schema shape.
   - Avoid showing the later probe questions.

6. Inspect the generated corpus.
   - Use bootstrap and service summaries to check service shape.
   - Confirm records exist for all target facts.
   - Confirm the agent did not simply paste source packets verbatim.
   - Confirm record fields support retrieval: source/provenance/status/topic/date where available.

7. Repair only if necessary.
   - If the corpus is missing critical facts, run a second agent pass with additional source material.
   - If the service design is unusably flat, let the agent review and evolve its own schema.
   - Avoid manual row edits except for mechanical owner/endpoint/snapshot compatibility.

8. Snapshot and score.
   - Archive the final AIPCS data directory as `authored-semantic-v1`.
   - Create a snapshot manifest.
   - Create a private ground-truth file for probes.
   - Run `run025` against the snapshot with normal weak scaffolding.

## Progress Log

| Date | What happened |
|---|---|
| 2026-06-12 | Plan created after `run024f` showed shape-preserving sanitisation is insufficient for recall-quality evaluation. |
| 2026-06-12 | Claude generated a `kropotkin_memoir` corpus from a public-domain memoir source, then evolved it after a retrieval-path audit to add exact-match `primary_topic` and `salience` facets. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Use agent-owned persistence rather than scripted main-content insertion | The AIPCS claim depends on agent-selected, agent-shaped memory, not just a hand-built database. |
| Keep synthetic labels out of record bodies | `run024f` showed Claude correctly downweights records that announce themselves as generated fixtures. |
| Preserve bursty timestamps as legitimate | Batch persistence is realistic for imports, pre-compaction writes, document ingestion, and retrospective summarisation. |
| Let the agent refine its own memoir schema under current tooling | The first-pass Kropotkin corpus was useful but had non-filterable comma-separated tags; the agent audited actual AIPCS retrieval and evolved exact-match fields instead of waiting for future membership search. |
| Score with private ground truth | Published transparency may later require a public fixture, but the immediate experiment needs controlled answers without leaking private source data. |

## Validation

```bash
bash scripts/validate-harness.sh
```

For generated snapshots:

```bash
python3 - <<'PY'
import pathlib
root = pathlib.Path("experiments/snapshots/authored-semantic-v1-data/.data")
bad = []
for needle in ["synthetic", "fictional", "generated for", "sanitised", "Mark", "markrandall", "/Users/", "indigo-blocks"]:
    hits = []
    for path in root.rglob("*.sqlite"):
        if needle.lower() in path.read_bytes().decode("latin-1", errors="ignore").lower():
            hits.append(str(path))
    print(needle, len(hits))
    if hits and needle in {"Mark", "markrandall", "/Users/", "indigo-blocks"}:
        bad.extend(hits)
raise SystemExit(1 if bad else 0)
PY
```

## Risks

| Risk | Mitigation |
|---|---|
| Fictionalisation removes too much semantic signal | Use narrative source packets and preserve relationships, constraints, and causal order. |
| Corpus leaks private data | Run marker scans and manual spot checks; keep raw source and transformation map private. |
| Agent persists prose blobs instead of structured records | Let it self-review schema after first pass; only repair through agent-led evolution unless mechanically blocked. |
| Agent overfits to experiment framing | Do not reveal probe questions during corpus generation. |
| Timestamp clustering is mistaken as artificial | Do not instruct agents to use timestamp spread as a realism criterion; include provenance/status fields where natural. |

---
