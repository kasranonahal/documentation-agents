"""Deterministic verification checks (docs/06-verification-and-evals.md).

Each check takes the draft markdown (plus context) and returns a list of problem
strings. An empty list means the check passed. Run these *before* any LLM judge:
they are free, fast and never hallucinate.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

CODE_BLOCK = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
MD_LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
BANNED = re.compile(r"\b(simply|just|easy|easily|obviously)\b", re.IGNORECASE)
INLINE_CALL = re.compile(r"`([A-Za-z_][\w\.]*)\(")


def check_code_blocks_have_language(md: str) -> list[str]:
    return [
        f"code block #{i + 1} has no language tag"
        for i, m in enumerate(CODE_BLOCK.finditer(md))
        if not m.group(1)
    ]


def check_python_blocks_run(md: str, timeout: int = 20) -> list[str]:
    """Execute each ```python block in a fresh interpreter. Skip blocks marked `# norun`."""
    problems = []
    for i, m in enumerate(CODE_BLOCK.finditer(md)):
        lang, code = m.group(1), m.group(2)
        if lang != "python" or "# norun" in code:
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code)
        try:
            r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=timeout)
            if r.returncode != 0:
                err = (r.stderr.strip().splitlines() or ["error"])[-1]
                problems.append(f"python block #{i + 1} failed: {err}")
        except subprocess.TimeoutExpired:
            problems.append(f"python block #{i + 1} timed out")
        finally:
            Path(f.name).unlink(missing_ok=True)
    return problems


def check_relative_links(md: str, base_dir: Path) -> list[str]:
    problems = []
    for target in MD_LINK.findall(md):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path = target.split("#", 1)[0]
        if path and not (base_dir / path).exists():
            problems.append(f"broken relative link: {target}")
    return problems


def check_required_headings(md: str, template: str) -> list[str]:
    have = {h.strip().lower() for _, h in HEADING.findall(md)}
    need = [h.strip() for level, h in HEADING.findall(template) if level == "##"]
    return [f"missing section: '{h}'" for h in need if h.lower() not in have]


def check_style(md: str) -> list[str]:
    prose = CODE_BLOCK.sub("", md)
    return [f"banned word: '{w}'" for w in sorted({w.lower() for w in BANNED.findall(prose)})]


def check_no_todos(md: str) -> list[str]:
    return [f"unresolved {t}" for t in re.findall(r"TODO\(fact\):[^\n]*", md)]


def check_symbols_exist(md: str, known: set[str]) -> list[str]:
    builtins = {"print", "len", "open", "dict", "list", "set", "str", "int", "range"}
    mentioned = {m.split(".")[-1] for m in INLINE_CALL.findall(md)}
    return [f"unknown symbol referenced: {s}()" for s in sorted(mentioned - known - builtins)]


def run_all(md: str, *, base_dir: Path, known: set[str], template: str | None = None, run_code: bool = True) -> list[str]:
    problems: list[str] = []
    problems += check_code_blocks_have_language(md)
    problems += check_relative_links(md, base_dir)
    problems += check_style(md)
    problems += check_no_todos(md)
    problems += check_symbols_exist(md, known)
    if template:
        problems += check_required_headings(md, template)
    if run_code:
        problems += check_python_blocks_run(md)
    return problems
