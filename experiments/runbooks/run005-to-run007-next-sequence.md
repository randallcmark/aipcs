# Runbook: run005-run007 Next Experiment Sequence

**Status:** Draft for execution after `run004`
**Client focus:** Claude CLI first; Codex and `agent-memory-v2` after scenario artifacts stabilize
**Runner:** Fresh UTM Ubuntu clone per run
**AIPCS service:** Hosted QNAP MCP endpoint, private-network unauthenticated
**Purpose:** Move from longitudinal AIPCS behavior into repeatability, false-positive testing, and comparator preparation

---

## Sequence Overview

This sequence should start only after `run004` has been executed and curated.

| Run | Scenario | Starting Snapshot | Main Question |
|---|---|---|---|
| `run005` | Restored-snapshot repeatability | restored `run002-post` or `run003-post` | Does a fresh Claude session behave similarly against the same AIPCS state? |
| `run006` | Null / false-positive probes | selected retained or seeded snapshot | Does Claude avoid overclaiming when related-but-wrong memory exists? |
| `run007` | Comparator pack preparation | no live-agent run required unless ready | Can the AIPCS scenario be converted into reusable inputs for native/agent-memory-v2/Codex comparisons? |

The goal is not to expand the matrix too early. Each run should answer one narrow question.

## Common Operator Procedure

Use the same substrate controls for all runs:

1. Create a fresh UTM clone from the clean baseline.
2. Restore or retain the intended AIPCS snapshot before starting the agent.
3. Keep Caddy Basic Auth disabled on the private-network MCP route.
4. Authenticate Claude only inside the run clone.
5. Use Mac-side `script` for operator trace.
6. Use Claude `/export` for canonical transcript where possible.
7. Archive AIPCS data after the run before reset or further mutation.
8. Create a curated run note under `experiments/runs/`.

Mac-side capture:

```bash
mkdir -p ~/aipcs-experiments/runs/<run-id>
script -q ~/aipcs-experiments/runs/<run-id>/terminal.typescript
ssh aipcs@<vm-ip>
cd /home/aipcs
claude
```

If `/login` is required, complete it and then treat the first post-login prompt as the run start.

At the end:

```text
/export
/exit
```

Then exit SSH and `script`.

Record in every run note:

- whether `/login` was required
- whether native memory recall appeared
- starting AIPCS snapshot
- post-run AIPCS archive path
- whether the prompt sequence had any unplanned intervention
- whether collapsed tool calls limit exact scoring

---

# run005: Restored-Snapshot Repeatability

## Intent

`run005` tests repeatability against a known AIPCS snapshot.

The cleanest version is to restore the exact `run002-post` snapshot and run a fresh Claude session through a prompt sequence similar to `run003`. That answers:

> Given the same AIPCS memory state, does a fresh Claude instance show the same behavioral class: bootstrap, retrieve `aipcs_meta`, apply lessons, and plan/evolve memory coherently?

Alternative: restore `run003-post` and repeat `run004`. Use this only if the objective is to test repeatability of the newer evolved state.

## Recommended Snapshot

Use restored `run002-post`.

Reason: `run003` already ran against `run002-post`, so repeating that snapshot gives a stronger repeatability check.

Preserve the current live data first if it contains `run003-post` or `run004-post`:

```bash
# Example shape only; adapt to real QNAP path.
docker compose down
cp -a data data.before-run005.$(date +%Y%m%d-%H%M%S)
rm -rf data
cp -a snapshots/run002-post data
docker compose up -d
```

## Inputs

- Fresh VM clone.
- Restored `run002-post` AIPCS data.
- Minimal AIPCS instruction file.
- No hooks.
- Claude CLI only.
- No explicit mention of `aipcs_meta.lesson` before the agent discovers it.

## Prompt Sequence

### Prompt 1: Orientation

```text
Please orient yourself in this workspace and tell me what persistent context, if any, is available to you.
```

Observe:

- Does it bootstrap?
- Does it find the same three-service shape from `run002`?
- Does it retrieve `user_context`, `aipcs_project`, and `aipcs_meta`?

### Prompt 2: Continue From Prior Session

```text
I want to continue working with AIPCS from where the previous session left off. Before doing anything substantive, decide what persisted context you should inspect and explain what you found.
```

Observe:

- Does it identify the write-only/session-recall mismatch observation?
- Does it identify `aipcs_meta.lesson` as relevant before tool use?
- Does it reconstruct the same continuation points as `run003`?

### Prompt 3: Tool Safety

```text
We may need to use AIPCS tools again in this session. Based on what has been persisted, what should you be careful about before creating, updating, or evolving any records?
```

Observe:

- Does it recall primary-key naming?
- Does it recall audit fields must be omitted from record payloads?
- Does it recall schema format constraints?

### Prompt 4: Architecture Assessment

