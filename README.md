# Claude Code verification loops

A ready-to-install kit of Claude Code skills based on Anthropic's
[Building verification loops in Claude Code](https://youtu.be/mQZB0l-rhxE)
([blog post](https://claude.com/blog/building-verification-loops-in-claude-code-with-skills)).
The idea: Claude checks its own work (tests, linters, custom checks) and fixes
what fails before it hands work back to you.

## Install on your laptop

```bash
git clone -b claude/laptop-shipment-prep-8csyu0 https://github.com/leomaguigad/Fun.git
cd Fun
./install.sh              # user-wide: ~/.claude/skills
./install.sh ~/code/app   # or one project: ~/code/app/.claude/skills
./install.sh --hook       # optional: also install the Stop-hook reminder
```

Restart Claude Code, then run `/verify-loop` or just ask it to "verify this".

## The skills and which pattern each shows

| Skill | Pattern | What it does |
|---|---|---|
| `verify-loop` | core | Finds the project's lint/typecheck/test/build commands, runs them, fixes failures, repeats (max 5 rounds). Never skips or disables tests to get green. |
| `verify-log-hygiene` | standalone | The blog's example: error logs must include the request ID and never the request body or secrets. |
| `verify-security` | standalone | Security pass over the diff: injection, authz, secrets, SSRF, path traversal. Reports only, no edits. |
| `verify-spec` | standalone | Checks the implementation against a markdown spec, requirement by requirement, and fills gaps. |
| `build-and-verify` | embedded | Implements a feature, then runs the right verify skills automatically before saying "done". |
| `polish-chain` | chained | simplify → verify-loop → targeted checks → review → PR summary. |
| `templates/github-workflows/claude-verify.yml` | on every PR | GitHub Action that runs the checks on each pull request. Copy it into a repo's `.github/workflows/`. |

## Optional Stop hook

`templates/hooks/` has a Stop hook that, when a session ends with uncommitted
changes, asks Claude once to run `verify-loop`. `./install.sh --hook` copies
the script; merge `templates/hooks/settings.json` into `~/.claude/settings.json`
yourself.

## Make your own

Look at what you correct most often by hand, write the procedure in plain
English as `skills/<name>/SKILL.md` (frontmatter `name` + `description`,
optional `allowed-tools`), then re-run `./install.sh`.
