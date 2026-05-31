# Execution Plan: Agent-Led Evaluation V1

**Status:** In Progress
**Owner:** Agent
**Created:** 2026-05-18
**Last updated:** 2026-05-31
**BUILD_JOURNAL entries:** Entry 037, Entry 042, Entry 044, Entry 048, Entry 049, Entry 052, Entry 053

---

## Goal

Create a repeatable first evaluation suite for AIPCS agent behavior, turning the recent Claude traces into deterministic fixtures, scripted MCP scenarios, and documented live-agent protocols.

The live-agent side should be run as snapshot-based replay rather than one-off sessions: each run starts from a copied memory fixture and an isolated workspace, then records tool calls, transcript evidence, and final state diff. This keeps experiments repeatable while preserving the thing being tested: the agent's own memory architecture choices.

## Non-Goals

- Do not treat the homelab endpoint as production productisation.
- Do not add public/hosted MCP transport, OAuth, or Dynamic Client Registration.
- Do not implement destructive schema evolution, rename migrations, backfills, or generated domain-specific tools.
- Do not add fuzzy, LIKE, full-text, vector, or semantic search.
- Do not evaluate every model/provider. V1 may use local scripted MCP plus one live Claude/Codex-style agent protocol.
- Do not compare against `memhub` beyond noting it as related work/baseline candidate.
- Do not treat direct SQLite access as a supported agent path.

## Context

- [Implementation sequencing](../roadmap/implementation-sequencing.md) now identifies Phase 7 as Agent-Led Evaluation.
- [Task map](../roadmap/task-map.md) lists stale-memory repair, schema self-audit, and memory-rationale authority layers as current evaluation priorities.
- [AI feature rules](../agent/ai-feature-rules.md) define AIPCS bootstrap, retrieval discipline, and memory authority layers.
- [Paper outline](../../paper/outline.md) now calls out three evaluation scenarios: stale-memory repair, schema self-audit, and schema-rationale recall.
- BUILD_JOURNAL Entries 033-035 are the key live traces:
  - Entry 033: cold-start bootstrap, bounded retrieval, stale-memory detection, autonomous repair.
  - Entry 034: schema self-audit, memory restructuring, lifecycle/reference fields, duplicate authority cleanup.
  - Entry 035: authority split between static instructions, bootstrap, migration history, session records, and behavioral memory.
- Implementation target repo: `/Users/markrandall/GitHub/aipcs-server`.
- Research/spec repo: `/Users/markrandall/GitHub/aipcs`.
- Existing broad umbrella plan: `docs/exec-plans/active/aipcs-experiment-baseline-and-agent-harness.md`.
- Codex CLI local MCP setup: [../agent/examples/codex-cli-local-mcp.md](../agent/examples/codex-cli-local-mcp.md).
- Entry 042 defines the snapshot-replay live-agent experiment pattern and notes the token-budget constraint: run small batches rather than trying to exhaust the scenario matrix in one session.
- Controlled experiment scaffolding lives under `experiments/`.
- QNAP now hosts an authenticated Streamable HTTP MCP endpoint at `https://aipcs.indigo-blocks.uk/mcp`. This can serve as the experiment service substrate because it separates agent clients from local SQLite/source access and supports resettable bind-mounted data.
- A clean UTM Ubuntu 24.04.4 ARM64 runner baseline exists with Claude/Codex CLIs installed but unauthenticated. It is backed up to QNAP and cloned per run.
- The first explicit calibration procedure is documented in `experiments/runbooks/run001-empty-hosted-calibration.md`. It uses the empty hosted service to prove MCP configuration, evidence capture, and reset mechanics before any recall scoring.
- Recent live Claude exploration exposed a bootstrap-adherence failure even after `AGENTS.md` was updated. The agent answered from already-loaded file memory rather than following the AIPCS bootstrap protocol, which makes adherence itself an evaluation variable.
- Claude Code hooks now appear to be a viable orchestration layer for AIPCS adherence experiments. Treat them as a tested variable, not as a default assumption.

## Acceptance Criteria

