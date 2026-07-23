# Architecture Boundaries

## Boundary Model

AIPCS is composed of three distinct trust zones:

| Zone | Description | Trust level |
|---|---|---|
| Agent | The AI client (Claude, ChatGPT, or any MCP-compatible) designing schemas and calling tools | Untrusted output — validate everything |
| AIPCS Server | MCP-native server + Registry DB + Schema Validator | Trusted infrastructure |
| Domain Services | Agent-designed SQLite + FastAPI services, dynamically created per domain | User-scoped; isolated per user |

## Allowed Dependencies

| From | May depend on | Notes |
|---|---|---|
| Agent | AIPCS management MCP tools only | Agent has no direct access to Registry DB or Domain Services — all mediated via MCP tools |
| AIPCS Server | Registry DB (SQLite), Domain Service process management | No direct user domain data access at management layer |
| Domain Services | Per-domain SQLite, MCP tool registration | No cross-user access; owner_id scoped on every entity |
| Reference Implementation | AIPCS Server (via MCP), Application Tracker data layer | AIPCS Server is a peer service in Docker Compose, not embedded |

## Disallowed Dependencies

| Rule | Reason |
|---|---|
| Agent-generated SQL executed without validation | Agent output is untrusted; SQL injection vector — all schemas pass through Schema Validator before execution |
| Cross-user domain service access | Every entity in every Domain Service is owner_id scoped |
| Credentials in agent-visible context | Secrets must not appear in tool descriptions, prompts, or responses |
| Agent calling Domain Services directly | All Domain Service access is via dynamically registered MCP tools only |
| Tier 3 access without explicit user consent | Elevated access is consent-gated and read-only |

## Boundary Rules

- All agent-generated artefacts (schemas, tool definitions, migration proposals) are validated by the Schema Validator before execution
- External AI clients access AIPCS only via MCP — no HTTP management API exposed to clients
- The AIPCS Server has no knowledge of the host application's domain — it receives schema descriptions generically
- OAuth/DCR flows are the only authorised mechanism for external MCP client registration (v2; v1 uses local trust within Docker network)
- Tier 3 elevated access requires explicit user consent grant, is read-only, and is audit-logged

## Three-Tier Access Boundaries

| Tier | Access path | Write access | Consent required |
|---|---|---|---|
| Tier 1 — Agent | MCP tools | Yes | Implicit (AIPCS connected) |
| Tier 2 — User | Natural language → agent → MCP tools | Via agent | Implicit |
| Tier 3 — Elevated (IT/compliance/practitioner) | Direct read-only query API or structured export | No | Explicit user consent grant |

## Enforcement

- Schema Validator enforces schema design requirements before materialisation
- `owner_id` enforced on every entity at the Domain Service layer
- Audit log in Registry DB records all management tool calls
- Local public-v1 coordination is resolved for same-host, same-effective-user
  SQLite processes: WAL permits concurrent readers and SQLite serialises one
  writer. Remaining gaps are hosted/cross-user/multi-host coordination (the
  residual scope of Q004), schema conflict resolution (Q005), and the Tier 3
  consent mechanism (Q011).

Record gaps in [../quality/technical-debt.md](../quality/technical-debt.md).
