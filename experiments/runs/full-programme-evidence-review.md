# Full Programme Evidence Review

## Question

Do the experiments realistically provide enough data to publish a paper introducing AIPCS as a novel memory pattern for AI agents?

## Short Answer

Yes, for an arXiv / systems-position paper that introduces AIPCS as a novel agent-owned memory architecture and reports early qualitative systems evidence.

No, not for a paper claiming statistically demonstrated superiority over other memory systems, broad model-family generality, or benchmark-level performance gains.

The evidence is strongest for:

- feasibility of the AIPCS primitive;
- agent-authored service/schema formation;
- cross-session recall and behavior change;
- schema evolution and memory maintenance;
- authority/conflict reasoning;
- discovery/bootstrap design lessons;
- representational tradeoffs against source access, curated flat artifacts, and model priors.

The evidence is weaker or absent for:

- quantitative superiority over agent-memory-v2;
- large-scale organic deployment over months;
- non-narrative data domains;
- multi-model replication;
- rigorous token/cost accounting across all conditions.

## Appropriate Paper Claim

The defensible claim is:

> AIPCS is a novel memory pattern in which agents instantiate, query, and evolve their own structured persistent context services. Early live-agent experiments show that agents can create schemas, persist useful records, recover them across sessions, repair stale memory, reason over conflicting records, and reuse authored memory corpora for later tasks. The pattern introduces useful tradeoffs against raw source access, curated flat memory artifacts, and model-prior synthesis.

The paper should not claim:

> AIPCS is empirically superior to all other memory approaches, or consistently produces better outputs than raw source access, curated notes, or strong model priors.

## Evidence Coverage

| Evidence Area | Status | Primary Runs / Entries | Judgment |
|---|---|---|---|
| Infrastructure feasibility | Supported | `run001` | Hosted/private-network MCP and Claude CLI can operate AIPCS tools, though auth/config ergonomics are productisation issues. |
| Agent-owned schema formation | Supported | `run002`, journal Entry 018 | Agent created service boundaries and persisted records from an empty store. Tool-contract friction was real but recoverable. |
| Cross-session recall/application | Strongly supported | `run003`, `run026`, `closeout01`, `closeout04` | Fresh sessions used AIPCS state to orient and generate useful outputs without source files. |
| Schema evolution and self-maintenance | Supported | `run003`, journal Entries 033-035, `run013`, Kropotkin refinement | Agents can inspect schema/memory, detect stale or poor structure, and evolve it additively. |
| Autonomous persistence | Supported with caveats | `run012`, `run015`, `run016` | Agents did persist without direct record-by-record instruction, but live harness/model/auth confounds remain. |
| Weak-scaffold AIPCS activation | Supported | `run014`, `run024f`, close-out runs | Agents often reached for AIPCS naturally when it was available and relevant. |
| Authority/conflict reasoning | Supported | `run011`, `run015`, `closeout04` | Agents applied scope/provenance/status reasoning and avoided simple "newest wins" logic in controlled cases. |
| Bootstrap/orientation scalability | Mixed, but informative | `run018`-`run021`, `run019b`, `run020b` | Original bootstrap degraded under breadth/verbosity; slim bootstrap fixed payload friction but not all service-selection issues. |
| Organic-shaped corpora | Partially supported | `run024e`, `run024f` | AIPCS worked over sanitised organic shape, but shape-only sanitisation was semantically weak. |
| Authored public-domain corpus recall | Strongly supported | `run026`, `closeout01`, `closeout01b` | Public-domain agent-authored memory corpora supported source-free later generation. |
| Retrieval-affordance legibility | Mixed / negative evidence | `run027` | Memory utility held, but membership-filter affordances were not naturally discovered; this drove implementation improvements. |
| Comparator evidence | Moderately supported | `closeout02`-`closeout06` | Raw source, curated flat artifact, and vanilla model baselines are now represented. agent-memory-v2 remains untested in the final matrix. |

## Evidence Ladder

### 1. Calibration And Mechanics

