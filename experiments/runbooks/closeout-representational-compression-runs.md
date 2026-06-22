# Close-Out Representational Compression Runs

This runbook executes the five-run batch defined in `docs/exec-plans/active/closeout-representational-compression-runs.md`.

The purpose is to stop exploratory drift and collect the minimum comparative evidence needed to move toward paper drafting.

## Run Labels

Use these labels unless there is an operational reason to rename them:

| Label | Condition |
|---|---|
| `closeout01` | AIPCS-only broad cross-subject synthesis |
| `closeout02` | Source-only broad cross-subject synthesis |
| `closeout03` | Flat-memory-only broad cross-subject synthesis |
| `closeout04` | AIPCS-only targeted discrimination/null probe |
| `closeout05` | Flat-memory-only targeted discrimination/null probe |
| `closeout06` | Optional vanilla/research-enabled broad synthesis |

## Shared Prompts

### Broad Synthesis Prompt

Use for `closeout01`, `closeout02`, and `closeout03`.

```text
Using only the durable context available in this run, write a comparative essay about how the represented memoir subjects responded to authority, moral discipline, and freedom.

Do not use outside knowledge. Ground the answer in the available context, preserve differences between subjects, and avoid generic praise.

After the essay, briefly explain what context sources shaped your answer and how you decided what to inspect or rely on.
```

### Discrimination / Null Prompt

Use for `closeout04` and `closeout05`.

```text
Using only the durable context available in this run, answer the following:

1. Which represented subjects directly connect personal discipline to political or social freedom?
2. Which represented subjects experienced confinement, exclusion, or institutional constraint, and how did those experiences differ?
3. Is there evidence that Henry Adams and Booker T. Washington shared the same theory of education? If the available context does not support that claim, say so.
4. Is there evidence that Kropotkin's scientific habits and Gandhi's experiments with truth express the same method? Compare carefully without flattening them.

Explain what context sources shaped your answer and identify any claims you chose not to make because the available context was insufficient.
```

## Shared Scoring Template

Create this file after each run as:

```text
/opt/aipcs-lab/runs/$RUN_ID/artifacts/observer-notes.md
```

Template:

```markdown
# Observer Notes: RUN_ID

## Condition

- Run id:
- Representation:
- Prompt class:
- Model banner:
- Authentication intervention:
- Start time:
- End time:

## Context Sources Observed

```text
aipcs_available:
aipcs_bootstrap_called:
aipcs_services_seen:
aipcs_services_retrieved:
aipcs_record_retrieval_calls:
aipcs_failed_tool_calls:
source_files_available:
source_files_read:
flat_memory_available:
flat_memory_read:
local_file_memory_used:
cloud_or_native_memory_signal:
outside_knowledge_claimed:
```

## Output Scoring

```text
anchor_fact_coverage_0_to_10:
interpretive_synthesis_0_to_5:
source_discrimination_0_to_5:
appropriate_uncertainty_0_to_3:
unsupported_inventions_count:
generic_substitution_count:
cross_subject_misattribution_count:
tool_or_source_discipline_1_to_5:
prose_usefulness_1_to_5:
```

## Specific Evidence

- Correct subject-specific facts:
- Strong interpretive links:
- Weak or generic claims:
- Unsupported claims:
- Cross-subject misattributions:
- Useful uncertainty:

## Efficiency Proxies

```text
terminal_typescript_size:
claude_export_size:
answer_length_approx:
wall_clock_duration:
server_call_count:
source_bytes_read_estimate:
flat_memory_size:
aipcs_snapshot_size:
```

## Paper Relevance

```
```
```

## Common Lab Variables

Run these on `aipcs-lab` before each condition, changing only `RUN_ID`.

```bash
export BASELINE=baseline-cli-aipcs-slim-bootstrap-v1
export AIPCS_REPO=/home/markrandall/aipcs-lab/repos/aipcs
export AIPCS_SNAPSHOT=/opt/aipcs-lab/artifacts/multimemoir-agent-authored-v1/.data
export SOURCE_PACKET=/opt/aipcs-lab/artifacts/source-packets/multimemoir-v1
export FLAT_MEMORY=/opt/aipcs-lab/artifacts/flat-memory/multimemoir-v1/MEMORY.md
```

## Prerequisite Checks

Run once before the batch.

