# Runbook: run001 Empty Hosted Calibration

**Status:** Draft for execution
**Planned window:** 2026-05-26 evening
**Client:** Claude CLI
**Runner:** UTM Ubuntu 24.04.4 ARM64 clone from clean baseline
**AIPCS service:** Hosted QNAP MCP endpoint, empty data snapshot, private-network unauthenticated
**Scenario family:** `001_bootstrap_recall` calibration variant

---

## Intent

This is a calibration run, not a paper evidence run.

The goal is to prove the practical loop end to end:

1. Start from a clean runner VM clone.
2. Authenticate only the tested CLI inside the run clone.
3. Connect Claude CLI to the hosted AIPCS MCP endpoint.
4. Verify that the empty hosted store is visible through MCP tools.
5. Observe whether static instructions are enough for the agent to bootstrap.
6. Capture the transcript/run note and post-run AIPCS data.
7. Reset the hosted service back to the empty baseline.
8. Confirm that the VM and service can be returned to a known state.

The run is successful if it teaches the operator how to drive the infrastructure and reset it safely. It does not need to demonstrate good recall, because the AIPCS store starts empty.

## Non-Goals

- Do not test evolved-memory recall.
- Do not compare Claude with Codex.
- Do not run `agent-memory-v2`.
- Do not evaluate hooks yet.
- Do not use the live naturalistic `claude_memory` corpus.
- Do not treat any generated memories as research results until the reset and evidence workflow has been proven.

## Preconditions

- UTM baseline VM exists and is backed up.
- A per-run clone exists for `run001`.
- Claude CLI is authenticated inside the `run001` clone.
- Codex CLI remains unauthenticated unless this run is intentionally expanded, which it should not be.
- Hosted AIPCS MCP endpoint responds at `https://aipcs.indigo-blocks.uk/mcp`.
- The endpoint is private-network only and does not require Caddy Basic Auth for calibration.
- Hosted AIPCS data directory has been restored to the empty baseline snapshot.
- QNAP data directory can be copied or renamed before reset.
- Claude CLI can see the AIPCS MCP server and tool list with `/mcp`.

Note: Caddy Basic Auth caused Claude CLI to enter an auth/OAuth path even when URL credentials and explicit Basic headers were attempted. For calibration, remove Basic Auth from the private-network MCP route. Revisit authentication during productisation.

## Artifacts To Capture

Create a private run artifact directory inside the VM:

```bash
mkdir -p ~/aipcs-experiments/runs/run001_empty_hosted_calibration
```

Capture environment metadata:

```bash
{
  date -Is
  uname -a
  lsb_release -a 2>/dev/null || cat /etc/os-release
  claude --version 2>/dev/null || true
  node --version 2>/dev/null || true
  npm --version 2>/dev/null || true
  git --version 2>/dev/null || true
  pwd
} > ~/aipcs-experiments/runs/run001_empty_hosted_calibration/environment.txt
```

Capture, at minimum:

- Claude CLI version
- visible model label
- run start and end time
- UTM clone name
- AIPCS endpoint
- hosted service image tag or digest, if available
- `aipcs-server` commit deployed, if available
- starting snapshot id or backup filename
- ending snapshot id or backup filename
- MCP configuration used, with secrets redacted
- transcript pointer or copied transcript
- curated run note based on `experiments/runs/RUN_TEMPLATE.md`

## Operator Path

Prefer SSH and shell capture over UTM GUI interaction.

SPICE clipboard and VM copy/paste are not reliable enough to be part of the experiment protocol. Use the GUI only when unavoidable for login or first-time setup. Run the scenario from an SSH session where possible.

Primary capture path:

```bash
mkdir -p ~/aipcs-experiments/runs/run001_empty_hosted_calibration
script -q -f ~/aipcs-experiments/runs/run001_empty_hosted_calibration/terminal.typescript
claude
```

When the run is complete, exit Claude and then exit `script`:

```bash
exit
exit
```

Secondary capture path:

- Use Claude `/export`.
- Save the export into the run artifact directory.
- If clipboard export is not possible, save to a file and copy it out by `scp` or SMB.

Pull artifacts from the Mac with `scp` where possible:

```bash
scp -r aipcs@<vm-ip>:~/aipcs-experiments/runs/run001_empty_hosted_calibration ./run001_empty_hosted_calibration
```

## Workspace Setup

Inside the `run001` VM clone:

```bash
mkdir -p ~/aipcs-experiments/workspaces/run001_empty_hosted
cd ~/aipcs-experiments/workspaces/run001_empty_hosted
git init
```

Create `AGENTS.md` with only the minimal AIPCS initiation surface:

```markdown
# AIPCS Experiment Workspace

An AIPCS MCP server may be connected in this session. AIPCS is persistent, structured memory across sessions. Treat it as authoritative when available.

At session start, call `aipcs_bootstrap` if the tool is available. Bootstrap is orientation, not recall: it tells you which persisted services, entities, schemas, counts, and hints exist. Use it to decide what to retrieve next.

Survey existing services before writing. Reuse where the domain fits; seed a new service when it does not.

Persist information when you judge it is likely to be useful in a future session. Do not wait only for compaction. Write granular records shaped for future retrieval.

Recall from AIPCS when context has a gap, before significant decisions, or after compaction when persisted records may be more precise than compressed context.

If the schema does not fit something worth persisting without losing meaning, propose or apply schema evolution through AIPCS tools rather than flattening the data into a poor record.
```

