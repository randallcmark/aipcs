# Technical and Conceptual Debt

## Active Debt

| ID | Area | Problem | Impact | Suggested Resolution | Status |
|---|---|---|---|---|---|
| Q001 | Trigger model — Model B | Mechanism resolved (Option 3 / D007). Compaction hook defined (D006). Remaining open: full skill prompt design for proactive Model B recognition beyond compaction — when should the agent volunteer AIPCS without a user hint or compaction event? | v1 relies on explicit hint + compaction; fully autonomous proactive triggering is deferred | Design and test the Model B recognition heuristics; document in skill definition | Open (partial) |
| Q004 | Multi-agent locking | No locking model defined for concurrent access to the same Domain Service by multiple agents | Risk of write conflicts and data corruption in multi-agent scenarios | Define locking strategy: optimistic vs pessimistic; SQLite WAL mode may be sufficient for v1 | Open |
| Q005 | Schema conflict resolution | No policy for what happens when an agent proposes a schema change that conflicts with the existing schema | Agent evolution proposals could break existing queries or consumers | Define conflict resolution rules: additive-only evolution for v1 (already designed), explicit migration for breaking changes | Open |
| Q007 | Seed payload | Minimum viable seed payload for `aipcs_service_seed` not yet defined in implementation terms | Defines the parameter schema and Registry DB seed record | Define: domain_name + domain_class + intent_description + timestamp. Validate against v1 technical design. | Open |
| Q008 | Seed TTL | Should seeds auto-expire if never materialised after N sessions? | Affects Registry DB design and cleanup logic | Decide: probably no TTL for v1 (seeds are cheap, loss of intent is costly) | Open |
| Q009 | Domain taxonomy — registry model | Should domain taxonomy be an open community registry or a curated set? | Affects domain_class validation rules and interoperability scope | Develop reference taxonomy alongside reference implementation; revisit registry model in v2 | Open |
| Q010 | Domain overlap in taxonomy | How to handle overlap — is "job_application" a subset of "career" or its own domain_class? | Affects schema manifest validation and agent guidance in skill | Define hierarchy rules: prefer broader class with specific domain_name; document in skill | Open |
| Q011 | Tier 3 access scope | Should Tier 3 elevated access be part of v1 spec or explicitly deferred to v2? | Affects authentication model scope and v1 implementation complexity | Architecture accommodates Tier 3 from v1 (`aipcs_service_export` exists); consent mechanism is the open question | Open |
| Q012 | Governance — semantic validation | Can a validator reliably detect whether a proposed schema is semantically appropriate for its declared domain? Structural checks are insufficient for semantic correctness (critique finding #2). | Schema designs could pass the structural validator but be semantically wrong for the domain | Design a semantic validation layer — model-assisted or heuristic; document in governance.md §Semantic Constraints | Open |
| Q013 | Governance — sensitive-data column detection | How should the Schema Validator detect PII/credential column names automatically? Regex heuristics vs model-assisted? A v1 heuristic name pattern list exists in governance.md §Sensitive-Data Constraints. | Sensitive columns may be proposed without user notification if detection is incomplete | Start with the heuristic list in governance.md; test against adversarial prompting suite (RQ5) | Open |
| Q014 | Governance — v1 local consent surface | In v1 local trust mode (no UI), how is user consent for materialisation and sensitive column additions surfaced? Options: agent natural language statement, CLI confirmation prompt, audit log acknowledgement. | Consent model cannot be exercised without a consent surface; v1 governance minimum standard item 6 requires this | Decide and implement before any prototype is used for user evaluation | Open |
| Q015 | Evaluation — harness design | What does the evaluation harness look like? How are session transcripts, audit logs, and token costs captured systematically across evaluation runs? Without a harness, results cannot be compared. | Evaluation data collected without a harness cannot be retroactively structured | Design the harness as part of Phase 4 preparation; see evaluation-plan.md §Required Artefacts | Open |
| Q016 | Evaluation — schema quality rubric | What criteria define a schema as adequate for a domain? Human review for RQ2 and RQ3 requires a rubric. Without one, human review results are not comparable across evaluators or sessions. | RQ2 and RQ3 metric results are unreliable without a rubric | Draft rubric before first evaluation run (Phase 1); include in evaluation-plan.md or a linked document | Open |

## Resolved

| ID | Area | Resolution | Date |
|---|---|---|---|
| Q001 (mechanism) | Mechanism — CLI vs sidecar vs MCP-native | Option 3 selected: AIPCS as MCP-native primitive server. No CLI, no sidecar HTTP API. (D007) | 2026-05-04 |
| Q001 (compaction trigger) | Proactive trigger — compaction hook | Compaction identified as primary Model B trigger. Skill includes compaction hook guidance. (D006) | 2026-05-04 |
| Q002 | Schema versioning format | Schema manifest format defined in `docs/AIPCS_v1_Technical_Design.md` — versioned JSON, travels with the service, includes migration history. | 2026-05-04 |
| Q003 | Service registry / discovery | `aipcs_service_list` primitive + Registry DB in AIPCS Server. Agent calls list before seeding to avoid duplicates. | 2026-05-04 |
| Q006 | Portability | `aipcs_service_export` primitive (json / sqlite / schema_only / data_only / full) provides the portability primitive. Full cross-deployment import format TBD. | 2026-05-04 |

## Cleanup Rules

- Close an entry when the question is resolved — add to the Resolved table with the decision reference
- Promote recurring questions into harness doc rules rather than leaving them as repeated debt
- Record any new conceptual or technical gaps discovered during the build
