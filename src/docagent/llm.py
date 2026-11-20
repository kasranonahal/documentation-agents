"""LLM clients.

`AnthropicLLM` calls the real API. `FakeLLM` returns canned answers so the whole
pipeline (and the tests) run offline with no API key. Both expose the same
`complete(system, user) -> str` method, so pipeline code never cares which one it has.
"""

from __future__ import annotations

import json
import os
from typing import Protocol

DEFAULT_MODEL = os.environ.get("DOCAGENT_MODEL", "claude-sonnet-5-5")


class LLM(Protocol):
    def complete(self, system: str, user: str, max_tokens: int = 4000) -> str: ...


class AnthropicLLM:
    def __init__(self, model: str = DEFAULT_MODEL):
        from anthropic import Anthropic  # imported lazily so --fake needs no SDK

        self.client = Anthropic()
        self.model = model

    def complete(self, system: str, user: str, max_tokens: int = 4000) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(block.text for block in resp.content if block.type == "text")


class FakeLLM:
    """Deterministic stand-in. Routes on a ROLE tag at the start of the system prompt."""

    def complete(self, system: str, user: str, max_tokens: int = 4000) -> str:
        if system.startswith("ROLE: planner"):
            return json.dumps(
                {
                    "title": "Reference",
                    "doc_type": "reference",
                    "audience": "Developers using this package",
                    "sections": ["Overview", "API"],
                    "sources": [],
                }
            )
        if system.startswith("ROLE: researcher"):
            return json.dumps([{"claim": "The package exposes public functions.", "source": "repo map"}])
        if system.startswith("ROLE: writer"):
            return "# Reference\n\n## Overview\n\nThis page lists the public API.\n\n## API\n\nSee the repo map.\n"
        if system.startswith("ROLE: reviewer"):
            return json.dumps({"scores": {"accuracy": 4, "completeness": 3, "clarity": 4}, "fixes": []})
        if system.startswith("ROLE: editor"):
            return user.split("DRAFT:\n", 1)[-1]
        return "ok"


def get_llm(fake: bool = False) -> LLM:
    return FakeLLM() if fake else AnthropicLLM()
