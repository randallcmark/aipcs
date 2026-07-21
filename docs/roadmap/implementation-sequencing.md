# Implementation Sequencing

## Current Transition: Research Record to Public-v1 Contract

The paper and research record remain first-class. Dogfooding also supports a bounded open-source
primitive-server v1 without turning the research claim into a production-superiority claim. The
public-v1 programme preserves private artefacts, freezes the generic-tool and compatibility contract,
adds truthful relational enforcement, SQLite/PostgreSQL storage ports, idempotency, lifecycle and
portable export/import, then adds an admin CLI, `uvx` packaging, public documentation, and late
maintenance-policy decisions.

Generated tools, per-domain FastAPI services, automatic seed expiry, aliases/classification counters,
dedicated merge/split, public remote MCP, OAuth/DCR, hosted tenancy, and homelab deployment are not
public-v1 release work. See `docs/architecture/public-v1-contract.md` and
`docs/exec-plans/active/public-v1-contract-synchronisation.md`.

---

## Current Phase: Paper Convergence And Agent-Led Evaluation

The pattern is documented, the harness is in place, and the standalone `aipcs-server`
prototype now proves the local MCP loop through service lifecycle, generic data operations,
bootstrap, exact retrieval, additive schema evolution, and deterministic evaluation fixtures.
The immediate priority is to collect evidence for the core hypothesis: context economy improves
when the agent can decide and evolve its own memory architecture. Hosting, hardening, OAuth/DCR, graph
stores, and generated domain-specific tools are productisation or future-substrate work unless
they directly support the evaluation.

---

## ✅ Phase 1: v1 Technical Design (M004 — complete 2026-05-04)

Key outputs:
- Two-state service lifecycle: SEEDED / MATERIALISED
- 8 management tool primitives defined (seed, design, materialise, evolve, list, inspect, suspend, export)
- Schema design requirements and validation rules
- Schema manifest format (versioned JSON with migration history)
- Schema evolution rules (additive-by-default, destructive with confirmation)
- AIPCS skill definition (Model A hint trigger + compaction hook Model B trigger)
- Three-tier access model designed
- Option 3 (MCP-native server) confirmed as mechanism

**Authoritative doc:** `docs/AIPCS_v1_Technical_Design.md`

---

## ✅ Phase 2: Local AIPCS Server Prototype (M005 — complete 2026-05-17)

**Goal:** A local MCP server with enough capability to test whether an agent can define and use its own memory patterns.

**Architecture:** standalone repo at `/Users/markrandall/GitHub/aipcs-server`; MCP `stdio`; SQLite registry and per-service domain databases.

Implemented locally:
- `aipcs_service_seed`, `list`, `inspect`, `design`, `materialise`
- generic record operations: `create`, `update`, `list`, `get`, `history`, `delete`
- additive schema evolution: `aipcs_service_evolve`
- structured validation errors with field path, code, message, remediation
- server-controlled owner/audit fields
- per-service SQLite materialisation and mutation history

Not yet complete:
- destructive schema evolution
- suspend/export
- generated FastAPI domain services
- dynamic domain-specific MCP tool registration
- remote/public MCP transport and auth

Research note: generated domain-specific MCP tools are no longer considered necessary for
the first paper proof. The current primitive tool surface is sufficient to test agent-owned
schema design, persistence, retrieval, and evolution. Generated tools remain a possible UX
layer once client restart/dynamic registration constraints are better understood.

**Evidence:** Claude CLI test with `claude-sonnet-4-6` created `claude_memory`, designed a schema, materialised it, and persisted records. See BUILD_JOURNAL Entries 018-022.

---

## Phase 3: Bootstrap, Discovery, And Retrieval Quality (current)

**Goal:** Make AIPCS usable at session start and useful at recall time without replacing native agent context mechanisms.

1. Add a bootstrap/discovery surface.
   - Return a lightweight map, not a content dump.
   - Include service id, domain name/class, state, seed intent, entity names, entity descriptions, record counts, and recent activity.
   - Treat the response as a data dictionary for persisted domains.
   - Let the agent decide what to probe next.
   - This also reduces semantic duplicate seeding without forcing a rigid taxonomy.

2. Add search/retrieval operations.
   - Start with structured exact search over known fields.
   - Keep arbitrary SQL out of the agent surface.
   - Consider text search after exact search if retrieval scenarios require it.
   - Treat semantic/vector search as a later infrastructure tier.

