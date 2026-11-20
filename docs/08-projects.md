# 08 — Capstone projects

Pick one. Each has a **minimum** (must ship) and **stretch** goals. Write a 1-page design doc first (`docs/design/<name>.md`): problem, users, architecture, eval plan, risks.

## A. README doctor ⭐ (good first capstone)
Point it at any GitHub repo; it audits the README against a rubric (install, quickstart, usage, config, contributing) and opens a PR with improvements.
- Minimum: audit + rewritten README with runnable quickstart verified in a container.
- Stretch: runs on 20 popular repos; report how many quickstarts actually work.

## B. API reference enricher
Takes mkdocstrings/Sphinx output and adds: one realistic example per function (mined from tests), "see also" links, and common errors.
- Minimum: Python package, examples executed in CI.
- Stretch: OpenAPI spec → full how-to guides per endpoint group.

## C. Drift guardian
The CI bot from Module 07, production-quality.
- Minimum: detects stale pages on PRs and comments with what changed.
- Stretch: proposes patch PRs; measure false positive rate over 30 real commits.

## D. Explanation writer from history
Reads ADRs, PR descriptions, and issue threads to write "Why is it designed this way?" pages with citations.
- Minimum: one explanation page per major component with linked sources.
- Stretch: answers "why" questions interactively.

## E. Multi-agent docs team on the harness
Use the [agent-harness](https://github.com/kasranonahal/agent-harness) runtime: orchestrator plans a doc set, worker subagents write pages in parallel, evaluator agent reviews, progress file allows resuming across sessions.
- Minimum: full doc site for a small library, resumable.
- Stretch: compare cost/quality vs the single-pipeline version.

## Grading yourself
| Criterion | Weight |
|---|---|
| Eval results (fact recall, hallucination rate) | 35% |
| Verification coverage (what's automatically checked) | 25% |
| Code quality & tests | 20% |
| Write-up quality (it's a docs project — your own docs must be great) | 20% |
