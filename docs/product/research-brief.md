# Research Brief

## What is AIPCS?

Agent-Instantiated Persistent Context Services (AIPCS) is an early pattern for governed agent-directed structured memory, where an agent can propose and evolve persistence schemas under runtime validation instead of relying solely on developer-defined memory models.

More specifically: an AI agent, upon encountering a sufficiently complex stateful tracking problem, proposes a domain-appropriate relational schema, which a governed runtime validates and materialises as a persistent, queryable service, registered as MCP tools — making structured memory available across future sessions and any MCP-compatible client.

The key distinction from prior work: the agent proposes the structure of its own memory, subject to runtime governance. Memory is structurally queryable (not just semantically searchable). The schema can evolve under agent direction as domain understanding grows.

> **Working core claim:** "AIPCS is a constrained runtime pattern for agent-directed creation and evolution of structured persistent memory services." See `docs/architecture/claims-and-scope.md` for the full claims boundary.

## Who is this for?

| Audience | What they get from AIPCS |
|---|---|
| Researchers | A novel pattern at the intersection of cognitive architecture, MCP, and self-organising memory |
| Developers | A deployable framework for giving AI agents structured, domain-specific persistent memory |
| AI tool users | Applications built on AIPCS that let their AI assistant track complex domains without developer pre-configuration |
| Future agents | Persistent, queryable memory they designed themselves — structured context that survives session boundaries |

## Research Goals

1. **Attribution** — publish an arXiv preprint establishing authorship. Open contribution: CC BY 4.0 for documents, MIT for code.
2. **Reference implementation** — prove the pattern in Application Tracker (career management platform), then extract as a general open framework.
3. **Paper** — a 6–10 page systems paper suitable for arXiv and optionally HotOS / SOSP / AI systems workshop.
4. **Governance specification** — prove the "agent proposes, runtime governs" claim with a fully specified governance model and an adversarial evaluation suite (RQ5).

## Origin

AIPCS emerged from Application Tracker's MCP architecture, which solved a specific problem: job seekers who have consumer AI subscriptions but cannot afford developer API keys. The OAuth 2.0 + Dynamic Client Registration (DCR) model lets users bring their own Claude/ChatGPT subscription as the AI engine. While designing that, the insight emerged: the agent could design its own memory schema, not just use one. That's the generalised pattern.

## Non-Goals

- Commercial restriction — attribution only; no proprietary lock-in
- Pre-defining memory schemas — that is the anti-pattern AIPCS replaces
- Arbitrary database generation at agent direction — the agent proposes within governance constraints
- Unrestricted code generation by the agent — schema design and tool generation are in scope; general code generation is not
- Replacing an application's canonical source-of-truth — AIPCS is the agent's working memory, not the product's data model
- Permissionless persistence — governance is not optional; see `docs/architecture/governance.md`
- Bypassing the host application's own auth, consent, or audit requirements
- Building a UI product in this repo — this repo is the pattern spec + paper; the reference implementation lives in `application_tracker`
- Supporting every possible AI client — MCP-compatible clients only

## Open Research Questions

Tracked in full in [../quality/technical-debt.md](../quality/technical-debt.md) and the BUILD_JOURNAL.

| # | Question |
|---|---|
| Q001 | Trigger model: how does the agent recognise it needs AIPCS? (partially resolved: Model A for v1) |
| Q002 | Schema versioning format |
| Q003 | Service registry / how does the agent discover existing memory? |
| Q004 | Multi-agent locking model |
| Q005 | Schema conflict resolution |
| Q006 | Portability — export/import between deployments |

## Prior Art Summary

AIPCS sits at a gap in the landscape. See `docs/AIPCS_Invention_Disclosure_v2.docx` for the full survey.

| Prior work | How it differs from AIPCS |
|---|---|
| MemFabric | Self-organising but flat markdown files, not structured queryable schema |
| PISA | Academic cognitive architecture, not a deployable MCP-native pattern |
| Nemori | Self-organising experience memory, not agent-designed schema |
| MemGPT / Letta | Pre-defined storage structure; agent manages paging, not schema design |
| mcp-memory-service | Fixed knowledge graph schema; developer-defined |
| Hindsight | Semantic retrieval; developer-defined schema |
| SchemaAgent | LLM-driven schema generation for existing data, not persistent memory primitive |
