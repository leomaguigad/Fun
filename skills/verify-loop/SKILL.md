---
name: verify-loop
description: Run the project's own checks (format, lint, typecheck, tests, build) on the current changes, fix what fails, and repeat until everything passes. Use after making code changes, before committing, or when asked to "verify", "check my work", or "make it green".
allowed-tools: [Read, Edit, Write, Grep, Glob, Bash]
---
# Verify loop

Close the feedback loop yourself: check, fix, re-check. Do not hand work back while a check you can run is failing.

## 1. Find the checks
Look for the commands a contributor would run locally, in this order:
- `CLAUDE.md`, `CONTRIBUTING.md`, `README.md` (a "Development" or "Testing" section)
- `package.json` scripts (`lint`, `typecheck`, `test`, `build`), `Makefile`, `justfile`, `Taskfile.yml`
- `pyproject.toml` / `tox.ini` / `noxfile.py`, `Cargo.toml`, `go.mod`
- CI config (`.github/workflows/*.yml`) — the steps CI runs are the ground truth

If nothing is configured, fall back to the language defaults (e.g. `ruff check` + `pytest`, `cargo clippy` + `cargo test`, `go vet` + `go test ./...`, `tsc --noEmit`).

Prefer the fastest scoped variant first (changed package, changed files), then the full suite once at the end.

## 2. Loop
Repeat, at most 5 rounds:
1. Run every check. Capture the exit code and the failing output.
2. If all pass, stop.
3. For each failure, find the root cause and fix it in the code. Never:
   - skip, disable, delete, or loosen a test or lint rule to get green
   - add `# type: ignore`, `eslint-disable`, `@ts-ignore`, `#[allow]` just to silence a real problem
   - special-case the test input in production code
4. Go back to 1.

If a failure is clearly unrelated to the change (fails the same way on a clean checkout of the base branch), note it and move on — don't widen the change to fix it.

## 3. Report
End with a short table: check → command → pass/fail. If anything is still failing after 5 rounds, say exactly what, the last error, and what you tried. Never claim a check passed that you did not run.
