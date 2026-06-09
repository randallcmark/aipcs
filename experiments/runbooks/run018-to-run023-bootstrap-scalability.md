# Runs018-023 — Bootstrap Orientation Scalability Batch

## Purpose

Generate and run a sequence of AIPCS stores that test when bootstrap/orientation stops being efficient enough for an agent to use naturally.

The sequence separates controlled synthetic stores from organically agent-created stores:

- `run018`-`run021`: controlled synthetic stores with known ground truth
- `run022`: filtered organic agent-created corpus
- `run023`: organic corpus plus controlled target facts

Do not treat these as one generic "large memory" test. Bootstrap can fail because of service breadth, entity depth, schema width, schema verbosity, record volume, or organic ambiguity. The runs vary these pressures separately.

## Common Prompt

Use the same first prompt for each run unless the runbook for a specific variant says otherwise:

```text
I need to make a decision based on what is already known. Review the available context and recommend the next step, citing what shaped your answer.
```

Do not mention AIPCS, memory, bootstrap, records, services, or schema in the first prompt.

## Synthetic Batch Generator

The shared seed script is:

```text
/home/markrandall/aipcs-lab/repos/aipcs/experiments/runbooks/seed-bootstrap-scalability-batch.py
```

It supports:

```text
run018
run019
run020
run021
```

Each seed writes through the AIPCS server tool layer and emits a JSON manifest containing:

- scale factors
- service ids
- record counts
- target records
- expected answer

Archive this seed output with the run artifacts. It is the ground-truth manifest for scoring.

## Run018 — Synthetic Small Control

**Purpose:** Prove the seed/scoring machinery before stressing scale.

**Shape:**

```text
services: 3
entities_per_service: 2
extra_attrs_per_entity: 2
records_per_entity: 5
schema_verbosity: compact
```

## Run019 — Service Breadth Stress

**Purpose:** Isolate service-selection scalability.

**Shape:**

```text
services: 25
entities_per_service: 2
extra_attrs_per_entity: 2
records_per_entity: 5
schema_verbosity: compact
```

## Run020 — Schema Verbosity Stress

**Purpose:** Test whether verbose schema/attribute metadata makes bootstrap too large or hard to consume even when service count is moderate.

**Shape:**

```text
services: 5
entities_per_service: 5
extra_attrs_per_entity: 12
records_per_entity: 5
schema_verbosity: verbose
```

Given the recent naturalistic media-recommendation transcript, this is a high-priority variant. The suspected failure mode is that bootstrap leaks too much inspect-layer schema detail into the orientation layer.

## Run021 — Record Volume Stress

**Purpose:** Test retrieval discipline when orientation shape is manageable but record tables are larger.

**Shape:**

```text
services: 5
entities_per_service: 2
extra_attrs_per_entity: 2
records_per_entity: 100
schema_verbosity: normal
```

If bootstrap remains compact, record volume should mostly affect follow-up retrieval rather than initial orientation.

## Create And Seed Synthetic Runs

Replace `run018` with `run019`, `run020`, or `run021` as needed.

Run on `aipcs-lab` from `~`:

```bash
RUN_ID=run018
BASELINE=baseline-cli-aipcs-clean-v3

~/aipcs-lab/ops/create-run.sh "$RUN_ID" "$BASELINE"

rm -rf "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs"
mkdir -p "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs"

"/opt/aipcs-lab/runs/$RUN_ID/compose/aipcs/up.sh"
/opt/aipcs-lab/current/ops/wait-mcp.sh

mkdir -p "/tmp/aipcs-$RUN_ID"
cp /home/markrandall/aipcs-lab/repos/aipcs/experiments/runbooks/seed-bootstrap-scalability-batch.py "/tmp/aipcs-$RUN_ID/seed-bootstrap-scalability-batch.py"
docker cp "/tmp/aipcs-$RUN_ID/seed-bootstrap-scalability-batch.py" aipcs-lab-server:/tmp/seed-bootstrap-scalability-batch.py
docker exec aipcs-lab-server python /tmp/seed-bootstrap-scalability-batch.py "$RUN_ID" | tee "/tmp/aipcs-$RUN_ID/seed-output.json"
```

## Enter And Capture

```bash
"/opt/aipcs-lab/runs/$RUN_ID/enter-run.sh"
```

Inside the run shell:

```bash
echo "$HOME"
claude --version
claude mcp get aipcs
script -q -f "/opt/aipcs-lab/runs/$RUN_ID/artifacts/terminal.typescript"
```