3. Add retrieval enrichment.
   - Return computed `_meta` alongside records where useful, especially persisted age.
   - Keep relative time computed at retrieval time, not stored.
   - Keep provenance as schema-level data because source/origin is durable.

4. Clarify the server-managed field contract.
   - Agents should understand that `id`, `owner_id`, timestamps, and tool provenance are server-owned.
   - Schema manifests can expose these fields as present but not normally writable.

5. Define session-start skill wording.
   - The skill should instruct agents to call bootstrap/discovery at session start when AIPCS is available.
   - The skill must explain AIPCS purpose and persistence triggers; the server map alone cannot trigger itself.
   - Existing agent context and compaction summaries still matter; AIPCS supplements them.

6. Define common domain-class guidance.
   - Provide stable definitions for common use cases.
   - Do not enforce a closed taxonomy in v1.
   - Use common categories to improve discovery and cross-agent alignment.

**Acceptance:** An agent can cold-start, discover the shape of existing AIPCS memory, choose a relevant service/entity, retrieve enriched records, and avoid duplicate domain creation in an unrehearsed scenario.

---

## Phase 4: Provenance, Temporal Semantics, And Schema Evolution

**Goal:** Capture memory origin and support changing schemas as agents learn better patterns.

1. Define provenance vocabulary. ✅ implemented in `aipcs-server` 2026-05-18
   - Recommended values: `user_stated`, `agent_inferred`, `agent_observed`, `imported`.
   - Recommended fields: `provenance_type`, `provenance_note`, `provenance_source`.
   - Provenance should be schema/query data, not only prompt policy.

2. Add retrieval-time temporal metadata. ✅ implemented in `aipcs-server` 2026-05-18
   - Compute `updated_age_seconds` and `updated_age_label` on retrieval.
   - Do not store relative time.

3. Add schema evolution.
   - Additive migrations first. ✅ implemented in `aipcs-server` 2026-05-18
   - Supports add entity, add optional attribute, add enum value, entity description update, and service intent update.
   - Use this to evolve `claude_memory` toward provenance-aware records.
   - Bootstrap V2 can follow without forcing rework because evolution depends on the current schema/materialisation contract, not on richer discovery hints.

4. Define interpretation policy in skill/prompt layer.
   - How to weight user-stated facts vs agent inferences.
   - How to treat stale memories.
   - When to re-verify old inferences.
   - How to encourage schema self-audit without causing arbitrary schema churn.

5. Decide whether session identity is a v1 field.
   - Useful for "last session" surfaces and debugging.
   - Requires a clean way for local and hosted agents to set or receive `session_id`.

**Completed plan:** `/Users/markrandall/GitHub/aipcs-server/docs/exec-plans/completed/schema-evolution-additive-v1.md`

---

## Phase 4b: Bootstrap V2 Data Dictionary

**Goal:** Improve the discovery map after schema evolution is underway, without making bootstrap a content retrieval surface.

1. Preserve the Bootstrap V1 boundary.
   - Bootstrap remains shape-only.
   - No record content.
   - No fuzzy/LIKE/vector search.

2. Add data-dictionary enrichment.
   - Include stronger service/entity descriptions and schema summaries. ✅ implemented in `aipcs-server` 2026-05-18
   - Surface schema convention support such as provenance fields. ✅ implemented in `aipcs-server` 2026-05-18
   - Include attribute metadata, schema-fit hints, and retrieval hints derived from schema/count metadata. ✅ implemented in `aipcs-server` 2026-05-18
   - Help agents decide whether to retrieve records or propose schema evolution.

3. Add common domain-class guidance.
   - Provide stable definitions for recurring use cases. ✅ implemented in `aipcs-server` 2026-05-18
   - Keep unknown domain classes valid.
   - Treat guidance as alignment support, not a closed taxonomy.

4. Keep session-start behavior split across two layers.
   - Static AIPCS instruction tells the agent to bootstrap and persist.
   - Dynamic bootstrap map tells the agent what currently exists.
   - Evolving rationale belongs in retrieved records such as session history, not in the static instruction or bootstrap payload.

**Completed plan:** `/Users/markrandall/GitHub/aipcs-server/docs/exec-plans/completed/bootstrap-v2-data-dictionary.md`

---

