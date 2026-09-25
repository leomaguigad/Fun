#!/usr/bin/env bash
# Install the verification skills on this machine.
#   ./install.sh            -> user-wide (~/.claude/skills), works in every project
#   ./install.sh <repo>     -> one project (<repo>/.claude/skills), commit it to share with a team
#   ./install.sh --hook     -> also install the optional Stop-hook reminder (user-wide)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
hook=0; target="$HOME/.claude"
for arg in "$@"; do
  case "$arg" in
    --hook) hook=1 ;;
    *) target="$(cd "$arg" && pwd)/.claude" ;;
  esac
done

mkdir -p "$target/skills"
for dir in "$here"/skills/*/; do
  name="$(basename "$dir")"
  rm -rf "$target/skills/$name"
  cp -R "$dir" "$target/skills/$name"
  echo "installed skill: $name -> $target/skills/$name"
done

if [ "$hook" = 1 ]; then
  mkdir -p "$HOME/.claude/hooks"
  cp "$here/templates/hooks/verify-reminder.sh" "$HOME/.claude/hooks/"
  chmod +x "$HOME/.claude/hooks/verify-reminder.sh"
  echo "installed hook script: ~/.claude/hooks/verify-reminder.sh"
  echo "now merge templates/hooks/settings.json into ~/.claude/settings.json (not overwritten automatically)"
fi
