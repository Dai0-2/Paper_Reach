#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Paper-Reach install check"
echo "Repository root: $ROOT"
echo ""

if command -v paper-reach >/dev/null 2>&1; then
  echo "[OK] paper-reach CLI found: $(command -v paper-reach)"
else
  echo "[WARN] paper-reach CLI not found in PATH"
fi

for path in \
  "$ROOT/SKILL.md" \
  "$ROOT/AGENTS.md" \
  "$ROOT/agents/openai.yaml" \
  "$ROOT/.claude-plugin/plugin.json" \
  "$ROOT/gemini-extension.json"; do
  if [ -f "$path" ]; then
    echo "[OK] Found $path"
  else
    echo "[WARN] Missing $path"
  fi
done

echo ""
echo "Common installed skill directories:"
for path in \
  "$HOME/.claude/skills/paper-reach" \
  "$HOME/.agents/skills/paper-reach" \
  "$HOME/.codex/skills/paper-reach"; do
  if [ -d "$path" ]; then
    echo "[OK] Present: $path"
  else
    echo "[INFO] Not installed: $path"
  fi
done

echo ""
if command -v paper-reach >/dev/null 2>&1; then
  echo "Running doctor:"
  paper-reach doctor
else
  echo "Skipping doctor because paper-reach is not installed in PATH"
fi
