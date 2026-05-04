#!/usr/bin/env bash
# Validates that the AIPCS agent harness is complete and in good shape.
# Run from the repo root: bash scripts/validate-harness.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

ERRORS=0
WARNINGS=0

fail() { echo "  FAIL: $1"; ((ERRORS++)); }
warn() { echo "  WARN: $1"; ((WARNINGS++)); }
ok()   { echo "    OK: $1"; }

echo ""
echo "=== AIPCS Harness Validation ==="
echo ""

# ── Required root files ──────────────────────────────────────────────────────
echo "[ Root files ]"
for f in CLAUDE.md AGENTS.md README.md; do
  if [[ -f "$f" && -s "$f" ]]; then
    ok "$f"
  else
    fail "$f missing or empty"
  fi
done

# ── Required agent docs ───────────────────────────────────────────────────────
echo ""
echo "[ docs/agent/ ]"
for f in \
  docs/agent/index.md \
  docs/agent/task-protocol.md \
  docs/agent/validation.md \
  docs/agent/ai-feature-rules.md \
  docs/agent/security-rules.md \
  docs/agent/doc-maintenance.md \
  docs/agent/paper-rules.md; do
  if [[ -f "$f" && -s "$f" ]]; then
    ok "$f"
  else
    fail "$f missing or empty"
  fi
done

# ── Required architecture docs ────────────────────────────────────────────────
echo ""
echo "[ docs/architecture/ ]"
for f in \
  docs/architecture/index.md \
  docs/architecture/boundaries.md \
  docs/architecture/decisions/template.md; do
  if [[ -f "$f" && -s "$f" ]]; then
    ok "$f"
  else
    fail "$f missing or empty"
  fi
done

# ── Required product/research docs ────────────────────────────────────────────
echo ""
echo "[ docs/product/ ]"
for f in \
  docs/product/research-brief.md \
  docs/product/research-journeys.md; do
  if [[ -f "$f" && -s "$f" ]]; then
    ok "$f"
  else
    fail "$f missing or empty"
  fi
done

# ── Required exec-plans ───────────────────────────────────────────────────────
echo ""
echo "[ docs/exec-plans/ ]"
if [[ -f "docs/exec-plans/template.md" && -s "docs/exec-plans/template.md" ]]; then
  ok "docs/exec-plans/template.md"
else
  fail "docs/exec-plans/template.md missing or empty"
fi
if [[ -d "docs/exec-plans/active" && -d "docs/exec-plans/completed" ]]; then
  ok "docs/exec-plans/active/ and completed/ exist"
else
  fail "docs/exec-plans/active/ or completed/ missing"
fi

# ── Required quality docs ─────────────────────────────────────────────────────
echo ""
echo "[ docs/quality/ ]"
for f in \
  docs/quality/technical-debt.md \
  docs/quality/quality-score.md; do
  if [[ -f "$f" && -s "$f" ]]; then
    ok "$f"
  else
    fail "$f missing or empty"
  fi
done

# ── Required roadmap docs ─────────────────────────────────────────────────────
echo ""
echo "[ docs/roadmap/ ]"
for f in \
  docs/roadmap/task-map.md \
  docs/roadmap/implementation-sequencing.md; do
  if [[ -f "$f" && -s "$f" ]]; then
    ok "$f"
  else
    fail "$f missing or empty"
  fi
done

# ── Journal and paper ─────────────────────────────────────────────────────────
echo ""
echo "[ Journal and paper ]"
if [[ -f "journal/BUILD_JOURNAL.md" && -s "journal/BUILD_JOURNAL.md" ]]; then
  ok "journal/BUILD_JOURNAL.md"
else
  fail "journal/BUILD_JOURNAL.md missing or empty"
fi
if [[ -f "paper/outline.md" && -s "paper/outline.md" ]]; then
  ok "paper/outline.md"
else
  fail "paper/outline.md missing or empty"
fi

# ── Paper outline sections ────────────────────────────────────────────────────
echo ""
echo "[ Paper outline sections ]"
SECTION_COUNT=$(grep -c "^## [0-9]" paper/outline.md 2>/dev/null || echo 0)
if [[ "$SECTION_COUNT" -ge 7 ]]; then
  ok "paper/outline.md has $SECTION_COUNT numbered sections (≥7 required)"
else
  fail "paper/outline.md has only $SECTION_COUNT numbered sections — expected 7"
fi

# ── Stale TODO(project) markers ───────────────────────────────────────────────
echo ""
echo "[ Stale markers ]"
TODO_HITS=$(grep -r "TODO(project)" docs/ AGENTS.md CLAUDE.md 2>/dev/null || true)
TODO_COUNT=$(echo "$TODO_HITS" | grep -v "docs/agent/validation.md" | grep -c "TODO(project)" || true)
if [[ "$TODO_COUNT" -eq 0 ]]; then
  ok "No TODO(project) markers found"
else
  warn "$TODO_COUNT TODO(project) marker(s) remain — replace with project-specific content"
fi

# ── Stale exec plans ──────────────────────────────────────────────────────────
echo ""
echo "[ Active exec plans ]"
STALE_PLANS=()
if [[ -d "docs/exec-plans/active" ]]; then
  while IFS= read -r -d '' plan; do
    AGE_DAYS=$(( ( $(date +%s) - $(stat -f %m "$plan" 2>/dev/null || stat -c %Y "$plan" 2>/dev/null || echo 0) ) / 86400 ))
    if [[ $AGE_DAYS -gt 30 ]]; then
      STALE_PLANS+=("$plan (${AGE_DAYS}d old)")
    fi
  done < <(find docs/exec-plans/active -name "*.md" ! -name ".gitkeep" -print0 2>/dev/null)
fi
if [[ ${#STALE_PLANS[@]} -eq 0 ]]; then
  ok "No stale active plans"
else
  for p in "${STALE_PLANS[@]}"; do
    warn "Stale plan: $p — complete, abandon, or move to completed/"
  done
fi

# ── Empty markdown files ──────────────────────────────────────────────────────
echo ""
echo "[ Empty markdown files ]"
EMPTY_MD=()
while IFS= read -r -d '' f; do
  if [[ ! -s "$f" ]]; then
    EMPTY_MD+=("$f")
  fi
done < <(find docs paper -name "*.md" -print0 2>/dev/null)
if [[ ${#EMPTY_MD[@]} -eq 0 ]]; then
  ok "No empty markdown files"
else
  for f in "${EMPTY_MD[@]}"; do
    fail "Empty markdown file: $f"
  done
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "================================="
if [[ $ERRORS -eq 0 && $WARNINGS -eq 0 ]]; then
  echo "PASSED — harness is complete and clean"
elif [[ $ERRORS -eq 0 ]]; then
  echo "PASSED with $WARNINGS warning(s)"
else
  echo "FAILED — $ERRORS error(s), $WARNINGS warning(s)"
  exit 1
fi
echo ""
