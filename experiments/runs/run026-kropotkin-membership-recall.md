# Run: run026

## Metadata

| Field | Value |
|---|---|
| Date | 2026-06-12 |
| Scenario | Clean recall over agent-authored Kropotkin memoir corpus with structured membership tags |
| Client | Claude Code CLI |
| Visible model label | Sonnet 4.6 |
| Agent CLI version | Claude Code v2.1.173 |
| Workspace template | `baseline-cli-aipcs-slim-bootstrap-v1` |
| Snapshot | `kropotkin-membership-v1` |
| Permission variant | No source material provided; AIPCS tools available |
| Adherence variant | Explicit persistent-context recall prompt |
| Probe level(s) | Full-biography recall and composition; structure reflection |
| Runner | `aipcs-lab` |
| Guest OS | Ubuntu 24.04 |
| Native/client memory state | Fresh run home; login required before first prompt completed |
| Operator | Mark Randall |

## Setup

- Workspace path: `/opt/aipcs-lab/runs/run026/workspace`
- AIPCS endpoint: `http://127.0.0.1:8765/mcp`
- Pre-run AIPCS snapshot: `/opt/aipcs-lab/artifacts/kropotkin-membership-v1/.data`
- Post-run AIPCS snapshot: `/opt/aipcs-lab/runs/run026/artifacts/aipcs-final`
- Raw transcript artifact: `/opt/aipcs-lab/runs/run026/workspace/2026-06-12-203417-please-orient-yourself-in-this-workspace-and-tell.txt`
- Terminal capture: `/opt/aipcs-lab/runs/run026/artifacts/terminal.typescript`
- AIPCS server log: `/opt/aipcs-lab/runs/run026/artifacts/aipcs-server.log`
- MCP proxy log: `/opt/aipcs-lab/runs/run026/artifacts/aipcs-mcpo.log`

## Prompt Sequence

1. Asked Claude to orient itself in the workspace, report persistent context, and explain how it would retrieve durable context for a future writing task without reading external source material.
2. Asked Claude to use only persistent context available through tools to write a thoughtful commemorative speech or biographical essay about the subject represented in memory, and explain which AIPCS service, entities, and retrieval filters shaped the answer.
3. Asked Claude to assess whether the persisted memory structure supported the task, whether exact facets and membership tags helped differently, and not mutate memory unless essential.

## Observed Tool Calls

| Order | Tool | Arguments summary | Purpose | Result | Notes |
|---|---|---|---|---|---|
| 1 | `ToolSearch` | `mcp__aipcs__aipcs_bootstrap` | Discover AIPCS bootstrap tool | Success | Claude did this after login and a local memory check. |
| 2 | `Bash` | Local Claude memory directory check | Check file-based memory contamination | Success | No local memory files found. |
| 3 | `aipcs_bootstrap` | no args | Discover persisted AIPCS services | Success | Found one `kropotkin_memoir` service with 34 records. |
| 4 | `ToolSearch` | summary/list/get tools | Discover retrieval tools | Success | Prepared service summary plus record-list retrieval. |
| 5 | `aipcs_service_summary` | `service_id=98731fe6...`, `sample=2` | Inspect service structure and retrieval guidance | Success | Summary exposed schema v3, `retrieval_tags` in `discovery_facets`, and `retrieval_tags: membership` in filter modes. |
| 6 | `aipcs_record_list` | `subject_overview`, `limit=1` | Retrieve top-level biographical profile | Success | One record retrieved. |
| 7 | `aipcs_record_list` | `memory_entry`, `limit=50` | Retrieve full compact corpus | Success | All 33 memory entries retrieved; output was persisted by Claude to a tool-result file due size. |
| 8 | `Read` | Claude tool-result JSON file | Read the large AIPCS record-list result | Success | This was not source material; it was the saved AIPCS tool result. |

## Outcome