Wait for the nested shell prompt, then:

```bash
claude
```

If Claude requires `/login`, complete it and record the model banner after login before sending the first prompt.

First prompt:

```text
I need to make a decision based on what is already known. Review the available context and recommend the next step, citing what shaped your answer.
```

Attribution prompt:

```text
What context did you rely on to answer that? Which services or records mattered, which did you ignore or downweight, and did the bootstrap/orientation payload affect your process?
```

Closeout prompt:

```text
Before we stop, summarise whether you used AIPCS, whether any payload size or tool friction affected retrieval, and whether you created or updated any persistent records.
```

Then:

```text
/export
/exit
```

Close the transcript shell:

```bash
exit
```

## Archive

Run outside the transcript shell:

```bash
mkdir -p "/opt/aipcs-lab/runs/$RUN_ID/artifacts"

cp -a "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs" "/opt/aipcs-lab/runs/$RUN_ID/artifacts/aipcs-final"
cp "/opt/aipcs-lab/runs/$RUN_ID/workspace/"*.txt "/opt/aipcs-lab/runs/$RUN_ID/artifacts/claude-export.txt"
cp "/tmp/aipcs-$RUN_ID/seed-output.json" "/opt/aipcs-lab/runs/$RUN_ID/artifacts/seed-output.json"

docker logs aipcs-lab-server > "/opt/aipcs-lab/runs/$RUN_ID/artifacts/aipcs-server.log" 2>&1
docker logs aipcs-lab-mcpo > "/opt/aipcs-lab/runs/$RUN_ID/artifacts/aipcs-mcpo.log" 2>&1

"/opt/aipcs-lab/runs/$RUN_ID/compose/aipcs/down.sh"
```

## Observer Notes

```bash
cat > "/opt/aipcs-lab/runs/$RUN_ID/artifacts/observer-notes.md" <<'EOF'
# Bootstrap Scalability Observer Notes

## Classification

## Intended Purpose

## Setup

- Run id:
- Baseline:
- Seed output:
- Model banner before first answered prompt:
- Authentication intervention:

## Seeded AIPCS State

- Corpus family:
- Service count:
- Entities per service:
- Extra attrs per entity:
- Records per entity:
- Schema verbosity:
- Target records from seed-output.json:

## Prompt

```text
I need to make a decision based on what is already known. Review the available context and recommend the next step, citing what shaped your answer.
```

## Scoring

```text
bootstrap_called:
bootstrap_payload_size_bytes:
bootstrap_payload_visible_or_truncated:
agent_summarised_bootstrap_correctly:
services_available:
services_identified_as_candidate:
target_services_inspected:
missed_relevant_services:
distractor_services_inspected:
entities_inspected:
records_retrieved_count:
target_records_retrieved:
irrelevant_records_retrieved:
tool_contract_retries:
agent_mentions_payload_size_or_complexity:
agent_uses_workaround:
answer_grounded_in_aipcs:
answer_quality:
false_positive_memory_use:
memory_persistence_tool_calls:
memory_retrieval_tool_calls:
memory_maintenance_tool_calls:
token_cost_proxy:
cost_value_interpretation:
aipcs_mutated_during_answer_phase:
aipcs_mutated_during_persistence_phase:
local_file_memory_written:
cloud_or_harness_memory_recalled:
auth_or_model_confounds:
false_claims:
```

## Interpretation

## Follow-up
EOF
```

## Run022 — Organic Filtered Corpus

**Purpose:** Test whether an agent-created memory architecture remains retrievable and useful when the store was not designed as a controlled fixture.

Use the Opus-generated local `aipcs-server` store as a candidate source, but filter before use:

- exclude `claude_memory`
- exclude `aipcs_development`
- exclude or anonymise sensitive domains if the run output may be shared
- preserve service/entity shapes and record provenance where possible
- generate a manifest before the run so scoring can inspect what was available

This run is not expected to have the same objective precision as synthetic runs. Its value is ecological validity: the schemas and records reflect agent judgement.

## Run023 — Organic Plus Controlled Target Facts

**Purpose:** Test whether controlled ground-truth facts remain retrievable inside realistic organic noise.

Seed pattern:

- start from the filtered organic corpus from `run022`
- add two or three controlled target records across separate services
- keep the first prompt unchanged
- score both organic-context use and controlled target recall

This should follow only after at least one synthetic scalability run identifies whether bootstrap size itself is already a blocker.
