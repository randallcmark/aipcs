# Runs018-021 — Bootstrap Orientation Scalability Summary

## Classification

Controlled synthetic bootstrap/orientation scalability ladder.

## Purpose

Measure whether Claude can use AIPCS naturally as the synthetic store scales along separate axes:

- `run018`: small control
- `run019`: service breadth
- `run020`: schema verbosity
- `run021`: record volume

All four runs used the same first prompt:

```text
I need to make a decision based on what is already known. Review the available context and recommend the next step, citing what shaped your answer.
```

The expected answer was to continue bootstrap/orientation scalability measurement and include cost/value accounting before broad comparator work.

## Result Matrix

| Run | Axis | Store Shape | Bootstrap / Payload Signal | Retrieval Behavior | Outcome |
|---|---|---|---|---|---|
| `run018` | Small control | 3 services, 2 entities/service, 30 records | Described as substantial but consumable | Selected target services and retrieved active ground-truth records | Pass |
| `run019` | Service breadth | 25 services, 2 entities/service, 250 records | 293,845 characters / 9,313 lines; saved to file | Sampled plausible but wrong services, missed target services | Fail: service-selection degradation |
| `run020` | Schema verbosity | 5 services, 5 entities/service, 125 records, verbose attributes | 437,609 characters / 6,783 lines; saved to file | Retrieved from all services and found target records despite friction | Pass with severe cost/friction |
| `run021` | Record volume | 5 services, 2 entities/service, 1,000 records | Claude reported 77.6 KB; saved/truncated then read | Stopped after bootstrap and recommended a search rather than executing retrieval | Fail/incomplete: retrieval not performed |

## Run018 Notes

`run018` validated the harness and seed manifest. Claude called bootstrap, selected `run018_01_research_planning` and `run018_02_lab_operations`, retrieved active high-priority target records, and recommended continuing orientation scalability with cost/value accounting.

Important caveat: Claude UI reported one recalled memory, but it did not appear load-bearing. Login was required and the model was set to Sonnet 4.6 before the first prompt.

## Run019 Notes

`run019` is the first clear degradation point. The target services were:

- `run019_07_media`
- `run019_18_lab_operations`

Claude instead sampled:

- `agent_behavior`
- `personal_context`
- `project_tracking`
- `authority_context`

It found only background/distractor records in those sampled services and concluded no active ground truth existed. That conclusion was wrong against the seed manifest: target records existed but were not inspected.

This is useful evidence. Service breadth made exhaustive orientation unattractive, and the oversized bootstrap pushed Claude into file/grep sampling. The failure was not hallucination over irrelevant records; it was missed relevant service selection.

## Run020 Notes

`run020` showed that schema verbosity creates severe overhead but does not necessarily break answer quality at moderate service count. Claude reported the bootstrap as roughly 437K characters and explicitly said schema descriptions were repeated and non-load-bearing.

Despite the friction, Claude retrieved active ground-truth records from the target services and answered correctly. This strongly supports the implementation conclusion that full attribute descriptions belong behind `aipcs_service_inspect`, not in bootstrap.

## Run021 Notes

`run021` showed a different failure mode. Record volume did not inflate bootstrap as severely as schema verbosity, but Claude stopped at bootstrap metadata and proposed a retrieval plan instead of executing it.

The target services were:

- `run021_01_research_planning`
- `run021_03_paper_positioning`

Claude recommended searching:

- `run021_04_agent_behavior`
- `run021_05_personal_context`

It retrieved no records. This is an incomplete/fail result against the scoring rubric, but the cause is partly prompt/harness behavior: Claude treated the answer as "the next step is to search" rather than performing bounded retrieval before answering.

## Interpretation

The runs establish that the current bootstrap design begins to degrade before the store is genuinely large.

The clearest findings:

- Small stores work.
- Service breadth can cause missed relevant services even with compact schemas.
- Schema verbosity drives large bootstrap payloads and turns bootstrap into a file/grep directory rather than an orientation map.
- Record volume alone is less damaging to bootstrap, but it can make the agent cautious and stop before retrieval.

This supports the design change already suspected from the organic media-recommendation transcript: bootstrap should be a compact orientation tier, and full schema/attribute detail should move to inspect-layer tools.

