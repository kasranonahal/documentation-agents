# 04 — Understanding a codebase

The quality ceiling of a doc agent is set by what it *sees*. Dumping the whole repo into the prompt fails on any real project: it's too big, and attention degrades as context grows (see Anthropic, [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Aim for the **smallest set of high-signal tokens**.

## 1. Layers of context (cheapest first)

1. **Repo map** — file tree + public symbols + signatures + first docstring line. A few thousand tokens describe a whole medium project. (Idea popularised by [Aider's repo map](https://aider.chat/docs/repomap.html).)
2. **Targeted files** — the full text of the files the plan names.
3. **Retrieved snippets** — chunks found by search for a section's topic.
4. **Supporting signals** — tests (great source of usage examples!), CHANGELOG, ADRs, PR descriptions, issues (great source of "why" and FAQs).

## 2. Extracting structure
- Python: the `ast` module gives you functions, classes, args, defaults, decorators, docstrings, `raise` statements. See `src/docagent/repo_scan.py`.
- Many languages: [tree-sitter](https://tree-sitter.github.io/tree-sitter/) with per-language queries.
- APIs: OpenAPI / GraphQL schemas are already structured reference — parse them, don't ask the LLM to re-derive them.

## 3. Ranking what goes into context
- Public before private (`_name`).
- Things imported by many files before leaf utilities (PageRank on the import graph is a fun upgrade).
- Things the plan mentions before everything else.
- Then **cut to budget**: estimate tokens (≈ chars/4 is fine to start) and drop lowest-ranked items.

## 4. Retrieval options
| Approach | Pros | Cons |
|---|---|---|
| grep / ripgrep for symbol names | exact, free, explainable | misses concepts |
| BM25 over chunks | cheap, good for identifiers | weak semantics |
| Embeddings | concept matching | needs index, can drift |
| **Agentic search** (let the model call `grep`/`read_file` tools) | adapts, how coding agents work today | more calls, needs good tools |

Start with grep + agentic search; add embeddings only if evals show recall problems.

## 5. Tests are documentation gold
A test shows a real call with real inputs and asserted outputs — the best source for examples. Have the researcher look in `tests/` for every public symbol.

## Exercises
1. Extend `repo_scan.py` to capture parameters with types/defaults, return annotation and `raise` statements.
2. Add `--budget-tokens N` that trims the map, keeping public API first.
3. Add a `find_relevant(topic, k=5)` function (start with keyword overlap).
4. Add TypeScript or Go support via tree-sitter.
