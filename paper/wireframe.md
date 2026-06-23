# AIPCS Paper Wireframe

**Working title:** Agent-Instantiated Persistent Context Services: A Pattern for Agent-Owned Structured Memory

**Purpose:** This is the working paper skeleton. It fixes the argument, section flow, evidence placement, figures, and tables before polished prose is drafted.

**Status:** Drafting scaffold. Use this file to work section by section without drifting back into open-ended experimentation.

---

## Abstract

The abstract should be drafted last, but should cover five moves:

- Problem: agent memory is often developer-defined, opaque, prose-based, or retrieval-pipeline-driven.
- Contribution: AIPCS inverts this by allowing the agent to instantiate, query, and evolve its own structured persistent context services.
- Implementation: MCP-native reference server with seed, design, materialise, evolve, CRUD, bootstrap, summary, and inspect tools.
- Evidence: live-agent runs show schema formation, cross-session recall, stale repair, authority reasoning, bootstrap scaling lessons, and representation tradeoffs.
- Limitation: early qualitative systems evidence, not benchmark-level superiority.

## 1. Introduction

The introduction should establish context pressure as the systems problem: long-running agent work depends on context that is easy to lose, over-compress, over-inject, or retrieve imprecisely.

Existing memory approaches usually reinsert prose, summaries, embeddings, or developer-defined facts. AIPCS asks a different question: what happens if the agent owns the memory architecture?

Contributions:

1. The AIPCS pattern: agent-instantiated, structured, persistent context services.
2. An MCP-native reference implementation.
3. Live-agent evaluation showing creation, recall, repair, evolution, and comparison against alternative representations.
4. Design lessons and limitations for agent-owned memory.

## 2. Background and Related Work

Cover these classes:

- Markdown/project memory.
- Semantic/vector recall.
- `agent-memory-v2`.
- MemGPT/Letta-style memory tiering.
- MCP memory servers.
- Knowledge graphs.
- Schema-generation systems.

Core comparison table:

| System class | Who designs memory? | How recall works |
|---|---|---|
| Markdown memory | User or agent prose | Reread text |
| Semantic memory | Developer pipeline | Embedding recall and injection |
| Fixed-schema memory | Developer | Structured retrieval |
| AIPCS | Agent | Agent-authored structured services |

The key distinction is architectural: in most systems the LLM is downstream of memory architecture. In AIPCS, the LLM is upstream as schema architect.

## 3. The AIPCS Pattern

Explain AIPCS as a lifecycle:

1. Seed: the agent marks a domain as worth remembering before a schema exists.
2. Design: the agent proposes the memory shape.
3. Materialise: AIPCS creates a persistent service from the accepted schema.
4. Operate: the agent creates, lists, searches, retrieves, updates, deletes, and audits records.
5. Evolve: the agent changes the schema when use reveals better retrieval needs.

Important principles:

- Seed is first-class persistence intent, not a placeholder.
- Schema evolution is a memory act, not only database maintenance.
- Authority, provenance, staleness, and scope are part of durable memory quality.
- Memory topology matters: how the agent structures services affects later retrieval cost and quality.

Lifecycle figure:

```mermaid
flowchart LR
    A["Agent observes task or domain"] --> B["Seed memory intent"]
    B --> C["Design schema"]
    C --> D["Materialise service"]
    D --> E["Create and retrieve records"]
    E --> F["Evolve schema from use"]
    F --> E
```

## 4. Reference Implementation

Describe the implementation as a small MCP-native substrate:

- MCP server.
- Registry SQLite database.
- Per-service SQLite stores.
- Owner-scoped services and records.
- Primitive service lifecycle tools.
- Bootstrap, summary, and inspect discovery layers.
- Additive schema evolution.
- Record CRUD and history tools.

Tool surface table:

| Tool group | Tools | Purpose |
|---|---|---|
| Lifecycle | seed, design, materialise, evolve | Create and adapt services |
| Discovery | bootstrap, summary, inspect | Orient the agent |
| Records | create, list, search, get, update, delete, history | Operate memory |

Make clear that dynamic domain-specific tools are optional future UX. The tested minimum is the stable primitive tool surface.

## 5. Evaluation

Frame this as qualitative live-agent systems evidence. Avoid claiming statistical superiority.

Evidence arcs:

