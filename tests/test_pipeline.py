from pathlib import Path

from docagent import checks
from docagent.llm import FakeLLM
from docagent.pipeline import run
from docagent.repo_scan import known_symbols, render_map, scan_repo

SRC = Path(__file__).resolve().parents[1] / "src"


def test_repo_map_finds_public_symbols():
    maps = scan_repo(SRC)
    text = render_map(maps)
    assert "scan_repo" in text
    assert "repo_scan.py:" in text  # citable location
    assert "scan_repo" in known_symbols(maps)


def test_pipeline_runs_offline(tmp_path):
    result = run(FakeLLM(), SRC, "reference", out_dir=tmp_path, run_code=False)
    assert (tmp_path / "reference.md").exists()
    assert (tmp_path / "plan.json").exists()
    assert result.plan.doc_type == "reference"


def test_checks_catch_common_problems(tmp_path):
    md = (
        "# T\n\nSimply call `made_up_fn()`.\n\n```\nno lang\n```\n\n"
        "[x](missing.md)\n\nTODO(fact): default timeout\n\n"
        "```python\nraise SystemExit(1)\n```\n"
    )
    problems = checks.run_all(md, base_dir=tmp_path, known={"real_fn"}, template="## Overview\n")
    joined = "\n".join(problems)
    assert "banned word: 'simply'" in joined
    assert "unknown symbol referenced: made_up_fn()" in joined
    assert "no language tag" in joined
    assert "broken relative link" in joined
    assert "TODO(fact)" in joined
    assert "missing section: 'Overview'" in joined
    assert "python block #2 failed" in joined