`run001` proved that Claude CLI could connect to an AIPCS MCP server and operate the tool surface from a controlled VM. It also exposed early tool-schema friction and operational problems with UTM, SPICE, transcript capture, and authentication.

This is not recall-quality evidence, but it matters methodologically. It established the experiment harness and the need for better run isolation, transcript capture, and reset workflows.

### 2. Empty-Store Memory Formation

`run002` is one of the important early results. Starting from an empty store, Claude designed meaningful service boundaries:

- `user_context`
- `aipcs_project`
- `aipcs_meta`

It persisted records about the user, the project, and how to use AIPCS itself. This supports the pattern's central inversion: the agent is upstream of memory architecture, not merely downstream of a developer-defined schema.

Caveat: tool contract friction was substantial. The agent learned through failed calls and validation feedback. This is evidence for the pattern and also evidence that tool affordances matter.

### 3. Cross-Session Recall And Behavior Change

`run003` is direct evidence for AIPCS memory changing future behavior. A fresh environment with retained AIPCS state retrieved prior tool-use lessons and applied them before mutating the store. Claude inspected schemas, remembered primary-key/audit-field lessons, evolved services, migrated records, and persisted new lessons.

This is stronger than "the agent remembered a fact." It used structured prior memory to change operational behavior.

### 4. Agent-Led Maintenance, Stale Repair, And Schema Audit

Journal entries before the lab-run sequence record live Claude traces where AIPCS enabled:

- cold-start bootstrap orientation;
- bounded retrieval;
- stale persisted fact detection;
- update/delete repair;
- schema self-audit;
- duplicate-authority cleanup;
- rationale separation across static instructions, bootstrap, migration history, session records, and behavioral memory.

These traces are not as experimentally tidy as the later run notes, but they provide important capability evidence. They show AIPCS is not only a storage target; it is a substrate for memory maintenance.

### 5. Controlled Recall, Null, And Authority Probes

Runs `run011`-`run015` extended beyond simple recall:

- `run011` tested applicability: one active constraint applied, one scoped/null record declined, one historical record treated as background.
- `run012` observed autonomous persistence.
- `run013` tested schema evolution rather than flattening observations into notes.
- `run014` showed AIPCS activation under weaker scaffolding.
- `run015` tested stale/conflicting authority records, with reasoning over recency, provenance, clarity, status, and scope.

These runs matter because they test judgment over memory, not only retrieval. The evidence is positive, but some fixtures were self-disclosing or scaffolded, so they should be reported as qualitative live-agent evidence rather than hard benchmark proof.

### 6. Scalability And Discovery Failure

Runs `run018`-`run021` are essential negative evidence.

Original bootstrap behavior degraded under:

- service breadth (`run019`);
- schema verbosity (`run020`);
- record-volume-induced caution (`run021`).

The revised slim-bootstrap design then showed:

- `run019b`: payload friction fixed, but harsh service selection still failed;
- `run020b`: schema-verbosity friction fixed and target retrieval succeeded cleanly.

This is publishable implementation-learning evidence. It shows the pattern needs an efficient discovery tier. It also prevents overstating the system: AIPCS retrieval quality depends on bootstrap/service-summary affordances and branch-selection metadata.

### 7. Organic And Public-Domain Corpora

`run024e` and `run024f` showed AIPCS over a sanitised organic-shaped corpus. Agents used AIPCS naturally and downweighted semantically hollow placeholder records. That is useful authority behavior, but not strong recall-quality evidence.

`run026` is stronger: a public-domain Kropotkin corpus authored into AIPCS supported a fresh source-free writing task. The agent discovered the service, used summary/list tools, retrieved the compact corpus, and generated a nuanced essay grounded in AIPCS records.

`run027` is useful negative evidence: a thematic prompt did not cause the agent to use membership filters. The memory still supported the answer, but retrieval efficiency failed because filter semantics were not legible enough. This directly motivated retrieval-affordance improvements.

### 8. Close-Out Comparative Runs

