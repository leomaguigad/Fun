#!/usr/bin/env python3
"""Merge this verification-loop kit into an existing Claude Code setup.

Unlike install.sh, this never clobbers what is already there:
  * the first run saves your originals to <claude dir>/backups/verify-kit/
  * installs the skills; a same-named skill you already have is saved first
  * merges the Stop hook into settings.json, keeping your settings and hooks
  * adds a marked "Verification" section to CLAUDE.md, keeping your text
  * safe to re-run (e.g. after pulling kit updates): it just refreshes the kit

--uninstall puts your originals back: kit-only skills are removed, skills it
replaced are restored, and only the kit's hook entry and CLAUDE.md section are
taken out, so edits you made to those files since are kept.

Usage:
  python3 integrate.py --dry-run        # show what would change, touch nothing
  python3 integrate.py                  # merge into ~/.claude
  python3 integrate.py --no-hook        # skip the Stop hook
  python3 integrate.py --project PATH   # merge into PATH/.claude instead (shareable via git)
  python3 integrate.py --uninstall      # undo (add --project PATH for a project)
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
MARK_BEGIN = "<!-- verify-kit:begin -->"
MARK_END = "<!-- verify-kit:end -->"
HOOK_NAME = "verify-reminder.sh"

CLAUDE_MD_SECTION = f"""{MARK_BEGIN}
## Verification

