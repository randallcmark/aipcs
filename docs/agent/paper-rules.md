# Paper Rules

The arXiv paper is a first-class output of this project. These rules ensure the build and the paper stay in sync.

## The journal–paper pipeline

Every BUILD_JOURNAL entry must include a **Paper notes** field. The question to answer in that field: *Would this appear in the paper? Which section? What does it illustrate?*

Raw journal notes accumulate per-section in the BUILD_JOURNAL under "Paper Sections — Running Notes." When a section is substantive enough, promote it to `paper/outline.md`.

## Paper sections and what feeds them

| Section | Source material |
|---|---|
| 1. Introduction | Journal milestones, motivation, the AIPCS irony (building without AIPCS) |
| 2. Background / Prior Art | Invention disclosure, BUILD_JOURNAL §2 running notes |
| 3. The AIPCS Pattern | Pattern spec (distilled), `docs/architecture/index.md` |
| 4. Reference Implementation | BUILD_JOURNAL §4 running notes, ADRs in `docs/architecture/decisions/` |
| 5. Evaluation | BUILD_JOURNAL §5 running notes — token cost, latency, failure modes, schema evolution |
| 6. Discussion | BUILD_JOURNAL §6 running notes — generalisability, security implications, future work |
| 7. Conclusion | Draft last |

## Writing conventions

- Target: **6–10 pages**, systems paper style
- Venue: arXiv first (free, immediate timestamp and DOI), then optionally HotOS / SOSP / AI systems workshop
- Tone: clear and precise, not breathless. The pattern stands on its own — don't oversell
- Prior art: cite all works in the invention disclosure; show clearly how each differs from AIPCS
- Claims: anchor every novelty claim to observable behaviour in the reference implementation

## When to write

- Don't wait until the build is done to start writing — the paper should grow with the build
- After each BUILD_JOURNAL entry, check if the paper notes belong in `paper/outline.md`
- The Introduction and Background sections can be drafted now from existing material
- Evaluation and Implementation sections require the build to be substantive

## Authorship

Author: Randall Mark. Date of conception: May 2026. Attribution via arXiv preprint; CC BY 4.0 for documents.
