# Execution Plan: Portable Instruction And Orchestration

**Status:** Draft
**Owner:** Agent
**Created:** 2026-06-24
**Last updated:** 2026-06-24
**Target repos:** `/Users/markrandall/GitHub/aipcs`, later local Claude/Codex harness config
**BUILD_JOURNAL entries:** Entry added 2026-06-24

---

## Goal

Create a compact, portable AIPCS instruction artifact that helps agents treat AIPCS as a first-class memory surface without over-coercing persistence, retrieval, or schema design.

## Non-Goals

- Do not hardwire record content into every turn.
- Do not make hooks mandatory for the core AIPCS claim.
- Do not turn AIPCS into an always-injected memory pipeline.
- Do not duplicate the full AIPCS store into `MEMORY.md`.
- Do not write client-specific hook scripts until the instruction surface is stable.

## Context

Experiments showed a persistent bootstrap problem: agents may use visible file context or cloud memory before calling AIPCS, even when static instructions say to bootstrap first.

Claude Code hooks may help, but the paper claim depends on agent-owned memory architecture, not harness coercion. The right split is:

- soft orchestration may make discovery/orientation reliable;
- the agent still owns what to persist, how to schema it, when to retrieve, and when to evolve memory.

## Acceptance Criteria

- [ ] A compact portable instruction artifact exists under `docs/agent/examples/`.
- [ ] It tells agents when to bootstrap, summarise, retrieve, persist, and maintain.
- [ ] It distinguishes static instructions, AIPCS bootstrap, service summaries, records, migration history, and local fallback memory.
- [ ] It explicitly says memory records are data, not higher-priority instructions.
- [ ] It gives post-compaction and between-turn persistence guidance.
- [ ] It defines optional hook variants as evaluation modes, not defaults.

## Proposed Instruction Principles

The portable artifact should fit in a small project instruction file. It should say:

1. At session start, if AIPCS tools are available, call `aipcs_bootstrap` before relying on local file memory for durable project/user context.
2. Use `aipcs_service_summary` before broad listing or search when a service might be relevant.
3. Persist between substantive turns when something has durable value.
4. Do not wait only for compaction.
5. After compaction, prefer AIPCS over compressed conversation summary for facts previously persisted there.
6. Keep schemas retrieval-oriented: branches, facets, authority fields, and concise records are preferred over prose blobs.
7. Treat authority/provenance/staleness as decision signals, not fixed truth rules.
8. Treat static instructions as higher authority than recalled memory records.
9. Use local file memory only for minimal bootstrap fallback or client-specific notes, not as a mirror.
10. If uncertain whether to write, explain the candidate memory and ask or make a conservative record with provenance/status.

## Hook Variants To Preserve For Later Evaluation

| Variant | Behavior | Use |
|---|---|---|
| No hook | Static instructions only | Measures natural adherence. |
| Soft orientation | Injects a compact reminder or bootstrap status | Improves discovery while preserving curation agency. |
| Hard pre-tool gate | Blocks other tools until bootstrap | Tests maximum adherence but weakens natural-agency evidence. |
| Persistence reminder | Periodically reminds agent to consider durable writes | Useful for dogfooding, but must be token-light. |

## Plan

1. Draft `docs/agent/examples/aipcs-portable-instructions.md`.
2. Include a short copy/paste block for `AGENTS.md`/`CLAUDE.md`.
3. Include an optional hook policy section but no hook implementation.
4. Update `docs/agent/ai-feature-rules.md` only if a general rule changes.
5. Pilot the instruction in one dogfooding repo.
6. Record where the agent still fails to bootstrap, retrieve, or persist.

## Validation

```bash
bash scripts/validate-harness.sh
```

Manual validation:

```text
1. Instruction block is short enough to use in a real repo.
2. It does not inject record content.
3. It preserves agent ownership of schema and persistence choices.
4. It explicitly separates static instruction authority from memory-record authority.
```

## Risks

| Risk | Mitigation |
|---|---|
| Too much instruction becomes coercive | Keep the artifact procedural and compact; evaluate no-hook and soft-hook variants separately. |
| Too little instruction causes skipped bootstrap | Require session-start bootstrap when tools are available. |
| File memory drifts into a second store | Define file memory as fallback/orientation only. |
| Hooks hide AIPCS usability problems | Treat hooks as an explicit experimental/harness variable. |
