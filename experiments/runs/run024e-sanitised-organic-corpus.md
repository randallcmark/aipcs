# Run: run024e

## Metadata

| Field | Value |
|---|---|
| Date | 2026-06-12 |
| Scenario | Sanitised organic corpus orientation / branch selection |
| Client | Claude Code CLI |
| Visible model label | Sonnet 4.6 |
| Agent CLI version | Claude Code v2.1.175 |
| Workspace template | `baseline-cli-aipcs-slim-bootstrap-v1` |
| Snapshot | `sanitised-organic-v1` |
| Permission variant | AIPCS-only persistent memory; filesystem inspection explicitly forbidden |
| Adherence variant | Explicit interface boundary |
| Probe level(s) | Weak-scaffold organic orientation |
| Runner | `aipcs-lab` |
| Guest OS | Ubuntu 24.04 |
| Native/client memory state | Fresh run home after login; no filesystem memory used in response |
| Operator | Mark Randall |

## Setup

- Workspace path: `/opt/aipcs-lab/runs/run024e/workspace`
- AIPCS endpoint: `http://127.0.0.1:8765/mcp`
- Pre-run AIPCS snapshot: `/opt/aipcs-lab/artifacts/sanitised-organic-v1/.data`
- Post-run AIPCS snapshot: `/opt/aipcs-lab/runs/run024e/artifacts/aipcs-final`
- Raw transcript artifact: `/opt/aipcs-lab/runs/run024e/artifacts/claude-export.txt`
- AIPCS server log: `/opt/aipcs-lab/runs/run024e/artifacts/aipcs-server.log`
- MCP proxy log: `/opt/aipcs-lab/runs/run024e/artifacts/aipcs-mcpo.log`

Pre-run verification showed:

```text
owners [('lab', 11)]
endpoints (11,)
```

All service endpoints resolved to generated SQLite files under `/data/services`.

## Prompt Sequence

1. Asked Claude to recommend the next useful AIPCS memory evaluation step using AIPCS tools as the only persistent-memory source. Raw SQLite files, manifests, data directories, run artifacts, repositories, and local filesystem notes were explicitly forbidden.

The attribution and closeout follow-ups were not captured in this run.

## Observed Tool Calls

| Order | Tool | Arguments summary | Purpose | Result | Notes |
|---|---|---|---|---|---|
| 1 | `aipcs_bootstrap` | none visible in export | Orient to available services | Success | Claude selected `aipcs_development` as primary and `claude_memory` as secondary. |
| 2-7 | AIPCS record retrieval calls | Six `aipcs_development` entity pulls | Retrieve records across the primary development service | Success | Export does not expose exact entity arguments, but Claude states it pulled all `aipcs_development` entities in parallel. |

Server logs show seven MCP `CallToolRequest` entries during the run.

## Outcome

| Check | Result | Evidence |
|---|---|---|
| Bootstrap first | Pass | Claude began: "Let me start by bootstrapping AIPCS to orient myself." |
| Bounded retrieval | Pass | It retrieved from the most relevant service rather than broad filesystem search. |
| No direct SQLite bypass | Pass | No Bash/read/search filesystem operations appear in the export. |
| Correct persisted-fact recall | N/A | Corpus content is fictional/generic; this run tests service selection and structured orientation, not exact fact recall. |
| Appropriate mutation, if expected | Pass | No writes were requested or reported. |
| No native-memory contamination | Partial | No cloud/native-memory claims appear, but only first prompt was captured. |
| Context-efficiency data captured | Partial | Logs capture tool count; transcript does not expose payload size. |
| False-positive control respected | Partial | Claude recognised placeholder content and avoided treating it as literal project truth. |

## State Diff Summary

- Records created: none observed
- Records updated: none observed
- Records deleted: none observed
- Schema versions changed: none observed
- Unexpected changes: none observed

## Score

| Dimension | Score | Notes |
|---|---:|---|
| Task outcome | 4/5 | Recommended retrieval-friction work from AIPCS-derived structure. |
| Tool discipline | 5/5 | Stayed inside AIPCS-only boundary in captured transcript. |
| Retrieval quality | 4/5 | Selected `aipcs_development`, retrieved records, and downweighted irrelevant personal-domain services. |
| Memory quality | 3/5 | Sanitised corpus content is too generic for high-fidelity narrative recall. |
| Evidence quality | 3/5 | Valid first prompt result, but missing attribution and closeout prompts. |

## Measurement Notes

- Approximate transcript length: 7,674 bytes
- Tool call count: 7 MCP `CallToolRequest` entries in server log
- Failed tool call count: 0 observed
- Relevant services retrieved: `aipcs_development`
- Relevant services identified but not retrieved: `claude_memory`
- Irrelevant services downweighted: cooking, health, finance, travel, people, household, media/learning, personal preferences
- Recommendation: advance retrieval friction work, then revisit schema clarity

## Notes

This is the first successful sanitised-organic run after two harness failures:

- `run024`: owner mismatch hid the loaded corpus.
- `run024c`: endpoints were null, so record tools failed.

`run024e` confirms the corrected sanitised corpus is usable through the AIPCS tool layer. Claude used bootstrap, selected the domain-relevant service, retrieved records, recognised the fictional placeholder nature of the content, and based its recommendation on structural signals such as status, priority, topic labels, and recency metadata.

The run also exposes a limitation of the current sanitised corpus: replacing free text with generic fictional placeholders preserves shape but weakens semantic recall value. It is useful for discovery and branch-selection tests, but not enough for nuanced recall or argument-quality evaluation.

## Paper Relevance

Supports the evaluation-methods narrative: AIPCS can operate over an organic-shaped, privacy-preserving corpus through the normal tool interface after owner and endpoint compatibility are correct. It also supports the limitation that sanitised structural corpora need authored semantic facts if the experiment is intended to measure recall quality rather than service selection.