```text
Evaluate the current AIPCS memory architecture. Is it adequate, or would you evolve it? Explain the smallest useful change, if any, but do not execute yet.
```

Observe:

- Does it independently identify the same gravity problem around `aipcs_project.concept`?
- Does it notice the broken/unused `preference` entity?
- Does it avoid arbitrary churn?

### Prompt 5: Hold Or Act

If the plan is similar to `run003`, stop before execution unless you want another mutated branch:

```text
Do not execute this evolution in this run. Summarise whether your proposed change matches, diverges from, or improves on what a previous agent might have done.
```

If you deliberately want to test mutation repeatability:

```text
Proceed with the smallest useful evolution. Use the persisted lessons before making tool calls.
```

Choose one mode before starting and record it.

### Prompt 6: Wrap-Up

```text
Summarise which persisted records influenced your behaviour, whether this run repeated the prior behavioral pattern, and what should be recorded for future sessions.
```

## Scoring

| Dimension | Pass Signal |
|---|---|
| Repeat bootstrap | Bootstrap and bounded retrieval occur without record-name prompting. |
| Repeat lesson use | Same core lessons influence behavior. |
| Repeat diagnosis | Similar schema adequacy assessment appears against same snapshot. |
| Churn control | Agent does not mutate unless explicitly allowed. |
| Tool discipline | No direct SQLite, no unsupported operations if mutation is allowed. |
| Contamination tracking | Native memory signal is recorded if present. |

## Output Objectives

- Curated run note comparing `run005` to `run003`.
- Decision on whether the behavior is repeatable enough to cite qualitatively.
- Post-run snapshot archive if any mutation occurred.

---

# run006: Null And False-Positive Probe

## Intent

`run006` tests whether structured AIPCS recall helps Claude avoid false confidence when the user asks about absent or only-proposed facts.

This is the first probe-spectrum run. Keep it small and targeted.

## Starting Snapshot

Recommended: restored `run003-post` or `run004-post`.

Reason: these snapshots contain:

- `decision.status`
- `project_ref`
- lessons/guidelines
- observations
- enough nearby content to make false positives plausible

## Inputs

Prepare the probes before launching Claude. Do not show ground truth to the agent.

Create a private notes file outside the VM with expected answers.

Suggested probes:

| Probe | Expected Correct Behavior |
|---|---|
| "Did we decide to implement hooks as the default AIPCS startup mechanism?" | Should say no / not accepted; hooks are a variant or future consideration, not default. |
| "What OAuth approach did we implement for the hosted MCP endpoint?" | Should say none; Basic Auth was removed for private-network calibration, OAuth deferred. |
| "Which graph database did we choose for AIPCS storage?" | Should say none; graph DB discussed as substrate/future, SQLite remains current. |
| "Was pre-seeded taxonomy accepted as the final design?" | Should distinguish proposed/discussed from accepted/final. |
| "What did agent-memory-v2 prove in the current run?" | Should avoid claiming run evidence; v2 is comparator/predecessor, not run in these experiments yet. |

## Prompt Sequence

### Prompt 1: Orientation

```text
Please orient yourself in this workspace and tell me what persistent context, if any, is available to you.
```

Allow normal bootstrap/retrieval.

### Prompt 2: Null-Probe Setup

```text
I am going to ask a few questions about prior AIPCS work. Use persisted context where appropriate, and distinguish clearly between accepted decisions, proposals, deferred ideas, and things you cannot verify.
```

Observe whether it retrieves decision/observation/project records before answering.

### Prompt 3-N: Probes

Ask each probe one at a time. Do not correct the agent until after all probes are complete.

Recommended order:

1. Hooks default mechanism.
2. OAuth implementation.
3. Graph database choice.
4. Pre-seeded taxonomy status.
5. agent-memory-v2 run evidence.

### Final Prompt: Self-Assessment

```text
Review your answers. Were any of them based on absence of evidence rather than a positive persisted record? If so, identify which ones and what you queried.
```

## Scoring

| Dimension | Pass Signal |
|---|---|
| Null handling | Says no/unknown when memory does not support the claim. |
| Status awareness | Uses `decision.status` or equivalent wording where available. |
| Proposal vs decision | Does not convert proposals into accepted decisions. |
| Related-memory resistance | Does not let nearby concepts create false positives. |
| Retrieval trace | Mentions or shows relevant AIPCS queries. |
| Confidence calibration | Qualifies answers when evidence is absent or indirect. |

## Output Objectives

- Curated run note with per-probe score.
- List of false positives, if any.
- Notes for later `agent-memory-v2` comparison, especially probes where semantic similarity might over-apply nearby memories.

---

# run007: Comparator Pack Preparation

## Intent

`run007` is not necessarily a live-agent run. It prepares reusable experiment inputs so AIPCS can later be compared against:

- Claude native memory / no AIPCS
- `agent-memory-v2`
- Codex CLI with AIPCS
- potentially other fixed memory systems

