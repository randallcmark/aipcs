# Validation

## Harness validation

Run after any change to harness files:

```bash
bash scripts/validate-harness.sh
```

This checks that all required files exist, are non-empty, have no stale TODO(project) markers, and that the journal and paper outline are present.

## Reference implementation validation

The reference implementation lives in the `application_tracker` repo. Validation commands for that project are maintained there. When working across both repos, run that project's validation suite as well.

## Pattern spec validation

There is no automated test for the pattern spec — it's a document. Validate manually:
- Does `docs/architecture/index.md` reflect the current v1 design decisions?
- Are the three core design answers (trigger / mechanism / registration) still accurate?
- Does the BUILD_JOURNAL decision log agree with the architecture docs?

## Paper outline validation

```bash
# Check paper outline has all 7 sections
grep -c "^##" paper/outline.md
# Expected: 7 (Introduction, Background, Pattern, Implementation, Evaluation, Discussion, Conclusion)
```

## Live-agent evidence validation

When a live Claude/Codex/hosted-agent transcript is used as evidence:

- Keep the BUILD_JOURNAL as the narrative source.
- Prefer a curated transcript note over citing a raw JSON transcript directly.
- Preserve the raw transcript artifact when a claim depends on exact tool calls, sequence, timing, or wording.
- Record enough context to reproduce or interpret the run: date, client, visible model label, instruction surface, AIPCS tool surface, scenario, and raw artifact pointer.
- If no raw transcript exists for an older observation, cite it as a development observation or rerun the scenario before using it as strong paper evidence.

## Checklist before completing any task

- [ ] `bash scripts/validate-harness.sh` passes
- [ ] BUILD_JOURNAL entry added if a decision was made
- [ ] Architecture docs updated if the pattern changed
- [ ] No TODO(project) markers in modified files
