# AIPCS Experiments

This directory holds controlled experiment scaffolding for AIPCS agent-led memory evaluation.

It is separate from the live `claude_memory` corpus. The live corpus is a naturalistic longitudinal store. Experiments here use isolated workspaces and copied memory snapshots so runs can be repeated and compared.

## Experiment Principles

- Do not run controlled experiments against the live AIPCS data directory.
- Start each run from a copied snapshot.
- Keep agent workspaces minimal so agents cannot inspect implementation internals unless the scenario explicitly tests boundary failure.
- Run live-agent experiments from a clean runner VM clone, not from the operator's daily desktop environment.
- Prefer SSH and shell transcript capture over VM GUI copy/paste. GUI clipboard/SPICE behavior is too fragile to be part of the protocol.
- Keep Claude/Codex authentication out of the base runner image; authenticate only inside per-run clones.
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
| `runbooks/` | Step-by-step operator procedures for executing specific runs. |
| `environments/` | Clean runner and service substrate definitions. |

## First Pilot

The first pilot should be intentionally small:

1. Clone the UTM baseline runner described in `environments/utm-clean-runner.md`.
2. Use `workspace-templates/with-aipcs-instruction`.
3. Use the hosted empty AIPCS service as the starting snapshot.
4. Follow `runbooks/run001-empty-hosted-calibration.md` to run the empty-service calibration variant of `scenarios/001_bootstrap_recall`.
5. Capture a curated run note from `runs/RUN_TEMPLATE.md`.
6. Restore/copy an evolved snapshot only after the empty-service mechanics and reset process are proven.
7. Compare Claude and Codex only after a single-agent run proves the protocol.

## Initial Run Queue

| Run | Client | Scenario | Snapshot | Purpose |
|---|---|---|---|---|
| `run001` | Claude CLI | `001_bootstrap_recall` calibration variant | `empty-hosted` | Prove clean-runner + hosted MCP + transcript/run-note/reset workflow; first attempt captured in `runs/run001-empty-hosted-calibration-attempt-1.md`. |
| `run002` | Claude CLI | empty-store persistence formation | `empty-hosted` | Observe agent-owned service/schema formation from an empty store; captured in `runs/run002-empty-store-persistence-formation.md`. |
| `run003` | Claude CLI | cold-start snapshot recall/application | `run002-post` | Fresh VM clone against retained AIPCS data; successful recall/application captured in `runs/run003-cold-start-snapshot-recall-application.md`. |
| `run004` | Claude CLI | repeat cold-start snapshot recall/application | `run003-post` or restored `run002-post` | Check repeatability and whether schema evolution improves the next cold start; procedure in `runbooks/run004-repeat-cold-start-snapshot-recall.md`. |
| `run005` | Claude CLI | restored-snapshot repeatability | restored `run002-post` or `run003-post` | Check whether a fresh Claude session behaves similarly against the same AIPCS state; procedure in `runbooks/run005-to-run007-next-sequence.md`. |
| `run006` | Claude CLI | null / false-positive probe | retained or restored evolved snapshot | Test whether structured recall avoids overclaiming when related-but-wrong memory exists; procedure in `runbooks/run005-to-run007-next-sequence.md`. |
| `run007` | N/A or Claude/Codex TBD | comparator pack preparation | scenario artifacts | Convert the successful AIPCS flow into reusable prompts, ground truth, and scoring for later native/v2/Codex comparisons; procedure in `runbooks/run005-to-run007-next-sequence.md`. |

## Evidence Levels

| Level | Use |
|---|---|
| Journal observation | Design direction and exploratory notes. |
| Curated run note | Qualitative paper evidence and comparison across runs. |
| Raw transcript artifact | Strong support for exact tool-call sequence, wording, timing, or behavior claims. |

Raw transcripts may contain sensitive material. Prefer storing raw/private artifacts outside git and linking to them from curated run notes.
