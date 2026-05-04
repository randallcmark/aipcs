# AIPCS — Agent-Instantiated Persistent Context Services

This repository documents and develops the AIPCS pattern: a novel paradigm in which an AI agent autonomously designs its own domain-specific memory schema, scaffolds a persistent queryable service around it, and registers that service as an MCP tool — making structured memory available across sessions and across any MCP-compatible client.

## Project Goals

1. **Attribution** — publish an arXiv preprint establishing authorship of the pattern
2. **Reference implementation** — prove the pattern in Application Tracker, then extract as a general framework
3. **Open contribution** — CC BY 4.0 for documents, MIT for code; no commercial restriction

## Repository Structure

```
aipcs/
├── CLAUDE.md              — you are here
├── AGENTS.md              — task routing map for agents
├── README.md              — public-facing project description
├── docs/
│   ├── *.docx             — invention disclosure + pattern specification (Word)
│   ├── agent/             — agent operating rules and task protocol
│   ├── architecture/      — AIPCS pattern architecture and ADRs
│   ├── product/           — research brief and development journeys
│   ├── exec-plans/        — working plans for complex tasks
│   ├── quality/           — health scoring and technical/conceptual debt
│   ├── roadmap/           — task map and implementation sequence
│   └── references/        — source notes and engineering references
├── journal/
│   └── BUILD_JOURNAL.md   — chronological decision log, the primary narrative record
├── paper/
│   └── outline.md         — living paper structure, seeded from journal notes
└── scripts/
    └── validate-harness.sh — harness completeness check
```

## How to Work in This Repo

**Start here** for any task → read [AGENTS.md](AGENTS.md) to find the right docs for your work.

**Before starting complex work** → create an execution plan in `docs/exec-plans/active/`.

**Every significant decision or milestone** → add an entry to [journal/BUILD_JOURNAL.md](journal/BUILD_JOURNAL.md). This is the primary record. Include a "Paper notes" field on every entry — that material feeds the arXiv paper.

**When the pattern spec changes** → update `docs/architecture/` and add a Spec Change Log entry in the journal.

**When finishing any task** → run `bash scripts/validate-harness.sh` to verify harness integrity.

## Key Context

- **v1 architecture decisions** are recorded in [docs/architecture/index.md](docs/architecture/index.md)
- **Open research questions** are tracked in [docs/quality/technical-debt.md](docs/quality/technical-debt.md) (Q001–Q006)
- **Milestones** are tracked in the BUILD_JOURNAL milestone tracker (M001–M010)
- **Paper structure** lives in [paper/outline.md](paper/outline.md)
- The reference implementation is being built in Application Tracker (separate repo: `randallcmark/application_tracker`)

## Author

Randall Mark — May 2026
