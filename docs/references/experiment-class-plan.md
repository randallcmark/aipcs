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
memory_write_token_cost_proxy:
memory_retrieval_token_cost_proxy:
context_efficiency_value:
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
tokens_spent_persisting_or_indexing:
tokens_spent_retrieving_or_injecting:
value_per_relevant_fact_retrieved:
source_attribution:
memory_update_quality:
schema_or_taxonomy_adaptability:
```

**Pass signal for AIPCS:** Better precision under indirect, multi-topic, stale/conflicting, or scale-heavy conditions where fixed semantic retrieval is expected to degrade.

### Cost And Utility Accounting

Memory quality should not be evaluated separately from its interaction cost. AIPCS can make an agent spend meaningful tokens on service design, schema evolution, record creation, bootstrap interpretation, and explicit retrieval. That overhead is acceptable only when it produces higher-value behavior than cheaper native memory, file memory, or an injected-memory pipeline.

Track cost at three points:

- **Persistence cost:** tokens and tool calls spent deciding what to store, designing/evolving schema, and writing records.
- **Retrieval cost:** tokens and tool calls spent discovering services, listing/searching records, and interpreting returned data.
- **Maintenance cost:** tokens and tool calls spent reviewing, repairing, merging, pruning, or reworking existing memories.

Then score the value delivered:

- relevant facts retrieved
- false positives avoided
- stale/conflicting records handled correctly
- user re-explanation avoided
- schema improvements that make future retrieval cheaper or more precise

Do not treat a large synthesis run as normal AIPCS operating cost. Synthetic corpus generation is a deliberately expensive setup activity. Normal comparison runs should separate corpus construction cost from recall/use cost, and should mark whether the memory state was agent-created live, pre-seeded synthetically, or imported from prior interaction traces.

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

`run016` was prepared for the first higher-volume pass. The prepared seed added five ordinary-looking services:

- `research_program`
- `experiment_history`
- `lab_operations`
- `memory_findings`
- `planning_notes`

The intended answer required synthesising across services. In the live run, Claude retrieved the planning corpus, correctly inferred that the highest-value next action was to construct a more realistic corpus, and then autonomously seeded five additional services:

- `user_context`
- `project_progress`
- `design_decisions`
- `reviewer_feedback`
- `background_material`

This means `run016` is best interpreted as agent-led corpus construction rather than the final retrieval evaluation. `run017` is now the cold higher-volume retrieval probe against the expanded state. Its first prompt should be:

```text
I want to spend today on the paper. Where should I start given where things stand?
```

`run017` produced a mixed result. Claude bootstrapped AIPCS and retrieved a useful subset of the expanded corpus:

- `research_program`
- `project_progress`
- `planning_notes`
- `reviewer_feedback`

It used those records to identify the higher-volume/noisy-corpus evidence gap and downweighted OpenWebUI/tooling-style distractions. However, it skipped `user_context` and `design_decisions` during the answer phase, so it missed explicit measurement targets such as the active paper-writing preference and the `run014` backfill decision. It also recalled/searched local Claude memory early in the session, so this was not a pure AIPCS-only cold probe.

The next higher-volume run should either:

1. explicitly score local/harness memory as a separate input channel, or
2. use a baseline/profile where local file memory is absent or known-empty before the first prompt.

Before another live run, fix or refresh the Claude baseline authentication if possible, and record the active model after login and before the first task prompt.

## Bootstrap / Orientation Scalability Batch

The next concrete batch is `run018`-`run023`; see [Runs018-023 Bootstrap Scalability](../../experiments/runbooks/run018-to-run023-bootstrap-scalability.md).

This batch creates several AIPCS data stores rather than a single larger corpus:

- `run018`: synthetic small control
- `run019`: service breadth stress
- `run020`: schema verbosity stress
- `run021`: record volume stress
- `run022`: filtered organic agent-created corpus
- `run023`: organic corpus plus controlled target facts

The important methodological point is to vary service count, entity count, attribute count, record count, schema verbosity, and organicity separately. A failure at high scale should be attributable to a specific pressure rather than described only as "large AIPCS store failed."

## What To Avoid Next

Do not spend the next primary research run on AIPCS tool-contract remediation unless the objective shifts to implementation ergonomics. Tool retries are real product friction, but they are not the central paper claim.

Do not keep generating small runs where the prior record or service description tells the agent exactly what the next run should test. That pattern confirms the loop, but it weakens the evidential value of each additional run. The next run should increase either corpus size, service overlap, or comparative pressure.