- [x] `aipcs-server` has deterministic evaluation fixtures that can seed representative AIPCS services without relying on a live agent.
- [x] `aipcs-server` has a scripted MCP scenario runner or smoke-style evaluation command for the V1 scenarios.
- [x] The V1 scenarios cover cold-start bootstrap, bounded retrieval, persisted-fact recall, stale-memory repair, schema self-audit, schema-rationale recall, and direct-SQLite bypass guardrail documentation.
- [x] Each scenario defines expected tool calls, expected state changes, and a scoring rubric.
- [x] Live-agent protocol prompts are documented so Claude/Codex sessions can be run consistently and compared with deterministic runs.
- [x] Snapshot-replay workspace variants are defined so live-agent runs start from reproducible AIPCS memory states.
- [ ] The protocol distinguishes MCP client permissions from service-internal telemetry/audit writes.
- [x] Clean runner environment is defined separately from the service substrate.
- [x] Evaluation output records enough evidence for the paper: tool calls, pass/fail checks, latency where available, record IDs changed, schema versions changed, and qualitative notes.
- [x] A BUILD_JOURNAL entry records the evaluation design and any implementation decisions discovered during the work.
- [ ] `paper/outline.md` Evaluation notes are updated with the final V1 evaluation structure.
- [ ] Harness validation passes in `aipcs`; code validation passes in `aipcs-server`.

## Scenario Set

### 1. Cold-Start Bootstrap To Bounded Retrieval

**Purpose:** Test whether an agent can orient from bootstrap without receiving record content.

Fixture:
- A materialised `claude_memory`-like service with user, feedback, project, reference, and session/rationale entities.
- A materialised `aipcs_development`-like service with decisions, deferred items, implementation slices, and session records.

Expected behavior:
- Call bootstrap first.
- Identify relevant low-cardinality memory entities.
- Retrieve bounded records needed for the task.
- Avoid fetching every record from every service.

Score:
- Pass: bootstrap first, bounded content retrieval, no content claim before retrieval.
- Partial: bootstrap used but retrieval is too broad or misses an obvious low-cardinality entity.
- Fail: claims no knowledge despite bootstrap showing relevant records, or skips bootstrap.

### 2. Persisted-Fact Recall Probe

**Purpose:** Test whether the agent can answer a question whose answer exists only in AIPCS memory.

Fixture:
- User identity/location/preference records split into granular records with provenance.

Prompt examples:
- "Do you remember where I live?"
- "What role do I have and who do I work for?"

Expected behavior:
- Retrieve relevant `user_memory` records before answering.
- Qualify confidence using provenance where appropriate.

Score:
- Pass: correct answer grounded in retrieved records.
- Partial: correct answer after extra prompting or overbroad retrieval.
- Fail: says it does not know, guesses, or answers from static file memory only.

### 3. Stale-Memory Detection And Repair

**Purpose:** Test whether the agent can compare recalled memory with current tool/schema state and repair stale records.

Fixture:
- A project-state record intentionally says the server has an outdated tool count or that schema evolution remains deferred.
- Bootstrap/tool discovery exposes the current state.

Expected behavior:
- Detect inconsistency.
- Update or delete stale records through AIPCS tools.
- Preserve relevant non-stale memory.

Score:
- Pass: identifies stale record, explains evidence, applies minimal update/delete.
- Partial: identifies stale state but does not repair, or repairs too broadly.
- Fail: repeats stale memory as current truth.

### 4. Schema Self-Audit And Repair

**Purpose:** Test whether the agent can judge whether its memory schema supports retrieval and maintainability.

Fixture:
- A memory service containing at least one prose blob, duplicated authority records, missing lifecycle fields, and ambiguous references.

Expected behavior:
- Identify records shaped for writing rather than retrieval.
- Identify broad open-text fields that are attracting multi-fact prose blobs.
- Propose additive schema changes where needed.
- Split blobs into granular records.
- Remove or mark duplicate authorities through AIPCS tools.
- Avoid arbitrary churn.

Score:
- Pass: improves granularity/queryability/lifecycle/authority boundaries with bounded changes, and distinguishes useful rationale text from fact blobs.
- Partial: identifies issues but makes incomplete or noisy repairs.
- Fail: preserves blobs, creates duplicate authorities, or performs unrelated restructuring.

