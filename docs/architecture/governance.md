# Governance Model

> **Author:** Randall Mark — May 2026
> **Status:** v1 — required for all prototypes beyond solo development
> **BUILD_JOURNAL:** Entry 009
> **ADR:** [ADR-001-governance-model.md](decisions/ADR-001-governance-model.md)

---

## Governance Thesis

AIPCS is a **governed** pattern. The agent proposes; the runtime governs.

The value of AIPCS is not unrestricted agent freedom. The value is governed agent-directed persistence. Without the governance layer, the claim that "the agent is the architect of its own memory" is a liability, not a contribution — it describes arbitrary agent-controlled persistence with no safety guarantees.

The authority chain is non-negotiable:

```
Agent proposes
     ↓
Validator constrains
     ↓
User consents (where required)
     ↓
Service persists
     ↓
Audit log explains
```

Every element of this chain must be present in any AIPCS deployment that is used with real users. Gaps in the chain are gaps in the claim.

---

## Constraint Categories

### 1. Proposal Constraints

What the agent may do at each governance tier:

| Action | Unilateral? | Governance gate |
|---|---|---|
| Seed a domain marker | Yes | None — seeding is always permitted |
| List existing services | Yes | None |
| Inspect a service manifest | Yes | None |
| Propose an initial schema | No | Schema Validator (structural + structural-semantic checks) |
| Materialise a validated schema | No | Validator pass required; audit entry written |
| Propose an additive migration (add column/table/index) | No | Validator gate |
| Propose a destructive migration (drop column, rename, type change) | No | Validator gate + explicit user confirmation |
| Export service data | No | Consent tier 2 (user confirmation); tier 3 for sensitive |
| Grant Tier 3 access | No | High bar — explicit user consent + audit entry |
| Add a column declared sensitive | No | User notification at materialisation + audit entry |

The agent may **not** unilaterally:
- Bypass validation
- Apply a destructive migration without confirmation
- Persist data belonging to a disallowed sensitive class
- Redefine the authorisation policy
- Grant or revoke Tier 3 access without explicit user consent
- Expose domain data to third parties without consent

### 2. Structural Constraints

The Schema Validator must enforce these rules before any schema is materialised:

- No reserved table names (`audit_log`, `schema_manifest`, `migration_history`, `aipcs_*`)
- No reserved column names (`owner_id`, `created_at`, `updated_at`, `_aipcs_*`)
- Every entity must have a primary key
- Foreign key references must name an entity defined in the same schema
- All audit fields (`created_at`, `updated_at`) must be present on every entity
- `owner_id` must be present on every entity (user scoping)
- Tool name format: `domain_object_action` — all lowercase, underscores only, maximum 60 characters
- Schema manifest must include `domain_class` field
- Migration history must be present and correctly sequenced

These are minimum constraints, not sufficient constraints.

### 3. Semantic Constraints

The following constraints describe what the Schema Validator must guard against, even where automated enforcement is not yet fully in place. The skill definition must also reinforce them.

- The schema must describe the agent's own accumulated domain knowledge — not a copy of the host application's data model
- The schema must not include credentials, system secrets, or authentication tokens as columns (see sensitive-data constraints)
- The schema must not reference tables from the host application's own database
- The agent may not propose a schema whose primary purpose is to replicate existing host application data (see `docs/architecture/claims-and-scope.md` §Non-Goals)
- Field names must be semantically meaningful and specific to the domain — not generic (`value`, `data`, `info`)

**Status of automation:** Structural constraints are enforceable by rule. Semantic constraints require either model-assisted validation or heuristic guards. Full automation is deferred as Q012 and Q013 in `docs/quality/technical-debt.md`.

### 4. Sensitive-Data Constraints

Columns whose names match a sensitive-data pattern trigger additional governance requirements:

**Sensitive name patterns (v1 heuristic list):**
- `password`, `passwd`, `secret`, `token`, `api_key`, `access_key`, `private_key`
- `ssn`, `national_id`, `tax_id`, `passport`
- `dob`, `date_of_birth`, `birth_date`
- `health_*`, `medical_*`, `diagnosis_*`, `medication_*`
- `credit_card`, `card_number`, `bank_account`, `routing_number`

When a column matches a sensitive-data pattern:
- The schema manifest must include `sensitive: true` for that column
- The user must be notified before materialisation
- An audit entry is written for every write to that column
- Export of that column requires explicit consent

Data classes that are **disallowed entirely** in any AIPCS schema:
- Raw credentials (passwords, API keys, private keys, tokens)
- Payment secrets (card numbers, CVVs, account numbers)
- Authentication secrets (session tokens, refresh tokens, OTP seeds)

These classes must never be stored as column values. The Schema Validator must reject any schema that includes column names or descriptions matching these patterns.

---

## User Transparency Requirements

At any point in time, a user must be able to determine:

