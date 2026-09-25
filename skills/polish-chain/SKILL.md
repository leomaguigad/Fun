---
name: polish-chain
description: Chained verification for a finished change — simplify the code, then verify it passes all checks, then do a final review. Use before opening a PR or when asked to "polish", "clean up and check", or "get this ready to ship".
---
# Polish chain

Run these in order. Each step works on the output of the previous one; if a step changes code, the later steps see that change.

1. **Simplify** — run `/simplify` if available; otherwise review the diff yourself for dead code, duplication, needless abstraction, and unclear names, and fix them. Behaviour must not change.
2. **Verify** — run the `verify-loop` skill. Simplification can break things; this catches it.
3. **Targeted checks** — run `verify-log-hygiene` and/or `verify-security` if the diff touches logging/errors or auth/input/files/network.
4. **Review** — run `/code-review` if available; otherwise re-read the full diff adversarially: what would a reviewer or CI reject? Fix real issues, then re-run step 2 if you changed code.
5. **Summary** — a PR-ready description: what changed, why, and how it was verified (commands + results).
