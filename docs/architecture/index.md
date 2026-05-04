# AIPCS Architecture

## Pattern Summary

AIPCS (Agent-Instantiated Persistent Context Services) is a pattern in which an AI agent, upon encountering a sufficiently complex stateful tracking problem:

1. **Recognises** the need for structured persistent memory
2. **Designs** an appropriate data schema for the domain
3. **Scaffolds** a lightweight persistent service (database + API) around that schema
4. **Registers** the service as an MCP tool, making it available across all future sessions and any MCP-compatible client

The agent is the schema architect — not a consumer of a pre-defined schema. This is the core novelty.

## v1 Design Decisions

Three questions define the v1 architecture. Each is resolved below.

### Q: How does the agent recognise it needs AIPCS? (Trigger)

**v1 decision: Model A — explicit user request**

The user says "track this for me" or similar. The agent recognises the intent and initiates AIPCS. This is the safe, tested starting point.

**Designed to evolve to: Model B — agent-initiated**

A skill or system prompt teaches the agent to recognise AIPCS trigger conditions proactively (multi-entity tracking, relational dependencies, cross-session persistence need) and propose instantiation. The user confirms. This is the pattern's full vision.

Model C (application-triggered) is rejected for the general pattern — it reintroduces developer-defined schema.

### Q: How does the scaffolding happen? (Mechanism)

**v1 decision: Option 4 — AIPCS sidecar with HTTP management API**

An always-running AIPCS sidecar service exposes an HTTP management API. The agent calls a `service_instantiate` MCP tool, which calls the sidecar. The sidecar:
- Generates a SQLite schema from the agent's domain description
- Generates a FastAPI service around it
- Starts the service on an available port
- Writes a service manifest

**Designed to evolve to: Option 3 — MCP tool that scaffolds other MCP tools**

The AIPCS runtime itself is an MCP server exposing `service_instantiate`. The agent calls it; it creates the database, API, and registers new tools — all within the MCP layer. Elegant and self-referential, but more complex to build.

Option 1 (pure prompt/no deployment) and Option 2 (CLI) are rejected — too loose and too much user friction respectively.

### Q: How does the result get registered? (Registration)

**v1 decision: Option B — dynamic MCP tool discovery**

New services appear as MCP tools immediately without requiring a client restart. MCP supports dynamic tool discovery. This is the correct model and not significantly harder than static config.

Option A (static config, requires restart) is acceptable temporarily for development only.
Option C (agent updates its own system prompt) is fragile and rejected.

## Subsystems

| Subsystem | Purpose | Owner doc |
|---|---|---|
| AIPCS Sidecar | HTTP management API; scaffolds services on demand | [decisions/](decisions/) |
| Schema Designer | Prompt that elicits domain schema from the agent | [../agent/ai-feature-rules.md](../agent/ai-feature-rules.md) |
| MCP Interface | Exposes `service_instantiate` and dynamically registers new tools | [boundaries.md](boundaries.md) |
| Service Registry | Manifest of instantiated services and their schemas | Open (Q003) |
| Reference Implementation | Application Tracker — the proving ground | `randallcmark/application_tracker` |

## Architecture Routes

- Boundary definitions → [boundaries.md](boundaries.md)
- Formal decisions (ADRs) → [decisions/](decisions/)
- Pattern principles (P1–P10) → `docs/AIPCS_Pattern_Specification_v0.1.docx`
- Open design questions → [../quality/technical-debt.md](../quality/technical-debt.md)

## Change Rules

- No change to the trigger/mechanism/registration decisions without a BUILD_JOURNAL entry and an ADR
- No new dependency without checking [boundaries.md](boundaries.md)
- Agent-generated outputs (schemas, API code) are always treated as untrusted input — validate before executing
