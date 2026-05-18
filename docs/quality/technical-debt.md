# Technical and Conceptual Debt

## Active Debt

| ID | Area | Problem | Impact | Suggested Resolution | Status |
|---|---|---|---|---|---|
| Q001 | Trigger model — Model B | Mechanism resolved (Option 3 / D007). Compaction hook defined (D006). Remaining open: full skill prompt design for proactive Model B recognition beyond compaction — when should the agent volunteer AIPCS without a user hint or compaction event? | v1 relies on explicit hint + compaction; fully autonomous proactive triggering is deferred | Design and test the Model B recognition heuristics; document in skill definition | Open (partial) |
| Q004 | Multi-agent locking | No locking model defined for concurrent access to the same Domain Service by multiple agents | Risk of write conflicts and data corruption in multi-agent scenarios | Define locking strategy: optimistic vs pessimistic; SQLite WAL mode may be sufficient for v1 | Open |
| Q005 | Schema conflict resolution | Additive-only evolution is implemented, but destructive conflicts, renames, type changes, and backfills remain undefined | Agent evolution proposals beyond additive changes could break existing queries or consumers | Keep v1 additive-only; define explicit confirmation and migration policy for breaking changes later | Open (partial) |
| Q007 | Seed payload | Minimum viable seed payload for `aipcs_service_seed` not yet defined in implementation terms | Defines the parameter schema and Registry DB seed record | Define: domain_name + domain_class + intent_description + timestamp. Validate against v1 technical design. | Open |
| Q008 | Seed TTL | Should seeds auto-expire if never materialised after N sessions? | Affects Registry DB design and cleanup logic | Decide: probably no TTL for v1 (seeds are cheap, loss of intent is costly) | Open |
| Q009 | Domain taxonomy — registry model | Should domain taxonomy be an open community registry or a curated set? | Affects domain_class validation rules and interoperability scope | Develop reference taxonomy alongside reference implementation; revisit registry model in v2 | Open |
| Q010 | Domain overlap in taxonomy | How to handle overlap — is "job_application" a subset of "career" or its own domain_class? | Affects schema manifest validation and agent guidance in skill | Define hierarchy rules: prefer broader class with specific domain_name; document in skill | Open |
| Q011 | Tier 3 access scope | Should Tier 3 elevated access be part of v1 spec or explicitly deferred to v2? | Affects authentication model scope and v1 implementation complexity | Architecture accommodates Tier 3 from v1 (`aipcs_service_export` exists); consent mechanism is the open question | Open |
| Q012 | Server-controlled fields | Server-managed field handling is clearer in record tools and schema evolution, but first-design manifests still represent these fields as attributes | Causes validation friction and encourages agents to route around the tool contract if filesystem access is available | Decide whether first-design manifests should continue listing server fields or move them into explicit metadata | Open (partial) |
| Q013 | Session bootstrap | Agents need an obvious session-start way to learn existing seeded/materialised domains | Without this, agents duplicate domains or only use AIPCS when the user explicitly reminds them | Define session-start skill wording and either enrich `aipcs_service_list` or add a dedicated bootstrap tool | Open |
| Q026 | Session-start retrieval discipline | Bootstrap exposes memory shape but agents may fail to retrieve critical low-cardinality content such as user identity or behavioral rules | Agent can falsely claim not to know persisted facts even though bootstrap showed where they are | Define skill guidance and eval cases for bootstrap → bounded content retrieval | Open |
| Q027 | Bootstrap instruction layer | The dynamic bootstrap tool cannot trigger itself; agents need static AIPCS instructions at session start | User must keep telling the agent AIPCS exists before discovery happens | Package portable AIPCS skill/instructions for local Claude/Codex and later hosted clients | Open |
| Q028 | Common domain-class definitions | `domain_class` is useful for alignment, but no reference definitions exist for common use cases | Agents may create semantically overlapping top-level categories across systems | Define non-binding common domain classes with descriptions; avoid closed taxonomy enforcement in v1 | Open |
| Q029 | Procedural skills boundary | Some multi-step AIPCS workflows may be better stored as skills than tools, but the boundary is undefined | Risk of overloading atomic tools with workflow policy or storing procedures as ordinary records | Define criteria for tool vs skill vs record once recurring multi-step operations emerge | Open |
| Q030 | memhub baseline scope | `memhub` is a strong fixed-taxonomy/pipeline memory system, but running it as an experimental baseline could expand scope | Paper may under-characterise related work if ignored, or lose focus if too many baselines are added | Decide whether to cite only or run a bounded comparator scenario | Open |
| Q018 | Interpretation policy | No standard policy exists for weighting provenance, stale records, or old inferences | Different agents may apply inconsistent recall behavior | Put guidance in the AIPCS skill; keep deployment-specific thresholds configurable later | Open |
| Q019 | Bootstrap export | The minimum portable state for an agent that starts without a live AIPCS connection is undefined | Risk of dual-store drift between file memory and AIPCS content | Define bootstrap export as a shape/map only, not full content duplication | Open |
| Q022 | Session identity | It is unclear whether records should carry server-set or agent-set `session_id` | Session-aware retrieval and debugging need stable context without overfitting to one client | Decide after the first retrieval/search implementation | Open |
| Q024 | Tool boundary enforcement | Local development agents with filesystem access can bypass MCP tools and write SQLite directly | This undermines server-managed fields, auditability, validation, and security claims | Treat direct DB access as out-of-contract; isolate DB files in homelab/hosted deployments | Open |
| Q025 | Public MCP transport | Hosted ChatGPT/Claude-style clients may require publicly reachable MCP or a bridge, unlike local `stdio` clients | Roadmap can overestimate what local MCP proves for hosted clients | Keep local, homelab/private, and public-hosted transport phases distinct | Open |

