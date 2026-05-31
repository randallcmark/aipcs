# UTM Clean Agent Runner

## Purpose

This environment is the controlled live-agent runner for AIPCS experiments.

It exists to separate the agent client from:

- the operator's daily machine state
- local AIPCS source code
- direct SQLite access
- prior Claude/Codex CLI configuration
- uncontrolled workspace files

The current service substrate is the QNAP-hosted AIPCS MCP endpoint. The current agent runner substrate is a UTM Linux VM cloned from a clean baseline image.

## Baseline

| Field | Value |
|---|---|
| VM manager | UTM |
| Host class | MacBook Pro M2 Pro, 16 GB RAM |
| Guest OS | Ubuntu 24.04.4 ARM64 |
| Base VM | `aipcs-runner-base` |
| Run VM pattern | `aipcs-runner-runNNN` |
| Base auth state | No Claude/Codex login state |
| Base source access | No mounted host GitHub directories |
| Base recovery | Baseline VM artifact copied to QNAP |

Record the exact UTM version, VM file location, base artifact hash where practical, and installed CLI versions in each run note.

## Service Endpoint

| Field | Value |
|---|---|
| Endpoint | `https://aipcs.indigo-blocks.uk/mcp` |
| Transport | MCP Streamable HTTP |
| Gateway auth | Caddy basic auth |
| Service host | QNAP Docker / `aipcs-server` container |
| Service data path | `/share/CACHEDEV1_DATA/Container/aipcs/data` |

The endpoint should be treated as an experiment substrate, not a production deployment.

The authenticated plain `curl` probe may return `406 Not Acceptable` if it does not send the MCP stream headers. That proves the request reached FastMCP through Caddy, but it is not a complete MCP-client validation.

## Baseline Rules

- Do not authenticate Claude or Codex in `aipcs-runner-base`.
- Do not run experiments in `aipcs-runner-base`.
- Clone the base VM for each run.
- Authenticate only the agent CLI being tested inside the per-run clone.
- Do not mount host source directories into the VM.
- Do not copy `aipcs-server` source or SQLite data into the VM.
- Do not store MCP basic-auth passwords in committed files.
- Delete or archive the run VM after artifacts are captured.

## Per-Run Setup

1. Clone `aipcs-runner-base` to a run VM such as `aipcs-runner-run001`.
2. Start the run VM.
3. Authenticate the selected agent CLI only.
4. Create a fresh workspace from the selected template.
5. Configure the MCP client against the intended endpoint and permission variant.
6. Record visible agent/client/model labels.
7. Run the fixed scenario prompt sequence.
8. Capture transcript, tool calls where available, run notes, and pre/post service snapshots.
9. Shut down the run VM.
10. Delete or archive the run VM after artifacts are secured.

## Snapshot Discipline

The QNAP AIPCS service data directory is the experiment state. For controlled runs:

- never run against the live naturalistic corpus
- restore or copy a named snapshot before the run
- capture a pre-run snapshot hash or archive name
- capture a post-run snapshot hash or archive name
- record the `aipcs-server` commit and Docker image tag/digest

For paper-cited runs, do not rely on `latest`; pin the service image tag or digest and record it in the run note.

