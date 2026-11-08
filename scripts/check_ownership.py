"""Check that a branch only changes files its owner may edit (see .github/team.yml).

    python scripts/check_ownership.py part3-gheorghevici            # compare with origin/main
    python scripts/check_ownership.py part3-gheorghevici main       # compare with another base
    python scripts/check_ownership.py --owner trafficmas/routing/router.py
    python scripts/check_ownership.py --write-codeowners

Branches that are not part branches (main, for example) are not restricted.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TEAM = yaml.safe_load((ROOT / ".github" / "team.yml").read_text(encoding="utf-8"))
SHARED = "shared"


def owner(path: str) -> str:
    """The part whose longest path prefix matches `path`, or "shared"."""
    best, length = SHARED, -1
    for part, cfg in TEAM["parts"].items():
        for prefix in cfg["paths"]:
            if (path == prefix or (prefix.endswith("/") and path.startswith(prefix))) and len(prefix) > length:
                best, length = part, len(prefix)
    return best


def editable_by(part: str) -> set[str]:
    allowed = {part, *TEAM["parts"][part].get("also_edits", [])}
    if TEAM.get("maintainer") == part:
        allowed.add(SHARED)
    return allowed


def check(branch: str, base: str) -> int:
    part = next((p for p, cfg in TEAM["parts"].items() if cfg["branch"] == branch), None)
    if part is None:
        print(f"{branch}: not a part branch, nothing to check")
        return 0
    changed = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=ROOT, check=True,
                             capture_output=True, text=True).stdout.split()
    allowed = editable_by(part)
    bad = [(f, owner(f)) for f in changed if owner(f) not in allowed]
    member = TEAM["parts"][part]["member"]
    if not bad:
        print(f"{branch} ({member}): {len(changed)} changed files, all inside {sorted(allowed)}")
        return 0
    print(f"{branch} ({member}) may only change {sorted(allowed)}, but changes:")
    for f, o in bad:
        who = TEAM["parts"][o]["member"] if o in TEAM["parts"] else "the maintainer (shared file)"
        print(f"  {f}  -> belongs to {o}: {who}")
    return 1


def write_codeowners() -> None:
    """Reviewers of every part: the people who may edit it plus the maintainer.

    Nobody can approve their own pull request on GitHub, so the maintainer reviews the
    owner's changes; who may *change* a part is enforced by the ownership check instead.
    GitHub applies the last matching rule, so shared files come first and longer paths last.
    """
    def handles(part: str) -> list[str]:
        owners = [p for p in TEAM["parts"] if part in editable_by(p) or p == TEAM.get("maintainer")]
        return [f"@{TEAM['parts'][p]['github']}" for p in owners if TEAM["parts"][p]["github"]]

    lines = ["# Generated from .github/team.yml by scripts/check_ownership.py --write-codeowners", ""]
    shared = handles(SHARED)
    lines.append(f"* {' '.join(shared)}" if shared else "# * (maintainer has no GitHub username yet)")
    rules = sorted((len(prefix), prefix, part) for part, cfg in TEAM["parts"].items() for prefix in cfg["paths"])
    for _, prefix, part in rules:
        h = handles(part)
        missing = f"# /{prefix} ({TEAM['parts'][part]['member']}: GitHub username missing)"
        lines.append(f"/{prefix} {' '.join(h)}" if h else missing)
    (ROOT / ".github" / "CODEOWNERS").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("wrote .github/CODEOWNERS")


def main(argv: list[str]) -> int:
    if argv[:1] == ["--write-codeowners"]:
        write_codeowners()
        return 0
    if argv[:1] == ["--owner"] and len(argv) == 2:
        o = owner(argv[1])
        print(f"{argv[1]}: {o}" + (f" ({TEAM['parts'][o]['member']})" if o in TEAM["parts"] else ""))
        return 0
    if len(argv) in (1, 2):
        return check(argv[0], argv[1] if len(argv) == 2 else "origin/main")
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