The close-out batch adds the comparator layer:

- AIPCS integrated corpus works (`closeout01`).
- AIPCS heterogeneous corpus works but with more retrieval/scratch-work (`closeout01b`).
- Raw source remains the direct provenance and quotation ceiling (`closeout02`).
- A curated flat artifact is a very strong baseline (`closeout03`, `closeout05`).
- AIPCS handles discrimination/null probes (`closeout04`).
- Vanilla Claude can synthesize thematically without supplied memory, but lacks bounded provenance (`closeout06`).

This makes the evaluation credible because the baselines are not weak.

## What Is Now Well Supported

### AIPCS Is Novel As A Memory Pattern

The repo's research brief and related-work framing support a plausible novelty claim: AIPCS makes the agent responsible for instantiating and evolving the memory schema. The experiments then show that live agents can actually exercise that responsibility.

This is stronger than a conceptual proposal alone.

### AIPCS Can Support Cross-Session Structured Recall

`run003`, `run026`, `closeout01`, and `closeout04` provide multiple independent examples where retained AIPCS state shaped a later session.

### AIPCS Can Preserve More Than Facts

The evidence includes:

- tool-use lessons;
- schema rationale;
- retrieval guidance;
- project state;
- interpretive biographical structure;
- authority/status/scope metadata;
- decisions about what not to trust.

This supports the "prior cognition" framing.

### AIPCS Produces Useful Failure Signals

The experiments did not only pass. They exposed:

- tool contract friction;
- bootstrap payload overload;
- branch-selection failure;
- membership-filter legibility failure;
- synthetic corpus semantic hollowness;
- curated flat artifact strength;
- model-prior strength.

That makes the evaluation more credible.

## What Remains Under-Supported

### Quantitative Performance Superiority

There is no statistically meaningful sample size, no automated scoring pipeline across many tasks, and no model-family replication. The paper can include scored case studies, not benchmark superiority claims.

### Comparison Against agent-memory-v2

agent-memory-v2 is discussed and architecturally contrasted, but the final close-out evaluation does not execute the comparator. This is acceptable for a first AIPCS pattern paper if framed as related/future work. It is not acceptable if the paper claims AIPCS beats fixed-schema semantic memory systems.

This comparison should remain in the future plan. agent-memory-v2 is architecturally different: it uses developer-defined extraction, enrichment, semantic recall, and prompt injection. AIPCS is intended as an evolution of that class of system: the agent can create and adapt the data model as actual memory needs emerge, rather than relying on the designer to anticipate every extractor, fact class, and retrieval dimension.

### Long-Term Organic Use

The evidence includes multi-session traces and constructed corpora, but not months of real organic use by multiple agents. Claims about long-running ecosystem behavior should be phrased as expected/future work.

This limitation was partly a deliberate contamination-control choice. AIPCS was not fully dogfooded in the author's normal Claude/Codex workflows because those same agent harnesses were also the experiment subjects. Using AIPCS personally during the evaluation risked contaminating Claude cloud/native memory and biasing Codex behavior. A cleaner API-driven environment would have helped, but paid API usage was not financially practical for exploratory runs.

### Large-Scale Retrieval Robustness

Bootstrap scalability was tested, and weaknesses were found and partly fixed. However, service breadth selection remains an open issue. The paper should say AIPCS requires compact discovery and good service metadata; it should not claim solved scaling.

Larger corpora remain a work-in-progress arc. The evidence already shows the relevant pressure points: bootstrap payload size, branch selection, metadata quality, service topology, and whether agents choose bounded retrieval over broad extraction. The paper can invite external use and feedback cautiously, but should not imply the scaling story is complete.

### Cost/Token Economics

The experiments capture transcript sizes, tool calls, and qualitative overhead, but not a rigorous token-cost model. Claims about context economy should be cautious: AIPCS can reduce repeated source reading and improve bounded retrieval, but schema creation and maintenance have their own costs.

