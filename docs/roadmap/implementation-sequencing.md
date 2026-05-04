# Implementation Sequencing

## Current Phase: Harness Established (M001-M003 complete)

The pattern is documented. The harness is in place. The reference implementation work begins.

---

## Phase 1: v1 Technical Design (→ M004)

**Goal:** Complete the v1 architecture so the build has a clear target.

1. Finalize the schema design prompt — what does the agent receive, what must it produce?
2. Define the `service_instantiate` tool contract — input schema, output, error cases
3. Define the service manifest format (partially addresses Q002)
4. Define the sidecar HTTP management API surface
5. Create ADR for trigger model (Model A → Model B evolution path)
6. Record v1 design decisions in BUILD_JOURNAL (type: Milestone)

**Acceptance:** `docs/architecture/index.md` reflects the final v1 design with no TBDs.

---

## Phase 2: AIPCS Sidecar Prototype (→ M005)

**Goal:** A running sidecar that can receive a schema description and scaffold a FastAPI + SQLite service.

1. Set up sidecar project structure in Application Tracker Docker Compose
2. Implement HTTP management API: `POST /instantiate`
3. Implement SQLite schema generation from agent input
4. Implement FastAPI scaffolding around the schema
5. Implement dynamic MCP tool registration (services appear without restart)
6. Basic validation: schema in → running service → queryable via MCP

**Acceptance:** Manual end-to-end test: agent describes a domain → sidecar scaffolds → agent queries via MCP tool.

---

## Phase 3: OAuth / DCR Foundation (→ M006)

**Goal:** Consumer AI clients (Claude, ChatGPT) can authenticate via their user subscription — no separate API key required.

1. Implement OAuth 2.0 server in Application Tracker
2. Implement Dynamic Client Registration (RFC 7591)
3. Implement MCP scope model: which tools each client type can access
4. Test with a real consumer OAuth flow

**Acceptance:** A Claude.ai user can connect to Application Tracker MCP without a developer API key.

---

## Phase 4: First Agent-Designed Service (→ M007)

**Goal:** An agent successfully designs and instantiates a domain-specific MCP service, unprompted by developer schema.

1. Craft the Model A trigger recognition prompt
2. Build the schema design prompt (agent receives domain description, produces schema spec)
3. Wire the schema design output to `service_instantiate`
4. First test: career tracking domain (Application Tracker's own domain)
5. Record everything — token cost, latency, schema quality, surprises — in BUILD_JOURNAL §4 and §5

**Acceptance:** Agent designs a career tracking schema end-to-end; resulting service is queryable via MCP.

---

## Phase 5: Validation and Evaluation (→ M008)

**Goal:** End-to-end flow validated; evaluation data collected for the paper.

1. Run the full Application Tracker workflow with AIPCS memory
2. Compare with a hand-designed schema: what's different?
3. Test schema evolution — agent adds a field; does it migrate cleanly?
4. Collect metrics: token cost, latency, schema quality, failure modes
5. Document findings in BUILD_JOURNAL §5 (Evaluation)

**Acceptance:** BUILD_JOURNAL §5 has substantive evaluation notes; M008 milestone closed.

---

## Phase 6: Framework Extraction (→ M009)

**Goal:** AIPCS extracted as a general framework, independent of Application Tracker.

1. Identify all Application Tracker-specific assumptions in the sidecar
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
