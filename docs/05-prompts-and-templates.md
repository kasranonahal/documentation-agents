# 05 — Prompts & templates

## 1. Anatomy of a writer system prompt
Write prompts at the "right altitude": specific enough to steer, not a brittle pile of if-then rules. A good structure:

```
<role>       who you are and who the reader is
<task>       the one doc type you write and its purpose
<rules>      the type's rules (from Module 01) + grounding rule
<style>      your style guide, condensed
<format>     the template to fill, exact headings
<examples>   1–2 short gold examples (few-shot)
```

### The grounding rule (put it in every writer prompt)
> Use only facts from the provided fact sheet and source excerpts. If something you need is missing, write `TODO(fact): <what is missing>` instead of guessing. Never invent function names, parameters, flags, defaults, or outputs.

## 2. Per-type prompt snippets

**Tutorial**
> You write tutorials for beginners. Provide one path that is guaranteed to work. Number every step. After each step, show what the reader should see. Don't offer alternatives or explain theory; link to explanation pages instead.

**How-to**
> You write how-to guides for competent users with a specific goal. Title starts with "How to". Begin with prerequisites. Steps in order. Cover common variations briefly at the end. Don't teach basics.

**Reference**
> You write reference documentation. Mirror the code's structure. For every public symbol: signature, one-sentence description, parameters table (name, type, default, description), return value, raised exceptions, one minimal example. Neutral, austere, complete.

**Explanation**
> You write explanations of design and concepts. Discuss why things are the way they are, alternatives considered, and trade-offs, citing the provided design records. No step-by-step instructions.

## 3. Templates
Templates in `templates/` define required headings. The verifier checks that every `##` heading from the template appears in the draft. This turns "follow the format" from a hope into a check.

## 4. Style rules as code
Turn your style guide into checks:
- Banned words regex: `\b(simply|just|easy|obviously)\b`
- Heading case: sentence case
- Code fences must have a language tag
- Max sentence length (e.g. 30 words)

Start with Python checks in `checks.py`; graduate to [Vale](https://vale.sh/).

## 5. Structured outputs
For planner/reviewer, ask for JSON and validate it (or use tool-use with an input schema — the model must "call" a `submit_plan` tool whose schema is your dataclass). Re-ask on validation failure, max 2 times.

## 6. Prompt iteration discipline
- Change one thing at a time.
- Run your eval set (Module 06) before and after.
- Keep prompts in version-controlled files, not inline strings, once they stabilise.

## Exercises
1. Write the 4 system prompts into `src/docagent/prompts/`.
2. Make the writer load the matching template and the verifier enforce headings.
3. Encode 5 style rules in `checks.py`.
4. A/B two writer prompts on 5 inputs; log results in PROGRESS.md.