1. Empty-store formation: early runs showed agents creating user/project/meta memory services from scratch.
2. Cross-session recall: fresh sessions retrieved prior AIPCS records and changed behaviour accordingly.
3. Authority and conflict reasoning: runs showed scope, recency, provenance, clarity, and status weighting.
4. Bootstrap scalability: heavyweight bootstrap inhibited use; slim bootstrap improved payload and agent willingness to proceed.
5. Authored public corpus recall: public-domain memoir runs showed source-free composition from AIPCS memory, while revealing retrieval-affordance limits.
6. Close-out comparison: AIPCS, raw source, flat `MEMORY.md`, and vanilla model-prior conditions showed tradeoffs rather than categorical victory.

Evidence table:

| Evidence class | Result | Limitation |
|---|---|---|
| Schema formation | Agents created useful services | Tool contract friction appeared |
| Recall | Fresh sessions used AIPCS | Native/cloud memory confounds remain possible |
| Authority reasoning | Agents weighed provenance, recency, scope, and status | Mostly qualitative observations |
| Scaling | Slim bootstrap reduced payload and restored use | Service selection remains open |
| Corpus recall | Source-free generation was possible | Public data overlaps model priors |
| Comparators | Strong baselines clarified tradeoffs | No final `agent-memory-v2` head-to-head |

Close-out comparator table:

| Condition | Strength | Weakness |
|---|---|---|
| AIPCS integrated corpus | Durable topology, inspectable retrieval, efficient reuse | Quality depends on schema and retrieval choices |
| AIPCS heterogeneous merged corpus | Usable across independently authored services | More broad retrieval and scratch-work |
| Raw source packet | Best provenance and quote ceiling | Heavy answer-time source triage |
| Curated `MEMORY.md` | Strong one-file baseline | Upper-bound artifact, not ordinary incidental memory |
| Vanilla model knowledge | Strong synthesis on known topics | Weak bounded provenance and no corpus continuity |

## 6. Discussion

Core claim: AIPCS is not simply better prose memory. It is a way to preserve structured prior cognition.

Discuss:

- Memory topology as an output of agent cognition.
- Discovery UX as part of the memory system.
- Agent ownership as both strength and risk.
- Schema evolution as a response to repeated retrieval work.
- Git analogy: git preserves outcome; AIPCS can preserve process knowledge and retrieval-useful rationale.

Useful paragraph:

> The evaluation suggests AIPCS should be understood less as a replacement for source access or summaries, and more as a durable architecture for preserving agent-selected structure across sessions.

Risks:

- Poor schemas.
- Authority drift.
- Over-broad retrieval.
- Stale records.
- Privacy concerns.
- Token and tool overhead.

## 7. Limitations

State these plainly:

- Evidence is primarily Claude Code, with Codex experience informing the work.
- No final `agent-memory-v2` head-to-head comparison has been completed.
- Public memoir corpora overlap with model priors.
- Private organic memory was avoided for publishability and contamination control.
- Synthetic data sometimes biased agent behaviour.
- Scaling to very large, long-lived stores remains partly open.
- Cost/token evidence is qualitative.
- Hosted agent harnesses and native cloud memory are opaque and can change.

## 8. Future Work

Near-term:

- `agent-memory-v2` comparator.
- Larger corpora and long-running stores.
- Dogfooding once privacy and contamination risks are acceptable.
- Codex CLI harness validation.
- Richer memory dimensionality.

Optional arcs:

- Non-natural-language data, such as statistics, iterative measurements, and software development patterns.
- Implicit cross-data recall, such as synthetic health or physiology trend recall.
- Indirect references to third parties in user-centred work.
- Security, authentication, productisation, export, and consent workflows.

## 9. Conclusion

The conclusion should be modest and architectural:

- AIPCS is viable as a pattern.
- Agents can instantiate and evolve structured memory.
- Early evidence supports the value of agent-owned persistent services.
- The strongest contribution is not that AIPCS is empirically best, but that it makes memory architecture agent-owned, durable, inspectable, and evolvable.

## Figure and Table Checklist

1. AIPCS lifecycle diagram.
2. Architecture diagram: agent -> MCP -> registry -> services.
3. Related-work comparison table.
4. Tool surface table.
5. Evidence ladder table.
6. Close-out comparator table.
7. Limitations and future-work table.

