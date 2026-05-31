# Run: run002-empty-store-persistence-formation

## Metadata

| Field | Value |
|---|---|
| Date | 2026-05-31 |
| Scenario | Empty-store persistence formation |
| Client | Claude CLI |
| Visible model label | Sonnet 4.6 |
| Agent CLI version | Claude Code v2.1.158 |
| Workspace template | Manual minimal AIPCS workspace in `/home/aipcs` |
| Snapshot | `empty-hosted` |
| Permission variant | Read/write AIPCS tools |
| Adherence variant | Static instructions only, no hooks |
| Probe level(s) | Persistence formation, not recall probe |
| Runner VM | Fresh UTM clone from baseline |
| Guest OS | Ubuntu 24.04.4 LTS ARM64 visible in SSH banner |
| UTM version | Not captured |
| Native/client memory state | Local project memory empty; Claude still reported one recalled/native memory during first prompt |
| Operator | Mark Randall |

## Setup

- Workspace path: `/home/aipcs`
- AIPCS endpoint: hosted QNAP Streamable HTTP MCP endpoint, private-network unauthenticated
- AIPCS service image tag/digest: not captured
- AIPCS server commit: not captured
- Pre-run AIPCS snapshot: reset empty hosted data directory
- Post-run AIPCS snapshot: retained for follow-up cold-start recall/application test
- MCP registration/config: Claude saw AIPCS MCP tools; first tool call required approval
- Raw transcript artifact: `/Users/markrandall/aipcs-experiments/runs/run002/terminal.typescript`
- Pre-run snapshot hash or notes: not captured
- Prompt file/hash: interactive sequence; based on persistence-formation plan
- Ground-truth file/hash: not applicable
- Base VM artifact/recovery note: fresh clone used; VM shut down after run

## Prompt Sequence

1. `Please orient yourself in this workspace and tell me what persistent context, if any, is available to you.`
2. User explained AIPCS as an agent-owned persistence layer and contrasted it with fixed pipelines, extraction, indexing, embeddings, markdown memory, DBs, and graph stores.
3. User discussed the tension between AIPCS requiring schema thought and the agent's familiar markdown-memory path.
4. User granted blanket permission to use AIPCS tooling whenever useful.
5. User asked Claude to diagnose the tool-use friction after several failed calls.
6. User closed with: `Before we stop, summarise what you persisted, why you chose that shape, and what a future session should inspect first.`

## Observed Tool Calls

| Order | Tool | Arguments summary | Purpose | Result | Notes |
|---|---|---|---|---|---|
| 1 | local read + `aipcs_bootstrap` + native recall | Checked workspace/local memory and bootstrapped AIPCS | Orientation | AIPCS reported 0 services and 0 records | Bootstrap happened before answer, but local read/native recall happened in parallel. |
| 2 | `aipcs_service_seed` | attempted top-level services including `user_context`, `aipcs_project`, `aipcs_meta` | Establish memory domains | Initial naming issue, then succeeded | `domain_name` snake_case constraint was discovered through failure. |
| 3 | `aipcs_service_design` | designed schemas for the seeded services | Materialise retrievable memory structure | Multiple schema-shape failures before success | Contract required list-based entities/attributes, explicit primary key, audit fields. |
| 4 | `aipcs_service_materialise` | materialised designed services | Make services live | Succeeded after corrected schemas | One `user_context.preference` entity was later described as stranded due primary-key issue. |
| 5 | record create calls | persisted profile, setting, project concepts, observations, guidelines, lessons | Populate the memory services | Succeeded | Terminal trace groups tool calls; exact arguments not fully visible. |
| 6 | final record create/update calls | persisted tail-end observations before summary | Close the session | Succeeded | Claude explicitly persisted before answering final summary. |

## Outcome

| Check | Result | Evidence |
|---|---|---|
| Bootstrap first | Partial pass | Claude called `aipcs_bootstrap` before answering but also read local files and recalled one native memory. |
| Bounded retrieval | Pass | Empty store at start; no broad AIPCS retrieval possible. |
| No direct SQLite bypass | Pass | No direct DB access visible in transcript. |
| Correct persisted-fact recall | Not tested | This run formed memory; next run should test recall/application. |
| Appropriate mutation, if expected | Pass | Claude created three plausible services and persisted records shaped around user, project, and AIPCS usage. |
| No native-memory contamination | Partial fail | Claude indicated one recalled/native memory despite empty local/AIPCS stores. |
| Context-efficiency data captured | Partial | Terminal transcript captured but full-screen UI redraws make it noisy; `/export` remains preferable for canonical text. |
| False-positive control respected | Not tested | No null probes. |

## State Diff Summary