Close your own feedback loop before reporting work as done:
- After code changes, run the `verify-loop` skill (lint, typecheck, tests, build) and fix failures until green.
- Changes to logging or error handling: also run `verify-log-hygiene`.
- Changes to auth, input parsing, file access, or outbound requests: also run `verify-security`.
- If the task came with a spec, run `verify-spec`.
- Never skip, disable, or loosen a test or lint rule to get green. Never claim a check passed that you did not run.
{MARK_END}
"""


class Plan:
    def __init__(self, dry):
        self.dry = dry

    def do(self, desc, fn=None):
        print(("[dry-run] " if self.dry else "") + desc)
        if fn and not self.dry:
            fn()


def copy_any(src, dest):
    if dest.is_dir():
        shutil.rmtree(dest)
    elif dest.exists():
        dest.unlink()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)


class State:
    """Remembers, across runs, what the kit replaced (saved) and what it created."""

    def __init__(self, root):
        self.root = root
        self.dir = root / "backups" / "verify-kit"
        self.file = self.dir / "manifest.json"
        data = json.loads(self.file.read_text()) if self.file.exists() else {}
        self.saved = set(data.get("saved", []))
        self.created = set(data.get("created", []))

    def known(self, rel):
        return rel in self.saved or rel in self.created

    def claim(self, path, plan):
        """Before the kit writes `path`, save the user's original the first time only."""
        rel = str(path.relative_to(self.root))
        if self.known(rel):
            return
        if path.exists():
            plan.do(f"save your original {rel} -> {self.dir / rel}", lambda: copy_any(path, self.dir / rel))
            self.saved.add(rel)
        else:
            self.created.add(rel)

    def write(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        self.file.write_text(json.dumps({"saved": sorted(self.saved), "created": sorted(self.created)}, indent=2) + "\n")


def load_settings(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"error: {path} is not valid JSON ({e}); fix it first, nothing was changed")


def is_ours(hook):
    return HOOK_NAME in hook.get("command", "")


def add_hook(settings, command):
    stops = settings.setdefault("hooks", {}).setdefault("Stop", [])
    if any(is_ours(h) for g in stops for h in g.get("hooks", [])):
        return False
    stops.append({"hooks": [{"type": "command", "command": command}]})
    return True


def remove_hook(settings):
    hooks = settings.get("hooks", {})
    stops = hooks.get("Stop", [])
    kept = []
    for g in stops:
        g = dict(g, hooks=[h for h in g.get("hooks", []) if not is_ours(h)])
        if g["hooks"]:
            kept.append(g)
    if kept == stops:
        return False
    if kept:
        hooks["Stop"] = kept
    else:
        hooks.pop("Stop", None)
        if not hooks:
            settings.pop("hooks", None)
    return True


def split_section(text):
    """Return (before, after) around our marked block, or None if absent."""
    if MARK_BEGIN not in text or MARK_END not in text:
        return None
    before, rest = text.split(MARK_BEGIN, 1)
    return before, rest.split(MARK_END, 1)[1].lstrip("\n")


def add_section(text):
    parts = split_section(text)
    if parts:
        return parts[0] + CLAUDE_MD_SECTION + parts[1]
    sep = "" if not text or text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    return text + sep + CLAUDE_MD_SECTION


def remove_section(text):
    parts = split_section(text)
    if not parts:
        return text
    before, after = parts
    return (before.rstrip("\n") + "\n" + ("\n" + after if after else "")) if before.strip() else after


def integrate(root, with_hook, plan, project):
    state = State(root)

    for src in sorted((KIT / "skills").iterdir()):
        if not (src / "SKILL.md").exists():
            continue
        dest = root / "skills" / src.name
        verb = "update" if state.known(f"skills/{src.name}") else ("replace your" if dest.exists() else "add")
        state.claim(dest, plan)
        plan.do(f"{verb} skill {src.name}", lambda src=src, dest=dest: copy_any(src, dest))

    if with_hook:
        hook_dest = root / "hooks" / HOOK_NAME
        state.claim(hook_dest, plan)

        def install_hook():
            copy_any(KIT / "templates" / "hooks" / HOOK_NAME, hook_dest)
            hook_dest.chmod(0o755)

        plan.do(f"install hook script {hook_dest}", install_hook)

        settings_path = root / "settings.json"
        settings = load_settings(settings_path)
        # Project settings get committed, so don't bake in this machine's absolute path.
        command = f'"$CLAUDE_PROJECT_DIR"/.claude/hooks/{HOOK_NAME}' if project else str(hook_dest)
        if add_hook(settings, command):
            state.claim(settings_path, plan)
            plan.do(
                f"add Stop hook to {settings_path} (your other settings and hooks kept)",
                lambda: settings_path.write_text(json.dumps(settings, indent=2) + "\n"),
            )
        else:
            plan.do(f"Stop hook already in {settings_path}")

    md = root / "CLAUDE.md"
    old = md.read_text() if md.exists() else ""
    new = add_section(old)
    if new != old:
        state.claim(md, plan)
        plan.do(f"{'refresh' if split_section(old) else 'add'} Verification section in {md}", lambda: md.write_text(new))
    else:
        plan.do(f"Verification section in {md} already up to date")

    if not plan.dry:
        state.write()
        print(f"\nDone. Originals saved in {state.dir}")
        print("Restart Claude Code, then try /verify-loop. Undo with: python3 integrate.py --uninstall")


def uninstall(root, plan):
    state = State(root)
    if not state.file.exists():
        sys.exit(f"nothing to undo: no {state.file}")

    # Skills and the hook script: put originals back, delete what the kit added.
    for rel in sorted(state.saved | state.created):
        if rel in ("settings.json", "CLAUDE.md"):
            continue
        path = root / rel
        if rel in state.saved:
            plan.do(f"restore your original {rel}", lambda rel=rel, path=path: copy_any(state.dir / rel, path))
        elif path.exists():
            plan.do(f"remove {rel}", lambda path=path: shutil.rmtree(path) if path.is_dir() else path.unlink())

    # settings.json and CLAUDE.md: take out only our parts, keep later edits.
    settings_path = root / "settings.json"
    if settings_path.exists():
        settings = load_settings(settings_path)
        if remove_hook(settings):
            plan.do(f"remove Stop hook from {settings_path}", lambda: settings_path.write_text(json.dumps(settings, indent=2) + "\n"))
            if "settings.json" in state.created and not settings:
                plan.do(f"remove {settings_path} (kit created it and it's now empty)", settings_path.unlink)

    md = root / "CLAUDE.md"
    if md.exists():
        text = md.read_text()
        stripped = remove_section(text)
        if stripped != text:
            if "CLAUDE.md" in state.created and not stripped.strip():
                plan.do(f"remove {md} (kit created it)", md.unlink)
            else:
                plan.do(f"remove Verification section from {md}", lambda: md.write_text(stripped))

    if not plan.dry:
        shutil.rmtree(state.dir)
        for d in (root / "hooks", root / "skills", root / "backups"):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
        print("\nUndone. Your previous setup is back.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="show what would change, touch nothing")
    ap.add_argument("--no-hook", action="store_true", help="don't install/merge the Stop hook")
    ap.add_argument("--project", metavar="PATH", help="use PATH/.claude instead of ~/.claude")
    ap.add_argument("--uninstall", action="store_true", help="undo the integration")
    args = ap.parse_args()

    root = (Path(args.project).expanduser().resolve() / ".claude") if args.project else Path.home() / ".claude"
    plan = Plan(args.dry_run)
    print(f"Claude config: {root}\n")
    if args.uninstall:
        uninstall(root, plan)
    else:
        integrate(root, not args.no_hook, plan, project=bool(args.project))


if __name__ == "__main__":
    main()
