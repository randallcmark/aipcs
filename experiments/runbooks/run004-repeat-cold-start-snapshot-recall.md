# Runbook: run004 Repeat Cold-Start Snapshot Recall

**Status:** Draft for execution
**Planned window:** 2026-06-01
**Client:** Claude CLI
**Runner:** Fresh UTM Ubuntu clone from clean baseline
**AIPCS service:** Hosted QNAP MCP endpoint, private-network unauthenticated
**Starting snapshot:** Prefer retained `run003-post`; optionally restore `run002-post` for repeatability comparison
**Scenario family:** Cold-start recall/application and longitudinal memory improvement

---

## Intent

`run004` is the next evidence run after the successful `run002`/`run003` pair.

The purpose is to test whether the behavior seen in `run003` repeats and improves:

1. A fresh Claude session starts with no OS-side project memory from previous runs.
2. The AIPCS service retains the memory state produced by `run003`.
3. Claude discovers that retained state through bootstrap.
4. Claude retrieves relevant records without being told exact entity names.
5. Claude uses the latest persisted lessons, observations, and schema changes to guide behavior.
6. Claude recognises that the schema has evolved since the first persistence-formation run.
7. Claude avoids repeating known tool-contract mistakes, especially `add_column`.

This is not a broad benchmark. It is a longitudinal repeat/continuation test: does AIPCS memory compound across sessions?

## Primary Research Question

Did the `run003` post-run memory state make the next cold-start session better oriented, more retrieval-disciplined, and less likely to repeat prior AIPCS tool mistakes?

## Non-Goals

- Do not compare Claude with Codex in this run.
- Do not run `agent-memory-v2`.
- Do not add hooks.
- Do not use null/false-positive probes yet.
- Do not deliberately mention `aipcs_meta.lesson`, `aipcs_meta.guideline`, `project_ref`, or `decision.status` before Claude has a chance to discover them.
- Do not reset AIPCS to empty for this run.

## Snapshot Choice

Use one of these two modes and record which was used.

### Preferred: `run003-post`

Use the live retained AIPCS data from after `run003`.

This tests longitudinal compounding:

- `run002` formed memory.
- `run003` recalled and evolved it.
- `run004` tests whether the evolved memory improves the next session.

Expected discoveries:

- `user_context` is schema v3 with typed settings.
- `aipcs_project` is schema v2 with `project_ref` and `decision.status`.
- `aipcs_meta` has at least 5 lessons.
- `aipcs_project` has at least 3 observations, including the contrast between write-only behavior and successful recall behavior.

### Alternative: restored `run002-post`

Restore the post-`run002` snapshot if the goal is repeatability against the same memory state used by `run003`.

This tests whether a fresh Claude session behaves similarly when presented with the same AIPCS state.

Do not mix the two interpretations. If using `run002-post`, score repeatability. If using `run003-post`, score longitudinal improvement.

## Preconditions

- The selected AIPCS snapshot is live and backed up before the run.
- A fresh UTM clone has been created from the clean baseline.
- The clone has no local project memory from `run002` or `run003`.
- Claude CLI can authenticate, if required.
- AIPCS MCP server is visible in `/mcp`.
- Caddy Basic Auth remains disabled for the private-network MCP route.
- A run artifact directory exists on the Mac:

```bash
mkdir -p ~/aipcs-experiments/runs/run004
```

## Capture Plan

Use both artifacts where possible:

1. **Mac-side terminal trace** for operator/audit evidence.
2. **Claude `/export`** for canonical readable transcript.

Start capture on the Mac before SSH:

```bash
script -q ~/aipcs-experiments/runs/run004/terminal.typescript
```

Inside the captured shell:

```bash
ssh aipcs@<vm-ip>
```

Do setup in the SSH session, then launch Claude:

```bash
cd /home/aipcs
claude
```

If Claude requires `/login`, complete it before scoring the run. Treat login as an authentication precondition, not an experiment intervention. After login, repeat the first prompt and treat the post-login prompt as the true run start.

At the end of the run:

1. Use Claude `/export`.
2. Save the export to a file if possible.
3. Exit Claude.
4. Exit SSH.
5. Exit `script`.

The terminal trace should remain on the Mac at:

```text
~/aipcs-experiments/runs/run004/terminal.typescript
```

## Environment Metadata

Capture this before or after the run. Prefer before launching Claude if convenient.

On the VM:

```bash
{
  date -Is
  uname -a
  lsb_release -a 2>/dev/null || cat /etc/os-release
  claude --version 2>/dev/null || true
  node --version 2>/dev/null || true
  npm --version 2>/dev/null || true
  git --version 2>/dev/null || true
  pwd
} > ~/run004-environment.txt
```

Copy it out later, or paste the key fields into the curated run note.

Record separately:

- UTM clone name
- starting AIPCS snapshot id/path
- post-run AIPCS archive path
- Docker image tag/digest if available
- `aipcs-server` commit if available
- whether `/login` was required
- whether any native memory recall signal appeared

## Prompt Sequence

Use these prompts in order unless the run blocks. Keep wording close so runs remain comparable.

### Prompt 1: Broad Orientation

```text
Please orient yourself in this workspace and tell me what persistent context, if any, is available to you.
```

Observe:

