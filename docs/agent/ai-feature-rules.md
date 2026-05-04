# AI Feature and Pattern Rules

This project IS an AI pattern. These rules apply to the design of AIPCS itself, to any prompt engineering done during the reference implementation, and to any AI-assisted work in this repo.

## Pattern design rules

- Treat the AIPCS pattern principles (P1–P10 in the pattern spec) as invariants — don't violate them without a spec change and a BUILD_JOURNAL entry
- The agent is the schema designer — any design that pre-defines the schema for the agent is not AIPCS
- Structured over semantic — AIPCS memory is queryable, not just semantically searchable; keep this distinction sharp
- MCP as the interface — the service must be MCP-native, not a proprietary API

## Prompt engineering rules

- Treat prompts, tool schemas, and agent instructions as code — version them in the repo
- Don't rely on undocumented or unverified model behaviour
- Validate at boundaries — the schema design prompt output must be parseable; build validation into the pipeline
- Make failure modes explicit: what happens if schema design fails, if the sidecar is unreachable, if tool registration is rejected?
- Record model choices, expected token cost, and latency implications in the BUILD_JOURNAL

## Required documentation for any substantial AI feature

- What behaviour is being elicited (goal)
- Which model and why
- Where the prompt lives in the repo
- Tool schemas and contracts
- How failures are handled
- Evaluation approach (even informal — "I tested X manually with Y inputs")

## Evaluation

- Deterministic tests for parsing, schema validation, and tool contracts
- Live-model tests only when credentials are available in the environment
- Record evaluation results in the BUILD_JOURNAL evaluation section — this material goes directly into the paper

## Paper implications

Every significant prompt design choice, failure mode discovered, or evaluation result is potential paper material. Capture it in the BUILD_JOURNAL with a "Paper notes" field pointing to the Evaluation or Implementation section.
