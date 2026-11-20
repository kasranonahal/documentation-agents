"""Planner → Researcher → Writer → Verifier/Reviewer → Editor pipeline.

Every stage writes its artifact to `out_dir` so you can inspect and debug it
(docs/03-doc-agent-architecture.md). This is a *workflow*: our code decides the
order; the LLM fills in each step.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import checks
from .llm import LLM
from .repo_scan import known_symbols, render_map, scan_repo

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"
DOC_TYPES = ("tutorial", "howto", "reference", "explanation")

STYLE = """Second person, present tense, active voice. Lead with the point.
Never use: simply, just, easy, obviously. Every code block has a language tag.
Sentence-case headings. Define acronyms on first use."""

GROUNDING = """Use ONLY facts from the FACTS list and the REPO MAP. If you need a fact that is
missing, write `TODO(fact): <what is missing>` instead of guessing. Never invent
function names, parameters, defaults, flags or outputs."""

TYPE_RULES = {
    "tutorial": "Beginner reader learning by doing. One guaranteed path, numbered steps, show expected result after each step, no alternatives.",
    "howto": "Competent reader with a goal. Title starts with 'How to'. Prerequisites first. Ordered steps. Variations at the end. No teaching basics.",
    "reference": "Reader looking things up. Mirror code structure. For each public symbol: signature, one-line description, parameters, returns, raises, minimal example. Austere and complete.",
    "explanation": "Reader wants to understand why. Discuss design, alternatives and trade-offs. No step-by-step instructions.",
}


@dataclass
class Plan:
    title: str
    doc_type: str
    audience: str
    sections: list[str]
    sources: list[str] = field(default_factory=list)


@dataclass
class RunResult:
    plan: Plan
    draft: str
    problems: list[str]
    review: dict
    rounds: int


def _extract_json(text: str):
    """Pull the first JSON object/array out of a model reply."""
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON in model output: {text[:200]}")
    return json.loads(m.group(1))


def load_template(doc_type: str) -> str:
    p = TEMPLATES_DIR / f"{doc_type}.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def plan(llm: LLM, request: str, repo_map: str, doc_type: str) -> Plan:
    system = (
        "ROLE: planner\nYou plan one documentation page. Reply with JSON only: "
        '{"title": str, "doc_type": str, "audience": str, "sections": [str], "sources": [str]}.\n'
        f"doc_type must be '{doc_type}'. Rules for this type: {TYPE_RULES[doc_type]}"
    )
    data = _extract_json(llm.complete(system, f"REQUEST:\n{request}\n\nREPO MAP:\n{repo_map}"))
    data["doc_type"] = doc_type
    return Plan(**{k: data.get(k, []) for k in ("title", "doc_type", "audience", "sections", "sources")})


def research(llm: LLM, p: Plan, repo_map: str) -> list[dict]:
    system = (
        "ROLE: researcher\nList the facts needed to write the planned page. Reply with a JSON array of "
        '{"claim": str, "source": "path:line"}. Cite only locations present in the repo map.'
    )
    return _extract_json(llm.complete(system, f"PLAN:\n{json.dumps(asdict(p))}\n\nREPO MAP:\n{repo_map}"))


def write(llm: LLM, p: Plan, facts: list[dict], repo_map: str, template: str) -> str:
    system = (
        f"ROLE: writer\nYou write {p.doc_type} documentation for: {p.audience}.\n"
        f"TYPE RULES: {TYPE_RULES[p.doc_type]}\nGROUNDING: {GROUNDING}\nSTYLE: {STYLE}\n"
        f"Use this template's '##' headings exactly:\n{template}\nReply with markdown only."
    )
    user = f"PLAN:\n{json.dumps(asdict(p))}\n\nFACTS:\n{json.dumps(facts, indent=1)}\n\nREPO MAP:\n{repo_map}"
    return llm.complete(system, user, max_tokens=8000)


def review(llm: LLM, p: Plan, draft: str) -> dict:
    system = (
        "ROLE: reviewer\nYou are a strict documentation reviewer. You did NOT write this draft. "
        "Score 1-5 on accuracy, completeness, clarity, type_fit. Quote evidence for any score < 4. "
        'Reply JSON: {"scores": {...}, "fixes": [str]}. Only list fixes that matter.'
    )
    return _extract_json(llm.complete(system, f"PLAN:\n{json.dumps(asdict(p))}\n\nDRAFT:\n{draft}"))


def edit(llm: LLM, draft: str, problems: list[str], facts: list[dict]) -> str:
    system = f"ROLE: editor\nFix every listed problem. Change nothing else. {GROUNDING} Reply with the full revised markdown only."
    user = f"PROBLEMS:\n- " + "\n- ".join(problems) + f"\n\nFACTS:\n{json.dumps(facts)}\n\nDRAFT:\n{draft}"
    return llm.complete(system, user, max_tokens=8000)


def run(
    llm: LLM,
    repo: str | Path,
    doc_type: str = "reference",
    request: str | None = None,
    out_dir: str | Path = "out",
    max_rounds: int = 2,
    run_code: bool = True,
) -> RunResult:
    if doc_type not in DOC_TYPES:
        raise ValueError(f"doc_type must be one of {DOC_TYPES}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    maps = scan_repo(repo)
    repo_map = render_map(maps)
    (out / "repo_map.md").write_text(repo_map, encoding="utf-8")
    known = known_symbols(maps)
    template = load_template(doc_type)
    request = request or f"Write {doc_type} documentation for this codebase."

    p = plan(llm, request, repo_map, doc_type)
    (out / "plan.json").write_text(json.dumps(asdict(p), indent=2), encoding="utf-8")

    facts = research(llm, p, repo_map)
    (out / "facts.json").write_text(json.dumps(facts, indent=2), encoding="utf-8")

    draft = write(llm, p, facts, repo_map, template)
    rounds, problems, rv = 0, [], {}
    for rounds in range(1, max_rounds + 1):
        (out / f"draft_round{rounds}.md").write_text(draft, encoding="utf-8")
        problems = checks.run_all(draft, base_dir=out, known=known, template=template, run_code=run_code)
        rv = review(llm, p, draft)
        all_problems = problems + list(rv.get("fixes", []))
        if not all_problems:
            break
        if rounds < max_rounds:
            draft = edit(llm, draft, all_problems, facts)

    (out / "review.json").write_text(json.dumps({"review": rv, "problems": problems}, indent=2), encoding="utf-8")
    (out / f"{doc_type}.md").write_text(draft, encoding="utf-8")
    return RunResult(p, draft, problems, rv, rounds)
