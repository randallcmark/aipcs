# Claims and Scope

> **Author:** Randall Mark — May 2026
> **Status:** Authoritative — all novelty language in the repo must be consistent with this document
> **BUILD_JOURNAL:** Entry 010
> **ADR:** [ADR-002-claim-narrowing.md](decisions/ADR-002-claim-narrowing.md)

---

> This document is the single authoritative statement of what AIPCS claims and what it does not. Where language elsewhere in the repo conflicts with this document, this document takes precedence.

---

## Working Core Claim

> **AIPCS is a constrained runtime pattern for agent-directed creation and evolution of structured persistent memory services.**

That is the claim we are currently prepared to defend.

## Safer External Framing

For use in the paper abstract, README, and any external presentation:

> **AIPCS is an early pattern for governed agent-directed structured memory, where an agent can propose and evolve persistence schemas under runtime validation instead of relying solely on developer-defined memory models.**

This framing is narrower, more defensible, and more accurate than "universal primitive" or "autonomous memory infrastructure."

---

## What AIPCS Claims

1. A structured alternative to brittle file/index/summary memory harnesses — relational schema, not flat files or key-value stores
2. A two-stage lifecycle (SEEDED → MATERIALISED) that makes persistence intent observable before schema design is complete — the seed is a first-class primitive
3. An agent-directed proposal model — the agent may propose memory structure; the runtime validates, constrains, and governs
4. A pattern in which memory structure can evolve under agent direction within explicit governance constraints
5. A portable, MCP-compatible control-plane surface — 8 management primitives accessible from any MCP-compatible client
6. A privacy-conscious, self-hostable orientation — user data under user control by default

---

## What AIPCS Does Not Yet Claim

1. That agent-proposed schemas are reliably high quality without runtime validation — schema quality depends on model capability; validation is required, not optional
2. That dynamic tool registration is universally supported across all MCP clients — session reconnect is the v1 fallback; some clients may not support live tool refresh
3. That AIPCS outperforms developer-defined schemas on any specific metric — this is an open research question (RQ2, RQ4 in evaluation-plan.md)
4. That compaction is the primary real-world trigger — it is a designed trigger; field evidence is pending (see D014)
5. That the 8 management primitives are the minimal or optimal primitive set — they are the v1 set; refinement is expected
6. That schema evolution in practice reliably follows the additive-only pattern — this is the design intent; field validation is RQ3
7. Cross-deployment portability of exported services — the export format is defined; re-import validation is RQ6 and not yet evaluated
8. Multi-agent coordination — locking model and conflict resolution are open questions (Q004, Q005)
9. That AIPCS is production-ready — it is a research pattern in active prototyping; the reference implementation is still being built

---

## Non-Goals

AIPCS is not, and does not claim to be:

- Arbitrary database generation at agent direction — the agent proposes within governance constraints, not freely
- Unrestricted code generation by the agent — schema design and tool generation are within scope; general application code generation is not
- A replacement for an application's canonical source-of-truth — AIPCS stores the agent's domain-specific working memory; it does not duplicate the host application's data model
- Permissionless persistence — governance is not optional scaffolding; it is part of the pattern definition
- A bypass around the host application's own auth, consent, or audit requirements — AIPCS operates within those requirements, not above them
- A general-purpose AI capability framework — scope is memory persistence specifically
- A solution for every domain — some domains (heavily regulated, canonical product state, highly structured existing schemas) are not appropriate AIPCS targets at this stage

---

## Scope Boundaries

### Control Plane vs Data Plane

AIPCS is primarily a **control-plane** pattern:

| Plane | Scope | Who owns it |
|---|---|---|
| Control plane | Recognise, seed, design, materialise, evolve, inspect, export | AIPCS Server + governance model |
| Data plane | Domain-specific tools and queries on materialised services | Agent (via dynamically generated MCP tools) |

AIPCS defines the control plane. The data plane is created by materialisation. Claims about AIPCS are claims about the control plane.

### Pattern vs Implementation

The AIPCS pattern is defined by the control-plane lifecycle and governance model. It is not defined by:
- SQLite (the v1 storage choice)
- FastAPI (the v1 service framework)
- Docker Compose (the v1 deployment topology)
- Dynamic tool registration (the v1 MCP interface mechanism)

Claims about the pattern survive even if these implementation choices change.

### Agent Autonomy vs Runtime Governance

"Agent-directed" does not mean "agent-controlled."

The agent **proposes**:
- Persistence structure
- Tool shapes
- Schema evolution

The runtime **governs**:
- Validates proposals
- Enforces constraints
- Requires confirmation where necessary
- Maintains the audit trail

This is not a subtle distinction. It is the core design principle that distinguishes AIPCS from unconstrained agent persistence. Any description of AIPCS that omits the governance layer misrepresents the pattern.

### Memory vs Canonical Product State

AIPCS is for the agent's domain-specific working memory — context that the agent accumulates across sessions that would otherwise be lost.

It is not intended to store the canonical state of a product's domain objects. If an application already has a `jobs` table, AIPCS should not replicate it. The boundary: AIPCS stores agent-instantiated memory and derived structured context; host applications remain the source of truth for canonical product entities unless explicitly designed otherwise.

---

## Open Claim Risks

The following are areas where existing language in the repo may still overreach. Address before paper submission.

1. **"Universal primitive"** — retired as of S002. Replace with "general-purpose pattern" until multi-domain generalisation evidence exists.
2. **MCP as primary novelty** — MCP is the chosen interface surface. It is not the novelty itself. The stronger claim is the governed agent-directed persistence mechanism. A description of AIPCS that leads with MCP misframes the contribution.
3. **"Autonomous" language** — avoid language that implies unconstrained autonomous operation. The correct framing is "agent-directed within governance constraints."
4. **Compaction as primary trigger** — "a designed Model B trigger" pending field validation. Do not claim it is the primary trigger until evaluation data supports that claim.

---

## References

- BUILD_JOURNAL Entry 010, D012, D014, S002
- [ADR-002-claim-narrowing.md](decisions/ADR-002-claim-narrowing.md)
- [docs/quality/critique-response.md](../quality/critique-response.md)
- [docs/quality/evaluation-plan.md](../quality/evaluation-plan.md)
