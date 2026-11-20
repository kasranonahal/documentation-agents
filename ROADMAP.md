# Roadmap

Each **Phase** = one GitHub Milestone. Each `- [ ]` line = one GitHub Issue (created by `scripts/setup_tracker.py`).
Tick the box here **and** close the issue when done. Suggested pace: one phase per 1–2 weeks.

## Phase 1 — Foundations of good documentation
- [ ] Read docs/01 and summarise the four Diátaxis types in your own words in PROGRESS.md
- [ ] Pick 3 real open-source projects and classify 10 of their pages by Diátaxis type
- [ ] Write a one-page personal style guide (voice, tense, headings, code-block rules)
- [ ] Hand-write one tutorial and one reference page for a small project of yours

## Phase 2 — Agent fundamentals
- [ ] Read docs/02 and implement a single LLM call that drafts a README section
- [ ] Implement prompt chaining: outline → draft → polish
- [ ] Implement the evaluator-optimizer loop with a 3-criterion rubric
- [ ] Implement routing: classify a request into one of the 4 Diátaxis types

## Phase 3 — Doc-agent architecture
- [ ] Read docs/03 and draw your pipeline diagram (commit it to docs/diagrams/)
- [ ] Run the starter pipeline with --fake and read every intermediate artifact
- [ ] Run it for real on this repo's src/ and save the output in examples/
- [ ] Add a Researcher step that collects facts with file:line citations

## Phase 4 — Understanding a codebase
- [ ] Read docs/04 and extend repo_scan.py to extract signatures + docstrings + raises
- [ ] Add a token budget: trim the repo map to fit N tokens, keeping public API first
- [ ] Add retrieval: given a section topic, fetch the 5 most relevant files
- [ ] Support one non-Python language (TypeScript or Go) in the repo map

## Phase 5 — Prompts & templates
- [ ] Read docs/05 and write a system prompt per Diátaxis type
- [ ] Make templates/ drive the writer (sections must match the template)
- [ ] Encode your style guide as checkable rules (e.g. no "simply", second person)
- [ ] A/B two prompt versions on 5 inputs and record which wins and why

## Phase 6 — Verification & evals
- [ ] Read docs/06 and make every code block in generated docs execute in CI
- [ ] Add a symbol check: every referenced function/class must exist in the repo
- [ ] Build an eval set of 10 cases with expected facts and score your agent
- [ ] Add an LLM-as-judge reviewer with a rubric; compare to your own grades

## Phase 7 — Docs-as-code in CI
- [ ] Read docs/07 and add a GitHub Action that regenerates reference docs on PR
- [ ] Add drift detection: flag doc pages whose source files changed
- [ ] Publish docs with MkDocs Material to GitHub Pages
- [ ] Make the agent open a PR (not push to main) with its changes

## Phase 8 — Capstone
- [ ] Pick a capstone from docs/08 and write a one-page design doc
- [ ] Build it, using the agent-harness repo as the runtime
- [ ] Evaluate it against your eval set and write up results
- [ ] Write a blog-style retrospective in PROGRESS.md
