"""LLM client abstraction — defaults to Claude via Anthropic SDK."""

from __future__ import annotations

import json
from typing import Optional

import anthropic


class LLMClient:
    """Thin wrapper around the Anthropic SDK for structured LLM calls."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self._client = anthropic.Anthropic()
        self.model = model

    def complete(
        self,
        system: str,
        prompt: str,
        max_tokens: int = 8192,
        temperature: float = 0.3,
    ) -> str:
        """Send a prompt and return the text response."""
        message = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def complete_json(
        self,
        system: str,
        prompt: str,
        max_tokens: int = 8192,
        temperature: float = 0.2,
    ) -> dict | list:
        """Send a prompt and parse the response as JSON."""
        text = self.complete(system, prompt, max_tokens, temperature)
        # Extract JSON from markdown code blocks if present
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0]
        return json.loads(text.strip())

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate (~4 chars per token)."""
        return len(text) // 4