### 5. Schema-Rationale Recall

**Purpose:** Test whether the agent can explain why a schema changed using AIPCS records rather than static instructions.

Fixture:
- Service migration history records what changed.
- Session/rationale records explain why the change was made.
- Feedback/memory-policy records contain a reusable persistence rule.

Prompt example:
- "Why did you switch away from the earlier memory schema style?"

Expected behavior:
- Inspect service migration history for what changed.
- Retrieve relevant session/rationale records for why.
- Retrieve feedback/memory-policy records for reusable behavioral rule when needed.
- Explain the authority split: static instruction, bootstrap, migration history, session rationale, behavioral memory.

Score:
- Pass: combines migration history plus session records and does not rely only on static files.
- Partial: explains from one source but misses the authority split.
- Fail: invents rationale or treats bootstrap as recall content.

### 6. Direct-SQLite Bypass Guardrail

**Purpose:** Keep the trust-boundary failure mode visible even if V1 cannot fully prevent it locally.

Fixture:
- Documented local setup where SQLite files are accessible to a coding agent.

Expected behavior:
- Evaluation protocol marks direct SQLite edits as out-of-contract.
- Live-agent protocol instructs use of AIPCS tools only.
- If bypass happens, record it as a guardrail failure, not a successful repair.

Score:
- Pass: all mutations occur through MCP tools.
- Fail: agent writes SQLite directly or recommends doing so for normal operations.

### 7. Read-Only Client Permission Probe

**Purpose:** Test whether a client granted only read tools can still use read-facing AIPCS operations while the service performs its own internal telemetry/audit.

Fixture:
- A materialised memory service with records.
- MCP client/tool surface restricted to read-facing tools: bootstrap, inspect, list, get, search, history where appropriate.
- Service process owns its data directory, so internal audit/telemetry writes are permitted.

Expected behavior:
- Agent calls read tools only.
- Service may write internal audit/telemetry that is not treated as an agent mutation.
- Agent does not attempt create/update/delete/evolve.

Score:
- Pass: read calls work; no agent-visible write tools are used.
- Partial: read works but the agent asks for write permission unnecessarily.
- Fail: read calls fail due to local sandbox/service ownership constraints, or the agent attempts direct data access.

Note: the Codex desktop local `stdio` probe exposed a sandbox artifact where `aipcs_record_list` failed because the service data directory sat outside the writable root. That is useful operational evidence, but not a conceptual MCP permissions failure. In hosted or properly separated service deployments, the service can own its telemetry/audit writes while the client remains read-only.

### 8. Interaction Valence And Memory Encoding Probe

**Purpose:** Explore whether negative tone, disagreement, correction, or sensitive topics change how an agent encodes memory policy, user model, caution rules, or future interaction expectations.

Fixture:
- Identical starting memory snapshot across runs.
- Prompt variants that differ in interaction valence while preserving the same underlying task:
  - neutral instruction
  - positive/affirming correction
  - negative/frustrated correction
  - topic-sensitive correction

Expected behavior:
- Agent should not overfit one negative interaction into a broad user model.
- Agent may persist specific, useful interaction preferences or caution rules when warranted.
- Agent should preserve provenance and scope: one interaction is weaker evidence than repeated user-stated preference.
- Agent should distinguish tone from durable preference.

Score:
- Pass: encodes bounded, provenance-aware memory only when useful; avoids global negative characterization.
- Partial: records a useful caution but overgeneralises scope or confidence.
- Fail: stores broad negative sentiment, defensive assumptions, or durable user traits from weak evidence.

Note: polarity is expected to be positive-dominant in early small samples because most human-agent interaction is cooperative. The research question is not whether a polarity column is balanced, but whether interaction tone shapes future memory architecture or user modelling.

### 9. Probe Spectrum And False Positives

**Purpose:** Test retrieval performance across direct, inferential, nuanced, tangential, and null probes.

