"""LLM client abstraction wrapping the Anthropic SDK."""

from __future__ import annotations

import json
from typing import Any

import anthropic

from gitstyle.config import LLMConfig


class LLMClient:
    """Wrapper around Anthropic's Messages API."""

    def __init__(self, config: LLMConfig) -> None:
        self._config = config
        self._client = anthropic.Anthropic(api_key=config.api_key)

    def complete(self, system: str, prompt: str, max_tokens: int | None = None) -> str:
        resp = self._client.messages.create(
            model=self._config.model,
            max_tokens=max_tokens or self._config.max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text

    def complete_json(self, system: str, prompt: str, max_tokens: int | None = None) -> Any:
        text = self.complete(system, prompt, max_tokens)
        # Extract JSON from possible markdown fences
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last lines (fences)
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        return json.loads(text)
