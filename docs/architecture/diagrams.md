# AIPCS Architecture Diagrams

This document captures three views of AIPCS:

1. The current local-only MCP reference implementation.
2. The current conceptual data model.
3. The exploded target productised infrastructure.

The diagrams distinguish the paper-minimum research surface from later productisation layers. The local implementation is enough to test the core claim: the agent owns, uses, and evolves its memory architecture through tool-mediated primitives.

---

## Local-Only MCP Service

```mermaid
flowchart LR
    subgraph agent["Local agent harness"]
        instructions["Static AIPCS instructions\nAGENTS.md / CLAUDE.md / Codex config"]
        client["MCP client\nClaude CLI / Codex CLI"]
        eval["Optional deterministic eval runner"]
    end

    subgraph server["aipcs-server local process"]
        transport["MCP stdio transport"]
        tools["FastMCP tool adapter"]
        bootstrap["Bootstrap and discovery service"]
        lifecycle["Service lifecycle service\nseed / design / materialise / inspect / list"]
        records["Generic record service\ncreate / list / get / search / update / delete / history"]
        evolve["Schema evolution service\nadditive migrations"]
        validation["Schema and request validation"]
        materialiser["SQLite materialiser"]
    end

    subgraph data["Local filesystem data directory"]
        registry[("Registry SQLite\nservices / manifests / audit")]
        svcdb1[("Domain service SQLite\nclaude_memory")]
        svcdb2[("Domain service SQLite\naipcs_development")]
        svcdbn[("Domain service SQLite\nfuture domains")]
    end

    instructions --> client
    client -->|"MCP tool calls over stdio"| transport
    eval -->|"same MCP/tool contract"| transport
    transport --> tools
    tools --> bootstrap
    tools --> lifecycle
    tools --> records
    tools --> evolve
    lifecycle --> validation
    lifecycle --> materialiser
    evolve --> validation
    evolve --> materialiser
    bootstrap --> registry
    lifecycle --> registry
    validation --> registry
    materialiser --> registry
    materialiser --> svcdb1
    materialiser --> svcdb2
    materialiser --> svcdbn
    records --> registry
    records --> svcdb1
    records --> svcdb2
    records --> svcdbn
```

### Local-Only Definitions

| Component | Definition |
|---|---|
| Static AIPCS instructions | Thin harness guidance that tells the agent AIPCS may exist, to call bootstrap, to retrieve bounded records, and to persist/evolve useful memory. |
| MCP stdio transport | The current local connection path. No public network service or hosted-client auth is required. |
| FastMCP tool adapter | The MCP-facing layer that exposes stable primitive tools to the agent. |
| Bootstrap and discovery service | Returns a shape-only data-dictionary map of services, entities, schemas, counts, and hints. It is orientation, not recall. |
| Service lifecycle service | Owns `seed`, `design`, `materialise`, `inspect`, and `list`. |
| Generic record service | Operates domain records through schema-aware generic tools. This is the current proof surface instead of generated domain-specific tools. |
| Schema evolution service | Applies additive schema evolution: add entity, add optional attribute, add enum value, update entity description, update service intent. |
| Registry SQLite | Server-owned metadata store for services, manifests, lifecycle state, migrations, and audit. |
| Domain service SQLite | One SQLite database per materialised service. The agent never writes these directly as part of the contract. |

### Local Boundary

The local agent may physically see repository and data files during development, but direct SQLite edits are out-of-contract. Normal behavior must go through MCP tools so validation, server-controlled fields, history, and audit remain meaningful.

---

## Data Model

```mermaid
erDiagram
    OWNER ||--o{ SERVICE : owns
    SERVICE ||--o{ ENTITY : defines
    ENTITY ||--o{ ATTRIBUTE : has
    SERVICE ||--o{ MIGRATION : records
    SERVICE ||--o{ RECORD : contains
    ENTITY ||--o{ RECORD : stores
    RECORD ||--o{ RECORD_HISTORY : has
    SERVICE ||--o{ AUDIT_EVENT : emits

    OWNER {
        string owner_id
    }

    SERVICE {
        uuid service_id
        string owner_id
        string domain_name
        string domain_class
        string intent_description
        string state
        string confidence
        int schema_version
        datetime created_at
        datetime updated_at
        datetime last_activity_at
    }

    ENTITY {
        string entity_name
        string description
        string service_id
        string retrieval_hint
        int record_count
    }

    ATTRIBUTE {
        string attribute_name
        string entity_name
        string type
        boolean required
        string allowed_values
        string description
    }

    RECORD {
        uuid id
        uuid service_id
        string entity_name
        string owner_id
        json agent_attributes
        datetime created_at
        datetime updated_at
        string created_via
    }

    RECORD_HISTORY {
        uuid history_id
        uuid record_id
        string operation
        json before
        json after
        datetime changed_at
        string changed_via
    }

    MIGRATION {
        int version
        string migration_name
        string rationale
        json operations
        datetime applied_at
    }

    AUDIT_EVENT {
        uuid event_id
        uuid service_id
        string event_type
        json detail
        datetime occurred_at
    }
```

