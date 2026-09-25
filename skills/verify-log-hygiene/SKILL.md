---
name: verify-log-hygiene
description: Check that error logs in the current diff include the request ID and never include the request body, headers with secrets, or other sensitive payloads. Use when changes touch error handling, logging, or request handlers.
allowed-tools: [Read, Edit, Grep, Glob, Bash]
---
# Verify log hygiene

1. Get the diff (`git diff` against the base branch, plus staged/unstaged changes).
2. Read every error-handling path the diff adds or modifies: `catch`/`except`/`rescue` blocks, error middleware, `logger.error`/`log.Error`/`console.error` calls, and anything that logs on a non-2xx response.
3. For each log call check:
   - **Has** a request/correlation/trace ID (`request_id`, `req.id`, `traceId`, a context-bound logger, etc.).
   - **Does not** log the request body, raw headers, cookies, auth tokens, passwords, or full user objects. Watch for indirect leaks: logging `req`, `request`, `err` objects that embed the request, or `JSON.stringify` of a payload.
4. Fix violations in place: add the ID from the surrounding context, and replace payloads with safe fields (method, path, status, error message/class).
5. Re-grep the changed files to confirm no violation remains, then list each file:line you changed and why.