- Did Claude call `aipcs_bootstrap` before answering?
- Did it identify the retained AIPCS services?
- Did it retrieve records from relevant entities?
- Did it notice the evolved schema (`project_ref`, `decision.status`, typed settings)?
- Did it rely on native memory or local files instead?

Expected but do not prompt for explicitly:

- `user_context`
- `aipcs_project`
- `aipcs_meta`

### Prompt 2: Continue From Prior Session

```text
I want to continue working with AIPCS from where the previous session left off. Before doing anything substantive, decide what persisted context you should inspect and explain what you found.
```

Observe:

- Does Claude inspect `aipcs_meta.lesson` and `aipcs_meta.guideline`?
- Does Claude inspect `aipcs_project.observation` to identify the latest session state?
- Does Claude inspect `aipcs_project.decision` and `project_ref` now that they exist?
- Does it distinguish current schema state from older migrated concept records?

Pass signal:

- It explains that prior sessions moved from persistence formation to recall/application and schema evolution.

### Prompt 3: Tool-Safety Recall

```text
We may need to use AIPCS tools again in this session. Based on what has been persisted, what should you be careful about before creating, updating, or evolving any records?
```

Observe:

- Does it recall `id` primary-key naming?
- Does it recall audit fields are declared in schema but omitted from payloads?
- Does it recall `add_attribute`, not `add_column`?
- Does it recall atomic migration validation?
- Does it mention inspecting schemas before mutation?

Pass signal:

- It names lessons from both `run002` and `run003`, especially the newer `add_attribute`/atomic-validation lesson.

### Prompt 4: Schema State Assessment

```text
Evaluate the current AIPCS memory architecture as it stands now. Is it adequate for continuing this research thread, or has the schema drifted enough that you would change anything? Do not make changes yet; explain your reasoning.
```

Observe:

- Does it avoid churn?
- Does it recognise recent improvements from `run003`?
- Does it identify remaining rough edges such as stranded entities, flatness, or entity boundaries?
- Does it distinguish "would improve retrieval" from "nice to clean up"?

Pass signal:

- It does not reflexively evolve schemas.
- It grounds any proposed changes in retrieved records and current schema inspection.

### Prompt 5: Bounded Action

Choose one of the following depending on how Prompt 4 goes.

If Claude says no evolution is needed:

```text
That seems reasonable. Persist a concise observation explaining why no schema evolution was needed this session and what future sessions should watch for.
```

If Claude proposes a credible small evolution:

```text
If you think that evolution is worthwhile, proceed. Keep the change bounded and use the persisted lessons before making tool calls.
```

If Claude proposes a broad or risky evolution:

```text
Before changing anything, narrow this to the smallest useful evolution that would improve future retrieval. Explain what you are deliberately not changing.
```

Observe:

- Does it use the correct evolve operations?
- Does it avoid `add_column`?
- Does it avoid broad churn?
- Does it persist a lesson/observation if new friction appears?

### Prompt 6: Wrap-Up

```text
Summarise which persisted records influenced your behaviour in this session, what changed in AIPCS if anything, and what a future session should inspect first.
```

Observe:

- Does it cite/identify records from `aipcs_meta`, `aipcs_project`, and `user_context`?
- Does it record any new lessons immediately?
- Does it provide useful retrieval guidance for a future cold start?

## Scoring Checklist

| Check | Pass Signal | Notes |
|---|---|---|
| Fresh OS clone | No local project history from prior runs | |
| AIPCS retained snapshot | Bootstrap shows `run003-post` state | |
| Bootstrap adherence | Bootstrap before substantive answer | |
| Bounded retrieval | Relevant entity retrieval, not blind full dump | |
| Lesson application | Prior lessons shape tool use | |
| New lesson recall | `add_attribute`, not `add_column`; atomic validation | |
| Schema awareness | Detects evolved entities/attributes from `run003` | |
| Churn control | Does not evolve just because asked | |
| Tool discipline | AIPCS tools only; no direct SQLite | |
| Native memory caveat | Any non-AIPCS memory signal recorded | |
| Evidence capture | Terminal trace + `/export` captured | |

## Failure Conditions

Treat these as findings, not wasted runs:

- Claude cannot authenticate or cannot see AIPCS.
- Claude skips bootstrap and answers from native memory.
- Claude fails to retrieve `aipcs_meta` before mutating records.
- Claude repeats known mistakes such as `add_column` without recognizing prior lessons.
- Claude over-evolves schemas without retrieval-based justification.
- Claude claims migrated/deleted concept records as if they remain authoritative.
- Claude uses direct SQLite or local filesystem data instead of AIPCS tools.

## Post-Run Capture

Before resetting anything:

1. Archive the hosted AIPCS data directory as `run004-post`.
2. Preserve the Claude `/export` file.
3. Preserve the Mac-side `terminal.typescript`.
4. Create a curated run note under `experiments/runs/`.
5. Record whether the run used `run003-post` or restored `run002-post`.

Do not delete the AIPCS post-run data until the curated note has been written and the next planned snapshot is chosen.

## Expected Outcome

The best outcome is not necessarily another schema evolution.

The best outcome is evidence that a fresh agent can:

- discover the retained memory state,
- retrieve the right operational lessons,
- avoid previously learned mistakes,
- judge whether further evolution is warranted,
- and leave the memory store more useful than it found it.

If no schema change is needed and Claude explains that well, that is a successful maturity signal.
