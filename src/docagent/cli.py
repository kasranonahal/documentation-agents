"""Command line: `docagent generate <repo> --type reference [--fake]`."""

from __future__ import annotations

import argparse
import json
import sys

from .llm import get_llm
from .pipeline import DOC_TYPES, run
from .repo_scan import render_map, scan_repo


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="docagent")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="generate one documentation page")
    g.add_argument("repo")
    g.add_argument("--type", choices=DOC_TYPES, default="reference")
    g.add_argument("--request", default=None, help="what the page should cover")
    g.add_argument("--out", default="out")
    g.add_argument("--rounds", type=int, default=2)
    g.add_argument("--fake", action="store_true", help="offline FakeLLM, no API key")
    g.add_argument("--no-run-code", action="store_true")

    m = sub.add_parser("map", help="print the repo map")
    m.add_argument("repo")

    a = ap.parse_args(argv)
    if a.cmd == "map":
        print(render_map(scan_repo(a.repo)))
        return 0

    result = run(
        get_llm(fake=a.fake), a.repo, a.type, a.request, a.out, a.rounds, run_code=not a.no_run_code
    )
    print(json.dumps({"rounds": result.rounds, "problems": result.problems, "review": result.review}, indent=2))
    print(f"\nWrote {a.out}/{a.type}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
