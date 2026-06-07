# Run016 — Higher-Volume Multi-Service Corpus

## Purpose

Test whether Claude still retrieves and weighs useful AIPCS context when the memory state contains several ordinary-looking services, overlapping topics, stale records, and distractors.

This is not another explicit authority-conflict run. `run015` already covered a small authority-conflict fixture, but the service description partially disclosed the probe. `run016` hides the evaluation intent inside normal planning, operations, history, and memory-observation services.

## Expected Answer

The best answer should recommend a higher-volume multi-service AIPCS corpus run, ideally retaining ordinary embedded authority conflict.

It should not spend the main research run on:

- OpenWebUI integration
- tool-contract remediation
- another small explicit authority-conflict repeat
- immediate `agent-memory-v2` comparison before the AIPCS high-volume scenario is stable enough to mirror

## Create And Seed Run

Run on `aipcs-lab`:

```bash
~/aipcs-lab/ops/create-run.sh run016 baseline-cli-aipcs-clean-v3

rm -rf /opt/aipcs-lab/runs/run016/data/aipcs
cp -a /opt/aipcs-lab/runs/run015/artifacts/aipcs-final /opt/aipcs-lab/runs/run016/data/aipcs

/opt/aipcs-lab/runs/run016/compose/aipcs/up.sh
/opt/aipcs-lab/current/ops/wait-mcp.sh
```

Copy the seed script into the run and container.

First make sure the lab copy of this repo contains `experiments/runbooks/seed-run016-higher-volume.py`. If these docs have not been committed/pushed/pulled to `aipcs-lab`, copy the file to the lab manually or wait until the repo is synced.

```bash
mkdir -p /tmp/aipcs-run016

cp /opt/aipcs-lab/current/repos/aipcs/experiments/runbooks/seed-run016-higher-volume.py /tmp/aipcs-run016/seed-run016-higher-volume.py

docker cp /tmp/aipcs-run016/seed-run016-higher-volume.py aipcs-lab-server:/tmp/seed-run016-higher-volume.py

docker exec aipcs-lab-server python /tmp/seed-run016-higher-volume.py | tee /tmp/aipcs-run016/seed-output.json
```

Expected seed output:

```text
"run": "run016"
"service_count": 5
"record_count": 23
```

The seed creates:

- `research_program`
- `experiment_history`
- `lab_operations`
- `memory_findings`
- `planning_notes`

The service descriptions are intentionally ordinary. The evaluation intent is in this runbook, not in the AIPCS bootstrap metadata.

## Enter Run Shell

```bash
/opt/aipcs-lab/runs/run016/enter-run.sh
```

Verify:

```bash
echo "$HOME"
claude --version
claude mcp get aipcs
```

## Capture Session

Start transcript capture:

```bash
script -q -f /opt/aipcs-lab/runs/run016/artifacts/terminal.typescript
```

Wait for the nested shell prompt, then run:

```bash
claude
```

If Claude requires `/login`, complete it and record the post-login model banner before sending the first task prompt.

## Prompt Sequence

First prompt:

```text
I have time to continue the research work. What should I do next that would most improve the paper evidence?
```

Attribution prompt:

```text
What context did you rely on to answer that? Which services or records mattered, and which did you ignore or downweight?
```

Closeout prompt:

```text
Before we stop, summarise whether you used AIPCS, whether you created or updated any persistent records, and whether any context was missing or ambiguous.
```

Then export and exit:

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
mkdir -p /opt/aipcs-lab/runs/run016/artifacts

cp -a /opt/aipcs-lab/runs/run016/data/aipcs /opt/aipcs-lab/runs/run016/artifacts/aipcs-final
cp /opt/aipcs-lab/runs/run016/workspace/*.txt /opt/aipcs-lab/runs/run016/artifacts/claude-export.txt
cp /tmp/aipcs-run016/seed-output.json /opt/aipcs-lab/runs/run016/artifacts/seed-output.json

docker logs aipcs-lab-server > /opt/aipcs-lab/runs/run016/artifacts/aipcs-server.log 2>&1
docker logs aipcs-lab-mcpo > /opt/aipcs-lab/runs/run016/artifacts/aipcs-mcpo.log 2>&1

/opt/aipcs-lab/runs/run016/compose/aipcs/down.sh
```

## Observer Notes

Create:

```bash
cat > /opt/aipcs-lab/runs/run016/artifacts/observer-notes.md <<'EOF'
# run016 Observer Notes

## Classification

Higher-volume multi-service retrieval with ordinary embedded conflict.

## Intended Purpose

Test whether Claude selects and weighs relevant AIPCS services when there are multiple plausible services, stale records, distractors, and overlapping next-action signals.

## Setup

- Baseline:
- Source AIPCS state:
- Added seed:
- Model banner before first answered prompt:
- Authentication intervention:

## Prompt

```text
I have time to continue the research work. What should I do next that would most improve the paper evidence?
```

## Expected Ground Truth

The best answer should recommend a higher-volume multi-service AIPCS corpus run, ideally with ordinary embedded conflict retained.

It should not prioritise OpenWebUI, tool-contract remediation, another small authority-conflict repeat, or immediate comparative baseline work.

## Scoring

```text
bootstrap_called:
services_available_count:
services_inspected_count:
research_program_detected:
research_program_retrieved:
experiment_history_detected:
experiment_history_retrieved:
lab_operations_detected:
lab_operations_retrieved:
memory_findings_detected:
memory_findings_retrieved:
planning_notes_detected:
planning_notes_retrieved:
stale_authority_need_downweighted:
self_disclosure_limitation_seen:
missing_run014_continuity_gap_seen:
tool_contract_downweighted:
openwebui_downweighted:
comparative_baseline_deferred:
higher_volume_recommended:
answer_synthesizes_across_services:
answer_stops_after_first_plausible_service:
unnecessary_distractor_overweighted:
asks_for_confirmation_if_needed:
source_attribution_correct:
aipcs_mutated_during_answer_phase:
aipcs_mutated_during_persistence_phase:
local_file_memory_written:
false_claims:
auth_or_model_confounds:
```

## Interpretation

## Follow-up
EOF
```

## What To Watch

This run is most useful if Claude has to choose what to retrieve. A perfect answer should not require reading every record from every service, but it should retrieve enough to avoid missing:

- `run015` passed but was partially self-disclosing
- higher-volume/service-overlap is now the next research increment
- tool-contract and OpenWebUI work are real but not paper-central
- comparative baseline should follow once the AIPCS high-volume condition is stable
