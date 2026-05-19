# AIPCS Experiments

This directory holds controlled experiment scaffolding for AIPCS agent-led memory evaluation.

It is separate from the live `claude_memory` corpus. The live corpus is a naturalistic longitudinal store. Experiments here use isolated workspaces and copied memory snapshots so runs can be repeated and compared.

## Experiment Principles

- Do not run controlled experiments against the live AIPCS data directory.
- Start each run from a copied snapshot.
- Keep agent workspaces minimal so agents cannot inspect implementation internals unless the scenario explicitly tests boundary failure.
- Capture evidence outside the agent workspace.
- Treat direct SQLite edits as out-of-contract unless the scenario is explicitly testing boundary failure.
- Batch runs to respect token limits; prefer repeatable high-signal pilots over broad one-off coverage.

## Directory Map

| Path | Purpose |
|---|---|
| `scenarios/` | Scenario definitions, prompts, expected behavior, and scoring notes. |
| `workspace-templates/` | Minimal repo templates used to create isolated Claude/Codex workspaces. |
| `snapshots/` | Snapshot manifests and instructions. Actual copied SQLite data should usually stay out of git. |
| `runs/` | Per-run notes, trace pointers, scores, and post-run observations. |

## First Pilot

The first pilot should be intentionally small:

1. Use `workspace-templates/with-aipcs-instruction`.
2. Use a copied `evolved-natural` memory snapshot.
3. Run `scenarios/001_bootstrap_recall`.
4. Capture a curated run note from `runs/RUN_TEMPLATE.md`.
5. Compare Claude and Codex only if budget allows.

## Evidence Levels

| Level | Use |
|---|---|
| Journal observation | Design direction and exploratory notes. |
| Curated run note | Qualitative paper evidence and comparison across runs. |
| Raw transcript artifact | Strong support for exact tool-call sequence, wording, timing, or behavior claims. |

Raw transcripts may contain sensitive material. Prefer storing raw/private artifacts outside git and linking to them from curated run notes.
