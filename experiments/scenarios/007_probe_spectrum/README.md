# Scenario 007: Probe Spectrum And False Positives

## Purpose

Test memory performance across a spectrum of retrieval difficulty rather than only direct factual recall.

This scenario is not part of the first calibration run. It should be used after the clean runner, hosted MCP endpoint, reset process, and basic bootstrap/recall scenarios have been proven.

## Core Hypothesis

`agent-memory-v2` is structure-at-retrieval: it stores verbose interactions, then tries to retrieve relevant prior context later through fact extraction, similarity, and prompt injection.

AIPCS is structure-at-persistence: the agent decides what has durable value and designs schema/records around anticipated retrieval patterns.

The expected advantage of AIPCS should be most visible when relevant information is subtle, inferential, embedded among multiple topics, or absent but near related memories.

## Probe Levels

| Level | Type | Example Shape | Expected Stress |
|---|---|---|---|
| 1 | Explicit/direct | "What decision was made about X?" | Basic recall parity. |
| 2 | Inferential | "What approach did we take to Y?" | Requires mapping from wording to remembered rationale. |
| 3 | Nuanced/contextual | "How do I prefer to handle Z?" | Tests preference/style inference and provenance handling. |
| 4 | Tangential/referential | Fact embedded in a verbose off-topic turn. | Tests whether signal survives multi-topic interaction. |
| 5 | Null/false-positive | Ask about absent fact with nearby related memories present. | Tests whether system says "no relevant memory" instead of applying nearest-but-wrong context. |

## Fixture Requirements

- Ground-truth file created before seeding.
- Seed interactions include both short direct facts and long multi-topic turns.
- Some facts are intentionally omitted while related content is present.
- Probe questions are not shown to the agent during seeding.
- Pre/post memory snapshots are preserved.

## Scoring

| Dimension | Pass Signal |
|---|---|
| Direct recall | Correct answer grounded in retrieved/persisted memory. |
| Inferential recall | Correctly maps paraphrased question to relevant memory. |
| Nuanced recall | Uses provenance and avoids overclaiming subtle preference/inference. |
| Tangential recall | Recovers relevant detail from a multi-topic/verbose source interaction. |
| Null handling | Correctly reports absence or uncertainty; does not force nearest memory into answer. |
| False-positive resistance | Does not let irrelevant injected/retrieved context shape the answer. |

## Notes

False positives are first-class evidence. Injection-based systems can make irrelevant memories look important because the model is trained to treat prompt content as relevant. AIPCS should be measured on whether explicit retrieval and structured results help the agent reject absent or irrelevant memory.

