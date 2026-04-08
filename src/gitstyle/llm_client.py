"""LLM client abstraction — defaults to Claude via Anthropic SDK."""

from __future__ import annotations

import json
import os
import time
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

    # Transient error types that should be retried with backoff
    _RETRYABLE_ERRORS = ("overloaded_error", "rate_limit_error")
    _MAX_RETRIES = 5
    _BASE_DELAY = 2.0  # seconds — doubles each retry (2, 4, 8, 16, 32)

    def complete(
        self,
        system: str,
        prompt: str,
        max_tokens: int = 8192,
        temperature: float = 0.3,
    ) -> str:
        """Send a prompt and return the text response.

        Uses streaming to avoid timeout errors with large models (e.g. Opus)
        where requests may exceed 10 minutes. Retries on transient API errors
        (overloaded, rate limit) with exponential backoff.
        """
        last_error = None
        for attempt in range(self._MAX_RETRIES + 1):
            try:
                with self._client.messages.stream(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                ) as stream:
                    message = stream.get_final_message()
                self._last_stop_reason = message.stop_reason
                return message.content[0].text
            except anthropic.APIStatusError as e:
                error_type = getattr(e.body, "get", lambda *a: None) if not isinstance(e.body, dict) else e.body.get
                err_type = error_type("error", {}).get("type", "") if callable(error_type) else ""
                # Also check dict-style body
                if isinstance(e.body, dict):
                    err_type = e.body.get("error", {}).get("type", "")

                is_retryable = (
                    err_type in self._RETRYABLE_ERRORS
                    or e.status_code == 429
                    or e.status_code >= 500
                )
                if is_retryable and attempt < self._MAX_RETRIES:
                    delay = self._BASE_DELAY * (2 ** attempt)
                    last_error = e
                    time.sleep(delay)
                    continue
                raise
        raise last_error  # type: ignore[misc]

    def complete_json(
        self,
        system: str,
        prompt: str,
        max_tokens: int = 32768,
        temperature: float = 0.2,
        retries: int = 1,
    ) -> dict | list:
        """Send a prompt and parse the response as JSON. Retries on parse failure.

        If the response is truncated (hit max_tokens), retries with higher limit.
        """
        last_error = None
        current_max_tokens = max_tokens
        for attempt in range(retries + 1):
            text = self.complete(system, prompt, current_max_tokens, temperature)
            # Detect truncation — if the model hit max_tokens, the JSON is incomplete
            if getattr(self, "_last_stop_reason", None) == "max_tokens" and attempt < retries:
                current_max_tokens = min(current_max_tokens * 2, 65536)
                continue
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
