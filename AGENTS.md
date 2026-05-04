# AIPCS Agent Routing Map

Read this file first. It routes you to the right documentation for any task.

Then read [docs/agent/index.md](docs/agent/index.md) for operating rules.

---

## Task Routes

| What you're doing | Start with |
|---|---|
| Understanding the project | [docs/product/research-brief.md](docs/product/research-brief.md) |
| Pattern / architecture work | [docs/architecture/index.md](docs/architecture/index.md) |
| Formal decision record (ADR) | [docs/architecture/decisions/template.md](docs/architecture/decisions/template.md) |
| AI pattern / prompt design | [docs/agent/ai-feature-rules.md](docs/agent/ai-feature-rules.md) |
| Security considerations | [docs/agent/security-rules.md](docs/agent/security-rules.md) |
| Complex task planning | [docs/exec-plans/template.md](docs/exec-plans/template.md) → create in `active/` |
| Paper work | [docs/agent/paper-rules.md](docs/agent/paper-rules.md) + [paper/outline.md](paper/outline.md) |
| Journaling a decision or milestone | [journal/BUILD_JOURNAL.md](journal/BUILD_JOURNAL.md) |
| Validation | [docs/agent/validation.md](docs/agent/validation.md) |
| Quality / debt review | [docs/quality/technical-debt.md](docs/quality/technical-debt.md) |
| Doc maintenance | [docs/agent/doc-maintenance.md](docs/agent/doc-maintenance.md) |
| Understanding development sequence | [docs/roadmap/implementation-sequencing.md](docs/roadmap/implementation-sequencing.md) |

---

## Operating Rules (short form)

- Don't invent facts about the AIPCS pattern — the spec documents and journal are authoritative
- Don't make broad changes without an execution plan for complex work
- Add a BUILD_JOURNAL entry for every non-trivial decision or milestone
- Include a "Paper notes" field in every journal entry — it feeds the arXiv paper
- Run `bash scripts/validate-harness.sh` before completing any task
- Treat the BUILD_JOURNAL as the primary narrative record; treat harness docs as the reference layer
- When stuck or confused, improve the harness rather than just pushing through

---

## First Time in This Repo?

1. Read this file (done)
2. Read [CLAUDE.md](CLAUDE.md) for project overview and repo structure
3. Read [docs/product/research-brief.md](docs/product/research-brief.md) to understand what AIPCS is
4. Read [docs/architecture/index.md](docs/architecture/index.md) for the v1 technical design
5. Scan [journal/BUILD_JOURNAL.md](journal/BUILD_JOURNAL.md) decision log for context
6. Then start your task
