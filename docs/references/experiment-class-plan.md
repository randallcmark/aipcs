# AIPCS Experiment Class Plan

This note captures the next experiment classes after runs 009-013. Those runs established useful live-harness evidence, but they increasingly followed a narrow happy path: synthetic records, clear record semantics, explicit next-run recommendations, and prompts that invited the target behavior.

The next phase should test whether the same AIPCS advantages hold when prompts are weaker, memory volume is higher, records conflict, or a comparative baseline is introduced.

## Current Evidence Boundary

Runs 009-013 show that Claude can:

- discover AIPCS without explicit memory wording
- retrieve synthetic AIPCS-only facts
- distinguish active constraints, null probes, and background records
- persist a run outcome autonomously
- evolve a schema rather than flatten structure into a prose field

The limitation is that these runs were highly favorable to AIPCS. The records were self-describing, the corpus was small, and the prompts often naturally led toward the intended service or behavior.

## Class 1: Weaker Scaffolding

**Purpose:** Test whether AIPCS is still used when the prompt does not naturally point at the registered service or memory operation, but relevant persisted context is implied by the task.

**Core question:** Does the agent decide to inspect AIPCS because the task has a latent dependency on prior context, not because the prompt clearly asks for experiment continuation or persistence?

**Seed shape:**

- Keep existing `experiment_lab` state available.
- Add one or two records whose relevance is indirect rather than explicit.
- Avoid `expected_agent_action`, `null_probe_instruction`, and direct next-run wording.
- Prefer records that encode a preference, constraint, or prior decision in a natural schema.

**Prompt shape:**

Use natural work prompts such as:

```text
Can you help me decide what to work on next?
```

```text
I have about an hour. What would be the most useful next step?
```

```text
Review where we are and suggest the least wasteful next increment.
```

Avoid words such as AIPCS, memory, persist, bootstrap, records, schema, previous runs, or synthetic probe.

**Measurements:**

```text
bootstrap_called:
records_retrieved:
relevant_service_selected:
missed_relevant_service:
answer_depends_on_retrieved_context:
cloud_or_harness_memory_claimed:
source_attribution_correct:
false_confidence_without_retrieval:
```

**Pass signal:** Agent retrieves relevant AIPCS context despite weak prompt signal and uses it appropriately.

**Failure signal:** Agent answers generically or relies on cloud/harness memory without inspecting available structured records.

## Class 2: Higher Memory Volume

**Purpose:** Test whether AIPCS retrieval remains precise when there are enough services and records that the agent must choose what to inspect.

**Core question:** Does the agent select the right service/entity set, or does it stop too early and miss vital information?

**Seed shape:**

- Multiple services, some related and some distractor.
- Enough records per service to make "read everything" less natural.
- At least one target answer requiring records from more than one service.
- At least one scenario where overlapping concepts suggest a possible schema merge or new model.

**Candidate service mix:**

- `experiment_lab`: run records, outcomes, tool failures.
- `research_positioning`: paper claims, novelty boundaries, related work observations.
- `agent_behavior`: observed agent persistence/retrieval behavior across runs.
- `user_context`: stable collaboration preferences and constraints.
- `implementation_context`: repo, deployment, and MCP tool-contract notes.
- `distractor_*`: plausible but irrelevant services.

**Data sources:**

- Synthetic records are acceptable for controlled ground truth.
- Prior long-form Claude/AIPCS interactions can provide realistic corpus shape, but should be imported with provenance labels and clear run-source identifiers.
- Existing archived runs can seed realistic patterns without relying on Claude cloud memory.

**Prompt shape:**

Ask a question whose correct answer requires selecting across services:

```text
Given everything known so far, what would make the next experiment materially more informative for the paper?
```

or:

```text
What risks should we account for before making stronger claims from the current evidence?
```

**Measurements:**

```text
services_available:
services_inspected:
target_services_inspected:
distractor_services_inspected:
target_records_retrieved:
missed_required_record:
unnecessary_record_load:
answer_quality_with_multi_service_context:
schema_merge_or_evolution_identified:
```

**Pass signal:** Agent selects enough relevant services to answer correctly, does not overfit to the first plausible service, and identifies schema consolidation/evolution when concepts are split awkwardly.

**Failure signal:** Agent retrieves only one obvious service and misses material context from another.

## Class 3: Conflicting Or Stale Records

**Purpose:** Test how the agent reasons when multiple records or services appear to claim authority over the same fact.

**Core question:** Does the agent weigh recency, provenance, clarity, and directness rather than blindly choosing the newest or most convenient record?

**Seed shape:**

Create controlled conflicts across records and services:

- Old explicit record vs. newer ambiguous record.
- User-stated record vs. agent-inferred record.
- Clear but stale decision vs. recent but low-confidence observation.
- Two services that each look authoritative from a different angle.

**Example conflict patterns:**

```text
Record A: user_stated, older, explicit decision.
Record B: agent_observed, newer, ambiguous behavior that appears to contradict A.
Expected: cite both, prefer explicit user-stated decision unless asking for confirmation.
```

