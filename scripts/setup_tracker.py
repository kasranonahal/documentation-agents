#!/usr/bin/env python3
"""Turn ROADMAP.md into GitHub Milestones (one per Phase) and Issues (one per task).

Usage:  python scripts/setup_tracker.py OWNER/REPO [--dry-run]
Needs:  the GitHub CLI (`gh`) logged in. Safe to re-run: existing milestones and
        issues with the same title are skipped.

The milestone page (Issues → Milestones) then shows a % complete bar per phase.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def parse_roadmap(path: Path) -> list[tuple[str, list[str]]]:
    phases: list[tuple[str, list[str]]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if m := re.match(r"^##\s+(Phase .+)$", line):
            phases.append((m.group(1).strip(), []))
        elif (m := re.match(r"^- \[[ x]\]\s+(.+)$", line)) and phases:
            phases[-1][1].append(m.group(1).strip())
    return phases


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    repo, dry = sys.argv[1], "--dry-run" in sys.argv
    phases = parse_roadmap(Path(__file__).resolve().parents[1] / "ROADMAP.md")

    if dry:
        for title, tasks in phases:
            print(f"[milestone] {title}")
            for t in tasks:
                print(f"    [issue] {t}")
        return 0

    try:
        gh("label", "create", "learning", "--repo", repo, "--color", "1d76db", "--force")
    except subprocess.CalledProcessError:
        pass

    existing_ms = {m["title"]: m["number"] for m in json.loads(gh("api", f"repos/{repo}/milestones?state=all&per_page=100"))}
    existing_issues = {
        i["title"] for i in json.loads(gh("api", f"repos/{repo}/issues?state=all&per_page=100"))
    }

    for idx, (title, tasks) in enumerate(phases, 1):
        if title not in existing_ms:
            ms = json.loads(gh("api", f"repos/{repo}/milestones", "-f", f"title={title}"))
            existing_ms[title] = ms["number"]
            print(f"created milestone: {title}")
        for task in tasks:
            issue_title = f"[P{idx}] {task}"
            if issue_title in existing_issues:
                continue
            body = f"Roadmap task from **{title}**.\n\n**Definition of done:** task complete, box ticked in ROADMAP.md, short note in PROGRESS.md."
            gh(
                "api", f"repos/{repo}/issues",
                "-f", f"title={issue_title}",
                "-f", f"body={body}",
                "-F", f"milestone={existing_ms[title]}",
                "-f", "labels[]=learning",
            )
            print(f"  created issue: {issue_title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