## Follow-Up

- Prioritise a slim-bootstrap implementation or variant before continuing with organic high-volume runs.
- Repeat at least `run019` and `run020` against slim bootstrap to determine whether the failure is implementation payload design rather than AIPCS as a pattern.
- For future record-volume runs, adjust the close of the first prompt or add an explicit continuation prompt so the agent performs bounded retrieval rather than stopping after recommending retrieval.
- Preserve `run022` and `run023` as ecological-validity runs, but avoid interpreting organic failures until bootstrap orientation is made compact enough to consume.

## Run019b Slim-Bootstrap Rerun

`run019b` reran the `run019` service-breadth fixture after the slim-bootstrap implementation landed in `aipcs-server` commit `2edda69`.

The ergonomic result improved:

- Bootstrap returned inline/readable rather than being written to a file.
- Claude did not use file reads, grep, or Bash extraction to understand service IDs.
- Claude used the new `aipcs_service_summary` layer with `sample=2`.
- No tool errors or payload truncation were reported.

The behavioral result did not pass the ground-truth target:

- Target services in the seed manifest were `run019_07_media` and `run019_18_lab_operations`.
- Claude selected `project_tracking`, `research_planning`, `paper_positioning`, `personal_context`, and `agent_behavior`.
- It sampled only non-target services and concluded the store contained no authoritative records.
- It did not call `aipcs_record_search` or `aipcs_record_list`.

This result should be interpreted carefully. Slim bootstrap fixed the original payload/workaround problem, but service selection still failed. The fixture also places target records in services that are not semantically obvious for the prompt. The run therefore exposes two remaining issues:

- Service metadata may still be insufficient to surface target-bearing branches under high service breadth.
- `service_summary(sample=2)` can reinforce a false absence conclusion when relevant records are not in the first samples.

The next slim-bootstrap validation should include `run020b`, then either revise the service-breadth fixture or add a variant where target records are discoverable through declared facet counts or semantically plausible service placement.

## Run020b Slim-Bootstrap Rerun

`run020b` reran the `run020` schema-verbosity fixture after the slim-bootstrap implementation landed in `aipcs-server` commit `2edda69`.

This is a clean before/after success:

- Bootstrap returned inline and was described by Claude as lightweight and fast.
- No file dump, grep, Bash extraction, or chunked reading was needed.
- Claude used bootstrap as a shape-only map across all 5 services.
- Claude called `aipcs_record_list` three times in parallel.
- It retrieved `RUN020-S02-NOTE_01-R003` and `RUN020-S02-NOTE_01-R004`.
- It recommended orientation scalability with cost-value accounting, matching the seed ground truth.

Compared with the original `run020`, the behavior changed from "correct answer despite severe payload friction" to "correct answer with normal discovery flow."

The remaining caveat is coverage depth. Claude retrieved `note_01` from three services and did not inspect later entities. That was sufficient because the fixture placed decisive records in `note_01` of `run020_02_lab_operations`. A future harder synthetic variant could move targets into later entities, but the current result is enough to show that the schema-verbosity payload problem has been addressed.

## Current Conclusion After Slim Bootstrap

The slim-bootstrap implementation solved the most concrete implementation bottleneck:

- `run019b`: payload and workaround problem fixed, but service selection still failed in a harsh/unnatural fixture.
- `run020b`: payload problem fixed and target retrieval/answer quality passed.

The next useful step is not more artificial synthetic stress unless a specific question is being tested. A sanitised organic corpus should give better evidence about whether agent-authored memory remains useful when services and records are plausible rather than obviously synthetic.

## Evidence Artifacts

Raw artifacts are stored on `aipcs-lab`:

```text
/opt/aipcs-lab/runs/run018/artifacts/
/opt/aipcs-lab/runs/run019/artifacts/
/opt/aipcs-lab/runs/run020/artifacts/
/opt/aipcs-lab/runs/run021/artifacts/
/opt/aipcs-lab/runs/run019b/artifacts/
/opt/aipcs-lab/runs/run020b/artifacts/
```

Each directory contains:

- `terminal.typescript`
- `claude-export.txt`
- `seed-output.json`
- `observer-notes.md`
- `aipcs-final/`
- AIPCS server and MCPO logs
