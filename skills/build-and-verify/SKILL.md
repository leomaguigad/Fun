---
name: build-and-verify
description: Implement a requested feature or fix, then automatically verify it before reporting done. Use for "build X", "add Y", "fix Z" tasks when you want verification embedded in the work rather than run separately.
---
# Build and verify (embedded pattern)

Verification is part of the job, not a follow-up.

1. **Understand**: read the relevant code and any tests around it. Restate the goal in one sentence.
2. **Plan**: list the files you'll touch. If there are existing tests for this area, note which ones should change.
3. **Implement** the change, matching the surrounding code style.
4. **Test**: add or update tests that fail without the change and pass with it.
5. **Verify** — do all that apply before reporting done:
   - Run the `verify-loop` skill (lint, typecheck, tests, build) until green.
   - Diff touches logging or error handling → run `verify-log-hygiene`.
   - Diff touches auth, input parsing, files, or outbound requests → run `verify-security`.
   - A spec was provided → run `verify-spec`.
6. **Report**: what changed (files), how it was verified (commands + results), and anything left open.
