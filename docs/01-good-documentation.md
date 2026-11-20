# 01 — What good documentation is

You can't build an agent that writes good docs until you can say precisely what "good" means. This module gives you that vocabulary.

## 1. Diátaxis: four kinds of documentation

Diátaxis (by Daniele Procida, [diataxis.fr](https://diataxis.fr/)) sorts documentation by **what the reader needs right now**, along two axes:

|                      | **Practical** (doing)        | **Theoretical** (knowing)   |
|----------------------|------------------------------|-----------------------------|
| **Acquiring skill** (study) | **Tutorial** — learning-oriented | **Explanation** — understanding-oriented |
| **Applying skill** (work)   | **How-to guide** — goal-oriented | **Reference** — information-oriented |

### Tutorial
- Reader: a beginner who wants to *learn by doing*.
- Promise: "follow this and you will succeed."
- Rules: one guaranteed path; concrete steps; show results after each step; no choices, no digressions; minimal explanation (link out instead).
- Agent failure mode: adds options and caveats ("you could also…"), skips "what you should see now".

### How-to guide
- Reader: someone competent with a specific goal ("rotate the API key").
- Rules: title is the goal ("How to …"); assumes knowledge; steps in order; handles real-world variations; no teaching.
- Agent failure mode: turns into a tutorial (explains basics) or into reference (lists every flag).

### Reference
- Reader: someone working who needs to *look up* a fact.
- Rules: austere, complete, consistent structure mirroring the code (module → class → method); describe, don't instruct; examples short.
- Agent failure mode: incomplete (misses parameters), inconsistent structure, invented parameters. **This is where grounding matters most** — and where deterministic tools (autodoc) should do most of the work.

### Explanation
- Reader: someone who wants to *understand* why.
- Rules: discusses context, design decisions, alternatives, trade-offs; can have opinions; no step-by-step.
- Agent failure mode: generic filler ("X is a powerful tool that…"); no real design rationale because the agent can't see it — feed it ADRs, PR descriptions, issues.

**Rule for your agent:** every page has exactly one type. If a request mixes types, the planner splits it.

## 2. Audience
Before writing, the agent needs: *who* (role, prior knowledge), *what they're trying to do*, *where they came from* (landing from search? from the tutorial?). Put these in the plan as explicit fields.

## 3. Style essentials (condensed from Google / Microsoft style guides)
- Second person ("you"), present tense, active voice.
- Lead with the point. Put the condition before the instruction ("To X, do Y").
- One idea per sentence; short paragraphs; descriptive headings in sentence case.
- No "simply", "just", "easy", "obviously" — they insult the stuck reader.
- Code: complete, copy-pasteable, with language tags; show expected output.
- Define every acronym on first use. Consistent terminology — pick one word per concept.
- Links: descriptive text, never "click here".

## 4. Docs-as-code
Docs live in the repo, in plain text (Markdown), reviewed in PRs, tested in CI, published automatically. This is what makes agents useful: they can participate in the same PR workflow as humans.

## 5. A quality checklist you'll reuse as an eval rubric
| Criterion | Question |
|---|---|
| Type-fit | Does the page stay in one Diátaxis mode? |
| Accuracy | Is every claim traceable to a source? |
| Completeness | Are all public params / steps / prerequisites covered? |
| Runnability | Do code samples execute and produce the shown output? |
| Clarity | Could the target reader act on it without asking someone? |
| Style | Does it follow the style guide? |
| Findability | Clear title, headings, links in and out? |

## Exercises
1. Classify 10 pages from 3 OSS projects (e.g. FastAPI, Django, Kubernetes) by Diátaxis type. Note any that mix types.
2. Write your personal style guide (≤ 1 page). It becomes your agent's style rules in Module 05.
3. Hand-write a tutorial + reference page for one small project of yours. These become "gold" examples for evals.
