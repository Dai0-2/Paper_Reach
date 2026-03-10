#!/usr/bin/env bash
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
echo "Source: $SRC"

TARGETS=(
  "$HOME/.claude/skills/paper-reach"
  "$HOME/.agents/skills/paper-reach"
  "$HOME/.codex/skills/paper-reach"
)

for target in "${TARGETS[@]}"; do
  echo ""
  echo "--- Syncing to $target ---"
  mkdir -p "$target"
  mkdir -p "$target/skills"
  mkdir -p "$target/paper_reach"
  mkdir -p "$target/docs"
  mkdir -p "$target/examples/agent-recipes"
  mkdir -p "$target/agents"
  mkdir -p "$target/.claude-plugin"

  cp "$SRC/SKILL.md" "$target/"
  cp "$SRC/AGENTS.md" "$target/"
  cp "$SRC/README.md" "$target/"
  cp "$SRC/gemini-extension.json" "$target/"
  cp "$SRC/agents/openai.yaml" "$target/agents/"
  cp "$SRC/.claude-plugin/plugin.json" "$target/.claude-plugin/"
  cp "$SRC/.claude-plugin/marketplace.json" "$target/.claude-plugin/"

  rsync -a "$SRC/skills/" "$target/skills/"
  rsync -a "$SRC/paper_reach/" "$target/paper_reach/"
  rsync -a "$SRC/docs/agent-integration.md" "$target/docs/"
  rsync -a "$SRC/examples/agent-recipes/" "$target/examples/agent-recipes/"

  echo "  Synced metadata, skills, package stubs, and integration docs"
done

echo ""
echo "Sync complete."