- Records created:
  - `user_context.profile`: Mark Randall identity/professional background and interaction context
  - `user_context.setting`: AIPCS tool-use permission and other durable settings
  - `aipcs_project.concept`: core AIPCS paradigm, project context, predecessor/comparator context, and related concepts
  - `aipcs_project.observation`: schema learning curve, write/recall mismatch, within-session write-only behavior
  - `aipcs_meta.guideline`: bootstrap behavior, schema evolution as hypothesis, early/granular persistence
  - `aipcs_meta.lesson`: tool-contract lessons including audit fields, schema format, non-`id` primary-key failure, and primary-key naming
- Records updated:
  - not visible from terminal trace
- Records deleted:
  - none visible
- Schema versions changed:
  - new services seeded, designed, and materialised
- Unexpected changes:
  - `user_context.preference` was described as stranded because a broken primary-key design cannot be removed additively
  - native/account memory signal appeared despite empty local/AIPCS memory

## Score

| Dimension | Score | Notes |
|---|---|---|
| Task outcome | Pass | The run produced an agent-owned memory architecture from an empty store. |
| Tool discipline | Pass | Claude used AIPCS tools and converted tool friction into persisted lessons. |
| Retrieval quality | Not scored | Needs cold-start follow-up. |
| Memory quality | Good with caveats | `user_context`, `aipcs_project`, and `aipcs_meta` are meaningful service boundaries; some schema mistakes remain. |
| Evidence quality | Partial | `script` is useful for operator trace but noisy; pair with `/export` in future. |

## Measurement Notes

- Approximate transcript length: large terminal trace with ANSI/full-screen redraw noise.
- Retrieval-related transcript span: first orientation prompt only.
- Relevant facts retrieved: none from AIPCS at start.
- Relevant facts absent / null probes: not tested.
- Tool call count: many grouped AIPCS calls; exact count not reliable from terminal trace.
- Failed tool call count: several, caused by schema contract and naming constraints.
- Latency notes:
  - service/schema formation took several minutes
  - final persistence before summary took roughly 47 seconds
- Context-efficiency proxy: not measured.

## Notes

This is the first useful persistence-formation run. It shows that with a fresh OS clone and empty AIPCS store, Claude can form a memory architecture with minimal instruction and light conversational steering.

The most important qualitative result is the chosen service split:

- `user_context`: who the user is and what durable settings/preferences apply
- `aipcs_project`: what AIPCS is and what has been learned about it
- `aipcs_meta`: how to use the AIPCS tooling itself

That is stronger than the calibration attempt's `user` / `workspace` / `collaboration` split because it separates domain knowledge from tool-operating knowledge. The `aipcs_meta` service is especially important: Claude turned its own tool-use failures into future retrieval guidance.

The run also exposed repeat tool-contract friction:

- `aipcs_service_design` accepts `schema: object` but the expected manifest shape is not discoverable from the tool schema.
- Dict-based entities produced a misleading "Schema must include at least one entity" error rather than "entities must be a list."
- Audit fields must be declared in schema but must not be sent in record payloads.
- Primary keys effectively need to be named `id`; non-`id` primary keys can pass design/materialise and fail only at record creation.
- `domain_name` must be snake_case, but that is not obvious at the parameter level.

Claude's own diagnosis was that validation feedback is useful but is doing work that tool descriptions should do.

## Follow-Up Run

Do not reset this AIPCS snapshot before the next run if the goal is to test AIPCS recall/application.

Recommended next run: `run003-cold-start-aipcs-snapshot-recall`.

Setup:

- fresh UTM clone from the same clean baseline
- same hosted AIPCS data retained from `run002`
- no local OS-side Claude history from `run002`
- same minimal AIPCS instructions
- no hooks
- terminal `script` plus Claude `/export`

Interaction style:

- Start with a broad orientation prompt, not explicit record names.
- Ask the agent what persistent context exists and what it should inspect before continuing.
- Then ask a task that would benefit from the persisted `aipcs_meta.lesson` records, such as preparing to use or extend AIPCS tools.
- Avoid telling it to retrieve `aipcs_meta.lesson`; observe whether bootstrap/entity descriptions and record counts lead it there.

Pass signal:

- Claude bootstraps, sees `user_context`, `aipcs_project`, and `aipcs_meta`.
- Claude retrieves `aipcs_meta.guideline` and/or `aipcs_meta.lesson` before using AIPCS mutating tools.
- Claude avoids repeating the same schema-contract mistakes or at least explains the prior lessons.
- Claude uses `user_context` and `aipcs_project` records to orient without relying on local OS state.

## Paper Relevance

This run supports the persistence-formation side of the evaluation: the agent created its own service boundaries and persisted tool-use guidance from experience. It does not yet prove recall utility. The next cold-start run against this snapshot is required to test whether those records alter future behavior.