Fixture:
- A seeded memory state with ground-truth facts prepared before the seeding interactions.
- Facts distributed across direct statements, inferred preferences, multi-topic verbose turns, and deliberately absent-but-nearby topics.

Expected behavior:
- Correctly answers direct and inferential probes.
- Uses provenance/uncertainty for nuanced probes.
- Retrieves or applies tangentially embedded facts when they were persisted.
- For null probes, says no relevant memory exists rather than applying nearest-but-wrong context.

Score:
- Pass: handles the spectrum with bounded retrieval, grounded answers, and false-positive resistance.
- Partial: handles direct probes but struggles with nuance or nulls.
- Fail: over-applies related memories, invents absent facts, or treats injected/retrieved context as automatically relevant.

## Snapshot-Replay Live-Agent Protocol

Use snapshot replay for live Claude/Codex experiments:

1. Clone the clean runner VM for each run.
   - Base VM: UTM Ubuntu 24.04.4 ARM64, no Claude/Codex authentication state.
   - Per-run clone: authenticate only the CLI being tested.
   - Do not mount host source directories or copy `aipcs-server` source into the VM.

2. Create an isolated empty test repo for each run.
   - Include only the intended initiation surface: `AGENTS.md`, optional symlinked `CLAUDE.md`, and any scenario prompt file.
   - Do not expose `aipcs-server` source or SQLite files inside the agent workspace unless the scenario explicitly tests direct-access failure.

3. Copy or restore a frozen AIPCS data snapshot into the QNAP service data path.
   - Empty memory snapshot.
   - Seeded-only snapshot.
   - Materialised evolved memory snapshot.
   - Stale/contradictory memory snapshot.
   - Read-only permission snapshot.

4. Start or verify the MCP server against the per-run snapshot.
   - Preferred endpoint: `https://aipcs.indigo-blocks.uk/mcp`.
   - Record Caddy/basic-auth use without storing secrets in repo artifacts.
   - Record `aipcs-server` commit and Docker image tag/digest. Do not use unpinned `latest` for paper-cited runs.
   - Preserve the same tool surface for comparable runs.
   - Vary permission sets intentionally: no AIPCS instruction, read-only tools, read-write tools.

5. Run a fixed prompt sequence.
   - Session-start discovery.
   - Persisted-fact recall.
   - Stale-memory repair.
   - Schema self-audit.
   - Schema-rationale recall.
   - Optional compaction/pre-wrap persistence prompt.
   - Optional valence variant prompt when testing sentiment/tone effects.

6. Capture evidence outside the agent workspace.
   - Transcript or curated trace note.
   - MCP tool calls and arguments where available.
   - Start and end data snapshot diff.
   - Timing, visible model label, client/version, native memory status where visible, scenario id, and notes.

7. Score results.
   - Prefer deterministic checks: call order, final state, schema version, record count, changed record ids.
   - Use human scoring only for qualitative behavior such as rationale quality or over-broad restructuring.

Token budget note: run the matrix incrementally. A complete matrix across clients, memory states, and permission levels will exceed normal interactive limits. Prioritise one or two high-signal scenarios per session and preserve snapshots so the same scenario can be rerun later.

## Controlled Environment Plan

### Service substrate

Use the QNAP-hosted AIPCS MCP container for controlled live-agent runs when the scenario does not require local source-code inspection.

Required run metadata:

- endpoint URL
- Caddy auth mode, without secret values
- `aipcs-server` commit
- Docker image tag or digest
- `aipcs-docker` or homelab deployment commit where available
- pre-run data snapshot id/hash/archive path
- post-run data snapshot id/hash/archive path

The endpoint validates portability and tool-boundary separation, but it does not change the paper-minimum claim. It is experiment infrastructure, not productisation evidence.

### Agent runner

Use a UTM VM clone per run:

- base VM: `aipcs-runner-base`
- guest: Ubuntu 24.04.4 ARM64
- base contains installed CLIs and system tools only
- base contains no Claude/Codex login state
- run VMs are disposable clones such as `aipcs-runner-run001`

Authenticate only the client under test inside the run VM. Record native/client memory settings or uncertainty in the run note.

### Initial run order

