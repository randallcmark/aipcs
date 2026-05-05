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
6. Implement Schema Validator — validate schema submissions against structural constraints (see governance.md §Structural Constraints)
7. Implement `aipcs_service_design` — accept schema, run validation, store manifest
8. Implement `aipcs_service_materialise` — SQLite init + FastAPI generation + dynamic MCP tool registration
8a. Implement `audit_log` table in Registry DB — all 8 auditable actions (see governance.md §Auditability Requirements)
8b. Implement sensitive-data column name heuristics in Schema Validator (heuristic pattern list in governance.md §Sensitive-Data Constraints)
8c. Implement v1 consent surface for materialisation — agent natural language confirmation before applying first materialisation or sensitive column addition (closes Q014)
9. Implement `aipcs_service_evolve` — additive migrations auto-applied; destructive with explicit user confirmation
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

## Phase 4b: Evaluation — Phase 1: Concept Validation (runs during Phase 4, triggers at M007)

**Goal:** Validate RQ1 (recognition) and RQ2 (initial design quality) with the career tracking scenario. Establish Baselines A and B.

1. Run scenario walkthroughs with and without explicit user hint — record recognition rate (RQ1)
2. Human quality review of agent-designed schema against Baseline B schema (RQ2 coverage and soundness)
3. Record session transcript, schema manifest, audit log, token cost (required artefacts per evaluation-plan.md)
4. BUILD_JOURNAL entry — evaluation run 1

**Acceptance:** Early success criteria 1 and 2 from evaluation-plan.md both pass.

---

## Phase 5: Evaluation — Phase 2: Governance Validation (→ M008)

**Goal:** Full Application Tracker workflow with AIPCS; governance effectiveness validation; evaluation data for the paper.

1. Run multi-session lifecycle: seed → materialise → evolve at least once (RQ3 evolution quality)
2. Run adversarial prompting suite — attempt schema injection, credential column addition, destructive migration without confirmation (RQ5 governance effectiveness)
3. Inspect audit log for completeness after each run
4. Compare end-to-end workflow with Baseline A on task continuation accuracy (partial RQ4)
5. Collect metrics: schema evolution frequency, token cost, latency; document in BUILD_JOURNAL

**Acceptance:** Early success criteria 3 and 5 from evaluation-plan.md both pass; no early failure conditions triggered; M008 milestone closed.

---

## Phase 5b: Evaluation — Phase 3: Portability Validation (overlaps Phase 6)

**Goal:** Validate RQ6 — export/import test in a clean environment.

1. Export a materialised domain service (full: schema + data + manifest + tool definitions)
2. Re-materialise the export in a clean Docker Compose environment
3. Verify all tools register and queries return expected results
4. BUILD_JOURNAL entry — evaluation run 3

**Acceptance:** Export artefact re-materialises cleanly; no early failure condition 5 triggered.

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

0. Run Evaluation Phase 4 (Comparative) — RQ4 comparative task tests across all three baselines (A, B, C). Generate paper §5 data. BUILD_JOURNAL entry — evaluation run 4.
1. Draft from `paper/outline.md` — all sections should be substantive by now; §5 populated from evaluation runs 1–4
2. Peer review from one trusted colleague
3. Format for arXiv (LaTeX or PDF)
4. Submit; record DOI in README and BUILD_JOURNAL
