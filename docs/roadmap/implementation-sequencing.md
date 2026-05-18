# Implementation Sequencing

## Current Phase: Retrieval And Bootstrap Hardening

The pattern is documented, the harness is in place, and the standalone `aipcs-server`
prototype now proves the local MCP loop through service lifecycle and generic data operations.
The Claude CLI experiment on 2026-05-17 confirmed the concept has practical signal, but also
showed that discovery/bootstrap and retrieval quality are now the important next design surfaces.

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
- structured validation errors with field path, code, message, remediation
- server-controlled owner/audit fields
- per-service SQLite materialisation and mutation history

Not yet complete:
- schema evolution
- suspend/export
- generated FastAPI domain services
- dynamic domain-specific MCP tool registration
- remote/public MCP transport and auth

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
   - Additive migrations first.
   - Use this to evolve `claude_memory` toward provenance-aware records.

4. Define interpretation policy in skill/prompt layer.
   - How to weight user-stated facts vs agent inferences.
   - How to treat stale memories.
   - When to re-verify old inferences.

5. Decide whether session identity is a v1 field.
   - Useful for "last session" surfaces and debugging.
   - Requires a clean way for local and hosted agents to set or receive `session_id`.

---

## Phase 5: Local-To-Hosted Deployment Path

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

## Phase 6: OAuth / DCR Foundation (→ M006)

**Goal:** Consumer AI clients (Claude, ChatGPT) can authenticate via their user subscription — no separate API key required.

1. Implement OAuth 2.0 server in Application Tracker
2. Implement Dynamic Client Registration (RFC 7591)
3. Implement MCP scope model: which tools each client type can access
4. Test with a real consumer OAuth flow

**V1 note:** Phase 2 uses local trust within the Docker network. Phase 3 adds the production authentication model.

**Acceptance:** A Claude.ai user can connect to Application Tracker MCP without a developer API key.

---

## Phase 7: Agent-Led Evaluation (→ M007/M008)

**Goal:** Evaluate whether agents can use AIPCS memory effectively, not just whether tools function.

1. Use `agent-memory-v2` as the fixed-schema/pipeline baseline.
2. Use AIPCS as the agent-instantiated schema candidate.
3. Include write and retrieval scenarios.
4. Measure schema design effort, adaptation latency, retrieval quality, correction behavior, and duplicate-domain avoidance.
5. Keep memory mechanics separate from model/tool-use capability.

**Acceptance:** BUILD_JOURNAL and paper §5 contain agent-led traces that compare AIPCS with `agent-memory-v2` on both persistence and retrieval behavior.

---

## Phase 8: Framework Extraction (→ M009)

**Goal:** AIPCS extracted as a general framework, independent of Application Tracker.

1. Identify all Application Tracker-specific assumptions in the AIPCS Server
2. Extract as a standalone Python package / Docker image
3. Write integration guide
4. Open-source under MIT

---

## Phase 9: arXiv Submission (→ M010)

**Goal:** Paper submitted to arXiv.

1. Draft from `paper/outline.md` — all sections should be substantive by now
2. Peer review from one trusted colleague
3. Format for arXiv (LaTeX or PDF)
4. Submit; record DOI in README and BUILD_JOURNAL
