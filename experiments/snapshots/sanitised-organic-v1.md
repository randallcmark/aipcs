# Snapshot: sanitised-organic-v1

## Purpose

Provide an organic-shaped AIPCS corpus for bootstrap, service-selection, recall, stale-authority, and multi-domain utility experiments without exposing the private raw corpus.

## Source

- Source data directory: private local `/Users/markrandall/GitHub/aipcs-server/.data`
- Source date: 2026-06-11
- Created by: deterministic sanitisation script at `experiments/runbooks/sanitise-aipcs-corpus.py`
- Sanitized: yes

## Contents

| Service | Domain class | Non-history records | Entities |
|---|---:|---:|---|
| `aipcs_development` | `software_development` | 27 | decision, deferred_item, implementation_note, implementation_slice, open_question, session |
| `claude_memory` | `agent_memory` | 45 | feedback_memory, project_memory, reference_memory, user_memory |
| `cooking` | `personal_culinary` | 91 | dietary_constraint, meal_log, pantry_staple, recipe |
| `health_fitness` | `health` | 90 | appointment, body_metric, health_event, workout |
| `household` | `home` | 34 | maintenance_task, possession, provider, supply |
| `media_learning` | `media` | 48 | highlight, media_item |
| `people` | `personal_crm` | 51 | contact, follow_up, gift_idea, interaction, key_date |
| `personal_finance` | `finance` | 34 | account, budget_note, purchase, subscription |
| `personal_preferences` | `user` | 37 | preference |
| `technical_knowledge` | `software_development` | 38 | command, gotcha, snippet, tool_config |
| `travel` | `travel` | 40 | lodging, place, travel_pref, trip |

Total non-history records: 535.

## Expected Properties

- Multi-service corpus with realistic agent-authored service boundaries.
- Mixed domain sensitivity classes represented through fictional content.
- Fresh SQLite output files created from schema and synthetic inserts, not copied from raw databases.
- Synthetic owner ID: `lab`, matching the current lab compose `AIPCS_OWNER_ID`.
- SQLite endpoints use container paths under `/data/services`, matching the current lab compose mount.
- Sanitised service IDs are deterministic UUIDv5 values derived from private source IDs.
- History tables are retained for volume and lifecycle shape, but before/after payloads are synthetic placeholders.

## Known Defects / Intended Stimuli

- The corpus is useful for realistic discovery shape, but not for measuring exact recall against the original private facts.
- Some generated values are intentionally generic; this may reduce semantic richness compared with raw interaction-derived records.
- The snapshot can test service selection, cross-domain relevance, and payload behavior before it tests nuanced user-specific recall.
- It should be followed by a stronger synthetic authoring pass if the experiment needs subtle narrative facts with known ground truth.

## Raw Artifact Location

Do not commit or publish the raw source corpus. A private backup exists on NAS.

```text
Private source: /Users/markrandall/GitHub/aipcs-server/.data
Generated local snapshot: experiments/snapshots/sanitised-organic-v1-data/.data
```

## Reproduction Notes

Generate:

```bash
python3 experiments/runbooks/sanitise-aipcs-corpus.py \
  --source-data /Users/markrandall/GitHub/aipcs-server/.data \
  --output-data /Users/markrandall/GitHub/aipcs/experiments/snapshots/sanitised-organic-v1-data/.data \
  --owner-id lab \
  --force
```

Validate:

```bash
python3 -m py_compile experiments/runbooks/sanitise-aipcs-corpus.py
bash scripts/validate-harness.sh
```
