"""Build a compact "repo map" of a Python codebase.

The map lists files, public classes/functions, signatures and the first docstring
line, each with a `path:line` location the researcher can cite. It is the cheapest
useful context for an LLM (see docs/04-codebase-understanding.md).

Exercises (Phase 4): add defaults/annotations, `raise` statements, a token budget,
and another language via tree-sitter.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}


@dataclass
class Symbol:
    name: str
    kind: str  # "function" | "class" | "method"
    signature: str
    doc: str
    location: str  # "path:line"


@dataclass
class FileMap:
    path: str
    symbols: list[Symbol] = field(default_factory=list)


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    return f"{node.name}({ast.unparse(node.args)})" + (
        f" -> {ast.unparse(node.returns)}" if node.returns else ""
    )


def _first_line(doc: str | None) -> str:
    return (doc or "").strip().splitlines()[0] if doc and doc.strip() else ""


def scan_file(path: Path, root: Path) -> FileMap:
    rel = str(path.relative_to(root))
    fm = FileMap(rel)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return fm
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            fm.symbols.append(
                Symbol(node.name, "function", _signature(node), _first_line(ast.get_docstring(node)), f"{rel}:{node.lineno}")
            )
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            fm.symbols.append(
                Symbol(node.name, "class", f"class {node.name}", _first_line(ast.get_docstring(node)), f"{rel}:{node.lineno}")
            )
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                    not item.name.startswith("_") or item.name == "__init__"
                ):
                    fm.symbols.append(
                        Symbol(
                            f"{node.name}.{item.name}",
                            "method",
                            _signature(item),
                            _first_line(ast.get_docstring(item)),
                            f"{rel}:{item.lineno}",
                        )
                    )
    return fm


def scan_repo(root: str | Path) -> list[FileMap]:
    root = Path(root).resolve()
    files = [
        p for p in sorted(root.rglob("*.py")) if not any(part in SKIP_DIRS for part in p.parts)
    ]
    return [scan_file(p, root) for p in files]


def render_map(maps: list[FileMap]) -> str:
    """Render the map as compact text for a prompt."""
    lines: list[str] = []
    for fm in maps:
        if not fm.symbols:
            continue
        lines.append(f"## {fm.path}")
        for s in fm.symbols:
            doc = f"  # {s.doc}" if s.doc else ""
            lines.append(f"- [{s.location}] {s.signature}{doc}")
    return "\n".join(lines)


def known_symbols(maps: list[FileMap]) -> set[str]:
    names: set[str] = set()
    for fm in maps:
        for s in fm.symbols:
            names.add(s.name)
            names.add(s.name.split(".")[-1])
    return names