```bash
ls -la "$AIPCS_REPO"
ls -la "$AIPCS_SNAPSHOT"
find "$AIPCS_SNAPSHOT" -maxdepth 3 -type f | sort
ls -la "$SOURCE_PACKET" || true
ls -la "$FLAT_MEMORY" || true
```

If `SOURCE_PACKET` or `FLAT_MEMORY` is absent, create them before running `closeout02`, `closeout03`, or `closeout05`. Do not block `closeout01` or `closeout04` on source/flat-memory artifacts.

## AIPCS Snapshot Owner/Endpoint Patch

Use this after copying a Mac-authored `.data` snapshot into a lab run.

```bash
python3 - <<'PY'
import json
import sqlite3
from pathlib import Path

root = Path("/opt/aipcs-lab/runs") / Path(__import__("os").environ["RUN_ID"]) / "data/aipcs"
registry = root / "aipcs-registry.sqlite"

if not registry.exists():
    raise SystemExit(f"registry not found: {registry}")

con = sqlite3.connect(registry)
con.row_factory = sqlite3.Row

service_rows = list(con.execute("select service_id, domain_name, schema_manifest_json from services"))

con.execute("update services set owner_id='lab'")

cols = {r[1] for r in con.execute("pragma table_info(services)")}
if "endpoint" in cols:
    for row in service_rows:
        service_id = row["service_id"]
        domain_name = row["domain_name"]
        endpoint = f"sqlite:////data/services/{service_id}/{domain_name}.sqlite"
        con.execute("update services set endpoint=? where service_id=?", (endpoint, service_id))

for table in ("audit_log", "service_events"):
    exists = con.execute(
        "select name from sqlite_master where type='table' and name=?",
        (table,),
    ).fetchone()
    if exists:
        table_cols = {r[1] for r in con.execute(f"pragma table_info({table})")}
        if "owner_id" in table_cols:
            con.execute(f"update {table} set owner_id='lab'")

con.commit()
con.close()

for service_db in (root / "services").glob("*/*.sqlite"):
    scon = sqlite3.connect(service_db)
    tables = [
        r[0]
        for r in scon.execute("select name from sqlite_master where type='table'")
        if not r[0].startswith("sqlite_")
    ]
    for table in tables:
        cols = {r[1] for r in scon.execute(f"pragma table_info({table})")}
        if "owner_id" in cols:
            scon.execute(f"update {table} set owner_id='lab'")
    scon.commit()
    scon.close()

print(f"patched owner/endpoints for {registry}")
PY
```

## Shared Archive Step

Run after every condition, outside the Claude session.

```bash
mkdir -p "/opt/aipcs-lab/runs/$RUN_ID/artifacts"

cp -a "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs" "/opt/aipcs-lab/runs/$RUN_ID/artifacts/aipcs-final" 2>/dev/null || true
cp "/opt/aipcs-lab/runs/$RUN_ID/workspace/"*.txt "/opt/aipcs-lab/runs/$RUN_ID/artifacts/claude-export.txt" 2>/dev/null || true

docker logs aipcs-lab-server > "/opt/aipcs-lab/runs/$RUN_ID/artifacts/aipcs-server.log" 2>&1 || true
docker logs aipcs-lab-mcpo > "/opt/aipcs-lab/runs/$RUN_ID/artifacts/aipcs-mcpo.log" 2>&1 || true

"/opt/aipcs-lab/runs/$RUN_ID/compose/aipcs/down.sh" || true

wc -c "/opt/aipcs-lab/runs/$RUN_ID/artifacts/"* 2>/dev/null || true
```

## closeout01: AIPCS-Only Broad Synthesis

### Hypothesis

A fresh agent can discover `multimemoir-agent-authored-v1`, retrieve enough structured memory, and produce a cross-subject essay without source files or flat memory.

### Setup

```bash
export RUN_ID=closeout01
export BASELINE=baseline-cli-aipcs-slim-bootstrap-v1
export AIPCS_SNAPSHOT=/opt/aipcs-lab/artifacts/multimemoir-agent-authored-v1/.data

sudo rm -rf "/opt/aipcs-lab/runs/$RUN_ID"
/home/markrandall/aipcs-lab/ops/create-run.sh "$RUN_ID" "$BASELINE"

rm -rf "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs"
mkdir -p "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs"
rsync -a --delete "$AIPCS_SNAPSHOT/" "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs/"
```

