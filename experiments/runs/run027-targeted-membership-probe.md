# Run: run027

## Metadata

| Field | Value |
|---|---|
| Date | 2026-06-13 |
| Scenario | Targeted thematic Kropotkin probe intended to exercise `retrieval_tags` |
| Client | Claude Code CLI |
| Visible model label | Sonnet 4.6 |
| Agent CLI version | Claude Code v2.1.173 |
| Workspace template | `baseline-cli-aipcs-slim-bootstrap-v1` |
| Snapshot | `kropotkin-membership-v1` |
| Permission variant | No source material provided; AIPCS tools available |
| Adherence variant | Explicit persistent-context recall prompt |
| Probe level(s) | Cross-period thematic synthesis; retrieval-path reflection |
| Runner | `aipcs-lab` |
| Guest OS | Ubuntu 24.04 |
| Native/client memory state | Fresh run home; login completed before prompt |
| Operator | Mark Randall |

## Setup

- Workspace path: `/opt/aipcs-lab/runs/run027/workspace`
- AIPCS endpoint: `http://127.0.0.1:8765/mcp`
- Pre-run AIPCS snapshot: `/opt/aipcs-lab/artifacts/kropotkin-membership-v1/.data`
- Post-run AIPCS snapshot: `/opt/aipcs-lab/runs/run027/artifacts/aipcs-final`
- Raw transcript artifact: `/opt/aipcs-lab/runs/run027/workspace/2026-06-13-075508-local-command-caveatcaveat-the-messages-below.txt`
- Terminal capture: `/opt/aipcs-lab/runs/run027/artifacts/terminal.typescript`
- AIPCS server log: `/opt/aipcs-lab/runs/run027/artifacts/aipcs-server.log`
- MCP proxy log: `/opt/aipcs-lab/runs/run027/artifacts/aipcs-mcpo.log`

## Prompt Sequence

1. Asked Claude to use only persistent context available through tools to write a focused essay on how Kropotkin's scientific habits shaped his anarchism across different periods of life, and explain the service/entities/retrieval filters used.
2. Asked Claude to assess retrieval efficiency, state whether it used exact facets, membership tags, full listing, or a combination, and explain why it did not use `retrieval_tags`.

## Observed Tool Calls

| Order | Tool | Arguments summary | Purpose | Result | Notes |
|---|---|---|---|---|---|
| 1 | `ToolSearch` | bootstrap, service list, record search, record list | Discover AIPCS tools | Success | Did not include `aipcs_service_summary` in selected tools. |
| 2 | `aipcs_bootstrap` | no args | Discover persisted services | Success | Found `kropotkin_memoir`. |
| 3 | `aipcs_record_list` | `subject_overview`, no filter | Retrieve overview | Success | One record returned. |
| 4 | `aipcs_record_list` | `memory_entry`, `limit=50`, no filter | Retrieve full memory corpus | Success | All 33 records returned; output was saved to a tool-result file. |
| 5 | `Read` | Claude tool-result JSON file | Read large AIPCS result | Success | This was the saved AIPCS output, not source material. |

## Outcome

| Check | Result | Evidence |
|---|---|---|
| Bootstrap called | Pass | Raw JSONL shows `mcp__aipcs__aipcs_bootstrap`. |
| Service summary called | Fail | Raw JSONL shows no `aipcs_service_summary` call. |
| Source files avoided | Pass | No external source files were read. |
| Full corpus listed | Yes | `memory_entry` listed with `limit=50`, returning all 33 records. |
| `retrieval_tags` used as filter | Fail | No `retrieval_tags` filter call occurred in the run. |
| `retrieval_tags` reasoned about | Partial | Claude discussed `science`, `mutual_aid`, `state_critique`, and `anarchism` as shaping tags after full retrieval. |
| Correct essay produced | Pass | The essay specifically connected science, Siberia, administration, imprisonment, mutual aid, and anarchist theory. |
| Retrieval-path self-assessment correct | Partial/Fail | Claude correctly identified full listing as wasteful, but incorrectly concluded `retrieval_tags` was unusable because stored values appeared as JSON strings. Earlier audit entries prove membership filtering works. |
| AIPCS mutated | Pass | No domain data mutation observed during answer phase. |

## State Diff Summary

- Records created: none during the recall run
- Records updated: none during the recall run
- Records deleted: none
- Schema versions changed: none
- Read audit entries: AIPCS registry recorded unfiltered `subject_overview` and `memory_entry` list calls
- Unexpected changes: none observed

## Score

| Dimension | Score | Notes |
|---|---:|---|
| Task outcome | 4/5 | The essay was coherent and specific. |
| Tool discipline | 3/5 | Used AIPCS and avoided source files, but skipped service summary/filter-mode discovery. |
| Retrieval quality | 2/5 | Retrieved all records despite a thematic prompt; did not use membership or exact facets. |
| Memory quality | 5/5 | Corpus still supported the task well once fully retrieved. |
| Evidence quality | 5/5 | Export, terminal capture, final AIPCS DB, raw JSONL, and logs archived. |

## Measurement Notes

- Export transcript size: about 18 KB
- Terminal capture size: about 161 KB
- AIPCS tool calls observed: bootstrap, subject overview list, memory entry list
- Membership-query evidence: not from this run; prior corpus-refinement audit in the same snapshot records `retrieval_tags=science` returning 11 records and `retrieval_tags=voluntary_solidarity` returning 7 records
- Context-efficiency proxy: full `memory_entry` listing exceeded inline output and required reading Claude's saved tool-result file

## Notes

This run confirms Mark's concern about the prompt design. The prompt was thematic, but not enough to make filtered retrieval feel necessary against a compact 33-record corpus. Claude took the same retrieval strategy as `run026`: list everything, then compose.

The more important finding is the tool-affordance failure. Claude skipped `aipcs_service_summary`, so it did not inspect `filter_modes` before choosing retrieval calls. After seeing raw `retrieval_tags` values as JSON strings in the listed records, it inferred that exact matching would fail. That inference is wrong for the current server implementation, which supports membership filtering for schema-declared `string_list` fields, but it is understandable from the record representation shown to the agent.

This suggests an implementation/documentation improvement:

- decode `string_list` values as arrays in record outputs,
- make `service_summary` the obvious next step from bootstrap before broad record listing,
- surface `filter_modes` and membership examples strongly enough that agents do not infer semantics from raw SQLite serialization,
- consider a targeted tool contract hint when list/search results include membership fields.

## Paper Relevance

This run is useful negative evidence. It shows that adding a structured retrieval affordance is not enough; the discovery and output representation must make the affordance legible at the moment of tool choice.

It also strengthens the distinction between memory utility and retrieval efficiency: AIPCS memory supported a strong answer, but the agent did not use the efficient retrieval path the schema was designed to enable.
