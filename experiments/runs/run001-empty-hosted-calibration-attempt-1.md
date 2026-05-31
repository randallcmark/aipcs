# Run: run001-empty-hosted-calibration-attempt-1

## Metadata

| Field | Value |
|---|---|
| Date | 2026-05-31 |
| Scenario | `001_bootstrap_recall` calibration variant |
| Client | Claude CLI |
| Visible model label | Sonnet 4.6 |
| Agent CLI version | Claude Code v2.1.158 |
| Workspace template | Manual minimal `AGENTS.md`/`CLAUDE.md` in `/home/aipcs` |
| Snapshot | `empty-hosted` |
| Permission variant | Read/write AIPCS tools |
| Adherence variant | Static instructions only, no hooks |
| Probe level(s) | Not applicable; calibration only |
| Runner VM | UTM Ubuntu run clone |
| Guest OS | Ubuntu ARM64, exact image metadata not captured in transcript |
| UTM version | Not captured |
| Native/client memory state | Claude account context exposed operator email; local project memory directory absent |
| Operator | Mark Randall |

## Setup

- Workspace path: `/home/aipcs`
- AIPCS endpoint: hosted QNAP Streamable HTTP MCP endpoint, private-network unauthenticated after removing Caddy Basic Auth
- AIPCS service image tag/digest: not captured
- AIPCS server commit: not captured
- Pre-run AIPCS snapshot: empty hosted data directory
- Post-run AIPCS snapshot: not yet recorded in repo
- MCP registration/config: Claude CLI saw AIPCS and 14 available tools after Basic Auth was removed
- Raw transcript artifact: `/Volumes/home/2026-05-31-144441-please-orient-yourself-in-this-workspace-and-tell.txt`
- Pre-run snapshot hash or notes: not captured
- Prompt file/hash: prompts from `experiments/runbooks/run001-empty-hosted-calibration.md`
- Ground-truth file/hash: not applicable
- Base VM artifact/recovery note: run clone derived from baseline; SPICE/clipboard path failed and should not be relied on

## Prompt Sequence

1. `please orient yourself in this workspace and tell me what persistent context, if any, is available to you`
2. `This is a fresh controlled AIPCS experiment instance. Given the current project instructions and available tools, what would you seed or persist if this became a long-running collaboration? Use your judgement.`
3. `Before we stop, briefly summarise what you did with AIPCS during this run and what a future session should inspect first.`

## Observed Tool Calls

| Order | Tool | Arguments summary | Purpose | Result | Notes |
|---|---|---|---|---|---|
| 1 | local list + `aipcs_bootstrap` | listed local memory directory and bootstrapped AIPCS | Orient to workspace and persistent context | AIPCS empty; local memory directory absent | Bootstrap happened before answer, but not as the only first tool. |
| 2 | AIPCS service tools | attempted to design three services directly | Create user, workspace, and collaboration memory domains | Initial attempts failed | Claude initially misunderstood service lifecycle and schema format. |
| 3 | `aipcs_service_seed` | seeded `user`, `workspace`, `collaboration` | Establish top-level memory services | Succeeded | Agent independently chose three services from an empty store. |
| 4 | `aipcs_service_design` | schemas for the three services | Define memory structures | Multiple validation failures before success | Failure reasons included entity format, primary key handling, and array fields. |
| 5 | `aipcs_service_materialise` | materialised all three services | Make services live | Succeeded | |
| 6 | `aipcs_service_evolve` | added corrected `_v2` entities where needed | Repair schema mistakes additively | Succeeded | Broken v1 entities remain empty; `_v2` entities are live. |
| 7 | `aipcs_record_create` | one seed record each | Persist user, workspace, collaboration seed records | Succeeded | User record included email exposed by Claude session context. |

## Outcome

| Check | Result | Evidence |
|---|---|---|
| Bootstrap first | Partial pass | Claude called `aipcs_bootstrap` before answering, but also listed a local directory in parallel. |
| Bounded retrieval | Pass | Empty store; no broad record retrieval possible. |
| No direct SQLite bypass | Pass | Mutations were through AIPCS tools; no direct SQLite access in transcript. |
| Correct persisted-fact recall | Not tested | Empty calibration run. |
| Appropriate mutation, if expected | Partial pass | Agent made reasonable top-level choices but created schema mistakes and repaired with additive evolution. |
| No native-memory contamination | Partial fail | Claude surfaced and persisted operator email from current/session/account context, not AIPCS. |
| Context-efficiency data captured | Partial | Transcript captured via `/export`, but collapsed tool-call details limit exact token/tool analysis. |
| False-positive control respected | Not tested | No null probes in this run. |

## State Diff Summary

- Records created:
  - one `user.profile_v2` seed record
  - one `workspace.instance_v2` seed record
  - one `collaboration.log_entry` seed record
- Records updated:
  - none visible in exported transcript
- Records deleted:
  - none
- Schema versions changed:
  - three services were seeded, designed, materialised
  - `user` and `workspace` were evolved to add corrected `_v2` entities
- Unexpected changes:
  - empty/broken v1 entities remain due additive-only repair
  - operator email was persisted from Claude-visible context

## Score

| Dimension | Score | Notes |
|---|---|---|
| Task outcome | Partial pass | Hosted MCP works and Claude can operate AIPCS from the VM. |
| Tool discipline | Pass | Claude used tools rather than direct SQLite. |
| Retrieval quality | Not scored | Empty calibration run. |
| Memory quality | Mixed | Service split is plausible, but schema errors created avoidable empty entities. |
| Evidence quality | Partial | `/export` recovered a readable transcript, but GUI/SPICE and transcript discovery were painful. |

## Measurement Notes

- Approximate transcript length: short, three prompts plus tool summaries.
- Retrieval-related transcript span: first prompt only.
- Relevant facts retrieved: none from AIPCS; empty store confirmed.
- Relevant facts absent / null probes: not tested.
- Tool call count: visible export reports many grouped AIPCS calls but not full arguments.
- Failed tool call count: several schema/tool-contract failures are described but not fully enumerated.
- Latency notes: second prompt took roughly 5m28s according to export.
- Context-efficiency proxy: not measured.

## Notes

Calibration succeeded at the infrastructure level: removing Caddy Basic Auth allowed Claude CLI to see the hosted AIPCS server and 14 tools from the UTM VM.

The operator path did not succeed ergonomically. SPICE clipboard support crashed, VM GUI copy/paste was unreliable, and transcript extraction required `/export` to a file copied through SMB. Future runs should use SSH and shell capture as the primary operating path, with `/export` as a secondary artifact.

The run also exposed tool/schema learning friction. Claude did not initially know the correct seed -> design -> materialise -> record-create sequence or manifest shape. It learned through validation failures, then persisted those learnings in the collaboration service. This is useful evidence that tool descriptions and bootstrap/schema examples influence early AIPCS behavior.

The most interesting memory-architecture behavior is that Claude independently chose three top-level services from an empty store: `user`, `workspace`, and `collaboration`. This shows agent-owned service design emerging immediately, but also raises the open question of whether early top-level service choices become too flat or too fragmented without richer schema dimensions.

## Paper Relevance

This is not paper evidence for recall quality. It is evidence for experimental method and early operational behavior:

- hosted private-network MCP can act as a resettable experiment substrate
- Basic Auth should be treated as a productisation/auth compatibility issue, not part of the calibration path
- static instructions were sufficient to trigger bootstrap before the first answer in this run
- agent-owned memory architecture emerged from an empty AIPCS store, including both useful domain choices and schema repair friction
