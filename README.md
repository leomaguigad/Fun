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

## Already have Claude Code set up on the laptop? Merge instead

`install.sh` just copies skills. If your laptop already has its own
`~/.claude` (settings, hooks, CLAUDE.md, skills), use `integrate.py` to fold
this kit into it without losing anything:

```bash
python3 integrate.py --dry-run     # preview every change, touches nothing
python3 integrate.py               # merge into ~/.claude
python3 integrate.py --uninstall   # put your previous setup back
```

What it does:
- **Skills**: adds the six skills. If you already have a skill with the same
  name, your version is saved first and comes back on `--uninstall`.
- **settings.json**: adds the Stop-hook reminder next to your existing hooks;
  all your other settings stay as they are. Skip it with `--no-hook`.
- **CLAUDE.md**: appends a short marked "Verification" section telling Claude
  to use these skills; your own text is untouched.
- **Re-runnable**: after `git pull`, run it again to refresh the kit. It never
  adds duplicates, and your originals stay saved from the first run
  (`~/.claude/backups/verify-kit/`).
- **Clean undo**: `--uninstall` restores replaced skills, deletes added ones,
  and removes only the kit's hook entry and CLAUDE.md section, so any edits
  you made to those files in the meantime are kept.

Use `--project ~/code/app` to do the same for one repo's `.claude/` so you
can commit it and share it. The hook path there uses `$CLAUDE_PROJECT_DIR`,
so it works on any machine.

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
