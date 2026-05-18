# Codex CLI Local AIPCS MCP Setup

Use this for local Codex CLI experiments against `aipcs-server` over MCP `stdio`.
This does not require a public MCP endpoint.

## Prerequisites

- `aipcs-server` checkout exists at `/Users/markrandall/GitHub/aipcs-server`
- `aipcs-server` virtual environment has been installed
- Codex CLI is installed and available as `codex`

Check Codex MCP support:

```bash
codex mcp --help
codex mcp add --help
```

## Shared Local Memory

This points Codex at the normal local AIPCS data directory.
Use it when intentionally working with the same memory store as other local clients.

```bash
codex mcp add aipcs \
  --env AIPCS_OWNER_ID=mark \
  --env AIPCS_DATA_DIR=/Users/markrandall/GitHub/aipcs-server/.data \
  -- /Users/markrandall/GitHub/aipcs-server/.venv/bin/aipcs-server
```

Verify:

```bash
codex mcp list
codex mcp get aipcs
```

Remove:

```bash
codex mcp remove aipcs
```

## Isolated Evaluation Memory

Use a separate data directory when running evaluation scenarios so the test agent does not mutate the real local memory store.

```bash
codex mcp add aipcs-eval \
  --env AIPCS_OWNER_ID=eval-user \
  --env AIPCS_DATA_DIR=/private/tmp/aipcs-codex-eval \
  -- /Users/markrandall/GitHub/aipcs-server/.venv/bin/aipcs-server
```

Verify:

```bash
codex mcp list
codex mcp get aipcs-eval
```

Remove:

```bash
codex mcp remove aipcs-eval
```

## Session Prompt

Start a Codex CLI session in the target repo and include the portable AIPCS instruction text:

```bash
codex --cd /Users/markrandall/GitHub/aipcs
```

Then paste or reference:

- [aipcs-persistent-memory-instruction.md](aipcs-persistent-memory-instruction.md)

Expected first behavior:

- discover available tools;
- call `aipcs_bootstrap`;
- treat bootstrap as shape-only orientation;
- retrieve bounded records before claiming persisted knowledge;
- mutate memory only through AIPCS MCP tools.

## Evaluation Notes

- Local Codex CLI MCP proves local `stdio` tool semantics and agent behavior.
- It is distinct from hosted ChatGPT/Claude public MCP, where the provider infrastructure initiates the connection and may require a public endpoint or bridge.
- Direct SQLite edits are out of contract. If an agent bypasses MCP tools, count it as a guardrail failure.