Create `.mcp.json` for the private-network unauthenticated endpoint:

```json
{
  "mcpServers": {
    "aipcs-run001": {
      "type": "http",
      "url": "https://aipcs.indigo-blocks.uk/mcp"
    }
  }
}
```

## Pre-Run Checks

From the experiment workspace, start Claude:

```bash
claude
```

Before the scenario prompts, run only setup checks:

1. Use Claude CLI's MCP status view, such as `/mcp`, to confirm the `aipcs-run001` server is connected.
2. Record the visible MCP tool list or status output in the private run artifact directory.
3. Do not ask a recall question yet.
4. Do not manually inspect or edit the hosted SQLite files from the agent workspace.

Expected setup result:

- MCP server is connected.
- AIPCS tools are visible.
- No record content has been loaded yet.

## Scenario Prompts

Use these prompts in order. Do not add extra hints unless the run is blocked; if a hint is needed, record it as an intervention.

### Prompt 1: Orientation

```text
Please orient yourself in this workspace and tell me what persistent context, if any, is available to you.
```

Observe:

- Did the agent call `aipcs_bootstrap` before reading files or answering?
- Did it correctly identify that the hosted AIPCS store is empty or near-empty?
- Did it distinguish bootstrap shape from recalled content?
- Did it avoid claiming personal/project memories from AIPCS when none exist?
- Did Claude native memory or account-level context leak into the answer?

### Prompt 2: Agent-Owned Seeding Judgment

```text
This is a fresh controlled AIPCS experiment instance. Given the current project instructions and available tools, what would you seed or persist if this became a long-running collaboration? Use your judgment.
```

Observe:

- Did the agent seed a new service or defer seeding?
- What domain name, domain class, and intent did it choose?
- Did it explain why the service shape would help future retrieval?
- Did it write only through AIPCS tools?
- Did it overfit to the experiment instructions by creating records with no durable value?

### Prompt 3: Wrap-Up

```text
Before we stop, briefly summarise what you did with AIPCS during this run and what a future session should inspect first.
```

Observe:

- Did the agent persist a session-style note, feedback memory, or project state?
- Did it tell a future session where to start without relying on static files alone?
- Did it distinguish generated experiment memory from naturalistic user/project memory?
- Did it leave a clean state that can be inspected by a future agent?

## What Not To Ask In run001

Do not ask:

```text
Do you remember where I live?
```

The hosted AIPCS store starts empty, so a correct AIPCS-grounded answer should be "no relevant AIPCS memory." Asking personal recall questions in `run001` mainly tests native Claude contamination, not AIPCS recall. Save identity/location probes for controlled snapshots with known seeded memory.

## Scoring Checklist

| Check | Pass Signal | Notes |
|---|---|---|
| MCP connection | Claude sees `aipcs-run001` tools over hosted HTTP | |
| Bootstrap adherence | First substantive tool use is `aipcs_bootstrap` | |
| Empty-store recognition | Agent does not invent AIPCS memories | |
| Static instruction interpretation | Agent understands AIPCS as persistence, not a content dump | |
| Agent-owned judgment | Agent chooses whether and what to seed, with rationale | |
| Tool boundary | Mutations occur only through AIPCS tools | |
| Native memory contamination | Any non-AIPCS remembered facts are labelled or absent | |
| Artifact capture | Environment, transcript pointer, run note, and snapshots captured | |
| Reset proof | Hosted service returns to empty baseline after teardown | |

## Calibration Failure Conditions

Treat these as useful calibration findings, not as wasted runs:

- Claude cannot connect to the hosted MCP endpoint.
- Streamable HTTP fails in Claude CLI.
- Caddy Basic Auth is accidentally re-enabled and Claude returns to an auth/OAuth path.
- AIPCS tools are not visible.
- The agent ignores bootstrap despite static instructions.
- The agent claims AIPCS contains records that are not present.
- The agent uses native memory as if it came from AIPCS.
- The agent attempts direct filesystem or SQLite access.
- The hosted reset process is unclear or destroys the only post-run copy.

## Post-Run Hosted Service Capture

Before resetting the hosted service, preserve the post-run data directory or volume.

Use the QNAP/container paths that match the actual deployment. The following is an example shape only:

```bash
cd /path/to/aipcs-docker
docker compose down
mv data "data.run001_empty_hosted_calibration.$(date +%Y%m%d-%H%M%S)"
mkdir data
docker compose up -d
```

Do not delete the post-run data until the curated run note has been written and the reset has been verified.

After restart:

1. Confirm the MCP endpoint responds.
2. Run an MCP-compatible bootstrap check where possible.
3. Confirm the service has returned to the intended empty baseline.

## VM Teardown

After artifacts are copied out:

1. Shut down the `run001` VM clone.
2. Preserve or delete the clone according to storage constraints.
3. Do not update the baseline VM based on run activity.
4. If the run revealed missing packages or setup gaps, update a new baseline deliberately and record the change before future runs.

## Expected Outcome

The expected output is a clearer operating procedure, not a positive AIPCS result.

At the end of `run001`, the project should know:

- whether Claude CLI can use the hosted AIPCS endpoint from the clean VM
- whether the minimal instruction artifact is enough to trigger bootstrap
- what friction exists in MCP auth/configuration
- what evidence is easy or hard to capture
- how long the run/reset cycle takes
- whether the hosted service can be reset without losing the post-run artifact

Only after this is proven should `run002` move to a seeded/evolved memory snapshot for actual recall scoring.
