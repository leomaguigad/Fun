---
name: verify-spec
description: Verify the current implementation against a markdown spec (PRD, design doc, acceptance criteria) and fix gaps. Use when a task came with a spec file or checklist, e.g. "check this against docs/spec.md".
allowed-tools: [Read, Edit, Write, Grep, Glob, Bash]
---
# Verify against spec

1. Locate the spec: the path the user gave, else `SPEC.md`, `docs/spec*.md`, `docs/prd*.md`, or the issue/PR description.
2. Extract every testable requirement into a numbered checklist (behaviour, inputs/outputs, edge cases, error cases, non-functional limits). Quote the spec line for each.
3. For each requirement, find the code that satisfies it and, where possible, a test that proves it. Mark it ✅ met (with file:line / test name), ⚠️ partial, or ❌ missing.
4. Fix ⚠️ and ❌ items: implement the behaviour and add a test for it. If the spec is ambiguous or contradicts itself, don't guess — list the question instead.
5. Run the `verify-loop` skill so the fixes pass the project's checks.
6. Finish with the checklist table and any open questions.
