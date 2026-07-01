# Execution Plan: Context Efficiency Instrumentation

**Status:** Draft
**Owner:** Agent
**Created:** 2026-06-24
**Last updated:** 2026-06-24
**Target repos:** `/Users/markrandall/GitHub/aipcs`, optionally `/Users/markrandall/GitHub/aipcs-server`
**BUILD_JOURNAL entries:** Entry added 2026-06-24

---

## Goal

Define and capture lightweight context-efficiency evidence during dogfooding and future experiments, so AIPCS overhead can be judged against the value it provides.

## Non-Goals

- Do not claim exact token accounting unless the client exposes exact token data.
- Do not block dogfooding on perfect measurement.
- Do not require paid API instrumentation.
- Do not instrument private content in a way that makes it publishable by accident.
- Do not optimise prematurely before measuring obvious payload/tool-call costs.

## Context

Experiments showed that AIPCS can improve persistence and recall, but it costs tool calls, bootstrap payload, service summaries, schema design, and explicit record retrieval. The right claim is not "AIPCS is always cheaper"; it is "AIPCS can justify its overhead when durable, structured, high-fidelity memory improves later work."

The paper and dogfooding need a pragmatic metric.

## Working Definition

Context efficiency should be reported as a composite, not a single universal number:

```text
context_efficiency =
  useful memory applied
  relative to
  discovery + retrieval + persistence + maintenance overhead
```

For each run/task, capture:

- AIPCS tool calls by type;
- bootstrap response size;
- service summary response size;
- record count retrieved;
- approximate retrieved JSON size;
- number of records created/updated;
- visible task outcome benefit;
- whether the agent avoided re-reading source files or re-asking the user;
- false positives or irrelevant memory use.

## Minimum Metrics

Use cheap proxies first:

```text
bootstrap_json_chars:
service_summary_json_chars:
retrieved_record_count:
retrieved_json_chars:
aipcs_tool_call_count:
persistence_tool_call_count:
maintenance_tool_call_count:
task_elapsed_minutes:
source_files_read_count:
output_quality_note:
memory_utility_note:
```

If exact client token usage is visible, also record it. If not, use character counts and transcript notes.

## Acceptance Criteria

- [ ] A context-efficiency note template exists.
- [ ] The template can be filled from transcripts and AIPCS outputs without paid API access.
- [ ] The metric distinguishes persistence cost, retrieval cost, and maintenance cost.
- [ ] The metric records benefit as qualitative outcome evidence, not only payload size.
- [ ] Dogfooding notes can use the same fields.
- [ ] The paper can cite the metric definition honestly as approximate.

## Plan

1. Add a reusable context-efficiency template under experiment/runbook docs.
2. Use it for dogfooding notes before building automation.
3. If repeated manual capture is painful, add a small helper script later to measure JSON artifacts.
4. Track before/after cases:
   - raw source/file use;
   - flat memory file use;
   - AIPCS persisted memory use;
   - AIPCS with maintenance/retrieval affordance improvements.
5. Use results to decide where optimisation matters.

## Template

```text
## Context Efficiency Note

Run/task:
Date:
Client/model:
AIPCS store/snapshot:

bootstrap_json_chars:
service_summary_json_chars:
retrieved_record_count:
retrieved_json_chars:
aipcs_tool_call_count:
persistence_tool_call_count:
maintenance_tool_call_count:
source_files_read_count:
task_elapsed_minutes:

Useful memory applied:
Irrelevant memory retrieved:
False positives:
Source/user re-explanation avoided:
Observed friction:
Outcome quality note:
```

## Validation

```bash
bash scripts/validate-harness.sh
```

Manual validation:

```text
1. Can the template be filled from an exported transcript?
2. Does it distinguish cost from utility?
3. Does it avoid exposing private content?
4. Does it help decide whether a server/tool improvement is needed?
```

## Risks

| Risk | Mitigation |
|---|---|
| Metrics become fake precision | Label character counts and tool calls as proxies unless exact token data exists. |
| Cost focus obscures memory quality | Always pair cost fields with utility and false-positive notes. |
| Manual capture is skipped | Keep the first template small; automate only after repeated use shows the pain point. |
| Private transcripts leak through metrics | Capture counts and notes, not raw private record content. |
