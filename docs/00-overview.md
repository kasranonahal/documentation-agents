# 00 — Overview & mental model

## The one-sentence goal
Build a system that turns **sources of truth** (code, configs, specs, existing docs) into **documentation a specific reader can act on**, and that **proves** what it wrote is correct.

## The system on one page

```
            ┌──────────────────────────── sources of truth ────────────────────────────┐
            │  code  ·  OpenAPI / schemas  ·  configs  ·  tests  ·  existing docs  ·  issues │
            └───────────────────────────────────────┬───────────────────────────────────┘
                                                    │  (Module 04: understand the codebase)
                                                    ▼
 request ──► PLANNER ──► outline (per Diátaxis type, Module 01/05)
                │
                ▼
            RESEARCHER ──► fact sheet with citations  (file:line)
                │
                ▼
            WRITER ──► draft that follows a template + style guide
                │
                ▼
            VERIFIER (deterministic) ──► links ok? code runs? symbols exist? (Module 06)
                │            ▲
                ▼            │ fix list
            REVIEWER (LLM judge, separate prompt + rubric) ──┘
                │
                ▼
            PUBLISH  (PR, not direct push — Module 07)
```

## Three ideas to hold on to

1. **Docs are a product for a reader.** Every page answers one reader's question in one mode (learn / do / look up / understand). An agent that doesn't know *which* is writing mush.
2. **Grounding beats eloquence.** The most common failure of LLM docs is confident invention: functions that don't exist, flags with the wrong name. Every claim should trace to a source.
3. **Never let the writer grade itself alone.** Separate the generator from the evaluator, and put cheap deterministic checks *before* the LLM judge.

## What "done" looks like for this repo
By the end of Phase 8 you should have an agent that, given a repo, opens a PR containing a reference page and a how-to guide, where every code sample executes, every symbol exists, and a reviewer score ≥ 4/5 on your rubric — and that re-runs when the code changes.

## Exercises
1. Find one piece of AI-generated documentation online that is wrong. Write down *why* it went wrong (no grounding? wrong audience? stale?).
2. Sketch the diagram above from memory.
