# Architecture Boundaries

## Boundary Model

AIPCS is composed of three distinct trust zones:

| Zone | Description | Trust level |
|---|---|---|
| Agent | The AI client (Claude, ChatGPT, etc.) designing the schema and calling tools | Untrusted output — validate everything |
| AIPCS Layer | Sidecar + MCP interface + service registry | Trusted infrastructure |
| Instantiated Services | Agent-designed FastAPI + SQLite services | User-scoped; isolated per user |

## Allowed Dependencies

| From | May depend on | Notes |
|---|---|---|
| Agent | AIPCS MCP tools only | Agent cannot directly access the sidecar HTTP API |
| AIPCS Sidecar | SQLite, FastAPI, service manifest storage | No direct user data access at management layer |
| Instantiated Services | SQLite (local), MCP registration | No cross-user access |
| Reference Implementation | AIPCS Sidecar (via HTTP), Application Tracker data layer | Sidecar is a sidecar, not embedded |

## Disallowed Dependencies

| Rule | Reason |
|---|---|
| Agent-generated SQL executed without validation | Agent output is untrusted; SQL injection vector |
| Cross-user service access | Each instantiated service is user-scoped |
| Credentials in agent-visible context | Secrets must not appear in tool descriptions, prompts, or responses |
| Sidecar embedded in main application process | Sidecar must be independently deployable |

## Boundary Rules

- All agent-generated artefacts (schemas, API code, tool descriptions) are validated before execution
- External systems (OAuth provider, MCP clients) accessed only through explicit adapters
- The AIPCS sidecar has no knowledge of the host application's domain — it receives a schema description and scaffolds generically
- OAuth/DCR flows are the only authorised mechanism for MCP client registration

## Enforcement

- Input validation on the schema design prompt output (enforce in sidecar before execution)
- Service isolation: each instantiated service runs on its own port with its own SQLite file
- Gaps: schema validation format is an open question (Q002); multi-agent locking is an open question (Q004)

Record gaps in [../quality/technical-debt.md](../quality/technical-debt.md).
