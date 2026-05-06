# Execution Plan: AIPCS Experiment Baseline and Agent Harness

**Status:** Draft
**Owner:** Agent
**Created:** 2026-05-06
**Last updated:** 2026-05-06
**BUILD_JOURNAL entries:** Entry 009, Entry 010

---

## Goal

Establish an actionable experiment plan that separates memory-system quality from agent/model capability, using the current `agent-memory-v2` implementation as the baseline and an OpenAI-backed mini agent harness as the first agent-class reference.

## Non-Goals

This plan does not implement the agent harness, modify `agent-memory-v2`, create a protocol document, add Claude/Gemini providers, rent cloud GPU capacity, or implement the AIPCS candidate memory system.

## Context

- `docs/product/research-brief.md` defines AIPCS as agent-instantiated, domain-adaptive memory where the agent is the schema architect.
- `docs/AIPCS_v1_Technical_Design.md` defines the v1 MCP-native primitive server, seeded/materialised lifecycle, and schema evolution model.
- `docs/architecture/index.md` records the current trigger, mechanism, registration, and primitive-tool decisions.
- `paper/outline.md` currently identifies Evaluation as requiring metrics for latency, token cost, schema quality, trigger behavior, and failure modes.
- Canonical baseline repo: `/Users/markrandall/GitHub/agent-memory-v2`.
- Stale repo path to avoid for baseline work: `/Volumes/Media/Repository/agent_memory_v2`.

## Acceptance Criteria

- [ ] This execution plan exists in `docs/exec-plans/active/` and is specific enough for another agent or engineer to implement.
- [ ] The plan defines separate Layer 1 memory-mechanics evaluation and Layer 2 agent-behavior evaluation.
- [ ] The plan lists reproducible current-baseline commands for the canonical `agent-memory-v2` checkout.
- [ ] The plan scopes the first API-backed agent reference to OpenAI without requiring Claude, Gemini, or cloud GPU.
- [ ] The plan explicitly defers cloud GPU unless local open-model comparison becomes a blocker.
- [ ] The plan captures the paper Evaluation implication: reported results must distinguish memory-system performance from model/agent capability.

## Plan

1. Record the experimental claim.
   - Memory mechanics must be measured independently from model behavior.
   - End-to-end behavior must be measured with an instruction-following agent harness.
   - No AIPCS claim should rely on `llama3:8b` behavior alone.

2. Define the systems under test.
   - `agent_memory_v2_fixed`: current fixed taxonomy, rule classifier, semantic router, structured extractor, sidecar, profile, and prompt builder.
   - `agent_memory_v2_agentic_wrapper`: current `agent-memory-v2` backend exposed through model-decided tool-loop operations.
   - `aipcs_candidate`: later primitive/schema-evolving candidate that lets the agent propose memory structure.

3. Define the model and provider ladder.
   - Required current baseline: `agent-memory-v2` deterministic, live, and scenario harnesses.
   - Required first agent-class reference: OpenAI API model through a provider-neutral harness interface.
   - Optional local ladder: `llama3:8b`, `gpt-oss:20b`, `gemma3:12b`, `gemma3:27b`.
   - Deferred API providers: Claude and Gemini.
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

8. Capture paper and journal implications after the first implementation work.
   - Add a BUILD_JOURNAL entry when harness implementation or baseline collection starts.
   - Update `paper/outline.md` Evaluation notes after the first real baseline results exist.
   - Report both memory-system performance and agent-class behavior; do not collapse them into one score.

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

## Decisions Made During Work

| Decision | Rationale |
|---|---|
| Use a two-layer evaluation model | Prevents weak local model behavior from being misreported as memory-system failure. |
| Use OpenAI as the first API-backed reference | Gives the experiment an agent-class model closer to the AIPCS assumption of reliable instruction following and tool use. |
| Defer Claude, Gemini, and cloud GPU | Keeps the first implementation bounded while preserving future comparison paths. |
| Treat `application_tracker` as a fixed-schema contrast only | It is a conventional application-access model, not the main memory-system baseline. |

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
