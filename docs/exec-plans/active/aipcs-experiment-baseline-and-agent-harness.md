# Execution Plan: AIPCS Experiment Baseline and Agent Harness

**Status:** Active
**Owner:** Agent
**Created:** 2026-05-06
**Last updated:** 2026-05-18
**BUILD_JOURNAL entries:** Entry 009, Entry 010, Entries 018-029

---

## Goal

Establish an actionable experiment plan that separates memory-system quality from agent/model capability, using the current `agent-memory-v2` implementation as the baseline, `aipcs-model-lab` as the model-interaction harness, and the homelab as the default deployment substrate for prototype services.

## Non-Goals

This plan does not implement the agent harness, modify `agent-memory-v2`, create a protocol document, add Claude/Gemini providers, rent cloud GPU capacity, deploy services to QNAP, or implement the AIPCS candidate memory system.

## Context

- `docs/product/research-brief.md` defines AIPCS as agent-instantiated, domain-adaptive memory where the agent is the schema architect.
- `docs/AIPCS_v1_Technical_Design.md` defines the v1 MCP-native primitive server, seeded/materialised lifecycle, and schema evolution model.
- `docs/architecture/index.md` records the current trigger, mechanism, registration, and primitive-tool decisions.
- `paper/outline.md` currently identifies Evaluation as requiring metrics for latency, token cost, schema quality, trigger behavior, and failure modes.
- Canonical baseline repo: `/Users/markrandall/GitHub/agent-memory-v2`.
- Stale repo path to avoid for baseline work: `/Volumes/Media/Repository/agent_memory_v2`.
- Adjacent related-work baseline: [`kninetimmy/memhub`](https://github.com/kninetimmy/memhub), a local per-repo coding memory system with predefined classes, classifier/retrieval pipeline, SQLite, MCP, staged writes, and FTS/hybrid recall.
- Companion model harness repo: `/Users/markrandall/GitHub/aipcs-model-lab`.
- Homelab operations repo: `/Users/markrandall/GitHub/homelab`.
- Homelab service substrate: QNAP-hosted Docker/Portainer stacks on the `homelab` network, Caddy reverse proxy under `*.indigo-blocks.uk`, Grafana/Prometheus/Loki observability, Open WebUI at `https://chat.indigo-blocks.uk`, and Brandon's vLLM relay available to homelab containers at `http://brandon-ts:8080/v1`.
- Hardware constraint: QNAP has enough memory for lightweight services, but CPU is a low-power Intel J4105 Celeron class system with no GPU. Use it for services, persistence, routing, and observability; do not expect it to run heavy local inference.
- First agent-led AIPCS test: Claude CLI / Claude Code with `claude-sonnet-4-6`, connected to local `aipcs-server` through MCP `stdio`, seeded and materialised `claude_memory`, and persisted records after self-correcting validation errors.
- Interpretation of that test: useful design signal, not a finished evaluation. AIPCS changed how the agent thought about memory patterning, but also exposed bootstrap/discovery, retrieval enrichment, provenance, and direct-database trust-boundary issues.
- Bootstrap is now treated as a three-layer design: static AIPCS instructions, dynamic data-dictionary map, and possible later procedural skills. The MCP tool only solves the dynamic map.
- Current lab runbook: [AIPCS Lab Experiment Runbook](../../references/aipcs-lab-experiment-runbook.md).
- Current next-phase experiment classes: [Experiment Class Plan](../../references/experiment-class-plan.md).

## Acceptance Criteria

- [ ] This execution plan exists in `docs/exec-plans/active/` and is specific enough for another agent or engineer to implement.
- [ ] The plan defines separate Layer 1 memory-mechanics evaluation and Layer 2 agent-behavior evaluation.
- [ ] The plan lists reproducible current-baseline commands for the canonical `agent-memory-v2` checkout.
- [ ] The plan scopes the first API-backed agent reference to an OpenAI-compatible provider interface without requiring Claude, Gemini, or cloud GPU.
- [ ] The plan explicitly defers cloud GPU unless local open-model comparison becomes a blocker.
- [ ] The plan captures the paper Evaluation implication: reported results must distinguish memory-system performance from model/agent capability.
- [ ] The plan captures that homelab is now the standard deployment target for service prototypes unless Apple Silicon or workstation-only constraints require local execution.
- [ ] The plan captures that bootstrap/discovery and retrieval quality are now first-order evaluation dimensions, not later polish.

## Plan

1. Record the experimental claim.
   - Memory mechanics must be measured independently from model behavior.
   - End-to-end behavior must be measured with an instruction-following agent harness.
   - No AIPCS claim should rely on `llama3:8b` behavior alone.

2. Define the systems under test.
   - `agent_memory_v2_fixed`: current fixed taxonomy, rule classifier, semantic router, structured extractor, sidecar, profile, and prompt builder.
   - `agent_memory_v2_agentic_wrapper`: current `agent-memory-v2` backend exposed through model-decided tool-loop operations.
   - `memhub_related_work`: fixed-domain coding memory with predefined facts/decisions/tasks/docs and a strong local retrieval/indexing implementation; use as related work or future comparator, not as an AIPCS candidate.
   - `aipcs_candidate`: later primitive/schema-evolving candidate that lets the agent propose memory structure.

3. Define the model and provider ladder.
   - Required current baseline: `agent-memory-v2` deterministic, live, and scenario harnesses.
   - Required first agent-class reference: an OpenAI-compatible API model through a provider-neutral harness interface.
   - Available API/provider references:
     - NVIDIA NIM via `aipcs-model-lab` (`meta/llama-4-maverick-17b-128e-instruct` proven on 2026-05-09).
     - Brandon vLLM relay from inside homelab containers via `http://brandon-ts:8080/v1`.
     - Brandon direct Mercury endpoint from machines with working Brandon tailnet DNS via `https://vllm.mercury.jpopweb.com:3927/v1`.
     - Google Gemini via API key when adapter support is added.
   - Optional local/workstation ladder: `llama3:8b`, `gpt-oss:20b`, `gemma3:12b`, `gemma3:27b`, only when local hardware is a better fit than homelab.
   - Deferred API providers: Claude and broader Gemini evaluation until the provider-neutral contract is stable.
   - Deferred infrastructure: rented cloud GPU, unless local open-model testing is too slow or blocks useful comparison.

4. Define the minimal agent harness contract.
   - `memory_write`: persist a fact, preference, task, or contextual item with a reason.
   - `memory_query`: retrieve candidate memories for a query.
   - `memory_inspect`: expose current profile, memory state, or schema summary.
   - `answer`: final response to the user.
   - `memory_evolve`: later AIPCS-only operation for schema or object-model proposals.
   - Harness rules: fixed max tool calls per turn, strict JSON parsing, invalid-call counts, saved traces, latency capture, and identical scenarios across providers.

5. Establish Layer 1 memory-mechanics evaluation.
   - Use existing `agent-memory-v2` deterministic and live harnesses before adding any OpenAI results.
   - Measure capture accuracy, extraction accuracy, recall precision, conflict handling, prompt cleanliness, storage growth, and maintenance behavior.
   - Preserve deterministic tests as model-independent evidence.

6. Establish Layer 2 agent-behavior evaluation.
   - Run the same scenarios through the minimal tool-loop harness.
   - Measure tool-use validity, tool-use judgment, answer correctness, answer grounding, latency, call count, and model sensitivity.
   - Use OpenAI as the first agent-class reference because AIPCS assumes reliable instruction following and tool use.

7. Define AIPCS-specific evaluation dimensions for later candidate work.
   - Schema autonomy: how much structure is agent-proposed rather than developer-predefined.
   - Schema usefulness: whether generated structure improves later query specificity or recall.
   - Evolution quality: whether changes are additive, relevant, and inspectable.
   - Inspectability: whether stored memory and schema decisions can be explained from artifacts.
   - Bootstrap quality: whether the agent can cold-start, discover existing domains, and avoid duplicate seeds.
   - Retrieval enrichment: whether provenance and computed temporal signals improve how agents weight recalled records.
   - Session-start retrieval discipline: whether the agent loads bounded content from memory-like entities after bootstrap.
   - Static instruction effectiveness: whether the agent calls bootstrap without the user reminding it AIPCS exists.
   - Authority model: whether content duplication occurs when file/bootstrap memory and AIPCS coexist.

8. Capture paper and journal implications after the first implementation work.
   - Add a BUILD_JOURNAL entry when harness implementation or baseline collection starts.
   - Update `paper/outline.md` Evaluation notes after the first real baseline results exist.
   - Report both memory-system performance and agent-class behavior; do not collapse them into one score.

9. Use homelab as the standard service substrate for AIPCS prototypes.
   - Develop locally where iteration speed matters, but target QNAP deployment for durable services.
   - Avoid creating standalone local Docker infrastructure unless the task requires Apple Silicon, workstation-only tools, or temporary isolated development.
   - For deployable AIPCS components, follow the homelab service pattern: repo-managed compose, `homelab` network membership, Caddy route only when needed, registry documentation, and observability where useful.
   - Treat Open WebUI as a human/model UX and Brandon vLLM as a model backend, not as the memory-service control plane.

10. Keep the first AIPCS memory prototype small.
   - Build a local-first MCP memory server with SQLite persistence and the v1 management primitives before introducing dynamic service materialisation complexity.
   - Prefer Python or Node based on MCP SDK maturity and deployment simplicity; do not add a database server for the first prototype.
   - Containerise only after the primitive tool loop is testable locally.
   - Deploy to homelab only when we need persistence, observability, Open WebUI adjacency, or multi-client access.

11. Add bootstrap and retrieval scenarios before formal scoring.
   - Bootstrap scenario: agent starts with AIPCS connected but no content in active context; it must discover existing services and choose whether to inspect/query.
   - Retrieval scenario: agent must answer from existing AIPCS records, including stale or inferred records where provenance/age matters.
   - Persisted fact probe: agent is asked about a known fact that exists in AIPCS but is absent from active context; it must fetch the relevant entity before answering.
   - Drift scenario: agent has both file bootstrap memory and AIPCS content; it must avoid duplicating content across stores.
   - Search scenario: agent must locate records using structured filters first; richer text/semantic retrieval can be added later.

12. Keep deployment layers distinct in evaluation notes.
   - Local `stdio` proves tool semantics and agent behavior with Claude CLI.
   - Homelab proves durable deployment and multi-client operations when useful.
   - Hosted Claude/ChatGPT require public MCP or a bridge because provider infrastructure initiates the connection.
   - Direct SQLite access by an agent is outside the AIPCS contract and should be treated as a trust-boundary failure mode, not a supported feature.

## Baseline Commands

Run these from the canonical checkout before implementing or comparing an AIPCS candidate:

```bash
cd /Users/markrandall/GitHub/agent-memory-v2
make doctor
make eval-all ARGS="--record-history"
make live-eval-all ARGS="--record-history --save-all"
make scenario-run ARGS="--scenario preference_recall"
```

After the OpenAI harness exists, repeat selected live/scenario runs through the OpenAI provider and save equivalent traces.

## Progress Log

| Date | What happened |
|---|---|
| 2026-05-06 | Created draft execution plan for the two-layer experiment and first OpenAI-backed harness scope. |
| 2026-05-06 | Recorded first `agent-memory-v2` baseline evidence in `docs/references/evaluation-baseline-2026-05-06.md`. |
| 2026-05-17 | Updated the plan to account for the homelab substrate, `aipcs-model-lab`, NVIDIA NIM proof, and Brandon vLLM relay. |
| 2026-05-18 | Updated the plan to reflect the first Claude CLI AIPCS test: bootstrap/discovery, retrieval enrichment, provenance, and deployment boundary are now explicit evaluation dimensions. |
| 2026-05-18 | Recorded the retrieval design choice: dedicated bootstrap, exact structured search, provenance conventions, and dynamic updated-age metadata. |
| 2026-05-18 | Added the second Claude CLI finding: bootstrap shape is insufficient unless agents follow a bounded session-start retrieval policy. |
| 2026-05-18 | Reframed bootstrap as static instructions plus dynamic data-dictionary map, with procedural skills deferred as a separate design boundary. |
| 2026-06-06 | Added a repeatable btrfs/isolated-HOME lab runbook for fast Claude CLI + run-local AIPCS experiments. |
| 2026-06-06 | Processed `run010` as a runbook/planning persistence test: empty AIPCS bootstrap was used as signal, Claude persisted structured run summaries/plans, and the runbook now captures outside-run file containment. |
| 2026-06-06 | Processed `run011` as a full multi-record discrimination pass: Claude retrieved all synthetic AIPCS-only records, applied the active constraint, declined the Codex-scoped null probe, and treated historical context as background. |
| 2026-06-06 | Processed `run012` as an autonomous persistence pass with caveats: Claude created `experiment_lab` and a run outcome record during the first answer, then wrote local file memory after the open-ended turn; auth/model changed after login. |
| 2026-06-06 | Preserved a `run012b` repeatability recipe seeded from `run011` final AIPCS state, while keeping the next live increment focused on `run013` schema ambiguity. |
| 2026-06-06 | Processed `run013` as a scaffolded schema-evolution pass: Claude added `tool_failure` to `experiment_lab` instead of flattening tool-failure structure into notes; next run should move beyond confirmation-on-confirmation. |
| 2026-06-06 | Added an experiment-class plan for weaker scaffolding, higher memory volume, conflicting/stale records, and comparative baselines to steer `run014+`. |
| 2026-06-06 | Processed `run014` as a weaker-scaffolding pass: Claude retrieved `research_direction` and `experiment_lab` from a natural time-box prompt, but recommended tool-contract remediation rather than the strongest research next step. |
| 2026-06-07 | Processed `run015` as a conflicting/stale authority-reasoning pass: Claude retrieved the seeded authority context, detected the conflict, weighed authority dimensions, recommended the ground-truth next step, then autonomously persisted the run outcome after delegated judgment. |
| 2026-06-07 | Prepared `run016` as a higher-volume multi-service corpus run with a reusable seed script and runbook, avoiding self-disclosing service descriptions from `run015`. |

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Use a two-layer evaluation model | Prevents weak local model behavior from being misreported as memory-system failure. |
| Use OpenAI as the first API-backed reference | Gives the experiment an agent-class model closer to the AIPCS assumption of reliable instruction following and tool use. |
| Defer Claude, Gemini, and cloud GPU | Keeps the first implementation bounded while preserving future comparison paths. |
| Treat `application_tracker` as a fixed-schema contrast only | It is a conventional application-access model, not the main memory-system baseline. |
| Treat homelab as the default deployment substrate | Avoids creating duplicate local infrastructure now that QNAP, Caddy, Portainer, observability, Open WebUI, and Brandon vLLM access are available. |
| Keep `aipcs-model-lab` as a companion harness | It provides model/provider interaction and traces, but AIPCS remains the mission and source of pattern truth. |
| Treat bootstrap/discovery as v1-critical | The first agent-led test showed the agent only used AIPCS because the task prompted it; cold-start orientation needs an explicit tool/skill surface. |
| Treat retrieval enrichment as evaluation-critical | Raw records are insufficient for memory quality; provenance and relative time affect how agents should weight recalled content. |
| Do not treat local direct SQLite access as a valid agent path | The Claude CLI experiment showed agents may route around tool contracts when filesystem access exists; hosted or homelab deployments must enforce MCP/tool boundaries. |
| Treat `memhub` as fixed-taxonomy related work | It is a strong local engineering baseline, but its schema/classes are developer-defined rather than agent-instantiated. |

## Validation

```bash
cd /Users/markrandall/GitHub/aipcs
bash scripts/validate-harness.sh
```

Before any later harness implementation:

```bash
cd /Users/markrandall/GitHub/agent-memory-v2
make doctor
make eval-all ARGS="--record-history"
make live-eval-all ARGS="--record-history --save-all"
```

## Risks

| Risk | Mitigation |
|---|---|
| Model capability dominates the results | Keep Layer 1 model-independent and report Layer 2 separately. |
| OpenAI results become incomparable with local runs | Use the same scenario definitions, tool budget, trace schema, and scoring rubric across providers. |
| Cloud GPU work expands scope too early | Defer GPU rental unless local open-model testing blocks useful evidence. |
| Stale NAS checkout contaminates baseline results | Require `/Users/markrandall/GitHub/agent-memory-v2` in all baseline commands and docs. |
| Paper claims overreach before AIPCS candidate exists | State that current work establishes baseline and harness, not final AIPCS performance. |
| Homelab work becomes a detour | Treat homelab as substrate only; every service or MCP experiment must directly support AIPCS memory prototyping or evaluation. |
| QNAP CPU bottlenecks distort model/harness results | Use QNAP for service hosting and persistence, not heavy inference. Use NVIDIA, Gemini, Brandon vLLM, or Apple Silicon when compute matters. |
| Bootstrap is mistaken for full reconstruction | Bootstrap should provide a map of domains/entities/counts/recent activity, not a dump of all memory content. |
| AIPCS duplicates file memory | Define file memory as bootstrap-only when AIPCS is connected; AIPCS is authoritative for content. |
| Evaluation overweights write success | Include retrieval and correction scenarios; write-only success does not prove memory usefulness. |
