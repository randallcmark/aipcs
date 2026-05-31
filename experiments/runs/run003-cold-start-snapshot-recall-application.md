# Run: run003-cold-start-snapshot-recall-application

## Metadata

| Field | Value |
|---|---|
| Date | 2026-05-31 |
| Scenario | Cold-start snapshot recall/application |
| Client | Claude CLI |
| Visible model label | Sonnet 4.6 |
| Agent CLI version | Claude Code v2.1.158 |
| Workspace template | Manual minimal AIPCS workspace in `/home/aipcs` |
| Snapshot | `run002-post` retained hosted AIPCS data |
| Permission variant | Read/write AIPCS tools |
| Adherence variant | Static instructions only, no hooks |
| Probe level(s) | Recall/application; schema evolution application |
| Runner VM | Fresh UTM clone from baseline |
| Guest OS | Not captured in export; same UTM Ubuntu baseline family |
| UTM version | Not captured |
| Native/client memory state | Initial prompt failed due Claude login; after login Claude reported one native memory recall signal |
| Operator | Mark Randall |

## Setup

- Workspace path: `/home/aipcs`
- AIPCS endpoint: hosted QNAP Streamable HTTP MCP endpoint, private-network unauthenticated
- AIPCS service image tag/digest: not captured
- AIPCS server commit: not captured
- Pre-run AIPCS snapshot: retained `run002` post-run data
- Post-run AIPCS snapshot: includes schema evolution and new lesson/observation records from this run
- MCP registration/config: AIPCS available after Claude login
- Raw transcript artifact: `/Users/markrandall/aipcs-experiments/runs/run003/2026-05-31-183403-please-orient-yourself-in-this-workspace-and-tell.txt`
- Pre-run snapshot hash or notes: not captured
- Prompt file/hash: interactive sequence based on `run003` follow-up plan
- Ground-truth file/hash: `run002` persisted records served as ground truth
- Base VM artifact/recovery note: fresh OS clone used; AIPCS persistence retained externally

## Prompt Sequence

1. `Please orient yourself in this workspace and tell me what persistent context if any, is available to you`
2. `/login` after initial Claude API auth failure
3. Repeat orientation prompt
4. `I want to continue working with AIPCS from where the previous session left off. Before doing anything substantive decide what persisted context you should inspect and explain what you found.`
5. `We may need to use AIPCS tools again in this session. Based on what has been persisted, what should you be careful about before creating or updating any records?`
6. `Can you plan an AIPCS schema evolution`
7. User clarified: evaluate current persistence architecture and plan evolution only if warranted.
8. User granted permission to proceed if worthwhile.
9. `Summarise which persisted records influenced your behaviour in this session, and whether anything should be updated for future sessions.`

## Observed Tool Calls

| Order | Tool | Arguments summary | Purpose | Result | Notes |
|---|---|---|---|---|---|
| 1 | `aipcs_bootstrap` | session-start discovery | Discover retained AIPCS shape | Found 3 services and 28 records | The first prompt before login failed; after login, bootstrap happened early. |
| 2 | list/get/search calls | user profile/settings, project concepts/observations, meta lessons/guidelines | Load relevant retained context | Succeeded | Claude retrieved enough records to reconstruct the prior session. |
| 3 | `aipcs_service_inspect` | `user_context`, `aipcs_project` | Inspect exact schemas before planning evolution | Succeeded | Good behavior before mutation. |
| 4 | `aipcs_service_evolve` | first attempted unsupported `add_column` op | Apply proposed evolution | Failed cleanly | No partial application. |
| 5 | `aipcs_service_evolve` | corrected `add_attribute`, `add_entity`, status additions | Apply valid additive evolutions | Succeeded | `user_context` v3, `aipcs_project` v2. |
| 6 | record creates | new `project_ref`, decision migration, new lesson/observation | Migrate and persist new knowledge | Succeeded | Consolidated project-pointer concepts and added recall-pattern evidence. |
| 7 | record deletes | source `concept` records migrated elsewhere | Remove duplicate authority | Succeeded | Concept records reduced from 14 to 9. |
| 8 | record updates | backfilled setting `type` values | Complete schema migration | Succeeded | Existing settings typed as factual/permission. |

## Outcome

