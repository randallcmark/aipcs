# Snapshot: gandhi-agent-authored-v1

Date: 2026-06-14

Purpose: Single-source Gandhi AIPCS corpus generated from Standard Ebooks source text.

Source:
- Mahatma Gandhi, The Story of My Experiments with Truth
- Repository: /Users/markrandall/GitHub/aipcs-sources/memoirs/mahatma-gandhi_the-story-of-my-experiments-with-truth_mahadev-desai

Generation rule:
The agent was asked to persist durable memory for future biographical, commemorative, and analytical writing tasks. It was allowed to choose its own service, schema, entity, and retrieval structure.

Observed structure:
- service: gandhi_autobiography
- entity: entry
- records: 58
- record types: phase, event, relationship, theme, value

Caveat:
No final exported Claude transcript was found for the Gandhi build. The corpus appears broadly complete from database inspection, but completion should be treated as inferred from record coverage rather than confirmed by an end-of-run audit.

Owner:
Generated locally as owner "mark". Lab imports must rewrite owner_id to "lab" and registry endpoints to /data/services/...
