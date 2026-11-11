#!/usr/bin/env bash
# Inject photo-concept-helper's durable memory into the model's context.
# Runs on SessionStart (startup/resume/clear/compact) - with source=compact it fires AFTER summarisation,
# so the rules land in the fresh context. Only MEMORY.md + feedback-* are injected (they cost context every
# session); user-/reference-/project-* files are read on demand via the index.
# Also warns when this checkout is still the shared template, and when onboarding hasn't run yet.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MEM="$REPO/memory"

# 1. Still pointing at the shared template repo? Work committed here can't be pushed, and must not be.
ORIGIN="$(git -C "$REPO" remote get-url origin 2>/dev/null || true)"
case "$ORIGIN" in
  *photo-concept-helper-template*)
    echo "<photo-concept-helper-warning>"
    echo "WARNING: this checkout's git origin is the SHARED TEMPLATE ($ORIGIN), not the photographer's own repo."
    echo "Before doing any work, tell the photographer, in your first reply:"
    echo "  1. On GitHub, open the template and click 'Use this template' -> 'Create a new repository' (make it Private)."
    echo "  2. Clone that new repo and open Claude Code there; or, in this folder, point origin at it:"
    echo "     git remote set-url origin <url-of-your-new-repo>"
    echo "Do not commit shoots, models or memory to this template checkout."
    echo "</photo-concept-helper-warning>"
    echo
    ;;
esac

[ -d "$MEM" ] || exit 0

# 2. First run: onboarding hasn't filled the photographer's profile yet.
if [ ! -f "$MEM/user-photographer.md" ] || grep -q '^  status: placeholder' "$MEM/user-photographer.md"; then
  echo "<photo-concept-helper-first-run>"
  echo "memory/user-photographer.md is still the placeholder: run the \`onboard\` skill before anything else"
  echo "(see CLAUDE.md -> First run). Until it has run, the defaults below are not yet tuned to this photographer."
  echo "</photo-concept-helper-first-run>"
  echo
fi

echo "<photo-concept-helper-memory>"
echo "Durable memory for this repo. feedback-* rules marked origin: template-default are starting defaults"
echo "from another photographer's shoots; this photographer's own word overrides them (see CLAUDE.md ->"
echo "Adapting to this photographer). Follow the rest without being re-told."
echo
[ -f "$MEM/MEMORY.md" ] && cat "$MEM/MEMORY.md"
echo
echo "## Standing behavioural rules (full text)"
for f in "$MEM"/feedback-*.md; do
  [ -f "$f" ] || continue
  echo
  echo "### $(basename "$f" .md)"
  awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2 || fm==0' "$f"
done
if [ -f "$REPO/PITFALLS.md" ]; then
  echo
  echo "## Known pitfalls (PITFALLS.md) - don't repeat these; add new ones as they happen"
  cat "$REPO/PITFALLS.md"
fi
echo "</photo-concept-helper-memory>"