## Phase 5: Paper-Minimum Evaluation Package

**Goal:** Complete the research evidence package without drifting into productisation.

1. Keep the local Python/SQLite/MCP stack as the primary reference implementation.
2. Use deterministic `aipcs-server` evaluation fixtures to establish memory mechanics.
3. Run closely timed live-agent traces against Claude/Codex-style harnesses.
4. Compare against fixed-schema/pipeline memory (`agent-memory-v2`) at the level of architecture and behavior.
5. Run `agent-memory-v2` in two configurations where feasible: `v2-hybrid` as shipped, and `v2-schema-only` to isolate fixed-taxonomy behavior from semantic safety nets.
6. Add context-efficiency measurement: tokens spent to retrieve and apply relevant facts across a scenario or longer session.
7. Record vendor/model dates, visible model labels, prompts, tool surfaces, and transcripts.
8. Explicitly separate deterministic memory mechanics from live-agent behavior.
9. Treat graph databases, vector databases, homelab hosting, OAuth/DCR, public MCP, and generated domain tools as future work unless a specific evaluation question requires them.

**Acceptance:** The paper can make a bounded claim about context-efficient, agent-owned memory architecture and schema evolution using local evidence, without implying production readiness.

---

## Phase 6: Local-To-Hosted Deployment Path

**Goal:** Move from local `stdio` proof to durable service deployment without confusing prototype mechanics with hosted MCP constraints.

1. Keep local `stdio` as the development and Claude CLI path.
2. Containerise `aipcs-server` for homelab once the retrieval surface is useful.
3. Use QNAP/homelab for durable lightweight services, persistence, routing, and observability.
4. Do not rely on QNAP for heavy inference.
5. Treat hosted ChatGPT/Claude MCP as a separate transport/auth problem.
   - Hosted clients initiate from provider infrastructure.
   - Publicly reachable MCP or a bridge will be required.
   - Direct SQLite/file access is never part of the agent contract.

---

## Phase 7: OAuth / DCR Foundation (→ M006)

**Goal:** Consumer AI clients (Claude, ChatGPT) can authenticate via their user subscription — no separate API key required.

1. Implement OAuth 2.0 server in Application Tracker
2. Implement Dynamic Client Registration (RFC 7591)
3. Implement MCP scope model: which tools each client type can access
4. Test with a real consumer OAuth flow

**V1 note:** Phase 2 uses local trust within the Docker network. Phase 3 adds the production authentication model.

**Acceptance:** A Claude.ai user can connect to Application Tracker MCP without a developer API key.

---

## Phase 8: Agent-Led Evaluation (→ M007/M008)

**Goal:** Evaluate whether agents can use AIPCS memory effectively, not just whether tools function.

1. Use `agent-memory-v2` as the fixed-schema/pipeline baseline.
2. Use AIPCS as the agent-instantiated schema candidate.
3. Compare on shared scenario inputs and outcome-shaped artifacts, not identical internal pipelines.
4. Include write and retrieval scenarios.
5. Include stale-memory detection and repair scenarios.
6. Include schema self-audit scenarios where the agent reviews whether existing memory is granular, queryable, non-duplicative, and lifecycle-aware.
7. Include schema-rationale recall scenarios where the agent must explain why a schema changed by using migration history plus session records.
8. Measure schema design effort, adaptation latency, retrieval quality, correction behavior, duplicate-domain avoidance, context efficiency, and authority-boundary handling.
9. Check that agents do not mischaracterise local/homelab memory as inherently cloud-backed.
10. Keep memory mechanics separate from model/tool-use capability.

**Acceptance:** BUILD_JOURNAL and paper §5 contain agent-led traces that compare AIPCS with `agent-memory-v2` on both persistence and retrieval behavior.

---

## Phase 9: Framework Extraction (→ M009)

**Goal:** AIPCS extracted as a general framework, independent of Application Tracker.

1. Identify all Application Tracker-specific assumptions in the AIPCS Server
2. Extract as a standalone Python package / Docker image
3. Write integration guide
4. Open-source under MIT

---

## Phase 10: arXiv Submission (→ M010)

**Goal:** Paper submitted to arXiv.

1. Draft from `paper/outline.md` — all sections should be substantive by now
2. Peer review from one trusted colleague
3. Format for arXiv (LaTeX or PDF)
4. Submit; record DOI in README and BUILD_JOURNAL
