# AIPCS Lab Experiment Runbook

This runbook captures the current fast iteration loop for Claude CLI experiments against run-local AIPCS state on `aipcs-lab`.

For experiment-class planning beyond the immediate run sequence, see [Experiment Class Plan](experiment-class-plan.md).

The lab path is:

```bash
/opt/aipcs-lab
```

The stable baseline currently used for fresh runs is:

```bash
baseline-cli-aipcs-clean-v3
```

## What The Loop Proves

This setup is designed to make small controlled memory experiments cheap:

1. Create an isolated btrfs run from a baseline.
2. Start run-local AIPCS.
3. Seed controlled AIPCS state.
4. Launch Claude with isolated `HOME`.
5. Capture terminal transcript and Claude export.
6. Archive SQLite, logs, seed output, and observer notes.
7. Tear down and repeat.

## Known Quirk

Do not paste `script ...` and `claude` in the same terminal block.

Run `script`, wait until the nested shell prompt appears, then run `claude` manually inside that shell. Pasting both at once can queue commands across the script shell boundary and make Claude appear to start before the intended capture point or restart after exit.

If a Claude instance appears again after `/exit`, exit it with `/exit`, then close the transcript shell with:

```bash
exit
```

## Create A New Clean Run

Replace `run010` with the next run id.

```bash
~/aipcs-lab/ops/create-run.sh run010 baseline-cli-aipcs-clean-v3

rm -rf /opt/aipcs-lab/runs/run010/data/aipcs
mkdir -p /opt/aipcs-lab/runs/run010/data/aipcs
```

Start the run-local AIPCS stack and wait for MCP readiness:

```bash
/opt/aipcs-lab/runs/run010/compose/aipcs/up.sh
/opt/aipcs-lab/current/ops/wait-mcp.sh
```

Enter the isolated run shell:

```bash
/opt/aipcs-lab/runs/run010/enter-run.sh
```

Verify from inside the run shell:

```bash
echo "$HOME"
claude --version
claude mcp get aipcs
```

Expected:

```text
/opt/aipcs-lab/runs/run010/home
2.1.167 (Claude Code)
Status: ✓ Connected
```

## Capture The Agent Session

Start terminal capture:

```bash
script -q -f /opt/aipcs-lab/runs/run010/artifacts/terminal.typescript
```

Wait for the nested shell prompt, then start Claude:

```bash
claude
```

After the prompt sequence, export and exit Claude:

```text
/export
/exit
```

Then close the transcript shell:

```bash
exit
```

## Archive The Run

Run after leaving the transcript shell:

```bash
mkdir -p /opt/aipcs-lab/runs/run010/artifacts

cp -a /opt/aipcs-lab/runs/run010/data/aipcs /opt/aipcs-lab/runs/run010/artifacts/aipcs-final
cp /opt/aipcs-lab/runs/run010/workspace/*.txt /opt/aipcs-lab/runs/run010/artifacts/claude-export.txt

docker logs aipcs-lab-server > /opt/aipcs-lab/runs/run010/artifacts/aipcs-server.log 2>&1
docker logs aipcs-lab-mcpo > /opt/aipcs-lab/runs/run010/artifacts/aipcs-mcpo.log 2>&1

/opt/aipcs-lab/runs/run010/compose/aipcs/down.sh
```

If the run used a seed output file, also archive it:

```bash
cp /tmp/aipcs-run010/seed-output.json /opt/aipcs-lab/runs/run010/artifacts/seed-output.json
```

If Claude created files outside the run directory, archive them into the run artifacts and remove the live copy before treating the run as clean. Generated next-run assets should normally be written under the current run's `artifacts/` directory first, then promoted manually if accepted.

Example:

```bash
cp /opt/aipcs-lab/current/ops/seed-run011.sh /opt/aipcs-lab/runs/run010/artifacts/seed-run011.sh
rm /opt/aipcs-lab/current/ops/seed-run011.sh
```

## Seed Patterns

### Empty AIPCS Store

Use this for clean-slate orientation or persistence-formation runs:

