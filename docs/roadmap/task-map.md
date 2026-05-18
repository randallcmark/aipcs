# Task Map

Quick reference for where to start any type of work.

| Task type | Start with | Usually also update |
|---|---|---|
| Understand the project | [../product/research-brief.md](../product/research-brief.md) | — |
| Understand the v1 technical design | [../../docs/AIPCS_v1_Technical_Design.md](../../docs/AIPCS_v1_Technical_Design.md) | — |
| Pattern / architecture change | [../architecture/index.md](../architecture/index.md) | ADR, BUILD_JOURNAL, paper §3 |
| Reference implementation work | [../architecture/index.md](../architecture/index.md) + [../../docs/AIPCS_v1_Technical_Design.md](../../docs/AIPCS_v1_Technical_Design.md) | BUILD_JOURNAL §4, paper §4 |
| AI feature / prompt / skill design | [../agent/ai-feature-rules.md](../agent/ai-feature-rules.md) | BUILD_JOURNAL §5, paper §5 |
| Security change | [../agent/security-rules.md](../agent/security-rules.md) | ADR, technical-debt.md |
| Paper section work | [../agent/paper-rules.md](../agent/paper-rules.md) | [../../paper/outline.md](../../paper/outline.md) |
| Journaling | [../../journal/BUILD_JOURNAL.md](../../journal/BUILD_JOURNAL.md) | paper/outline.md if promoted |
| Complex task | [../exec-plans/template.md](../exec-plans/template.md) | CREATE in active/ |
| Quality review | [../quality/quality-score.md](../quality/quality-score.md) | technical-debt.md |
| Resolve open question | [../quality/technical-debt.md](../quality/technical-debt.md) | BUILD_JOURNAL, close Q-entry |
| Doc maintenance | [../agent/doc-maintenance.md](../agent/doc-maintenance.md) | Relevant harness doc |
| Validation | [../agent/validation.md](../agent/validation.md) | — |

## Milestone Tracker Cross-Reference

Milestones are tracked in the BUILD_JOURNAL. For quick reference:

| Milestone | Description | Status |
|---|---|---|
| M001 | Invention disclosure published | ✅ 2026-05-04 |
| M002 | Pattern spec v0.1 published | ✅ 2026-05-04 |
| M003 | Public GitHub repo live | ✅ 2026-05-04 |
| M004 | v1 technical design complete | ✅ 2026-05-04 |
| M005 | AIPCS Server prototype running | ✅ 2026-05-17 |
| M006 | OAuth/DCR foundation implemented | Pending |
| M007 | First MCP tool registered by agent | Partial 2026-05-17 |
| M008 | End-to-end flow validated in App Tracker | Pending |
| M009 | Framework extracted from app-specific code | Pending |
| M010 | arXiv preprint submitted | Pending |

## Current Implementation Priorities

The active prototype is `/Users/markrandall/GitHub/aipcs-server`.

| Priority | Why it matters | Planning source |
|---|---|---|
| Bootstrap/discovery surface | Agents need a map of seeded/materialised domains before probing. This supplements existing context rather than replacing it. | BUILD_JOURNAL Entries 018, 021, 022, 024 |
| Bootstrap instruction layer | The agent must know AIPCS exists and should call bootstrap without the user prompting it each session. | BUILD_JOURNAL Entries 026, 027 |
| Common domain-class guidance | Common categories need stable definitions for interoperability, but should not become a closed taxonomy. | BUILD_JOURNAL Entries 007, 027 |
| Search/retrieval | The prototype can write and mutate records; the next value test is whether agents can recall with exact structure before broader retrieval is added. | BUILD_JOURNAL Entries 018, 020, 024 |
| Retrieval enrichment | Provenance and relative time affect how an agent weights old memories. Provenance belongs in schema; relative time is computed at retrieval. | BUILD_JOURNAL Entries 020, 025 |
| Session-start retrieval policy | Bootstrap gives shape, not working memory; agents must retrieve bounded content from memory-like entities before claiming what they know. | BUILD_JOURNAL Entry 026 |
| Schema evolution | Additive V1 is implemented. Destructive migrations, renames, and backfills remain deferred. | BUILD_JOURNAL Entries 018, 020, 030, 031 |
| Bootstrap V2 data dictionary | Implemented locally. Bootstrap now includes schema summaries, attribute metadata, schema-fit hints, retrieval hints, and non-binding domain-class guidance without exposing record content. | BUILD_JOURNAL Entries 027, 030, 032 |
| Stale-memory repair evaluation | Live Claude trace showed the agent can detect stale persisted facts and update/delete memory through AIPCS. This should become an explicit evaluation scenario. | BUILD_JOURNAL Entry 033 |
| Deployment boundary | Local `stdio` is the development path; hosted Claude/ChatGPT require public MCP or a bridge later. Direct SQLite access is not the agent contract. | BUILD_JOURNAL Entries 018, 022 |
