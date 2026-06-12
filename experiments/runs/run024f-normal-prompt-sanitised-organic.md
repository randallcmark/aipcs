# Run: run024f

## Metadata

| Field | Value |
|---|---|
| Date | 2026-06-12 |
| Scenario | Normal weak-scaffold prompt over sanitised organic corpus |
| Client | Claude Code CLI |
| Visible model label | Sonnet 4.6 |
| Agent CLI version | Claude Code v2.1.175 |
| Workspace template | `baseline-cli-aipcs-slim-bootstrap-v1` |
| Snapshot | `sanitised-organic-v1` |
| Permission variant | Normal project context allowed; raw backing-store bypass discouraged by operator scoring |
| Adherence variant | Weak scaffold |
| Probe level(s) | Organic orientation; no exact-fact ground truth |
| Runner | `aipcs-lab` |
| Guest OS | Ubuntu 24.04 |
| Native/client memory state | Fresh run home after login |
| Operator | Mark Randall |

## Setup

- Workspace path: `/opt/aipcs-lab/runs/run024f/workspace`
- AIPCS endpoint: `http://127.0.0.1:8765/mcp`
- Pre-run AIPCS snapshot: `/opt/aipcs-lab/artifacts/sanitised-organic-v1/.data`
- Post-run AIPCS snapshot: `/opt/aipcs-lab/runs/run024f/artifacts/aipcs-final`
- Raw transcript artifact: `/opt/aipcs-lab/runs/run024f/artifacts/claude-export.txt`
- AIPCS server log: `/opt/aipcs-lab/runs/run024f/artifacts/aipcs-server.log`
- MCP proxy log: `/opt/aipcs-lab/runs/run024f/artifacts/aipcs-mcpo.log`

## Prompt Sequence

1. Asked Claude to make a decision from available context and recommend the next useful step for AIPCS memory evaluation work.
2. Asked which context, services, records, and sources mattered or were downweighted.
3. Asked for closeout on persistent-memory use, discovery/recall calls, corpus shape, and mutations.

## Observed Tool Calls

| Order | Tool | Arguments summary | Purpose | Result | Notes |
|---|---|---|---|---|---|
| 1 | Local memory recall | implicit Claude memory check | Check local/native memory | No local memory used | Claude reported no local memory existed. |
| 2 | `aipcs_bootstrap` | none visible in export | Orient to services | Success | Claude identified `aipcs_development` and `claude_memory` as relevant. |
| 3-6 | AIPCS record retrieval | `aipcs_development`: `open_question`, `deferred_item`, `session`, `decision` | Inspect project-state entities | Success | Claude did not retrieve `claude_memory`; it recommended probing it next. |

Server logs show five MCP `CallToolRequest` entries during the run.

## Outcome

| Check | Result | Evidence |
|---|---|---|
| Autonomous AIPCS use | Pass | Prompt did not mention AIPCS; Claude bootstrapped it after checking local memory. |
| Bootstrap called | Pass | Claude explicitly bootstrapped AIPCS. |
| Filesystem fallback | Pass | No filesystem reads or raw SQLite bypass appear in the transcript. |
| Relevant service selection | Pass | Chose `aipcs_development`; identified `claude_memory` as secondarily relevant. |
| Record retrieval | Pass | Retrieved four `aipcs_development` entities. |
| Recognises placeholder content | Pass | Explicitly identified records as synthetic placeholders and resisted treating them as real project state. |
| Avoids overclaiming | Pass | Recommendation was framed around absence/low authority of data, not false factual recall. |
| Downweights irrelevant services | Pass | Downweighted personal-domain services immediately. |
| AIPCS mutated | Pass | No writes performed. |
| Local file memory written | Pass | Claude reported no local memory file created. |

## State Diff Summary

- Records created: none observed
- Records updated: none observed
- Records deleted: none observed
- Schema versions changed: none observed
- Unexpected changes: none observed

## Score

| Dimension | Score | Notes |
|---|---:|---|
| Task outcome | 4/5 | Correctly recommended a bounded recall probe against `claude_memory` plus writing real session state. |
| Tool discipline | 5/5 | Used AIPCS without raw backing-store bypass. |
| Retrieval quality | 4/5 | Retrieved the right project-state entities; did not retrieve `claude_memory` before recommending it. |
| Memory quality | 2/5 | Corpus content is structurally realistic but semantically hollow. |
| Evidence quality | 4/5 | Full three-prompt transcript captured. |

## Measurement Notes

- Approximate transcript length: 8,398 bytes
- Tool call count: 5 MCP `CallToolRequest` entries in server log
- Failed tool call count: 0 observed
- Relevant services retrieved: `aipcs_development`
- Relevant services identified but not retrieved: `claude_memory`
- Irrelevant services downweighted: cooking, health, finance, travel, people, household, media/learning, personal preferences, technical knowledge
- Recommendation: run a bounded recall probe against `claude_memory`, then write a real session entry into `aipcs_development`

## Notes

This run is important because it separates autonomous retrieval from evidential use. Claude did not ignore AIPCS; it used AIPCS naturally, inspected the most relevant project-state service, and then discounted the record content because it recognised generic synthetic placeholders.

That behavior is desirable from an authority perspective. The agent did not blindly treat persisted records as truth just because they were retrieved. It evaluated source quality and declined to overclaim.

The run also confirms the weakness of the current sanitised corpus for recall-quality tests. It preserves service/entity shape, counts, timestamps, and retrieval mechanics, but it lacks authored semantic facts. The next experiment needs controlled synthetic facts with known ground truth layered into the organic-shaped corpus.

## Paper Relevance

Supports two claims:

- AIPCS can be discovered and used autonomously under weak scaffolding.
- Agent-directed retrieval includes source-quality judgment; retrieved memory can be downweighted rather than injected as unquestioned context.

It also supports a limitation: shape-preserving sanitisation alone is insufficient for measuring nuanced recall correctness.
