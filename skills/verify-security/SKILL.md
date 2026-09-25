---
name: verify-security
description: Standalone security pass over the current diff — injection, authz gaps, secrets, unsafe deserialization, SSRF, path traversal. Invoke deliberately before merging anything touching auth, input handling, file access, or external calls.
allowed-tools: [Read, Grep, Glob, Bash]
---
# Verify security

Review only what the diff changes, but follow data into the code it calls.

For each changed entry point (route, handler, CLI arg, message consumer, file reader), trace untrusted input to where it is used and check:
- **Injection**: SQL/NoSQL built by string concatenation, shell commands with interpolated input, template rendering of raw input, `eval`/`exec`.
- **AuthN/AuthZ**: new endpoints or actions missing the auth check the neighbours have; object access not scoped to the current user (IDOR).
- **Secrets**: keys, tokens, passwords committed in code, config, tests, or fixtures. Run `git diff | grep -nEi '(api[_-]?key|secret|token|passw|BEGIN .*PRIVATE KEY)'` as a first sweep.
- **Files & network**: user-controlled paths without normalization (traversal), user-controlled URLs fetched server-side (SSRF), unsafe deserialization (`pickle`, `yaml.load`, Java serialization).
- **Crypto**: homemade crypto, MD5/SHA1 for passwords, non-constant-time secret comparison, `Math.random` for tokens.

Report findings as: severity (high/medium/low) · file:line · what an attacker does · suggested fix. Only report issues you can point to concretely; say "no findings" if there are none. Do not edit code unless asked.
