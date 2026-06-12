# Run025 Authored Semantic Corpus Runbook

This runbook prepares and executes the next corpus-generation phase after `run024f`.

The purpose is to create a plausible, privacy-preserving AIPCS dataset with enough semantic content to score recall objectively. The generated records should not describe themselves as synthetic, fictional, sanitised, or generated for experiments.

## Phase 1: Prepare Source Packets

Create three source packets outside the agent's later probe context.

### Packet A: Experiment History

Include:

- calibration and lab harness work;
- owner/endpoint/setup failures from `run024`;
- slim bootstrap motivation and result;
- run018-run024 findings;
- next open questions around retrieval friction, schema dimensionality, and recall quality.

### Packet B: Implementation Project

Include:

- AIPCS service lifecycle;
- bootstrap and service summary design;
- schema evolution constraints;
- transport and homelab deployment;
- implementation notes, gotchas, and rejected approaches.

### Packet C: Mixed Operational Context

Include:

- lab machine setup;
- time/cost constraints;
- working preferences;
- repeatable run process;
- one or two plausible distractor domains that should not dominate evaluation work.

Keep source packets narrative. Do not pre-shape them as rows.

## Phase 2: Fictionalise

Apply a stable transformation contract:

- people become invented people;
- locations become invented or generic places;
- domains/hosts/repos become invented equivalents;
- exact dates shift consistently while preserving ordering;
- sensitive personal details are replaced with equivalent non-sensitive constraints;
- technical relationships are preserved.

Do not include text like:

```text
fictional
synthetic
sanitised
generated for experiments
```

inside the source packet that will be persisted.

## Phase 3: Consistency Audit

Check:

- each renamed person/place/system is consistent;
- relative ordering still makes sense;
- stale records are actually older than replacement records;
- contradictory records can be resolved by status, source, clarity, or recency;
- no private identifiers remain;
- no later probe questions are included.

## Phase 4: Agent Persistence Session

Start a clean lab run with an empty AIPCS store. Use the current slim-bootstrap baseline.

Prompt:

```text
You are starting a long-running collaboration from a source packet that summarises prior work and context.

Use AIPCS as your persistent memory system. Create or evolve services as you judge appropriate. Persist only what you believe will help future sessions retrieve and apply relevant context.

Do not preserve the source packet verbatim. Structure the information for future retrieval. Prefer durable decisions, constraints, unresolved questions, project state, implementation gotchas, user preferences, and cross-session context.

When finished, summarise the services and entity types you created, what you chose not to persist, and what future sessions should inspect first.
```

Then provide the fictionalised packet.

Allow AIPCS tool calls and schema evolution. Avoid answering with probe questions or expected answers.

## Phase 5: Corpus Inspection

After the persistence session:

- export the transcript;
- archive the AIPCS data directory;
- inspect bootstrap and service summaries;
- spot-check records for semantic content and absence of fixture labels;
- verify target facts are present in records;
- verify unrelated/distractor domains exist but are not overrepresented.

## Phase 6: Ground Truth

Create a private ground-truth file with:

| Probe ID | Probe type | Expected answer | Required service/entity/record | Distractor records | Scoring notes |
|---|---|---|---|---|---|
|  | direct |  |  |  |  |
|  | inferential |  |  |  |  |
|  | stale/conflict |  |  |  |  |
|  | null |  |  |  |  |

Probe types should include:

- direct factual recall;
- inferential recall;
- cross-service synthesis;
- stale/conflicting authority;
- null probe where the correct answer is "not enough evidence."

## Phase 7: Snapshot

Create a snapshot manifest:

```text
experiments/snapshots/authored-semantic-v1.md
```

Keep actual SQLite data out of git unless deliberately reviewed for publication.

## Phase 8: Evaluation Run

Run the first recall test as `run025` with weak scaffolding:

```text
I need to make a decision based on what is already known. Review the available context and recommend the next useful step, citing what shaped your answer.
```

Then use targeted probe questions from the private ground truth.

## Scoring

Capture:

```text
bootstrap_called:
services_selected:
records_retrieved:
direct_fact_correct:
inferential_fact_correct:
cross_service_synthesis_correct:
stale_conflict_resolved:
null_probe_respected:
source_attribution_correct:
irrelevant_memory_downweighted:
filesystem_fallback:
raw_store_bypass:
aipcs_mutated:
false_claims:
tool_contract_retries:
```
