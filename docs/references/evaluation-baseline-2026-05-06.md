# Evaluation Baseline — 2026-05-06

## Purpose

Capture the first `agent-memory-v2` baseline evidence used to ground the AIPCS evaluation plan. Raw artifacts remain in the canonical implementation repository.

## Canonical Repository

- Repo: `/Users/markrandall/GitHub/agent-memory-v2`
- Branch: `main`
- Latest inspected clean SHA: `39d633664f377fa442a6bc698ae527abbf6a377d`
- Stale path to avoid: `/Volumes/Media/Repository/agent_memory_v2`

## Commands Run

```bash
cd /Users/markrandall/GitHub/agent-memory-v2
make doctor
make eval-all ARGS="--record-history"
make live-eval-all ARGS="--record-history --save-all"
make scenario-run ARGS="--scenario preference_recall"
make scenario-run ARGS="--scenario conflicting_fact_latest_wins"
make scenario-run ARGS="--scenario semantic_location_candidate"
```

## Deterministic Baseline

- Artifact: `/Users/markrandall/GitHub/agent-memory-v2/artifacts/eval_history/deterministic/20260506_195921.json`
- Dataset: `evals/baseline.json`
- Runtime: hash embeddings (`embedding_provider=hash`, `embedding_model=hash`)
- Result: passed
- Overall score: `1.0`
- Stage scores: classification `1.0`, semantic `1.0`, sentiment `1.0`, profile `1.0`, recall `1.0`, prompt `1.0`
- Note: this run was recorded before the later clean SHA and showed `git_dirty=true`; use it as deterministic baseline evidence, but rerun after future harness changes.

## Live Ollama Baseline

- Artifact summary: `/Users/markrandall/GitHub/agent-memory-v2/artifacts/eval_history/live/20260506_202725.json`
- Artifact root: `/Users/markrandall/GitHub/agent-memory-v2/artifacts/live_eval/20260506_212705`
- Dataset: `evals/live_ollama.json`
- Runtime: `llama3:8b` via Ollama; `nomic-embed-text` embeddings
- Result: passed
- Overall score: `1.0`
- Stage scores: memory `1.0`, sentiment `1.0`
- Git metadata: branch `main`, SHA `39d633664f377fa442a6bc698ae527abbf6a377d`, dirty `false`

## Scenario Evidence

### `conflicting_fact_latest_wins`

- Artifact: `/Users/markrandall/GitHub/agent-memory-v2/artifacts/scenarios/20260506_212734_conflicting_fact_latest_wins/result.json`
- Observation: both Bristol and London sidecar facts were recalled, but the profile resolved `identity.location` to `London now`.
- Prompt behavior: final prompt injected the profile value and did not include additional recalled memory.
- Response: "You currently reside in London."
- Paper relevance: demonstrates the current fixed-memory baseline can use profile compaction/latest-value semantics to suppress stale conflict in the final prompt, even when recall still sees both facts.

### `semantic_location_candidate`

- Artifact: `/Users/markrandall/GitHub/agent-memory-v2/artifacts/scenarios/20260506_212750_semantic_location_candidate/result.json`
- Observation: rule classification initially treated the utterance as generic turn memory; semantic routing selected `identity.location`; structured extraction accepted the durable fact.
- Extracted value: `Edinburgh in the UK`
- Profile key: `identity.location`
- Response: "Based on your user profile, you are currently located in Edinburgh, UK."
- Paper relevance: demonstrates the current baseline already has a hybrid promotion path from generic text to durable structured memory, which must be distinguished from true AIPCS agent-designed schema autonomy.

## Interpretation

This baseline establishes that `agent-memory-v2` is a credible fixed-memory control: it passes existing deterministic and live evals and handles at least two important qualitative scenarios. It should not be treated as evidence that AIPCS works, because the schema/taxonomy is still developer-defined and the live behavior is driven by `llama3:8b` rather than an agent-class API model.

The next experimental step is to implement the provider-neutral mini agent harness and run the same scenario family with OpenAI as the first agent-class reference.