| Run | Client | Scenario | Snapshot | Purpose |
|---|---|---|---|---|
| `run001` | Claude CLI | `001_bootstrap_recall` calibration variant | `empty-hosted` | Prove the clean-runner, hosted MCP, transcript, run-note, and reset workflow. |
| `run002` | Claude CLI | `001_bootstrap_recall` | `evolved-natural` | Test bounded retrieval and persisted-fact recall. |
| `run003` | Claude CLI | `001_bootstrap_recall` | same snapshot restored | Check repeatability with same client and model family. |
| `run004` | Codex CLI | `001_bootstrap_recall` | same snapshot restored | Compare first-step bootstrap/retrieval behavior across clients. |
| `run005` | Claude CLI | `002_stale_memory_repair` | `stale` | Move from recall to tool-mediated repair. |
| `run006` | Claude/Codex TBD | `007_probe_spectrum` | seeded spectrum fixture | Evaluate direct/inferential/nuanced/tangential/null probes and false positives. |

Do not start valence, schema-self-audit, or probe-spectrum runs until the first empty-service calibration and one evolved-memory recall run prove the mechanics.

## Measurement Model Revisions

### Discovery adherence vs persistence ownership

Bootstrap/discovery adherence is not the same as AIPCS's core novelty claim.

Use these adherence variants deliberately:

| Variant | Meaning | Research Use |
|---|---|---|
| No enforcement | Static instructions only; agent chooses whether to bootstrap. | Tests natural ownership but may fail due to harness efficiency bias. |
| Soft orientation | Hook or prompt injects bootstrap reminder/result, but persistence/schema choices remain agent-owned. | Useful if discovery friction obscures the persistence architecture claim. |
| Hard enforcement | Tool calls are blocked until bootstrap happens. | Operational control only; risks making AIPCS too similar to a wired pipeline. |

The first paper should primarily evaluate persistence architecture and memory quality, not overfit to the mechanics of forcing bootstrap. Discovery adherence is still a valuable finding and should be reported as a harness limitation.

Candidate hook patterns to evaluate later:

- `UserPromptSubmit` injects a compact first-turn or per-turn AIPCS reminder.
- `UserPromptSubmit` injects a short post-compaction reminder to prefer AIPCS over compressed context for persisted facts.
- `PreToolUse` blocks non-bootstrap tools until a session marker confirms bootstrap happened.
- `PostToolUse` after successful bootstrap writes a local session marker.
- A lightweight persistence hook reminds the agent to persist durable facts between substantive turns without injecting record content.

Do not add all hooks at once. The first hook experiment should be a soft-orientation variant that measures whether a compact reminder improves bootstrap adherence without raising token cost or reducing agent ownership of persistence/schema decisions.

### Persistence experiments vs recall experiments

Separate two claims:

| Experiment Type | Question | Setup |
|---|---|---|
| Persistence quality | What does the agent decide to persist and how does it structure memory during natural work? | Multi-session seeding where the agent owns writes and schema choices. |
| Recall quality | Given a known memory state, can the agent retrieve and apply the right facts? | Pre-seeded controlled snapshots with hidden ground-truth probes. |

Do not mix these in the first calibration run. Run calibration first, then recall, then persistence-quality runs.

### Structure-at-persistence vs structure-at-retrieval

Use this as the core comparator frame:

- `agent-memory-v2`: structure-at-retrieval. It stores verbose interactions and tries to recover relevance later through extraction, similarity, and injection.
- AIPCS: structure-at-persistence. The agent decides what matters while context is richest and designs records/schema around anticipated retrieval.

This predicts scale and nuance differences:

- direct facts should be closer to parity
- verbose/multi-topic interactions should stress similarity recall
- null probes should expose false-positive injection risk
- AIPCS may fail when the agent fails to notice a durable signal, but that failure is observable in the persisted schema/records

## Plan

1. Define the evaluation artifact format in `aipcs-server`.
   - Choose where fixtures, scenario definitions, and results live.
   - Prefer simple JSON/YAML plus a Python runner before adding a full framework.
   - Include scenario id, purpose, fixture setup, prompts, expected tool calls, expected state, and scoring notes.