The practical bar is not "AIPCS is cheaper in every scenario." The practical bar is that AIPCS should not blow normal agent budgets, and that any added persistence/retrieval overhead should buy enough durability, precision, provenance, or reuse to justify it. Many real users already spend large context budgets on `AGENTS.md`, hooks, skills, MCP tools, and repository-specific rules; AIPCS should be evaluated against that broader configuration cost, not as a zero-overhead primitive.

### Data Sanitisation And Public-Corpus Bias

The experiment programme deliberately avoided publishing private personal memory data. Early synthetic corpora were useful for mechanics but could be leading, transparent to the agent, or semantically hollow. Sanitised organic-shaped data preserved service shape but weakened factual recall value. Public memoir corpora avoided privacy risk and created richer semantic memory, but overlapped with model training knowledge, which made vanilla Claude a strong baseline and weakened output quality as proof of AIPCS necessity.

This is not a fatal flaw. It is an expected tension for memory-system research: realistic memory often contains private data, while publishable datasets often need sanitisation or public-domain substitutes. The paper should state this explicitly. In real business or personal deployments, users may also need synthetic or redacted corpora when sharing evidence, precisely because persisted memories are likely to contain sensitive information.

### Harness Generalisation

The live-agent evidence is mostly from Claude Code, with Codex experience informing the design but not represented as a full controlled matrix. This is acceptable for a first paper because the contribution is a tool-mediated memory pattern, not a universal model-behavior benchmark. The claim should be bounded to MCP-capable agent harnesses with sufficient tool-use and schema-reasoning ability.

Future work can wire AIPCS into Codex CLI more directly now that the project is moving out of contamination-control mode. That would provide a useful second-harness validation without needing to claim universal generality.

## Objective Publication Readiness

### Ready For

An arXiv preprint or early systems paper with this shape:

1. Define the AIPCS pattern.
2. Describe the MCP reference implementation.
3. Present live-agent case-study evaluation.
4. Report both successes and failure-driven design changes.
5. Compare qualitatively against source access, curated flat artifacts, and model priors.
6. Position fixed-schema/injection systems such as agent-memory-v2 as future comparator work or architectural contrast.

### Not Ready For

A benchmark paper claiming:

- statistically significant improvement over existing memory systems;
- superior recall accuracy across domains;
- robust scaling to large memory stores;
- model-agnostic behavior across Claude, Codex, local LLMs, and others;
- lower total token cost in all conditions.

## Recommended Paper Framing

The first paper should be framed as:

> A pattern and reference implementation, evaluated through qualitative live-agent traces and controlled case-study runs.

Not:

> A benchmark proving AIPCS is the best memory system.

The title and abstract should emphasize:

- agent-instantiated;
- persistent context services;
- schema ownership;
- adaptive memory architecture;
- MCP-native reference implementation;
- early qualitative evaluation.

## Minimum Before Drafting

No more experiments are required before drafting.

Recommended non-experiment work before drafting:

- Convert this evidence review into an evaluation-section outline.
- Create one table mapping paper claims to run evidence.
- Create one limitations table.
- Decide whether to include run IDs in the paper body or move them to an appendix.
- Make clear that agent-memory-v2 is an architectural comparator not yet experimentally compared in the close-out matrix.

Optional later arcs, after the first paper draft exists:

- agent-memory-v2 head-to-head comparison;
- larger and longer-running AIPCS corpora;
- personal dogfooding after adding another memory-dimensionality layer;
- Codex CLI harness validation;
- non-natural-language data;
- implicit cross-domain recall;
- third-party/indirect-reference memory handling.

## Bottom Line

The project has enough evidence to publish AIPCS as a novel memory pattern with a reference implementation and credible early evaluation.

The evidence is credible because it includes successes, failures, corrections, and strong baselines. The claim must remain architectural and qualitative:

> AIPCS gives agents a way to own, persist, inspect, retrieve, and evolve structured memory across sessions.

That claim is supported.

The stronger claim:

> AIPCS is empirically better than other memory systems.

is not yet supported.
