# 📚 Documentation Agents

> A learning-and-building project: understand what makes documentation genuinely good, then build AI agents that produce it — grounded in real code, verified, and kept up to date automatically.

![status](https://img.shields.io/badge/status-in%20progress-blue) ![python](https://img.shields.io/badge/python-3.11%2B-informational)

---

## Why this repo exists

Most "AI doc generators" produce text that *looks* like documentation but is vague, wrong, or stale a week later. The goal here is to learn — step by step — how to build agents that:

1. **Know what good docs are** (Diátaxis types, audience, style guides).
2. **Read the real source of truth** (code, APIs, configs, existing docs) instead of guessing.
3. **Plan before writing** (outline → sections → examples).
4. **Verify what they wrote** (run code samples, check links, check claims against source).
5. **Get reviewed** by a separate critic agent with a rubric — never self-grading only.
6. **Stay current** by running in CI and flagging drift when code changes.

## How to use this repo

| Step | Where | What you do |
|---|---|---|
| 1 | [`ROADMAP.md`](ROADMAP.md) | Follow the phases in order. Tick boxes as you go. |
| 2 | [`docs/`](docs/) | Read the module for the current phase. Each one ends with exercises. |
| 3 | [`src/docagent/`](src/docagent/) | Starter code. Extend it as the exercises ask. |
| 4 | [`PROGRESS.md`](PROGRESS.md) | Write a short log entry each session (what you did, what you learned, what's next). |
| 5 | GitHub **Issues → Milestones** | Each phase is a milestone; each task is an issue. The milestone bar shows your % done. |

## Learning modules

| # | Module | Focus |
|---|---|---|
| 00 | [Overview & mental model](docs/00-overview.md) | The whole system on one page |
| 01 | [What good documentation is](docs/01-good-documentation.md) | Diátaxis, audiences, style, docs-as-code |
| 02 | [Agent fundamentals](docs/02-agent-fundamentals.md) | Augmented LLM, workflows vs agents, the 5 core patterns |
| 03 | [Doc-agent architecture](docs/03-doc-agent-architecture.md) | Planner → Researcher → Writer → Verifier → Reviewer |
| 04 | [Understanding a codebase](docs/04-codebase-understanding.md) | Repo maps, AST extraction, retrieval, context budgets |
| 05 | [Prompts & templates](docs/05-prompts-and-templates.md) | Per-doc-type system prompts, templates, style rules |
| 06 | [Verification & evals](docs/06-verification-and-evals.md) | Grounding checks, runnable examples, LLM-as-judge, eval sets |
| 07 | [Docs-as-code in CI](docs/07-docs-as-code-ci.md) | PR bot, drift detection, publishing |
| 08 | [Capstone projects](docs/08-projects.md) | Graded project ideas to prove the skills |

## Quick start

```bash
git clone https://github.com/kasranonahal/documentation-agents.git
cd documentation-agents
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Offline dry-run (no API key needed — uses a fake LLM):
docagent generate ./src --type reference --fake

# Real run:
export ANTHROPIC_API_KEY=sk-ant-...
docagent generate ./src --type reference --out out/reference.md
pytest
```

## Repo layout

```
documentation-agents/
├── docs/              # learning modules (read these)
├── src/docagent/      # starter doc-agent pipeline (extend this)
│   ├── llm.py         # LLM client + FakeLLM for offline tests
│   ├── repo_scan.py   # builds a compact "repo map" from Python source
│   ├── pipeline.py    # planner → writer → verifier → reviewer
│   ├── checks.py      # deterministic checks (links, code blocks, symbols)
│   └── cli.py
├── templates/         # Diátaxis templates the writer fills in
├── evals/             # rubric + eval cases
├── scripts/           # setup_tracker.py → creates milestones/issues from ROADMAP
└── tests/
```

## Companion repo

The agent *runtime* (loop, tools, context management, permissions) is studied in depth in **[agent-harness](https://github.com/kasranonahal/agent-harness)**. This repo focuses on the *documentation* problem; that one on the *engine*. Later phases here reuse the harness.

## Key resources

See [`RESOURCES.md`](RESOURCES.md) for the full curated list.