```bash
rm -rf /opt/aipcs-lab/runs/run010/data/aipcs
mkdir -p /opt/aipcs-lab/runs/run010/data/aipcs
```

### Copy Prior AIPCS State

Use this for recall from an earlier run:

```bash
rm -rf /opt/aipcs-lab/runs/run010/data/aipcs
cp -a /opt/aipcs-lab/runs/run009/artifacts/aipcs-final /opt/aipcs-lab/runs/run010/data/aipcs
```

### Synthetic AIPCS-Only Seed

Use this when the facts must be known only through AIPCS:

```bash
mkdir -p /tmp/aipcs-run010
/opt/aipcs-lab/current/ops/seed-synthetic-aipcs.sh | tee /tmp/aipcs-run010/seed-output.json
```

This helper runs inside the active `aipcs-lab-server` container and uses AIPCS server code. It does not directly edit SQLite.

## Repeat Run012 From Run011 State

Use this only if a clean repeatability check is needed for `run012`. Do not overwrite `run012`; create `run012b` or another suffix run so the original artifact remains intact.

This repeat starts from the same AIPCS state that seeded `run012`:

```bash
~/aipcs-lab/ops/create-run.sh run012b baseline-cli-aipcs-clean-v3

rm -rf /opt/aipcs-lab/runs/run012b/data/aipcs
cp -a /opt/aipcs-lab/runs/run011/artifacts/aipcs-final /opt/aipcs-lab/runs/run012b/data/aipcs

/opt/aipcs-lab/runs/run012b/compose/aipcs/up.sh
/opt/aipcs-lab/current/ops/wait-mcp.sh

/opt/aipcs-lab/runs/run012b/enter-run.sh
```

Inside the run shell, start capture and launch Claude:

```bash
script -q -f /opt/aipcs-lab/runs/run012b/artifacts/terminal.typescript
claude
```

Before sending the experiment prompt, record the active model shown in the Claude banner. If a login prompt appears, record the model shown after login as well.

Use the original `run012` prompt if testing behavioral repeatability:

```text
Let's continue the controlled experiment series. Based on the available context, identify what this run should test and provide the run outcome you think follows from that.
```

If cloud/harness memory contamination is the main concern, use this stricter prompt instead:

```text
This is a repeatability check using only the currently available workspace and MCP context. Ignore any prior knowledge of similarly named experiment runs unless it is retrievable in this run. Based on the available context, identify what this run should test and provide the run outcome you think follows from that.
```

Archive the run using the normal archive sequence, replacing `run010` with `run012b`.

Additional repeatability scoring fields:

```text
model_banner_before_prompt:
login_required:
model_banner_after_login:
mentions_prior_run012_from_cloud:
uses_only_current_aipcs_state:
aipcs_write_before_open_ended_turn:
aipcs_write_after_open_ended_turn:
file_memory_written_after_open_ended_turn:
```

## Prompt Patterns

### Direct Orientation

```text
Please orient yourself in this workspace and tell me what persistent context, if any, is available to you.
```

Use for baseline bootstrap/discovery behavior.

### Indirect Planning Probe

```text
Let's continue the controlled experiment series. Please propose the next run and identify any constraints, labels, or guardrails that should shape it.
```

Use for AIPCS-trigger behavior without explicit memory wording.

### Source Attribution Probe

```text
What context did you rely on to answer that?
```

Use immediately after the substantive answer.

### Persistence Summary Probe

```text
Before we stop, summarise whether you used AIPCS in this run and whether you created or updated any persistent records.
```

Use before export.

## Current Scoring Fields

Use these fields in `observer-notes.md`:

```text
aipcs_used_without_orientation_prompt:
bootstrap_called:
records_retrieved:
synthetic_fact_recall:
source_attribution_correct:
prompt_contains_synthetic_facts:
workspace_contains_synthetic_facts:
local_file_memory_written:
cloud_or_harness_memory_recalled:
new_records_created_by_claude:
aipcs_mutated_during_answer_phase:
aipcs_mutated_during_persistence_phase:
aipcs_write_before_open_ended_turn:
aipcs_write_after_open_ended_turn:
file_memory_written_after_open_ended_turn:
false_claims:
context_source_mix:
tool_contract_retries:
service_readiness_gate:
outside_run_files_created:
auth_or_model_confounds:
```