## Resolved

| ID | Area | Resolution | Date |
|---|---|---|---|
| Q001 (mechanism) | Mechanism — CLI vs sidecar vs MCP-native | Option 3 selected: AIPCS as MCP-native primitive server. No CLI, no sidecar HTTP API. (D007) | 2026-05-04 |
| Q001 (compaction trigger) | Proactive trigger — compaction hook | Compaction identified as primary Model B trigger. Skill includes compaction hook guidance. (D006) | 2026-05-04 |
| Q002 | Schema versioning format | Schema manifest format defined in `docs/AIPCS_v1_Technical_Design.md` — versioned JSON, travels with the service, includes migration history. | 2026-05-04 |
| Q003 | Service registry / discovery | `aipcs_service_list` primitive + Registry DB in AIPCS Server. Agent calls list before seeding to avoid duplicates. | 2026-05-04 |
| Q006 | Portability | `aipcs_service_export` primitive (json / sqlite / schema_only / data_only / full) provides the portability primitive. Full cross-deployment import format TBD. | 2026-05-04 |
| Q014 | Search/retrieval shape | Dedicated `aipcs_record_search` uses exact structured filters only for the first retrieval slice. Partial text, fuzzy, FTS, embedding, and cross-service search are deferred. | 2026-05-18 |
| Q016 | Retrieval metadata | Retrieval responses from list/get/search return `_meta` with `computed_at`, `updated_age_seconds`, `updated_age_label`, and provenance when convention fields are present. | 2026-05-18 |
| Q017 | Provenance vocabulary | Recommended schema convention defined: `provenance_type`, `provenance_note`, `provenance_source`, with type values `user_stated`, `agent_inferred`, `agent_observed`, `imported`. | 2026-05-18 |
| Q021 | Bootstrap tool boundary | Dedicated `aipcs_bootstrap` selected for the first session-start shape surface instead of overloading `aipcs_service_list`. | 2026-05-18 |

## Cleanup Rules

- Close an entry when the question is resolved — add to the Resolved table with the decision reference
- Promote recurring questions into harness doc rules rather than leaving them as repeated debt
- Record any new conceptual or technical gaps discovered during the build
