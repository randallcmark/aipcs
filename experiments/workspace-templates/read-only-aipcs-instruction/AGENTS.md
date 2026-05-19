# Experiment Workspace: AIPCS Read-Only

An AIPCS MCP server may be connected in this session. AIPCS is persistent, structured memory across sessions.

This run is read-only from the agent's perspective.

Allowed behavior:

- Call discovery and read-facing AIPCS tools when available.
- Use `aipcs_bootstrap` to orient.
- Retrieve bounded records before claiming persisted knowledge.
- Use recalled records to inform answers.
- Explain when a task would require write access.

Disallowed behavior:

- Do not create, update, delete, materialise, or evolve AIPCS memory.
- Do not attempt direct SQLite or filesystem access to memory stores.
- Do not treat service-owned audit/telemetry as an agent write.

If the user asks for persistence or repair, explain that the current run is read-only and describe the change that would be made in a write-enabled run.
