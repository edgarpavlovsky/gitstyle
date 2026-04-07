---
title: "Patterns & Architecture"
category: style
confidence: high
sources: [openai/openai-python, openai/openai-node, openai/tiktoken, openai/whisper, openai/CLIP, openai/gym, openai/openai-cookbook]
related: [code-structure, type-discipline, dependencies, languages/python, languages/typescript]
last_updated: 2026-04-07
---

# Patterns & Architecture

## Resource Client Pattern (SDKs)

The central architectural pattern in OpenAI's SDKs is the resource client, directly borrowed from Stripe's API design. A top-level `OpenAI` client holds resource objects as attributes, and each resource exposes CRUD methods. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```python
client = OpenAI()

# resource access via attribute chain
completion = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# nested resources use dot notation
job = client.fine_tuning.jobs.create(
    training_file="file-abc123",
    model="gpt-4o-mini"
)
```

Every resource method ultimately delegates to `self._post()`, `self._get()`, `self._delete()` on the base client, which handles authentication, retries, and response parsing. This single-dispatch-through-HTTP pattern keeps the resource classes thin — they are routing layers over a shared HTTP client. [b8c4d19](https://github.com/openai/openai-python/commit/b8c4d19)

## Server-Sent Events Streaming

OpenAI standardizes on Server-Sent Events (SSE) for streaming responses across both SDKs. The `stream=True` parameter switches the return type from a concrete model to an iterator of delta chunks. The implementation uses a custom SSE parser rather than a third-party library. [c7a3e18](https://github.com/openai/openai-python/commit/c7a3e18)

```python
# streaming returns an iterator of typed chunks
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Count to 10"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

The Python SDK wraps this in a `Stream[ChatCompletionChunk]` generic type, and the Node SDK returns an `AsyncIterable<ChatCompletionChunk>`. Both provide `.close()` for early termination. The async variants yield from an async iterator. [d2f1a93](https://github.com/openai/openai-python/commit/d2f1a93)

## Structured Error Hierarchy

SDK error handling uses a typed exception hierarchy rooted at `APIError`. Each HTTP status code maps to a specific exception class: `AuthenticationError` (401), `PermissionDeniedError` (403), `NotFoundError` (404), `RateLimitError` (429), `InternalServerError` (>=500). [e5b7c41](https://github.com/openai/openai-python/commit/e5b7c41)

```python
from openai import (
    APIError,
    APIConnectionError,
    RateLimitError,
    AuthenticationError,
    BadRequestError,
)

try:
    client.chat.completions.create(...)
except RateLimitError:
    # 429 — back off and retry
except AuthenticationError:
    # 401 — invalid API key
except APIConnectionError:
    # network-level failure
except APIError as e:
    # catch-all for other API errors
    print(e.status_code, e.message)
```

This mirrors Stripe's `stripe.error` hierarchy. Each exception carries `status_code`, `message`, `body`, and `code` attributes for programmatic handling. See [[type-discipline]] for how these integrate with type checkers.

## Automatic Retries with Exponential Backoff

Both SDKs implement automatic retry logic for transient failures (connection errors, 408, 409, 429, >=500). The default is 2 retries with exponential backoff. Retry count is configurable at client construction and per-request. [f8a2c64](https://github.com/openai/openai-python/commit/f8a2c64)

```python
# client-level default
client = OpenAI(max_retries=5)

# per-request override
client.chat.completions.create(
    ...,
    max_retries=0  # disable retries for this call
)
```

The retry logic respects `Retry-After` headers from 429 responses. This is Stainless-generated behavior, consistent across openai-python and openai-node.

## Keyword-Only Arguments in SDKs

All SDK resource methods use keyword-only arguments (after `*` in Python, named options objects in TypeScript). Positional arguments are never accepted for API parameters. This prevents argument-order bugs and makes calls self-documenting. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```python
# correct — keyword-only
client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    temperature=0.7,
)

# this would raise TypeError — no positional args
# client.chat.completions.create("gpt-4", [...])
```

## Research Code: PyTorch nn.Module Pattern

Research repositories follow standard PyTorch conventions. Models inherit from `nn.Module`, define layers in `__init__`, and implement `forward()`. Whisper, CLIP, and gym's neural network policies all follow this pattern without deviation. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

```python
# whisper/model.py
class AudioEncoder(nn.Module):
    def __init__(self, n_mels, n_ctx, n_state, n_head, n_layer):
        super().__init__()
        self.conv1 = nn.Conv1d(n_mels, n_state, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(n_state, n_state, kernel_size=3, stride=2, padding=1)
        self.blocks = nn.ModuleList(
            [ResidualAttentionBlock(n_state, n_head) for _ in range(n_layer)]
        )
        self.ln_post = nn.LayerNorm(n_state)

    def forward(self, x: Tensor) -> Tensor:
        x = F.gelu(self.conv1(x))
        x = F.gelu(self.conv2(x))
        ...
```

No custom training frameworks, no Lightning, no Accelerate wrappers — raw PyTorch. See [[dependencies]] for why.

## gym: Abstract Interface + Registry Pattern

Gym established the interface + registry pattern that became standard for RL environments. The `Env` base class defines the contract (`step`, `reset`, `render`), and `gym.make("CartPole-v1")` resolves a string ID to a concrete class via a global registry. [f1a9d52](https://github.com/openai/gym/commit/f1a9d52)

```python
# registration
gym.register(
    id='CartPole-v1',
    entry_point='gym.envs.classic_control:CartPoleEnv',
    max_episode_steps=500,
)

# resolution
env = gym.make('CartPole-v1')
observation, info = env.reset()
observation, reward, terminated, truncated, info = env.step(action)
```

The wrapper pattern in gym is equally influential: `TimeLimit`, `RecordVideo`, `FlattenObservation` all decorate an `Env` instance, adding behavior without modifying the underlying environment. This is the decorator pattern applied at the application architecture level.

## Dataclass Configuration in Research Code

Research repos use Python dataclasses for model configuration, similar to many ML projects. Whisper's `ModelDimensions` and CLIP's model constructors take configuration as structured data with explicit fields. [e7f2c83](https://github.com/openai/whisper/commit/e7f2c83)

```python
@dataclass
class ModelDimensions:
    n_mels: int
    n_audio_ctx: int
    n_audio_state: int
    n_audio_head: int
    n_audio_layer: int
    n_vocab: int
    n_text_ctx: int
    n_text_state: int
    n_text_head: int
    n_text_layer: int
```

This contrasts with the SDK code, which uses Pydantic `BaseModel` for all structured data. The choice is deliberate — research code avoids the Pydantic dependency, while SDK code leverages it for validation and serialization. See [[type-discipline]].

## Cookbook: Example-Driven Pattern Documentation

The openai-cookbook repository functions as the organization's pattern library. Each Jupyter notebook demonstrates a complete use case: RAG, function calling, embeddings for search, fine-tuning workflows. Notebooks follow a consistent structure: motivation section, setup, step-by-step implementation, evaluation. [c1d4e87](https://github.com/openai/openai-cookbook/commit/c1d4e87)

```python
# typical cookbook cell structure:
# Cell 1: imports and client setup
# Cell 2: data preparation
# Cell 3: API call with explanation
# Cell 4: result processing
# Cell 5: evaluation / visualization
```

The cookbook notably demonstrates patterns using multiple model providers — not just OpenAI's API but also open-source models — reflecting the organization's position as both an API provider and a contributor to the broader ecosystem.

## Context Manager Pattern for Resources

Both SDKs support context manager usage for automatic resource cleanup, particularly important for streaming connections. [d2f1a93](https://github.com/openai/openai-python/commit/d2f1a93)

```python
with client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    stream=True,
) as stream:
    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")
# connection automatically closed on exit

# also for the client itself
with OpenAI() as client:
    client.chat.completions.create(...)
# underlying httpx client closed
```