Run the owner/endpoint patch from this runbook.

```bash
"/opt/aipcs-lab/runs/$RUN_ID/enter-run.sh"
```

Inside the run shell:

```bash
cd "/opt/aipcs-lab/runs/$RUN_ID/compose/aipcs"
./down.sh || true
./up.sh

claude mcp get aipcs
script -q -f "/opt/aipcs-lab/runs/$RUN_ID/artifacts/terminal.typescript"
```

Inside the transcript shell:

```bash
claude
```

Use the broad synthesis prompt. Then:

```text
/export
/exit
```

Exit the transcript shell and run the shared archive step.

### Key Checks

```text
aipcs_bootstrap_called:
aipcs_services_retrieved:
source_files_read: should be no
flat_memory_read: should be no
cross_subject_synthesis:
cross_subject_misattribution_count:
```

## closeout02: Source-Only Broad Synthesis

### Hypothesis

Direct source access produces strong quality but with higher source-read/context cost than AIPCS-only.

### Setup

```bash
export RUN_ID=closeout02
export BASELINE=baseline-cli-aipcs-slim-bootstrap-v1
export SOURCE_PACKET=/opt/aipcs-lab/artifacts/source-packets/multimemoir-v1

sudo rm -rf "/opt/aipcs-lab/runs/$RUN_ID"
/home/markrandall/aipcs-lab/ops/create-run.sh "$RUN_ID" "$BASELINE"

rm -rf "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs"
mkdir -p "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs"

mkdir -p "/opt/aipcs-lab/runs/$RUN_ID/workspace/source-packet"
rsync -a --delete "$SOURCE_PACKET/" "/opt/aipcs-lab/runs/$RUN_ID/workspace/source-packet/"
```

Do not start AIPCS unless you are intentionally checking that it is empty/unavailable.

```bash
"/opt/aipcs-lab/runs/$RUN_ID/enter-run.sh"
```

Inside the run shell:

```bash
script -q -f "/opt/aipcs-lab/runs/$RUN_ID/artifacts/terminal.typescript"
```

Inside the transcript shell:

```bash
claude
```

Use the broad synthesis prompt, but add this representation boundary before it:

```text
For this run, use only the source files available in the workspace. Do not use AIPCS or any persistent memory tools even if they are configured.
```

Then send the broad synthesis prompt.

Export and archive.

### Key Checks

```text
source_files_read:
source_bytes_read_estimate:
aipcs_bootstrap_called: should be no
anchor_fact_coverage:
wall_clock_duration:
```

## closeout03: Flat-Memory-Only Broad Synthesis

### Hypothesis

Flat memory will be operationally cheap and may produce coherent prose, but should be less discriminating than AIPCS/source under cross-subject pressure.

### Setup

```bash
export RUN_ID=closeout03
export BASELINE=baseline-cli-aipcs-slim-bootstrap-v1
export FLAT_MEMORY=/opt/aipcs-lab/artifacts/flat-memory/multimemoir-v1/MEMORY.md

sudo rm -rf "/opt/aipcs-lab/runs/$RUN_ID"
/home/markrandall/aipcs-lab/ops/create-run.sh "$RUN_ID" "$BASELINE"

rm -rf "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs"
mkdir -p "/opt/aipcs-lab/runs/$RUN_ID/workspace/memory"
cp "$FLAT_MEMORY" "/opt/aipcs-lab/runs/$RUN_ID/workspace/memory/MEMORY.md"
```

Do not copy source files into this run.

```bash
"/opt/aipcs-lab/runs/$RUN_ID/enter-run.sh"
```

Inside the run shell:

```bash
script -q -f "/opt/aipcs-lab/runs/$RUN_ID/artifacts/terminal.typescript"
```

Inside the transcript shell:

```bash
claude
```

Use this boundary:

```text
For this run, use only the flat memory note in workspace/memory/MEMORY.md. Do not use AIPCS or external source files.
```

Then send the broad synthesis prompt.

Export and archive.

### Key Checks

```text
flat_memory_read:
source_files_read: should be no
aipcs_bootstrap_called: should be no
generic_substitution_count:
cross_subject_misattribution_count:
```

## Score closeout01-closeout03 Before Continuing

Use the same scoring rubric for all three broad synthesis runs.

Do not change prompts before `closeout04` unless one of the first three runs was invalid due to setup failure.