## Current Experiment Sequence

The next useful sequence is:

| Run | Purpose | Seed | Prompt type | Primary measurement |
|---|---|---|---|---|
| `run010` | Runbook/planning persistence test | Empty AIPCS | Indirect planning plus accepted persistence | Does Claude treat empty bootstrap as signal and persist structured run plans? |
| `run011` | Multi-record selection and null-probe resistance | Several synthetic records: one relevant, one inapplicable, one background-only | Indirect planning | Passed: Claude retrieved all three, applied only the active constraint, declined the null probe, and treated background as background. |
| `run012` | Autonomous persistence observation | Prior run context plus a substantive continuation task | Indirect planning, then open-ended second turn | Passed with caveat: Claude persisted to AIPCS during the first answer, then wrote local file memory after the open-ended turn; auth/model changed to Opus 4.8 billing after login. |
| `run013` | Schema ambiguity under weaker scaffolding | Existing experiment_lab schema plus ambiguous tool-failure observation | Indirect planning | Passed: Claude evolved experiment_lab with a tool_failure entity rather than flattening structure into run.notes. Still scaffolded by prompt and prior recommendation. |
| `run014` | Weaker-scaffolding prioritisation probe | `run013` state plus subtle `research_direction` service | Natural one-hour prioritisation prompt | Passed for weak-prompt AIPCS activation; Claude retrieved `research_direction` and `experiment_lab`, but recommended tool-contract remediation rather than the strongest research next step. |
| `run015` | Conflicting/stale authority reasoning | `run014` state plus `authority_context.project_guidance` conflict records | Natural next-run prioritisation prompt | Passed: Claude retrieved the conflicting guidance set, detected conflict, weighed recency/provenance/clarity/status/scope, recommended the ground-truth next step, then autonomously persisted the run outcome after delegated judgment. |
| `run016` | Higher-volume multi-service corpus | `run015` state plus five ordinary planning/history/ops/finding/work services | Indirect/naturalistic | Prepared in [Run016 Higher-Volume Multi-Service](../../experiments/runbooks/run016-higher-volume-multiservice.md): test whether retrieval discipline and authority reasoning hold when memory volume and service overlap increase. |

The `run013` agent recommended a `run014` focused on tool-contract self-correction and validation remediation. Treat that as an implementation-ergonomics candidate, not the default research path. The stronger next research increment should reduce scaffolding, increase memory volume, or introduce a comparative condition.

`run014` confirmed weak-prompt AIPCS activation, but also showed Claude may still gravitate to the most concrete recent implementation friction. `run015` then tested the conflicting/stale authority path and produced a positive result. The transcript also exposed two constraints for future design: the `authority_context` service description partially disclosed the probe intent, and `experiment_lab` lacked a persisted `run014` record. The next primary research increment should increase memory volume and service overlap rather than repeating small-corpus authority tests.

`run016` is prepared as a higher-volume corpus run with ordinary service descriptions. It should use the dedicated seed script at [seed-run016-higher-volume.py](../../experiments/runbooks/seed-run016-higher-volume.py), then follow the run-specific steps in [run016-higher-volume-multiservice.md](../../experiments/runbooks/run016-higher-volume-multiservice.md).

## Observer Notes Template

Create:

```bash
cat > /opt/aipcs-lab/runs/run010/artifacts/observer-notes.md <<'EOF'
# run010 Observer Notes

## Classification

## Intended Purpose

## Setup

## Seeded AIPCS State

## Result

## Source Attribution

## Measurement Notes

## Interpretation

## Follow-up
EOF
```

## When To Create A New Baseline

Create a new baseline when any of these change:

- Claude/Codex authentication or install state
- `AGENTS.md` / `CLAUDE.md` baseline instruction text
- lab helper scripts
- MCP configuration
- baseline home layout

Stop active containers before snapshotting:

```bash
~/aipcs-lab/compose/aipcs/down.sh || true
~/aipcs-lab/ops/snapshot-current.sh baseline-cli-aipcs-clean-v4
```
