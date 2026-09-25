#!/usr/bin/env bash
# Stop hook: if the session leaves uncommitted changes, ask Claude once to run verify-loop.
# Nudges only once per stop (stop_hook_active), so it can never loop.
input=$(cat)
if echo "$input" | grep -q '"stop_hook_active": *true'; then exit 0; fi
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
if git diff --quiet HEAD 2>/dev/null && [ -z "$(git ls-files --others --exclude-standard)" ]; then exit 0; fi
echo "There are uncommitted changes. If you haven't run the verify-loop skill on them, run it now; otherwise just finish." >&2
exit 2
