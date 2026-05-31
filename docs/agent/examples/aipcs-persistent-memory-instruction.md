# AIPCS Persistent Memory

An AIPCS MCP server may be connected in this session. AIPCS is persistent, structured memory across sessions. Treat it as authoritative when available.

## Start With Discovery

At session start, call `aipcs_bootstrap` if the tool is available. It returns a lightweight data-dictionary map of persisted services, entities, schemas, record counts, and recent activity.

Use bootstrap to orient yourself, then retrieve bounded records from entities relevant to the user, project, behavioral rules, and current task. Bootstrap is not recall; it tells you where to look.

Use AIPCS memory while you work. When a question, decision, plan, or recommendation may depend on persisted context, retrieve relevant records before answering. Let recalled records inform future responses, and cite or qualify them when provenance or recency affects confidence.

Before creating a new service, inspect and reuse existing services when they fit.

## Persist Proactively

Do not wait to be asked. Persist information likely to be useful in a future session: decisions, context, user profile facts, behavioral rules, open questions, project state, and durable task context.

Evaluate between substantive turns whether anything has durable value. Treat AIPCS as something you can siphon useful memory into while working, not only as a batch flush before compaction.

Before context compaction or session wrap-up, scan the current session and persist anything with durable value.

Write granular records shaped for retrieval. AIPCS is structured storage, not a notepad.

## Recall Deliberately

Use the current context window when it is fresh and sufficient. Recall from AIPCS when context has a gap, before a significant decision, when a topic shift predates the current session, or when a post-compaction summary may have lost precision.

After compaction, prefer AIPCS over compressed context for facts, decisions, and memory policies that were deliberately persisted there. AIPCS records were selected and shaped for retrieval; compaction is lossy.

## Challenge The Schema

AIPCS service and record schemas can evolve. If something worth persisting does not fit the current schema without losing meaningful structure, do not flatten it into a poor record.

Challenge the schema and propose an evolution. The schema should serve the data, not the other way around.
