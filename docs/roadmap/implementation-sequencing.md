# Implementation Sequencing

## Current Phase: v1 Technical Design Complete (M001-M004 done)

The pattern is documented, the harness is in place, and the v1 technical design is complete. The AIPCS Server build begins.

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

## Phase 2: AIPCS Server Prototype (→ M005)

**Goal:** A running AIPCS MCP server with the 8 management primitives, capable of seeding, validating, materialising, and listing domain services.

**Architecture:** Option 3 — AIPCS is an MCP server. All management via MCP tool calls. No HTTP management API.

1. Set up AIPCS server project structure in Application Tracker Docker Compose
2. Implement Registry DB schema (services, seeds, manifests, migrations, audit_log tables)
3. Implement `aipcs_service_seed` — plant domain marker, write to Registry DB
4. Implement `aipcs_service_list` — return all seeded and materialised services with state
5. Implement `aipcs_service_inspect` — return schema manifest for a service
6. Implement Schema Validator — validate schema submissions against design requirements
7. Implement `aipcs_service_design` — accept schema, run validation, store manifest
8. Implement `aipcs_service_materialise` — SQLite init + FastAPI generation + dynamic MCP tool registration
9. Implement `aipcs_service_evolve` — additive migrations auto-applied; destructive with confirmation
10. Implement `aipcs_service_suspend` — deregister tools, preserve data
11. Implement `aipcs_service_export` — JSON / SQLite dump, schema_only / data_only / full

**Acceptance:** Manual end-to-end test: agent seeds a domain → accumulates knowledge → designs schema → materialises → queries via domain MCP tool.

---

## Phase 3: OAuth / DCR Foundation (→ M006)

**Goal:** Consumer AI clients (Claude, ChatGPT) can authenticate via their user subscription — no separate API key required.

1. Implement OAuth 2.0 server in Application Tracker
2. Implement Dynamic Client Registration (RFC 7591)
3. Implement MCP scope model: which tools each client type can access
4. Test with a real consumer OAuth flow

**V1 note:** Phase 2 uses local trust within the Docker network. Phase 3 adds the production authentication model.

**Acceptance:** A Claude.ai user can connect to Application Tracker MCP without a developer API key.

---

## Phase 4: First Agent-Designed Service (→ M007)

**Goal:** An agent successfully designs and instantiates a domain-specific MCP service via the AIPCS skill.

1. Finalise AIPCS skill definition — Model A hint trigger + compaction hook
2. Test skill with career tracking domain (Application Tracker's own domain)
3. Validate full flow: hint → seed → design → materialise → use → evolve
4. Record everything in BUILD_JOURNAL §4 and §5 — token cost, latency, schema quality, surprises

**Acceptance:** Agent designs a career tracking schema end-to-end; resulting service is queryable via MCP.

---

## Phase 5: Validation and Evaluation (→ M008)

**Goal:** Full Application Tracker workflow with AIPCS memory; evaluation data for the paper.

1. Run end-to-end Application Tracker workflow with AIPCS
2. Collect metrics: seed-to-materialise speed, schema evolution frequency, token cost, latency
3. Test compaction hook — does it surface domains that would otherwise be lost?
4. Compare agent-designed schema with hand-designed: what's different?
5. Document in BUILD_JOURNAL §5

**Acceptance:** BUILD_JOURNAL §5 has substantive evaluation notes; M008 milestone closed.

---

## Phase 6: Framework Extraction (→ M009)

**Goal:** AIPCS extracted as a general framework, independent of Application Tracker.

1. Identify all Application Tracker-specific assumptions in the AIPCS Server
2. Extract as a standalone Python package / Docker image
3. Write integration guide
4. Open-source under MIT

---

## Phase 7: arXiv Submission (→ M010)

**Goal:** Paper submitted to arXiv.

1. Draft from `paper/outline.md` — all sections should be substantive by now
2. Peer review from one trusted colleague
3. Format for arXiv (LaTeX or PDF)
4. Submit; record DOI in README and BUILD_JOURNAL