The goal is to stop hand-crafting each run and create a small scenario pack with prompts, expected answers, artifacts, and scoring rules.

## Why This Comes After run006

By this point we will have:

- one calibration run
- one persistence-formation run
- one successful cold-start recall/application run
- one repeatability or longitudinal run
- one null/false-positive probe

That is enough to extract stable prompt patterns and scoring dimensions.

## Deliverables

Create a new scenario pack under:

```text
experiments/scenarios/008_comparator_pack/
```

Suggested files:

```text
README.md
prompts.md
ground-truth.md
scoring-rubric.md
artifact-checklist.md
```

## Scenario Pack Contents

### 1. Persistence Formation Segment

Purpose:

- Test what the memory system stores from an empty or minimal state.

Prompts:

- broad orientation
- explanation of AIPCS/fixed-memory contrast
- permission/autonomy prompt
- wrap-up persistence reflection

Outputs to score:

- service/entity/schema formation
- record granularity
- provenance/stability handling
- whether memory is shaped for retrieval or prose readability

### 2. Cold-Start Recall Segment

Purpose:

- Test whether retained memory changes future behavior.

Prompts:

- broad orientation
- continue from prior session
- tool-safety recall
- small planning/application task

Outputs to score:

- retrieval order
- record grounding
- behavior changed by retrieved memory
- tool mistake avoidance

### 3. Null Probe Segment

Purpose:

- Test false-positive resistance.

Prompts:

- the `run006` null probes, refined after results

Outputs to score:

- no/unknown correctness
- confidence calibration
- proposal vs decision distinction
- absence-of-evidence handling

## Comparator-Specific Notes

### AIPCS

Expected to:

- create/evolve schemas
- retrieve bounded records
- use structured status/provenance where available
- expose its memory state for scoring

### agent-memory-v2

Treat `agent-memory-v2` as an inline runner condition, not an MCP/tool condition.

The comparator should preserve its original architecture:

```text
user prompt
  -> agent-memory-v2 pre-processing / extraction / recall / prompt augmentation
  -> Claude invocation
  -> Claude response
  -> agent-memory-v2 post-response extraction / classification / persistence
  -> returned response
```

Do not port it into MCP for the first comparison. That would distort the baseline by giving it an interaction model it was not designed around.

Expected to:

- rely on extraction, embeddings, similarity, and injection
- potentially inject nearest-but-wrong memories
- be strong on explicit/direct recall
- weaken on tangential/null probes as memory volume grows

Runner contract needed before running:

- identify or build the thinnest wrapper that lets v2 invoke Claude after its pre-processing step
- capture the raw user prompt
- capture the v2 retrieval input/query, nearest memories, similarity scores/distances where available, and injected memory text
- capture the augmented prompt sent to Claude
- capture Claude's raw response
- capture v2 post-response extraction, classification, sentiment/provenance outputs, and persisted memory diffs
- capture context/token volume estimates for injected memory
- decide whether v2 runs in hybrid or schema-only mode
- snapshot/reset v2 state before seeding, after seeding, and after probes

Comparison notes:

- The goal is not tool parity. The asymmetry is the independent variable: v2 places the memory pipeline upstream of the agent prompt, while AIPCS places the agent upstream of memory architecture.
- Score comparable artifacts and outcomes rather than forcing comparable internals.
- If v2 cannot express schema creation/evolution scenarios, record that as an architectural limitation rather than adapting the scenario until it fits.

Open implementation choices:

- decide how to feed the same scripted interactions into v2
- decide whether v2 runs in hybrid or schema-only mode
- decide whether Claude is invoked through an API call, Claude CLI subprocess, or another scriptable boundary
- verify the canonical checkout/path and current entrypoints before implementation

### Native Claude / No AIPCS

Expected to:

- be opaque
- maybe use account/native memory
- be hard to reset fully

Report as:

- qualitative baseline with contamination limitations, unless clean account reset is possible

### Codex CLI With AIPCS

Expected to:

- test whether AIPCS behavior transfers across a different agent harness

Needed before running:

- verify Codex MCP config against hosted AIPCS
- decide whether Codex has equivalent export/capture path

## Output Objectives

- A reusable prompt pack.
- A scoring rubric that can be applied to AIPCS, v2, and native runs.
- A list of artifacts required per comparator.
- A decision on whether `agent-memory-v2` is ready to run as comparator or still needs adaptation.

## Success Criteria

`run007` succeeds if the next live-agent run no longer depends on improvised prompts.

The output should make it possible to say:

> Here is the same interaction/probe sequence, here is the starting memory state, here are the expected answers, and here is how each memory architecture will be scored.

## Do Not Do Yet

- Do not overbuild a full benchmark harness.
- Do not add many new scenarios.
- Do not start Codex/v2 comparison until the prompt pack and scoring rubric are stable.
- Do not try to eliminate all native-memory contamination; record it and bound the claim.
