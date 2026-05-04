# Technical and Conceptual Debt

## Active Debt

| ID | Area | Problem | Impact | Suggested Resolution | Status |
|---|---|---|---|---|---|
| Q001 | Trigger model | CLI vs sidecar vs skill — how does the agent trigger instantiation? Partially resolved: sidecar Option 4 for v1, but the skill/prompt trigger (Model B proactive) is not yet designed | v1 must rely on explicit user request; proactive triggering (the full pattern vision) is deferred | Design the schema design prompt and recognition heuristics for Model B | Open |
| Q002 | Schema versioning | No defined format for schema versions in the service manifest — what travels with the service when it evolves? | Cannot safely evolve a deployed service's schema without migration risk | Define manifest format: version field, schema hash, migration log | Open |
| Q003 | Service registry | No mechanism for an agent to discover what memory services already exist for a user | Agent may instantiate duplicate services or fail to reuse existing memory | Design a service registry API on the sidecar; define the discovery protocol | Open |
| Q004 | Multi-agent locking | No locking model defined for concurrent access to the same instantiated service by multiple agents | Risk of write conflicts and data corruption in multi-agent scenarios | Define locking strategy: optimistic vs pessimistic; SQLite WAL mode may be sufficient for v1 | Open |
| Q005 | Schema conflict resolution | No policy for what happens when an agent proposes a schema change that conflicts with the existing schema | Agent evolution proposals could break existing queries or consumers | Define conflict resolution rules: additive-only evolution for v1, explicit migration for breaking changes | Open |
| Q006 | Portability | No export/import mechanism for schemas and data between deployments | Users cannot migrate their AIPCS memory between environments (e.g., local dev to hosted) | Define a portability format: schema manifest + data dump | Open |

## Cleanup Rules

- Close an entry when the question is resolved — add the resolution and link to the BUILD_JOURNAL decision
- Don't let resolved questions sit as open debt
- If a question keeps being asked, promote the answer into a harness doc rule
- Record any new conceptual or technical gaps discovered during the build