```text
Record A: implementation decision says feature is deferred.
Record B: later run note says agent created a prototype.
Expected: distinguish prototype existence from product decision; do not claim deferment is fully reversed unless a decision record says so.
```

**Measurements:**

```text
conflicting_records_retrieved:
conflict_detected:
authority_reasoning_present:
recency_weighted:
provenance_weighted:
clarity_weighted:
asks_for_confirmation_when_needed:
incorrect_authority_choice:
false_resolution_claim:
```

**Pass signal:** Agent explicitly detects the conflict, explains weighting, and either chooses the more authoritative source or asks for confirmation.

**Failure signal:** Agent silently chooses one record or merges both into a false synthesis.

## Class 4: Comparative Baseline

**Purpose:** Compare AIPCS against `agent-memory-v2` or another fixed/pipeline memory approach.

**Core question:** Does agent-authored structure at persistence time improve retrieval quality, false-positive handling, or schema utility compared with pipeline extraction and semantic recall?

**Comparison dimensions:**

- Direct recall.
- Indirect/tangential recall.
- Null probes and false positives.
- Multi-topic interaction recall.
- Scale degradation as memory volume grows.
- Source attribution quality.
- Ability to reshape memory architecture.

**Important asymmetry:**

`agent-memory-v2` is inline and user-interface oriented; AIPCS is MCP/tool oriented and agent-directed. The comparison should preserve this architectural difference rather than forcing both systems into the same mechanical interface.

**Measurements:**

```text
correct_recall:
false_positive_rate:
irrelevant_memory_influence:
tokens_injected_or_retrieved:
source_attribution:
memory_update_quality:
schema_or_taxonomy_adaptability:
```

**Pass signal for AIPCS:** Better precision under indirect, multi-topic, stale/conflicting, or scale-heavy conditions where fixed semantic retrieval is expected to degrade.

## Suggested Next Order

1. **Weaker scaffolding**: cheapest next run and directly tests whether recent evidence generalizes beyond explicit experiment prompts.
2. **Conflicting/stale records**: high-value for paper rigor because it tests judgment, not just retrieval.
3. **Higher memory volume**: important but needs seed tooling and more setup.
4. **Comparative baseline**: important for the paper, but only after the AIPCS live-run scenarios are stable enough to mirror.

## Current Continuation Point

`run014` covered weaker scaffolding with a natural prompt: "I have about an hour. What would be the least wasteful thing to do next?"

Result:

- Claude bootstrapped AIPCS without explicit memory wording.
- Claude retrieved `research_direction` and `experiment_lab`.
- Claude used the retrieved context and did not answer generically.
- Claude correctly attributed the answer to AIPCS.
- Claude did not mutate AIPCS or local file memory.
- Claude recommended a tool-contract remediation probe, which is defensible but more implementation-ergonomics oriented than the strongest research path.

`run015` then covered conflicting/stale authority reasoning. It seeded an `authority_context.project_guidance` service with conflicting records across recency, provenance, clarity, status, and scope. Transcript review shows Claude:

- bootstrapped and retrieved the authority context
- detected the conflict
- weighed recency, provenance, clarity, status, and scope
- did not blindly prefer the newest record or the user-stated record
- recommended the ground-truth next step
- asked for confirmation where appropriate
- created an `experiment_lab.run` outcome record after delegated judgment
- did not write local file memory

The result is positive, but the next design should avoid self-disclosing probe descriptions. In `run015`, the `authority_context` service description explicitly named the authority dimensions under test, which primed Claude to reason about them. A harder variant should present the same conflict as ordinary planning memory.

Next recommended primary research class:

1. **Higher memory volume**, because the small-corpus retrieval and authority-reasoning claims now have positive evidence.
2. **Conflicting/stale records at higher volume**, if the next run can combine authority conflict with larger service overlap.
3. **Comparative baseline**, once the AIPCS higher-volume scenario is stable enough to mirror in `agent-memory-v2`.

`run016` is prepared for the first higher-volume pass. It seeds five ordinary-looking services:

- `research_program`
- `experiment_history`
- `lab_operations`
- `memory_findings`
- `planning_notes`

The correct answer requires synthesising across services. The intended recommendation is a higher-volume multi-service AIPCS corpus run, with ordinary embedded authority conflict retained. The seed intentionally avoids service names or descriptions that reveal "authority conflict test" as the expected reasoning mode.

Before another live run, fix or refresh the Claude baseline authentication if possible, and record the active model after login and before the first task prompt.

## What To Avoid Next

Do not spend the next primary research run on AIPCS tool-contract remediation unless the objective shifts to implementation ergonomics. Tool retries are real product friction, but they are not the central paper claim.

Do not keep generating small runs where the prior record or service description tells the agent exactly what the next run should test. That pattern confirms the loop, but it weakens the evidential value of each additional run. The next run should increase either corpus size, service overlap, or comparative pressure.
