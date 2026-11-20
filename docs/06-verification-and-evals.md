# 06 — Verification & evals

Two different questions:
- **Verification** — is *this* draft correct? (runs every time, blocks publishing)
- **Evaluation** — is *my agent* getting better or worse? (runs on a fixed dataset when you change prompts/code)

## 1. Deterministic verification (cheap, run first)
| Check | How |
|---|---|
| Code blocks run | Extract ```` ```python ```` blocks, run each in a subprocess with timeout; compare to shown output if present |
| Symbols exist | Find `identifier(` and `` `module.name` `` mentions; check against repo map |
| Links valid | Relative links → file exists; anchors → heading exists; external → HEAD request (in CI only) |
| Template followed | All required headings present |
| No TODOs | `TODO(fact)` means the researcher must go again |
| Style rules | Regex rules from Module 05 |

These are implemented as starters in `src/docagent/checks.py`.

## 2. Grounding check (LLM-assisted)
For each sentence that states a fact, ask a judge: "Is this claim supported by these source excerpts? Answer SUPPORTED / UNSUPPORTED / NOT_A_CLAIM." Unsupported claims go back to the editor. Keep the judge prompt narrow — one claim at a time is more reliable than "check this whole doc".

## 3. LLM-as-judge reviewer
- **Separate** model call, ideally a fresh context, with a rubric (see `evals/rubric.yaml`).
- Ask for a score **and** evidence (quote the offending line) per criterion — scores without evidence drift.
- **Calibrate**: grade 10 drafts yourself, then compare the judge's scores to yours. Adjust the rubric wording / add few-shot examples until they agree. Generators tend to praise their own work, so tune the judge to be skeptical.

## 4. Building an eval set
Each case in `evals/cases/` contains:
- `input`: the request + which repo/files
- `must_include`: facts that must appear (e.g. "default timeout is 30s")
- `must_not_include`: known hallucination traps (e.g. a flag that doesn't exist)
- `type`: expected Diátaxis type

Metrics per run:
- **Fact recall** = must_include found / total
- **Hallucination rate** = must_not_include found / total
- **Verifier pass rate**
- **Judge mean score**
- **Cost & latency**

Start with 10 cases. Grow it every time you find a new bug — every bug becomes a test case.

## 5. Regression discipline
Store results as `evals/results/<date>-<git-sha>.json`. Never merge a prompt change that lowers fact recall or raises hallucination rate.

## Exercises
1. Make code-block execution part of the verifier and CI.
2. Implement the symbol check against your extended repo map.
3. Write 10 eval cases; write `scripts/run_evals.py`; record the baseline.
4. Calibrate the judge against your own grades on 10 drafts; report agreement.