### Data Model Definitions

| Term | Definition |
|---|---|
| Owner | The user or account scope for records and services. The current local prototype assumes single-user local operation but keeps `owner_id` as a scoping primitive. |
| Service | A seeded or materialised persistent context service for one domain, such as `claude_memory` or `aipcs_development`. |
| Domain class | A broad, non-binding top-level anchor such as `project`, `career`, or `memory`. It supports discovery and interoperability but is not a closed taxonomy. |
| Intent description | The seed-level explanation of what the service is meant to track. Bootstrap should expose this so agents know where to probe. |
| Entity | A schema-defined record type inside a service, such as `decision`, `feedback_memory`, or `reference_memory`. |
| Attribute | A schema-defined field on an entity. Constrained fields create retrieval pressure; open-text fields are allowed but should be self-audited for prose leakage. |
| Record | A persisted domain object. Server fields are controlled by AIPCS; agent-defined fields come from the entity schema. |
| Record history | Append-style mutation history for creates, updates, and deletes where available. This preserves repair/evolution context. |
| Migration | Schema evolution history. It records what changed, why, and which operations were applied. |
| Audit event | Server/system event log. Productised administrative controls should use audit/history rather than silently altering memory. |

### Lifecycle State

```mermaid
stateDiagram-v2
    [*] --> Seeded
    Seeded --> Designed: aipcs_service_design accepted
    Designed --> Materialised: aipcs_service_materialise
    Materialised --> Materialised: aipcs_service_evolve additive migration
    Materialised --> Suspended: aipcs_service_suspend future
    Suspended --> Materialised: resume future
```

### Server-Controlled Versus Agent-Owned Fields

| Server-controlled | Agent-owned through schema |
|---|---|
| `id`, `owner_id`, `created_at`, `updated_at`, `created_via`, mutation history, lifecycle timestamps | Entity names, attribute names, optional provenance fields, status fields, record payload values, service intent refinements |

The server enforces the tool contract. The agent owns the memory architecture within that contract.

---

## Exploded Productised Infrastructure

