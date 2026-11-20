# 03 — Doc-agent architecture

## 1. Roles
Each role is a separate prompt (and ideally separate context). Separation keeps each prompt focused and stops the writer from grading itself.

| Role | Input | Output | Notes |
|---|---|---|---|
| **Planner** | request, repo map, doc type | `Plan` JSON: title, type, audience, sections[], sources[] | Splits mixed-type requests |
| **Researcher** | plan, repo access | `FactSheet`: list of facts each with `source: path:line` | Agentic: may open files; only cites what it read |
| **Writer** | plan, fact sheet, template, style guide | Markdown draft | Forbidden to state facts not in fact sheet |
| **Verifier** | draft, repo | list of failures (deterministic) | links, code blocks run, symbols exist, template sections present |
| **Reviewer** | draft, plan, rubric | scores + fix list | Separate prompt; few-shot calibrated |
| **Editor** | draft + all feedback | revised draft | Loop back to Verifier, max N rounds |

## 2. Artifacts are the interface
Make every hand-off a **structured artifact on disk** (`out/run-<id>/plan.json`, `facts.json`, `draft.md`, `review.json`). Benefits:
- You can inspect and debug each stage.
- You can re-run one stage without the rest.
- Long jobs can resume (a key harness idea — see agent-harness Module 06).

## 3. Data shapes (see `src/docagent/pipeline.py`)

```python
@dataclass
class Plan:
    title: str
    doc_type: str          # tutorial | howto | reference | explanation
    audience: str
    sections: list[str]
    sources: list[str]     # files the researcher should read

@dataclass
class Fact:
    claim: str
    source: str            # "src/docagent/llm.py:42"
```

## 4. Control flow

```
plan = planner(request, repo_map)
facts = researcher(plan)
draft = writer(plan, facts, template)
for round in range(MAX_ROUNDS):
    problems = verifier(draft) + reviewer(draft, plan)
    if not problems: break
    draft = editor(draft, problems, facts)
publish(draft)
```

## 5. Design decisions worth making explicit
- **Where do facts come from?** Only the fact sheet. If the writer needs something missing, it emits `TODO(fact): …` rather than inventing — the verifier fails on TODOs, which sends the researcher back.
- **Max rounds** — always bound loops (2–3). If still failing, open the PR as draft with the problems listed.
- **Model choice** — use a strong model for planner/reviewer, a cheaper one for bulk section writing if cost matters.
- **Human in the loop** — the agent proposes a PR; a human merges.

## Exercises
1. Draw your own pipeline and commit it to `docs/diagrams/`.
2. Run `docagent generate ./src --type reference --fake` and read every file in `out/`.
3. Run it for real; save the output to `examples/` and annotate what's wrong with it.
4. Make the Researcher cite `path:line` for every fact (start from `repo_scan.py`).