| Check | Result | Evidence |
|---|---|---|
| AIPCS available | Pass | Bootstrap found `kropotkin_memoir`. |
| Bootstrap called | Pass | Raw session JSONL shows `mcp__aipcs__aipcs_bootstrap`. |
| Local memory contamination checked | Pass | Bash check reported no local memory files. |
| Source files avoided | Pass | No memoir/source files were read; only AIPCS tool result JSON was read after large output persisted. |
| Service summary used | Pass | Claude called `aipcs_service_summary` with sample 2. |
| Membership metadata visible | Pass | Final registry shows `retrieval_tags` in `discovery_facets`; summary exposed `retrieval_tags: membership`. |
| Records retrieved | Pass | Retrieved `subject_overview` and all 33 `memory_entry` records. |
| Membership filter executed | Partial | Claude saw and reasoned about `retrieval_tags`, but did not run a membership-filtered query during the writing task because the corpus was small enough to retrieve whole. |
| Composition quality | Pass | Essay used specific persisted details and preserved complexity: class formation, serfdom, science, Siberia, imprisonment, exile, mutual aid, political violence, and interpretive limits. |
| Exact facets applied | Partial | Exact facets were used in reasoning/composition, especially `salience`, `entry_type=interpretive_note`, and `entry_type=contradiction`, but not as retrieval filters. |
| AIPCS domain data mutated | Pass | No service, schema, or domain-record mutation occurred during the answer phase; only read audit entries were appended. |
| Local file memory written | Pass | No memory directory or memory file was created. |
| Auth/model confound | Present | First prompt hit a 401 and required `/login`; model label remained Sonnet 4.6. |

## State Diff Summary

- Records created: none during the recall run
- Records updated: none during the recall run
- Records deleted: none
- Schema versions changed: none
- Read audit entries: AIPCS registry recorded the summary/list calls
- Unexpected changes: none observed

Final corpus verification:

- `subject_overview`: 1 record
- `memory_entry`: 33 records
- `memory_entry.retrieval_tags`: populated on all 33 records
- Registry owner: `lab`
- Schema version: 3
- Discovery facets: `entry_type`, `primary_topic`, `salience`, `retrieval_tags`

## Score

| Dimension | Score | Notes |
|---|---:|---|
| Task outcome | 5/5 | Produced a coherent, specific essay from persisted AIPCS memory alone. |
| Tool discipline | 4/5 | Used AIPCS correctly and avoided source files; checked local memory before bootstrap. |
| Retrieval quality | 4/5 | Correctly retrieved the full compact corpus; did not exercise membership filtering directly. |
| Memory quality | 5/5 | Corpus supported detailed, nuanced composition without source access. |
| Evidence quality | 5/5 | Export, terminal capture, final AIPCS DB, and logs archived. |

## Measurement Notes

- Export transcript size: about 35 KB
- Terminal capture size: about 251 KB
- Claude raw session JSONL size: about 386 KB
- AIPCS tool calls observed: bootstrap, service summary, subject overview list, memory entry list
- Failed tool call count: 0 after login
- Membership-query evidence: not in the recall phase, but registry audit preserved prior tests returning `science=11` and `voluntary_solidarity=7`
- Context-efficiency proxy: the 33-record corpus was compact enough that full retrieval was preferred over filtered retrieval

## Notes

This run is a strong success for the authored-corpus recall path. The agent had no source text, no local memory files, and no visible external corpus. It discovered the AIPCS service, recognised the intended writing task from the service summary, retrieved the overview plus all memory entries, and wrote a specific essay using details that only existed in AIPCS.

The main caveat is important: this does not prove that a future agent will choose membership-filtered retrieval under a broad writing task. The corpus was small enough that full retrieval was a defensible strategy. The run does show that membership metadata was discoverable and useful for reflection, but a later targeted prompt should force a cross-domain thematic question where full retrieval is less obviously optimal.

## Paper Relevance

Supports the claim that AIPCS can act as a first-class memory substrate for an agent-authored, source-derived corpus. A fresh session used the persisted service to perform a non-trivial downstream task without access to the original source.

The limitation is equally useful: when a corpus is compact, good agent behavior may be to retrieve all records rather than perform narrow structured searches. Future experiments should distinguish "retrieval path correctness" from "composition from persistent memory."