```mermaid
flowchart TB
    subgraph clients["Client and agent layer"]
        local_cli["Local clients\nClaude CLI / Codex CLI"]
        hosted_agents["Hosted agents\nChatGPT / Claude.ai"]
        open_webui["Homelab clients\nOpen WebUI / local tools"]
        admin_ui["User and admin UI\nfuture"]
    end

    subgraph transport["Transport and edge layer"]
        stdio["Local MCP stdio"]
        private_net["Private MCP over Tailscale\nhomelab/private"]
        public_mcp["Public MCP HTTPS\nhosted-client reachable"]
        caddy["Caddy reverse proxy\nindigo-blocks.uk"]
        cloudflare["Cloudflare DNS and TLS"]
    end

    subgraph auth["Identity, consent, and policy layer"]
        oauth["OAuth 2.0 and DCR\nfuture hosted auth"]
        scopes["MCP scopes and client policy"]
        consent["Consent and export approval"]
        tenancy["Owner and tenant scoping"]
    end

    subgraph aipcs["AIPCS application layer"]
        mcp_gateway["MCP gateway"]
        primitive_tools["Primitive tool surface\nseed / bootstrap / design / materialise / evolve"]
        record_tools["Generic record tools\ncreate / list / get / search / update / delete / history"]
        optional_tools["Optional generated domain tools\nproduct UX layer"]
        admin_api["Administrative control plane\nexport / expunge / immutable seeds"]
    end

    subgraph core["Core service layer"]
        registry_service["Registry service"]
        schema_service["Schema validator and manifest service"]
        materialise_service["Materialisation and migration service"]
        retrieval_service["Retrieval and metadata enrichment"]
        audit_service["Audit and history service"]
        maintenance_service["Maintenance discovery\nfuture"]
    end

    subgraph storage["Data and persistence layer"]
        registry_db[("Registry database")]
        service_dbs[("Per-service databases")]
        backups[("Backups and exports")]
        artifact_store[("Trace and evidence artifacts")]
        secret_store[("Secrets and client credentials")]
    end

    subgraph ops["Operations layer"]
        portainer["Portainer\ncontainer management"]
        observability["Grafana / Prometheus / Loki"]
        logs["Structured logs and metrics"]
    end

    subgraph model_plane["Model and inference plane"]
        frontier["Hosted frontier models"]
        nim["NVIDIA NIM / Gemini"]
        vllm["Brandon vLLM relay"]
        local_models["Optional Apple Silicon models"]
    end

    local_cli --> stdio
    open_webui --> private_net
    hosted_agents --> public_mcp
    admin_ui --> public_mcp
    private_net --> caddy
    public_mcp --> cloudflare
    cloudflare --> caddy
    caddy --> mcp_gateway
    stdio --> mcp_gateway

    mcp_gateway --> oauth
    oauth --> scopes
    scopes --> consent
    consent --> tenancy
    tenancy --> primitive_tools
    tenancy --> record_tools
    tenancy --> optional_tools
    tenancy --> admin_api

    primitive_tools --> registry_service
    primitive_tools --> schema_service
    primitive_tools --> materialise_service
    record_tools --> retrieval_service
    record_tools --> audit_service
    optional_tools --> record_tools
    admin_api --> audit_service
    admin_api --> registry_service
    admin_api --> maintenance_service

    registry_service --> registry_db
    schema_service --> registry_db
    materialise_service --> service_dbs
    retrieval_service --> service_dbs
    audit_service --> registry_db
    audit_service --> service_dbs
    admin_api --> backups
    mcp_gateway --> secret_store
    retrieval_service --> artifact_store

    mcp_gateway --> logs
    primitive_tools --> logs
    record_tools --> logs
    registry_service --> logs
    retrieval_service --> logs
    logs --> observability
    portainer --> mcp_gateway
    portainer --> registry_db
    portainer --> service_dbs

    hosted_agents -.-> frontier
    open_webui -.-> vllm
    local_cli -.-> local_models
    hosted_agents -.-> nim
```

### Productised Layer Definitions

| Layer | Purpose | Current status |
|---|---|---|
| Client and agent layer | Places where agents or users initiate work. Includes local CLIs, hosted clients, Open WebUI, and future admin UI. | Local CLI proven; hosted and admin UI future. |
| Transport and edge layer | Moves from local `stdio` to private homelab and public hosted-client reachability. | Local `stdio` proven; homelab substrate exists; public MCP future. |
| Identity, consent, and policy layer | OAuth/DCR, MCP scopes, user consent, owner/tenant scoping, and export approvals. | Designed, deferred from first paper proof. |
| AIPCS application layer | The externally visible tool/API surface. Stable primitives remain core; generated domain tools are optional product UX. | Primitive and generic record tools implemented locally. |
| Core service layer | Internal services that validate, materialise, retrieve, enrich, audit, and maintain memory. | Partially implemented in `aipcs-server`. |
| Data and persistence layer | Registry, per-service stores, backups, trace/evidence artifacts, and secrets. | Local SQLite implemented; production stores/backups/secrets future. |
| Operations layer | QNAP/homelab hosting, container management, logs, metrics, dashboards. | Homelab available as deployment substrate; not needed for paper-minimum proof. |
| Model and inference plane | The model providers used by clients. AIPCS hosts memory services, not heavy inference. | External to AIPCS; can include hosted models, NVIDIA/Gemini, vLLM, or local Apple Silicon. |

### Productisation Boundaries

- The paper-minimum proof is local Python/SQLite/MCP plus deterministic and live-agent evidence.
- Homelab deployment is the preferred durable service substrate once the local semantics are stable, but it should not distort the research claim.
- Hosted ChatGPT/Claude-style clients require public MCP or a bridge because provider infrastructure initiates the connection.
- Administrative controls such as expunge, immutable external seeds, and compliance export belong to a separate control plane. They should not silently rewrite the normal agent memory plane.
- Direct database access is never a supported agent path in productised deployments.