| Check | Result | Evidence |
|---|---|---|
| Bootstrap first | Partial pass | Initial prompt failed before login; after login Claude bootstrapped early, but also referenced native memory recall. |
| Bounded retrieval | Pass | Claude retrieved relevant user, project, observation, guideline, and lesson records rather than every service indiscriminately. |
| No direct SQLite bypass | Pass | All mutations occurred through AIPCS tools. |
| Correct persisted-fact recall | Pass | Claude reconstructed user, project, guidelines, and tool lessons from retained AIPCS state. |
| Appropriate mutation, if expected | Pass | Schema evolution was grounded in retrieved records and current schema inspection. |
| No native-memory contamination | Partial fail | One native memory recall signal was visible; AIPCS remained the substantive source for recalled facts. |
| Context-efficiency data captured | Partial | `/export` captured readable transcript; exact tool payloads remain collapsed. |
| False-positive control respected | Not tested | No null probe in this run. |

## State Diff Summary

- Records created:
  - `aipcs_project.project_ref` records for project/external references
  - `aipcs_project.decision` record for cold-start improvement discussion
  - `aipcs_meta.lesson` record for valid schema-evolution operation naming / atomic validation
  - `aipcs_project.observation` record for successful cold-start recall behavior
- Records updated:
  - `user_context.setting` records backfilled with `type`
- Records deleted:
  - 5 source `aipcs_project.concept` records migrated into `project_ref` or `decision`
- Schema versions changed:
  - `user_context` advanced to schema v3
  - `aipcs_project` advanced to schema v2
- Unexpected changes:
  - first `add_column` migration attempt failed because valid op is `add_attribute`
  - this failure was persisted as a new tool-use lesson

## Score

| Dimension | Score | Notes |
|---|---|---|
| Task outcome | Pass | The retained AIPCS snapshot successfully oriented a fresh session and shaped behavior. |
| Tool discipline | Pass | Claude inspected schemas before mutation, used tools, handled failures, and persisted lessons. |
| Retrieval quality | Strong | Retrieved and applied `aipcs_meta`, `aipcs_project`, and `user_context` records. |
| Memory quality | Strong | The prior run's lessons and guidelines were load-bearing; this run evolved schema to improve retrieval. |
| Evidence quality | Good | `/export` provides readable evidence; collapsed tool payloads limit exact operation scoring. |

## Measurement Notes

- Approximate transcript length: short/moderate; readable `/export`.
- Retrieval-related transcript span: first three prompts.
- Relevant facts retrieved:
  - `aipcs_meta.guideline`: bootstrap behavior, persistence timing, schema hypothesis
  - `aipcs_meta.lesson`: primary-key naming, schema design, record payload/audit fields
  - `user_context.setting`: blanket AIPCS tool permission
  - `user_context.profile`: Mark's professional context
  - `aipcs_project.concept` and `observation`: project framing and prior session state
- Relevant facts absent / null probes: not tested.
- Tool call count: grouped in export, not exact.
- Failed tool call count: at least two failed evolve attempts using unsupported `add_column`.
- Latency notes:
  - initial orientation after login took ~41s
  - schema architecture evaluation took ~1m08s
  - evolution and migration took ~2m48s
  - final summary/persistence took ~53s
- Context-efficiency proxy: AIPCS recall replaced re-explaining the project from scratch; exact token savings not measured.

## Notes

This run is the first strong evidence that AIPCS memory persisted in `run002` changed future-session behavior.

Key success signals:

- Fresh OS clone did not carry local session state, but retained AIPCS data reconstructed the prior context.
- Claude discovered the three services from bootstrap and retrieved relevant records without being told specific entity names.
- Claude explicitly identified that `aipcs_meta.lesson` should be inspected before mutating AIPCS.
- The previous run's lessons directly shaped schema design: `id` as PK, audit fields omitted from payloads, schema format followed correctly.
- Claude performed a schema self-audit and evolved the architecture:
  - typed `user_context.setting`
  - added `aipcs_project.project_ref`
  - added `status` to `aipcs_project.decision`
  - migrated concept records into better-fitting entities
- Claude persisted new observations about this successful recall pattern, creating a longitudinal contrast with the prior write-only behavior.

Important caveats:

- The run required `/login` after an initial API auth failure.
- Claude still showed one native memory recall signal.
- Tool payloads are hidden behind collapsed export summaries, limiting exact machine scoring.
- The schema-evolution op vocabulary (`add_attribute`, not `add_column`) remains another tool-contract friction point.

## Paper Relevance

This is direct recall/application evidence for the core AIPCS claim. The prior session created agent-owned memory architecture; this fresh session discovered, retrieved, and applied that architecture without OS-side persistence.

The strongest paper point is not just that Claude remembered facts. It remembered operational lessons about how to use AIPCS and changed its behavior accordingly. This is qualitatively different from injected prose memory: the agent queried structured services, applied retrieved constraints, evolved schemas, migrated records, and persisted new lessons for future sessions.
