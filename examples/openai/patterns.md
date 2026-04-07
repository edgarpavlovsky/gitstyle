---
title: "Patterns & Architecture"
category: style
confidence: high
sources: [openai/openai-python, openai/openai-node, openai/tiktoken, openai/whisper, openai/CLIP, openai/gym, openai/openai-cookbook]
related: [code-structure, type-discipline, dependencies, languages/python, languages/typescript]
last_updated: 2026-04-07
---

# Patterns & Architecture

## Resource Client Pattern (SDKs, Stainless-Generated)

The central SDK pattern is the resource client, borrowed from Stripe's API design via the Stainless code generator. A top-level `OpenAI` client holds resource objects as attributes; each resource exposes CRUD methods that delegate to `self._post()`, `self._get()`, `self._delete()` on a shared HTTP client. The resource classes are thin routing layers — authentication, retries, and response parsing all live in the base client. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21) [b8c4d19](https://github.com/openai/openai-python/commit/b8c4d19)

```python
client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
job = client.fine_tuning.jobs.create(
    training_file="file-abc123",
    model="gpt-4o-mini"
)
```

## Server-Sent Events Streaming

Both SDKs use SSE for streaming, with a custom parser rather than a third-party library. The `stream=True` parameter switches the return type from a concrete model to a typed iterator of delta chunks. The Python SDK wraps this in `Stream[ChatCompletionChunk]`; the Node SDK returns `AsyncIterable<ChatCompletionChunk>`. Both provide `.close()` for early termination. [c7a3e18](https://github.com/openai/openai-python/commit/c7a3e18) [d2f1a93](https://github.com/openai/openai-python/commit/d2f1a93)

```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Count to 10"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

## Structured Error Hierarchy (Stainless-Generated)

SDK error handling uses a typed exception hierarchy rooted at `APIError`, with each HTTP status code mapped to a specific class: `AuthenticationError` (401), `PermissionDeniedError` (403), `NotFoundError` (404), `RateLimitError` (429), `InternalServerError` (>=500). This mirrors Stripe's `stripe.error` hierarchy — it is a Stainless convention, not an OpenAI-specific design. Each exception carries `status_code`, `message`, `body`, and `code` for programmatic handling. [e5b7c41](https://github.com/openai/openai-python/commit/e5b7c41)

```python
try:
    client.chat.completions.create(...)
except RateLimitError:
    # 429 — back off and retry
except AuthenticationError:
    # 401 — invalid API key
except APIConnectionError:
    # network-level failure
except APIError as e:
    # catch-all
    print(e.status_code, e.message)
```

## Automatic Retries with Exponential Backoff (Stainless-Generated)

Both SDKs retry transient failures (connection errors, 408, 409, 429, >=500) with exponential backoff, defaulting to 2 retries. Configurable at client construction and per-request. The retry logic respects `Retry-After` headers. This is Stainless-generated behavior, consistent across both SDKs. [f8a2c64](https://github.com/openai/openai-python/commit/f8a2c64)

```python
client = OpenAI(max_retries=5)
client.chat.completions.create(..., max_retries=0)  # per-request override
```

## Keyword-Only Arguments in SDKs

All SDK resource methods use keyword-only arguments (after `*` in Python, options objects in TypeScript). Positional arguments are never accepted for API parameters. This prevents argument-order bugs and makes calls self-documenting — a Stainless convention enforced across both SDKs. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

## Research Code: Raw PyTorch nn.Module

Research repos follow standard PyTorch conventions without deviation. Models inherit `nn.Module`, define layers in `__init__`, implement `forward()`. No Lightning, no Accelerate, no custom training frameworks — raw PyTorch throughout Whisper, CLIP, and gym's neural network policies. See [[dependencies]] for why. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

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

## gym: Abstract Interface + Registry Pattern

Gym established the interface + registry pattern that became the industry standard for RL environments. The `Env` base class defines the contract (`step`, `reset`, `render`); `gym.make("CartPole-v1")` resolves a string ID to a concrete class via a global registry. [f1a9d52](https://github.com/openai/gym/commit/f1a9d52)

```python
gym.register(
    id='CartPole-v1',
    entry_point='gym.envs.classic_control:CartPoleEnv',
    max_episode_steps=500,
)
env = gym.make('CartPole-v1')
observation, info = env.reset()
observation, reward, terminated, truncated, info = env.step(action)
```

The wrapper pattern is equally influential: `TimeLimit`, `RecordVideo`, `FlattenObservation` decorate an `Env` instance without modifying it — the decorator pattern applied at the application architecture level.

The historical significance bears emphasizing: gym's `Env` interface and registry became the de facto standard for RL environments industry-wide. Gymnasium (the maintained fork), PettingZoo (multi-agent), and virtually every RL library since 2016 implements or extends gym's interface. The `step() -> (obs, reward, terminated, truncated, info)` signature is as canonical in RL as `forward()` is in PyTorch. Few open-source projects have defined an interface that an entire subfield adopted wholesale.

## Dataclass Configuration in Research Code

Research repos use `@dataclass` for model configuration rather than Pydantic `BaseModel`. The choice is deliberate: research code avoids the Pydantic dependency entirely, while SDK code leverages it for validation and serialization. This is one of the clearest markers for identifying which "side" of the org a piece of code comes from. See [[type-discipline]]. [e7f2c83](https://github.com/openai/whisper/commit/e7f2c83)

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

## Cookbook: Example-Driven Pattern Documentation

The openai-cookbook functions as a pattern library. Each Jupyter notebook demonstrates a complete use case (RAG, function calling, embeddings, fine-tuning) with a consistent structure: motivation, setup, step-by-step implementation, evaluation. [c1d4e87](https://github.com/openai/openai-cookbook/commit/c1d4e87)

## Context Manager Pattern for Resources

Both SDKs support context manager usage for automatic resource cleanup, particularly important for streaming connections. [d2f1a93](https://github.com/openai/openai-python/commit/d2f1a93)

```python
with client.chat.completions.create(
    model="gpt-4", messages=[...], stream=True,
) as stream:
    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")
# connection automatically closed on exit
```
