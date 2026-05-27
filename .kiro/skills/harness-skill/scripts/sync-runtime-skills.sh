#!/usr/bin/env bash
# Mirror the canonical skill from skills/harness-skill/ into each runtime's
# discovery directory. Mirrors are exact copies (stale files are pruned), so
# only ever edit skills/harness-skill/ then run this script.
#
# assets/templates is required at runtime by the fallback generator; examples
# stay only in the canonical dir to keep mirrors lean.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SRC="$ROOT/skills/harness-skill"

for dir in .kiro .cursor .agents .claude .codex; do
  target="$ROOT/$dir/skills/harness-skill"
  rm -rf "$target"
  mkdir -p "$target/assets"
  cp "$SRC/SKILL.md" "$target/SKILL.md"
  cp -R "$SRC/references" "$target/"
  cp -R "$SRC/scripts" "$target/"
  cp -R "$SRC/assets/templates" "$target/assets/"
  # drop any python caches that may have been copied from scripts/
  find "$target" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
done

echo "Synced harness-skill to runtime mirrors (.kiro .cursor .agents .claude .codex)."