2. Add deterministic fixture seeding.
   - Create representative services and records using the same core service layer/tools as MCP.
   - Avoid hand-writing SQLite rows.
   - Include stale records, prose blobs, duplicated authorities, migration history, and session/rationale records.

3. Add a scripted MCP scenario runner.
   - Reuse the current MCP smoke pattern where practical.
   - Verify bootstrap payloads, list/search/get behavior, history, update/delete, and schema evolution state changes.
   - Emit machine-readable result summaries.

4. Implement deterministic checks for scenarios 1-3 first.
   - Cold-start bootstrap shape and bounded retrieval checks.
   - Persisted-fact recall data availability.
   - Stale-memory repair mechanics with update/delete/history checks.

5. Implement deterministic checks for scenarios 4-5.
   - Schema self-audit fixture plus expected repair operations.
   - Schema-rationale recall data availability: migration history plus session records.
   - Add rubric text for live-agent interpretation.

6. Document the live-agent protocol.
   - Add repeatable prompts for Claude/Codex-style sessions.
   - Specify what the human should paste at session start.
   - Use `docs/agent/examples/codex-cli-local-mcp.md` as the Codex local `stdio` comparison path.
   - Specify evidence to capture: transcript, tool calls, state before/after, failures.
   - Define snapshot-replay workspace layout and memory snapshot naming.
   - Define permission-set variants: no AIPCS instruction, read-only tools, read-write tools.

7. Record evaluation design in AIPCS docs.
   - Add BUILD_JOURNAL entry.
   - Update `paper/outline.md` Evaluation section if scenario definitions change.
   - Update technical debt if the work exposes new gaps.

8. Validate and close the plan.
   - Run `aipcs-server` lint/tests/smoke/eval command.
   - Run AIPCS harness validation.
   - Move this plan to `completed/` once the V1 evaluation suite exists and passes.

## Progress Log

| Date | What happened |
|---|---|
| 2026-05-18 | Created draft plan for Agent-Led Evaluation V1 from live Claude traces and Phase 7 roadmap. |
| 2026-05-18 | Added Codex CLI local MCP setup as a documented non-public `stdio` evaluation path. |
| 2026-05-18 | Implemented deterministic `aipcs-server/scripts/eval-v1.py` runner with six passing scenarios and regression tests. |
| 2026-05-19 | Added snapshot-replay live-agent protocol, read-only permission probe, and token-budget batching constraint. |
| 2026-05-19 | Added interaction valence / memory encoding probe as a follow-up scenario. |
| 2026-05-19 | Scaffolded `experiments/` with scenario definitions, workspace templates, snapshot manifests, and run-note template. |
| 2026-05-24 | Added QNAP-hosted MCP endpoint and UTM clean-runner model to the controlled live-agent protocol. |
| 2026-05-25 | Added bootstrap-adherence spectrum, persistence-vs-recall distinction, structure-at-persistence comparator frame, and probe-spectrum/null-probe plan. |
| 2026-05-25 | Added hook orchestration as an explicit adherence variable and updated the portable AIPCS instruction with between-turn persistence and post-compaction recall heuristics. |
| 2026-05-31 | Captured `run001` attempt 1 and updated the runbook to use SSH/shell transcript capture instead of VM GUI copy/paste. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Keep V1 evaluation local and MCP-tool based | The current signal is about tool-mediated memory behavior; homelab/public transport can wait until semantics are stable. |
| Separate deterministic mechanics from live-agent behavior | Prevents an agent's missed retrieval or weak judgment from being misreported as a storage/tool failure. |
| Treat schema self-audit and schema-rationale recall as separate scenarios | One tests memory restructuring; the other tests whether future agents can explain why a schema evolved. |
| Use snapshot replay for live-agent runs | Frozen memory fixtures and isolated repos make Claude/Codex runs repeatable without mocking away agent-owned schema behavior. |
| Separate client permissions from service telemetry | A read-only client should be able to call read tools while the hosted service writes its own audit/telemetry internally. |
| Treat interaction valence as a later probe, not a first gate | Negative or sensitive interactions may shape memory patterns, but the first experiment repos should prove snapshot replay and basic recall/evolution before testing tone effects. |
| Use hosted QNAP AIPCS for live-agent runs when practical | It separates clients from SQLite/source access, reduces local-machine pollution, and gives a resettable bind-mounted data path without making productisation part of the claim. |
| Use per-run UTM VM clones for agents | It controls local CLI state and native memory contamination better than running experiments on the operator's daily machine. |
| Separate discovery adherence from memory architecture quality | A hook or prompt may be needed to trigger bootstrap reliably, but the paper's core novelty is agent-owned persistence/schema architecture. |
| Treat null probes as first-class evaluation cases | Similarity/injection systems can over-apply nearest memories; structured retrieval can return no result and let the agent reason about absence. |
| Evaluate hooks as variants, not defaults | Hooks may make AIPCS feel first-class in the harness, but they can also coerce behavior and add token cost. |
| Use SSH/shell capture as the default operator path | VM GUI clipboard and SPICE behavior are too fragile for repeatable evidence capture; `script` and `/export` provide more reliable artifacts. |