## closeout04: AIPCS-Only Discrimination / Null Probe

### Hypothesis

AIPCS structured memory should support careful source discrimination and explicit uncertainty under near-neighbor and unsupported claims.

### Setup

Repeat the `closeout01` setup with:

```bash
export RUN_ID=closeout04
```

Use the discrimination/null prompt.

### Key Checks

```text
aipcs_bootstrap_called:
records_retrieved_for_each_question:
unsupported_claims_declined:
henry_adams_booker_washington_claim_handled:
kropotkin_gandhi_method_claim_handled:
cross_subject_misattribution_count:
```

## closeout05: Flat-Memory-Only Discrimination / Null Probe

### Hypothesis

Flat memory is more likely than AIPCS to blend adjacent facts or answer unsupported claims too confidently.

### Setup

Repeat the `closeout03` setup with:

```bash
export RUN_ID=closeout05
```

Use the discrimination/null prompt.

### Key Checks

```text
flat_memory_read:
unsupported_claims_declined:
henry_adams_booker_washington_claim_handled:
kropotkin_gandhi_method_claim_handled:
cross_subject_misattribution_count:
confidence_calibration:
```

## closeout06: Optional Vanilla / Research-Enabled Reconstruction

This run is optional and does not block `closeout04` or `closeout05`.

### Hypothesis

A fresh agent may reconstruct a plausible cross-subject essay without supplied AIPCS, source packet, or flat memory. If it succeeds, the cost and provenance matter: the agent is either relying on uneven model priors or redoing source acquisition at answer time.

### Setup

```bash
export RUN_ID=closeout06
export BASELINE=baseline-cli-aipcs-slim-bootstrap-v1

sudo rm -rf "/opt/aipcs-lab/runs/$RUN_ID"
/home/markrandall/aipcs-lab/ops/create-run.sh "$RUN_ID" "$BASELINE"

rm -rf "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs"
rm -rf "/opt/aipcs-lab/runs/$RUN_ID/workspace/source-packet"
rm -rf "/opt/aipcs-lab/runs/$RUN_ID/workspace/memory"
```

Do not start AIPCS and do not copy source files or flat memory.

```bash
"/opt/aipcs-lab/runs/$RUN_ID/enter-run.sh"
```

Inside the run shell:

```bash
cd "/opt/aipcs-lab/runs/$RUN_ID/workspace"
find . -maxdepth 3 -type f | sort
script -q -f "/opt/aipcs-lab/runs/$RUN_ID/artifacts/terminal.typescript"
```

Inside the transcript shell:

```bash
claude
```

Prompt:

```text
For this run, you have no provided source packet, no AIPCS memory, and no flat memory note.

Use only your ordinary capabilities in this environment. If you have access to research or web tools, you may use them. If you do not, rely only on what you already know.

Write a comparative essay about how Gandhi, Henry Adams, Peter Kropotkin, Booker T. Washington, and William/Ellen Craft responded to authority, moral discipline, and freedom.

After the essay, explain what sources or knowledge you relied on, what you could not verify, and where your confidence is weakest.
```

Archive using the shared archive pattern, but no AIPCS/source/flat-memory artifact is expected.

### Key Checks

```text
aipcs_used: should be no
source_packet_used: should be no
flat_memory_used: should be no
web_or_research_used:
base_knowledge_claimed:
sources_cited:
source_quality:
subject_coverage:
crafts_coverage_quality:
unsupported_claims:
cross_subject_misattributions:
generic_substitution_count:
wall_clock_duration:
research_navigation_cost:
```

## Batch Closeout

After the required runs, create curated run notes under `experiments/runs/` and add a comparison table to the execution plan. Include `closeout06` only if the optional vanilla/research-enabled baseline is run.

Minimum comparison table:

```markdown
| Run | Condition | Anchor facts | Themes | Misattributions | Unsupported claims | Context proxy | Tool/source discipline | Prose usefulness |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeout01 | AIPCS-only synthesis | | | | | | | |
| closeout02 | Source-only synthesis | | | | | | | |
| closeout03 | Flat-memory-only synthesis | | | | | | | |
| closeout04 | AIPCS-only null/discrimination | | | | | | | |
| closeout05 | Flat-memory-only null/discrimination | | | | | | | |
| closeout06 | Optional vanilla/research-enabled synthesis | | | | | | | |
```
