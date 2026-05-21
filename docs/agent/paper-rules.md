# Paper Rules

The arXiv paper is a first-class output of this project. These rules ensure the build and the paper stay in sync.

## The journal–paper pipeline

Every BUILD_JOURNAL entry must include a **Paper notes** field. The question to answer in that field: *Would this appear in the paper? Which section? What does it illustrate?*

Raw journal notes accumulate per-section in the BUILD_JOURNAL under "Paper Sections — Running Notes." When a section is substantive enough, promote it to `paper/outline.md`.

## Evidence artifacts

The BUILD_JOURNAL remains the primary narrative record. Raw agent transcripts are supporting evidence artifacts, not the main working memory of the project.

Use three evidence levels:

| Level | Use |
|---|---|
| Journal observation | Design direction, hypotheses, roadmap choices, and development narrative |
| Curated transcript note | Paper examples and qualitative evaluation evidence |
| Raw transcript artifact | Citation-grade support for exact agent behavior, tool calls, timing, sequencing, and reproducibility |

When a live-agent session produces a notable behavior, preserve the raw transcript if available and create a curated note that records the date, agent/client/model label, instruction surface, available AIPCS tools, key behavior, selected excerpt or event sequence, paper relevance, and raw artifact pointer.

Do not bulk-ingest every transcript by default. Preserve raw transcripts selectively when the behavior may become part of an evaluation claim or paper example. For older observations without raw artifacts, treat the journal summary as valid design evidence but avoid overclaiming exact behavior unless the scenario is rerun under the current harness.

## Paper sections and what feeds them

| Section | Source material |
|---|---|
| 1. Introduction | Context economy framing, journal milestones, motivation, the AIPCS irony (building without AIPCS) |
| 2. Background / Prior Art | Invention disclosure, BUILD_JOURNAL §2 running notes |
| 3. The AIPCS Pattern | Pattern spec (distilled), `docs/architecture/index.md` |
| 4. Reference Implementation | BUILD_JOURNAL §4 running notes, ADRs in `docs/architecture/decisions/` |
| 5. Evaluation | BUILD_JOURNAL §5 running notes — context efficiency, token cost, latency, failure modes, schema evolution, comparator behavior |
| 6. Discussion | BUILD_JOURNAL §6 running notes — generalisability, security implications, future work |
| 7. Conclusion | Draft last |

## Writing conventions

- Target: **6–10 pages**, systems paper style
- Venue: arXiv first (free, immediate timestamp and DOI), then optionally HotOS / SOSP / AI systems workshop
- Tone: clear and precise, not breathless. The pattern stands on its own — don't oversell
- Primary framing: context economy first, statelessness second. Statelessness is a symptom; context-window pressure is the stronger systems problem.
- Primary contribution: LLM-upstream memory architecture. Developer-defined systems place the LLM downstream of memory; AIPCS places the LLM upstream as schema architect.
- Prior art: cite all works in the invention disclosure; show clearly how each differs from AIPCS
- Claims: anchor every novelty claim to observable behaviour in the reference implementation
- Evaluation framing: compare systems on shared scenario inputs and outcome-shaped artifacts; do not force identical internals when the upstream/downstream distinction is the independent variable.

## When to write

- Don't wait until the build is done to start writing — the paper should grow with the build
- After each BUILD_JOURNAL entry, check if the paper notes belong in `paper/outline.md`
- The Introduction and Background sections can be drafted now from existing material
- Evaluation and Implementation sections require the build to be substantive

## Authorship

Author: Randall Mark. Date of conception: May 2026. Attribution via arXiv preprint; CC BY 4.0 for documents.
