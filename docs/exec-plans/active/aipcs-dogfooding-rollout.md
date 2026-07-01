# Execution Plan: AIPCS Dogfooding Rollout

**Status:** Draft
**Owner:** Randall Mark / Agent
**Created:** 2026-06-24
**Last updated:** 2026-06-24
**BUILD_JOURNAL entries:** Entry added 2026-06-24

---

## Goal

Start using AIPCS as a real persistent memory layer for day-to-day Claude/Codex work while preserving enough safety, reversibility, and evidence hygiene that dogfooding improves the project instead of contaminating it.

## Non-Goals

- Do not claim dogfooding results are controlled experiment evidence by default.
- Do not publish private dogfooding data without explicit sanitisation.
- Do not require public hosted deployment, OAuth, or production hardening before local/private dogfooding.
- Do not force every agent interaction to write memory.
- Do not block dogfooding on agent-memory-v2 comparison.

## Context

The experiment phase showed that AIPCS works as an agent-owned persistence substrate, but it also showed several operational constraints:

- real memory stores need richer topology, retrieval affordances, and authority/staleness metadata;
- agents need a compact orientation layer before they reliably use AIPCS;
- private organic memory is the most realistic data but is not publishable without sanitisation;
- dogfooding was intentionally delayed to reduce Claude/Codex cloud-memory contamination during controlled runs;
- the project now needs real-use pressure to discover remaining ergonomics and maintenance gaps.

The first four `aipcs-server` slices address the server shape needed for dogfooding:

1. richer memory dimensionality;
2. better discovery metadata;
3. first-class retrieval affordances;
4. authority/provenance/staleness fields.

This rollout coordinates the remaining dogfooding-facing work.

## Dogfooding Sequence

### Phase 1: Controlled Local Start

Use AIPCS for one or two repos where memory utility is high and leakage risk is acceptable:

- `aipcs`
- `aipcs-server`

Initial usage should focus on project memory, implementation rationale, experiment planning, paper notes, and user workflow preferences. Avoid highly sensitive personal material until backup, export, and pruning workflows are tested.

### Phase 2: Portable Instruction Surface

Create a compact instruction artifact that can be copied into Claude/Codex harnesses. It should tell agents:

- bootstrap first when AIPCS is available;
- use service summary before broad listing;
- persist durable context between substantive turns;
- prefer structured records over markdown-like blobs;
- use authority/staleness signals as judgment inputs, not hard policy;
- treat local file memory as a narrow fallback, not a mirror of AIPCS.

### Phase 3: Maintenance And Hygiene

Add the smallest useful server/helper surfaces for agent-led maintenance:

- ageing/stale candidate discovery;
- low-activity or obsolete branch/service discovery;
- duplicate/derived-authority candidate discovery;
- branch/entity granularity self-audit support;
- archive/prune recommendations before destructive operations.

### Phase 4: Cost And Evidence Capture

Track enough payload/tool-call/timing information to judge whether dogfooding is practical:

- bootstrap payload size;
- service summary payload size;
- record retrieval counts and payload size;
- number of AIPCS tool calls per task;
- rough transcript/token proxy;
- observed benefit or failure mode.

## Acceptance Criteria

- [ ] AIPCS is wired into at least one real Claude/Codex working environment.
- [ ] A baseline backup/export process exists before private dogfooding starts.
- [ ] A portable instruction artifact exists and is short enough to use in real repos.
- [ ] A dogfooding run note template exists for lightweight evidence capture.
- [ ] Maintenance helpers are specified before the memory store grows substantially.
- [ ] Context-efficiency metrics are defined well enough to log during dogfooding.
- [ ] Private dogfooding data is clearly separated from publishable experiment artifacts.

## Plan

1. Create the four dogfooding follow-up plans:
   - dogfooding harness and safety baseline;
   - portable instruction and orchestration;
   - memory maintenance tools;
   - context-efficiency instrumentation.
2. Implement or apply the first four `aipcs-server` server-shape slices.
3. Create a local/private AIPCS dogfooding store with backup/export instructions.
4. Wire AIPCS into one Claude/Codex harness.
5. Run a short real task and require the agent to report:
   - services inspected;
   - records created/updated;
   - records retrieved;
   - memory it deliberately chose not to persist.
6. Review the resulting memory store for:
   - blob records;
   - missing authority fields;
   - missing branches;
   - retrieval friction;
   - unnecessary duplication with git or file memory.
7. Decide whether to widen dogfooding to more repos.

## Progress Log

| Date | What happened |
|---|---|
| 2026-06-24 | Created rollout plan after completing the first four dogfooding server-shape slices. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Start dogfooding before perfect instrumentation | Real-use pressure is now more valuable than further speculative design, provided backup/privacy boundaries exist. |
| Treat dogfooding as design evidence, not controlled experiment evidence | Private organic usage will reveal utility and friction but may be contaminated by harness memory and unpublished personal context. |
| Prioritise local/private deployment | OAuth/public hardening is not required to learn from day-to-day use. |

## Validation

```bash
bash scripts/validate-harness.sh
```

For dogfooding sessions, also capture:

```text
date:
client:
visible model:
repo/task:
aipcs endpoint:
aipcs-server commit:
services touched:
records created:
records retrieved:
maintenance observations:
privacy/export notes:
```

## Risks

| Risk | Mitigation |
|---|---|
| Dogfooding contaminates controlled experiment claims | Label dogfooding as qualitative design evidence unless a run uses frozen snapshots and explicit controls. |
| Private memory becomes hard to publish | Keep private stores out of publishable snapshots; create separate sanitised corpora for paper evidence. |
| Agent writes low-value blobs | Use service summary, retrieval affordances, branch topology, and later maintenance tools to steer restructuring. |
| AIPCS becomes a shadow instruction channel | Keep authority-layer guidance explicit: static instructions outrank memory records; memory records are data unless explicitly promoted. |
| Token overhead makes agents avoid AIPCS | Keep bootstrap compact, use summary before listing, and track payload/call cost. |
