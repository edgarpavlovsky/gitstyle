"""LLM client abstraction — defaults to Claude via Anthropic SDK."""

from __future__ import annotations

import json
import os
from typing import Optional

import anthropic


class LLMClient:
    """Thin wrapper around the Anthropic SDK for structured LLM calls."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")

        if api_key:
            self._client = anthropic.Anthropic(api_key=api_key)
            self._auth_method = "ANTHROPIC_API_KEY"
        elif auth_token:
            self._client = anthropic.Anthropic(auth_token=auth_token)
            self._auth_method = "ANTHROPIC_AUTH_TOKEN"
        else:
            raise RuntimeError(
                "No Anthropic API credentials found.\n\n"
                "Set one of the following:\n"
                "  export ANTHROPIC_API_KEY=sk-ant-...   # from console.anthropic.com\n"
                "  export ANTHROPIC_AUTH_TOKEN=...        # OAuth token\n\n"
                "Note: Claude CLI login (claude auth login) uses OAuth which is not\n"
                "yet supported by the Anthropic API for third-party tools."
            )

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
        max_tokens: int = 16384,
        temperature: float = 0.2,
        retries: int = 1,
    ) -> dict | list:
        """Send a prompt and parse the response as JSON. Retries on parse failure."""
        last_error = None
        for attempt in range(retries + 1):
            text = self.complete(system, prompt, max_tokens, temperature)
            extracted = self._extract_json_text(text)
            try:
                return json.loads(extracted)
            except json.JSONDecodeError as e:
                last_error = e
                if attempt < retries:
                    # Retry: ask the LLM to fix its own output
                    prompt = (
                        f"Your previous response was not valid JSON (error: {e}).\n"
                        f"Here is what you returned:\n```\n{text[:2000]}\n```\n\n"
                        f"Please return ONLY valid JSON matching the schema in your instructions. "
                        f"Original request:\n\n{prompt}"
                    )
        raise last_error  # type: ignore[misc]

    @staticmethod
    def _extract_json_text(text: str) -> str:
        """Extract JSON from markdown code blocks or raw text."""
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0]
        return text.strip()

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate (~4 chars per token)."""
        return len(text) // 4
