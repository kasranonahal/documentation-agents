# 02 — Agent fundamentals (applied to documentation)

Background reading: Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents). Its core advice: start with the simplest thing that works, call the LLM API directly before reaching for a framework, and add complexity only when it measurably helps.

## 1. Workflows vs agents
- **Workflow**: *your code* decides the steps; the LLM fills in each step. Predictable, testable, cheap.
- **Agent**: the LLM decides which step/tool comes next, in a loop, until done. Flexible, harder to control.

For documentation, **most of the pipeline should be a workflow** (plan → research → write → verify → review). Use agentic loops *inside* steps where exploration is needed — e.g. the Researcher deciding which files to open.

## 2. The building block: the augmented LLM
An LLM + **retrieval** (find relevant code/docs) + **tools** (read file, run code, check link) + **memory** (fact sheet, outline). Everything else composes this.

## 3. Five workflow patterns and their doc use-cases

| Pattern | How it works | Doc use-case |
|---|---|---|
| **Prompt chaining** | Fixed sequence; each output feeds the next; optional "gates" between | outline → draft → style polish |
| **Routing** | Classify input, send to a specialised prompt | request → tutorial / how-to / reference / explanation writer |
| **Parallelization** | Run sub-tasks concurrently (sectioning) or same task many times (voting) | write each reference section in parallel; 3 reviewers vote |
| **Orchestrator-workers** | An LLM splits work dynamically and delegates | "document this repo" → orchestrator picks pages, workers write them |
| **Evaluator-optimizer** | Generator writes, evaluator critiques, loop until pass | writer ↔ reviewer with rubric |

And then **autonomous agents**: a loop of `model → tool calls → results → model …` until the model stops. Covered in depth in the [agent-harness](https://github.com/kasranonahal/agent-harness) repo.

## 4. Minimal code for each pattern

```python
from anthropic import Anthropic
client = Anthropic()
MODEL = "claude-sonnet-5-5"

def llm(system: str, user: str) -> str:
    r = client.messages.create(model=MODEL, max_tokens=2000, system=system,
                               messages=[{"role": "user", "content": user}])
    return r.content[0].text

# Chaining
outline = llm("You plan documentation outlines.", f"Outline a how-to for:\n{code}")
draft   = llm("You write how-to guides.",        f"Outline:\n{outline}\n\nSource:\n{code}")

# Routing
kind = llm("Answer with one word: tutorial, howto, reference, explanation.", request).strip().lower()

# Evaluator-optimizer
for _ in range(3):
    critique = llm(RUBRIC_PROMPT, draft)
    if critique.startswith("PASS"):
        break
    draft = llm(WRITER_PROMPT, f"Revise using this critique:\n{critique}\n\nDraft:\n{draft}")
```

## 5. When NOT to use an agent
- Pure reference from docstrings → use mkdocstrings/Sphinx autodoc; let the agent *enrich* (examples, cross-links), not generate the signature table.
- One-off README → a single good prompt is enough.

## Exercises
1. Implement chaining (outline → draft → polish) for one function of your choice.
2. Implement routing with the four Diátaxis types; test on 8 hand-written requests; record accuracy.
3. Implement evaluator-optimizer with a 3-criterion rubric. Log how many iterations it takes to pass.
