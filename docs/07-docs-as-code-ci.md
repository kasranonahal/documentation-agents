# 07 — Docs-as-code in CI

## 1. Where the agent plugs in

```
developer opens PR ──► CI: tests ──► CI: doc-agent
                                       ├─ detect changed public API
                                       ├─ find doc pages that cite changed files (drift)
                                       ├─ regenerate / patch those pages
                                       ├─ run verifier
                                       └─ push commit to a docs/ branch + open PR or comment
```

## 2. Drift detection
Because every fact cites `path:line`, you can store a **source manifest** per page (`docs/.manifest.json`: page → list of source files + content hashes). On each PR:
1. Compute hashes of the cited files.
2. Pages whose sources changed are "possibly stale".
3. Re-run the researcher only for those pages; diff the fact sheets; if facts changed, patch the page.

This is cheaper and safer than regenerating everything.

## 3. Safety rules for a CI agent
- Never push to `main`. Open a PR or a review comment.
- Least-privilege token: `contents: write` only on a docs branch, `pull-requests: write`.
- Secrets: the API key is a repository secret; don't run the agent on PRs from forks (they can't access secrets anyway, and shouldn't steer your agent).
- Bound cost: max pages per run, max tokens per page.

## 4. Example workflow skeleton

```yaml
name: docs-agent
on:
  pull_request:
    paths: ["src/**"]
permissions:
  contents: write
  pull-requests: write
jobs:
  docs:
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e .
      - run: docagent drift --base origin/${{ github.base_ref }} --out out/
        env: { ANTHROPIC_API_KEY: "${{ secrets.ANTHROPIC_API_KEY }}" }
      # then: commit out/ changes to a branch and open a PR (e.g. peter-evans/create-pull-request)
```

## 5. Publishing
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/) + GitHub Pages: `mkdocs gh-deploy` from a workflow on `main`. Organise `docs/` into `tutorials/`, `how-to/`, `reference/`, `explanation/` — Diátaxis made visible.

## Exercises
1. Add the workflow above (start with `--fake` so it runs without secrets).
2. Implement `docagent drift` using the manifest idea.
3. Publish to GitHub Pages.
4. Make the agent open a PR via `gh pr create` or the create-pull-request action.
