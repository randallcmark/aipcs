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
| `run002` | Claude CLI | `001_bootstrap_recall` | `evolved-natural` | Test bounded recall against a controlled memory snapshot. |
| `run003` | Claude CLI | `001_bootstrap_recall` | same snapshot restored | Check repeatability against the same client. |
| `run004` | Codex CLI | `001_bootstrap_recall` | same snapshot restored | Compare tool-use discipline and recall behavior across clients. |
| `run005` | Claude CLI | `002_stale_memory_repair` | `stale` | Test repair once basic recall is proven. |
| `run006` | Claude/Codex TBD | `007_probe_spectrum` | seeded spectrum fixture | Test direct, inferential, nuanced, tangential, and null probes after mechanics are stable. |

## Evidence Levels

| Level | Use |
|---|---|
| Journal observation | Design direction and exploratory notes. |
| Curated run note | Qualitative paper evidence and comparison across runs. |
| Raw transcript artifact | Strong support for exact tool-call sequence, wording, timing, or behavior claims. |

Raw transcripts may contain sensitive material. Prefer storing raw/private artifacts outside git and linking to them from curated run notes.
