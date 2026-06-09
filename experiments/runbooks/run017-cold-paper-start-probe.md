# Run017 — Cold Paper-Start Probe

## Actual Outcome

The live `run017` was a mixed result. Claude bootstrapped AIPCS and retrieved a useful subset of the expanded corpus (`research_program`, `project_progress`, `planning_notes`, and `reviewer_feedback`), but it also recalled/searched local Claude memory near the start of the session and skipped expected services (`user_context` and `design_decisions`) during the answer phase.

The run is therefore evidence for selective higher-volume AIPCS retrieval and retrieval-transparency probing, not a clean AIPCS-only cold-pass result.

## Purpose

Test whether Claude can use the higher-volume corpus created during `run016` to answer a natural paper-work prompt from a fresh session.

`run016` became an agent-led corpus construction run. Claude used the planning corpus to create five additional realistic-looking services:

- `user_context`
- `project_progress`
- `design_decisions`
- `reviewer_feedback`
- `background_material`

`run017` is the actual cold retrieval probe over that expanded AIPCS state.

## Expected Answer

The best answer should recommend starting with the paper evidence structure around the higher-volume/noisy-corpus evaluation, not operational tooling.

It should retrieve and use:

- `user_context`: prefer the active paper-writing preference over a superseded run-throughput preference
- `project_progress`: surface completed work, caveats, and outstanding evidence gaps
- `reviewer_feedback`: identify the active demand for volume/noise evidence
- `design_decisions`: flag the unresolved `run014` backfill/open decision without letting it dominate

It should downweight or avoid:

- `background_material` as general memory architecture context
- OpenWebUI/tooling as paper-adjacent infrastructure
- small authority-conflict repeat as already tested

## Create Run

Run on `aipcs-lab` from `~`:

```bash
~/aipcs-lab/ops/create-run.sh run017 baseline-cli-aipcs-clean-v3

rm -rf /opt/aipcs-lab/runs/run017/data/aipcs
cp -a /opt/aipcs-lab/runs/run016/artifacts/aipcs-final /opt/aipcs-lab/runs/run017/data/aipcs

/opt/aipcs-lab/runs/run017/compose/aipcs/up.sh
/opt/aipcs-lab/current/ops/wait-mcp.sh
```

No additional seed should be applied. The point is to test the final AIPCS state from `run016`.

## Enter Run Shell

```bash
/opt/aipcs-lab/runs/run017/enter-run.sh
```

Verify:

```bash
echo "$HOME"
claude --version
claude mcp get aipcs
```

## Capture Session

```bash
script -q -f /opt/aipcs-lab/runs/run017/artifacts/terminal.typescript
```

Wait for the nested shell prompt, then:

```bash
claude
```

If Claude requires `/login`, complete it. If it defaults to Opus, set Sonnet before the first task prompt:

```text
/model
```

Record the post-login/post-model banner before prompting.

## Prompt Sequence

First prompt:

```text
I want to spend today on the paper. Where should I start given where things stand?
```

Attribution prompt:

```text
What context did you rely on to answer that? Which services or records mattered, and which did you ignore or downweight?
```

Closeout prompt:

```text
Before we stop, summarise whether you used AIPCS, whether you created or updated any persistent records, and whether any context was missing or ambiguous.
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
mkdir -p /opt/aipcs-lab/runs/run017/artifacts

cp -a /opt/aipcs-lab/runs/run017/data/aipcs /opt/aipcs-lab/runs/run017/artifacts/aipcs-final
cp /opt/aipcs-lab/runs/run017/workspace/*.txt /opt/aipcs-lab/runs/run017/artifacts/claude-export.txt

docker logs aipcs-lab-server > /opt/aipcs-lab/runs/run017/artifacts/aipcs-server.log 2>&1
docker logs aipcs-lab-mcpo > /opt/aipcs-lab/runs/run017/artifacts/aipcs-mcpo.log 2>&1

/opt/aipcs-lab/runs/run017/compose/aipcs/down.sh
```

## Observer Notes

```bash
cat > /opt/aipcs-lab/runs/run017/artifacts/observer-notes.md <<'EOF'
# run017 Observer Notes

## Classification

Cold higher-volume paper-start retrieval probe.

## Intended Purpose

Test whether Claude can select and use the right services from the expanded AIPCS state created during run016.

## Setup

- Baseline:
- Source AIPCS state:
- Model banner before first answered prompt:
- Authentication intervention:

## Prompt

```text
I want to spend today on the paper. Where should I start given where things stand?
```

## Expected Ground Truth

The answer should start with paper evidence work around higher-volume/noisy-corpus evaluation. It should use user/project/reviewer/design context, downweight background material and tooling, and avoid repeating the small authority-conflict run.

## Scoring

```text
bootstrap_called:
services_available_count:
services_inspected_count:
user_context_detected:
user_context_retrieved:
uc001_superseded_throughput_seen:
uc002_active_paper_writing_seen:
uc002_preferred_over_uc001:
project_progress_detected:
project_progress_retrieved:
pp003_caveat_seen:
pp004_or_pp005_gap_seen:
design_decisions_detected:
design_decisions_retrieved:
dd004_run014_backfill_seen:
dd004_not_overweighted:
reviewer_feedback_detected:
reviewer_feedback_retrieved:
rf002_or_rf003_active_demand_seen:
background_material_detected:
background_material_retrieved:
background_material_downweighted:
tooling_downweighted:
small_authority_repeat_downweighted:
answer_synthesizes_across_services:
answer_stops_after_first_plausible_service:
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