1. Which domains are being tracked on their behalf (`aipcs_service_list`)
2. What data is stored in each domain (`aipcs_service_inspect` + domain query tools)
3. When each schema was last changed and what changed (migration history in the manifest)
4. Which agent actions triggered schema changes and data writes (audit log)
5. How to export all their data from any domain (`aipcs_service_export`)
6. How to pause or delete a domain service and all its data (`aipcs_service_suspend` + delete)
7. Whether any Tier 3 access grant is currently active and to whom

Transparency is not optional. Without it, the three-tier access model has no legitimacy.

---

## Auditability Requirements

### Auditable Actions

Every occurrence of the following must produce an audit entry in the Registry DB `audit_log` table:

1. `service_seeded` — domain marker planted
2. `schema_design_submitted` — agent submitted a schema for validation
3. `schema_validated` or `schema_rejected` — outcome of validation
4. `service_materialised` — schema deployed as a live service
5. `schema_evolution_proposed` — migration proposed by agent
6. `schema_evolution_applied` or `schema_evolution_rejected` — outcome
7. `service_exported` — data or schema export performed
8. `tier3_access_granted` or `tier3_access_revoked` — elevated access changed

### Audit Entry Fields

| Field | Type | Notes |
|---|---|---|
| `event_id` | UUID | Unique identifier for the event |
| `event_type` | String | One of the 8 auditable action types above |
| `service_id` | String | The domain service identifier |
| `actor` | String | `agent`, `user`, or `system` |
| `timestamp` | ISO 8601 | UTC |
| `outcome` | String | `success`, `rejected`, or `pending` |

---

## Consent Model

Different actions require different levels of user involvement.

| Tier | Label | Examples | Required gate |
|---|---|---|---|
| Tier 0 | Implicitly allowed | Seeding, listing, inspecting, proposing (not applying) schema | None |
| Tier 1 | Explicit confirmation recommended | First materialisation of a new service, destructive migration, sensitive column addition, data export | User-visible confirmation before proceeding |
| Tier 2 | High bar — explicit + logged | Tier 3 access grant, bulk export of sensitive data, tombstone/delete of a service | Explicit consent + audit entry + cannot be reversed silently |

In v1 local trust mode, "user-visible confirmation" means a natural language statement from the agent before proceeding, giving the user an opportunity to decline. How this is surfaced in practice is open as Q014.

---

## Correction and Redress Model

The system must assume the agent will sometimes record things incorrectly. Therefore, the following operations must be available to the user via natural language (mediated by the agent through MCP tools):

| Operation | Description |
|---|---|
| Inspect | View current state of all domains and data |
| Amend | Correct a specific record |
| Dispute | Flag a record as incorrect without deleting it (preserves audit trail) |
| Deprecate | Mark a service as no longer in active use (preserves data) |
| Merge | Consolidate two services into one — future work |
| Tombstone | Mark a service as deleted whilst retaining the audit trail |
| Export | Full data export before deletion |
| Delete | Remove a service and all associated data; irrevocable; requires Tier 2 consent |

A memory system without correction and redress is not mature enough for durable use beyond development contexts.

---

## Minimum Governance Standard for Early Prototypes

Any AIPCS prototype deployed with real users (not solo development) must satisfy all of the following:

1. Audit log exists and produces entries for all 8 auditable actions
2. Schema Validator enforces structural constraints before any materialisation
3. User can list all domain services (`aipcs_service_list`)
4. User can export any domain service (`aipcs_service_export`)
5. User can delete any domain service and all associated data
6. Sensitive column declarations are surfaced to the user before materialisation
7. Tier 3 access grants are visible in `aipcs_service_list` output and in the audit log

Without these seven requirements, the prototype should not be treated as a reference implementation. It may be useful for exploration, but it should not be presented as evidence that AIPCS is governed.

---

## Portability and Runtime Constraints

The governance model must not assume all runtimes behave identically. Therefore:

- Dynamic tool registration should have a documented fallback (session reconnect is v1)
- Compaction-trigger hooks are optional — the governance model does not depend on them
- Local trust mode must be explicitly marked as non-production
- Cross-client portability is a testable property, not an assumption — see RQ6 in `docs/quality/evaluation-plan.md`

---

## Open Questions

| Q | Question |
|---|---|
| Q012 | Can a validator reliably detect whether a proposed schema is semantically appropriate for its declared domain? |
| Q013 | How should the Schema Validator detect PII/credential column names automatically? |
| Q014 | In v1 local trust mode (no UI), how is user consent for materialisation surfaced? |

See `docs/quality/technical-debt.md` for status.

---

## References

- BUILD_JOURNAL Entry 009
- [ADR-001-governance-model.md](decisions/ADR-001-governance-model.md)
- [boundaries.md](boundaries.md)
- [claims-and-scope.md](claims-and-scope.md)