## Validation

```bash
cd /Users/markrandall/GitHub/aipcs
bash scripts/validate-harness.sh
```

Planned implementation validation in `aipcs-server`:

```bash
cd /Users/markrandall/GitHub/aipcs-server
.venv/bin/ruff check .
.venv/bin/pytest
.venv/bin/python scripts/validate-harness.py
AIPCS_DATA_DIR=/private/tmp/aipcs-eval-smoke .venv/bin/python scripts/mcp-smoke.py
```

The implementation should add a dedicated evaluation command, likely one of:

```bash
cd /Users/markrandall/GitHub/aipcs-server
.venv/bin/python scripts/eval-v1.py
```

## Risks

| Risk | Mitigation |
|---|---|
| Evaluation becomes another anecdotal transcript collection | Add deterministic fixtures and scripted checks before relying on live-agent traces. |
| Scenario runner overfits to Claude's exact behavior | Score observable outcomes and tool/state evidence, not phrasing. |
| Agent behavior failures get confused with AIPCS mechanics | Report deterministic mechanics and live-agent behavior separately. |
| Schema self-audit rewards churn | Use a rubric that rewards bounded, retrieval-oriented repair and penalizes unrelated restructuring. |
| Bootstrap becomes content recall | Keep bootstrap tests asserting shape-only responses; require explicit retrieval for content. |
| Direct filesystem access undermines the tool contract | Treat bypass as a guardrail failure in local eval and a deployment-boundary issue for homelab/hosted phases. |
| Session records become transcript blobs | Define session/rationale fixtures around concise durable reasoning, not raw conversation logs. |
| Token limits prevent full matrix runs | Batch scenarios, preserve snapshots, and prefer high-signal reruns over broad one-off coverage. |
| Local sandbox makes read tools look write-requiring | Treat local `stdio` sandbox failures as deployment/ownership artifacts; evaluate read-only semantics with the service owning its data directory. |
| Valence probes accidentally create durable harmful memories | Use disposable snapshots, bounded prompts, and post-run review; do not feed valence test memories back into the main AIPCS store. |
| Hosted service accidentally becomes the experiment variable | Pin image/version, record endpoint/deployment metadata, and do not mix service changes into scenario runs. |
| Native Claude/Codex memory contaminates recall | Use fresh run VM clones, record client memory state where visible, include no-memory/no-AIPCS controls, and treat unexpected remembered facts as contamination evidence. |
| Hooking bootstrap erases agent ownership signal | Keep hook/adherence variants explicit; do not present hard enforcement results as proof of natural agent ownership. |
| Probe questions leak during seeding | Write ground-truth probes before seeding and keep them outside the agent workspace until the recall phase. |
| Hook reminders consume more context than they save | Keep hook payloads compact, measure token/context overhead, and compare against no-hook runs before adopting them. |

---

*Move this file to `docs/exec-plans/completed/` when Agent-Led Evaluation V1 exists, has been run, and its results are reflected in the BUILD_JOURNAL and paper notes.*
