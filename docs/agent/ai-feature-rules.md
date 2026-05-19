# AI Feature and Pattern Rules

This project IS an AI pattern. These rules apply to the design of AIPCS itself, to any prompt engineering done during the reference implementation, and to any AI-assisted work in this repo.

## Pattern design rules

- Treat the AIPCS pattern principles (P1–P10 in the pattern spec) as invariants — don't violate them without a spec change and a BUILD_JOURNAL entry
- The agent is the schema designer — any design that pre-defines the schema for the agent is not AIPCS
- Structured over semantic — AIPCS memory is queryable, not just semantically searchable; keep this distinction sharp
- MCP as the interface — the service must be MCP-native, not a proprietary API

## Prompt engineering rules

- Treat prompts, tool schemas, and agent instructions as code — version them in the repo
- Don't rely on undocumented or unverified model behaviour
- Validate at boundaries — the schema design prompt output must be parseable; build validation into the pipeline
- Make failure modes explicit: what happens if schema design fails, if the sidecar is unreachable, if tool registration is rejected?
- Record model choices, expected token cost, and latency implications in the BUILD_JOURNAL

## Required documentation for any substantial AI feature

- What behaviour is being elicited (goal)
- Which model and why
- Where the prompt lives in the repo
- Tool schemas and contracts
- How failures are handled
- Evaluation approach (even informal — "I tested X manually with Y inputs")

## Evaluation

- Deterministic tests for parsing, schema validation, and tool contracts
- Live-model tests only when credentials are available in the environment
- Record evaluation results in the BUILD_JOURNAL evaluation section — this material goes directly into the paper

## AIPCS session-start orientation

- Example thin instruction artifact: [examples/aipcs-persistent-memory-instruction.md](examples/aipcs-persistent-memory-instruction.md). Treat it as a starting point for Claude/Codex/hosted-agent variants, not a final spec.
- Codex CLI local MCP setup example: [examples/codex-cli-local-mcp.md](examples/codex-cli-local-mcp.md). Use this for local `stdio` experiments without public MCP exposure.
- AIPCS bootstrap has two mandatory layers:
  - Static agent instructions: what AIPCS is, when to seed, when to persist, and how to use the tools.
  - Dynamic service map: the current data-dictionary view of persisted domains, entities, counts, and descriptions.
- Bootstrap is orientation, not recall. It tells an agent which services and entities exist; it does not load working memory.
- The bootstrap map should help the agent know what information is likely to be found down each domain branch, including the seed intent and schematic approach where available.
- After bootstrap, agents must explicitly retrieve the records needed for the task or session role.
- For memory-like services, agents should prioritise low-cardinality identity, preference, feedback, behavioral rule, and project-state entities before answering questions about the user or project.
- Do not fetch every record from every service by default. Use bootstrap counts, entity names, and exact search/list operations to choose a bounded retrieval set.
- Treat invalid filters as hard failures. Do not silently strip invalid fields, because that can broaden recall and hide tool-contract mistakes.
- Agents should seed and persist when they judge information is likely to be useful in a future session, not only when the user explicitly requests memory.
- Prefer common top-level domain categories with stable definitions when they fit, but do not force all services into a closed taxonomy. Propose a new `domain_class` when the common categories do not describe the domain.
- Treat common domain classes as anchors, not constraints. Immutable externally registered seeds may exist later for application, vendor, IT, or compliance integrations, but that is a productisation control-plane case rather than the normal agent-owned memory pattern.
- Treat provenance, recency, and staleness as decision signals, not fixed scoring rules. The agent should weigh them in context with the user's goals and any explicit user correction.
- The agent may restructure, delete, split, merge, or reclassify its own memory through AIPCS tools when doing so preserves or improves future utility. Prefer bounded, explainable changes and preserve history where the tools provide it.
- Prefer agent-facing maintenance and discovery tools over automatic expiry. Administrative or compliance deletion belongs outside the ordinary agent tool surface, but should leave an audit/history signal visible to the agent where legally and operationally appropriate.
- Do not ban prose records. Prose is valid for rationale, notes, and emerging structure; avoid prose blobs when narrower fields would better support future retrieval.
- Multi-step procedures may later live as portable skills when they are better expressed as agent workflow than as atomic MCP tools. This is deferred and should not be confused with record content.

## AIPCS memory authority layers

- Keep static instruction files thin. They should make the agent aware of AIPCS, trigger bootstrap, and define broad persistence responsibilities; they should not become an evolving memory store.
- Use bootstrap for shape-only orientation: which services, entities, schemas, counts, and hints exist.
- Use service migration history to understand what schema changed and when.
- Use session records to preserve why important memory or schema changes were made. Session records should capture durable rationale, not full transcripts.
- Use feedback or memory-policy records for reusable behavioral rules about how to persist, retrieve, and maintain memory.
- When explaining or evaluating a schema change, combine migration history with relevant session records rather than relying on static instructions alone.

## Paper implications

Every significant prompt design choice, failure mode discovered, or evaluation result is potential paper material. Capture it in the BUILD_JOURNAL with a "Paper notes" field pointing to the Evaluation or Implementation section.
