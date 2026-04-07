---
title: "Code Structure"
category: style
confidence: high
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-sdk-typescript, anthropics/anthropic-cookbook, anthropics/courses, anthropics/claude-code]
related: [naming-conventions, patterns, dependencies, languages/python, languages/typescript]
last_updated: 2026-04-07
---

# Code Structure

## Resource-Based Client Architecture (Stainless Convention)

Both SDKs organize the client around API resources rather than HTTP verbs or endpoint paths. The top-level `Anthropic` client exposes namespaced resource objects — `client.messages`, `client.completions`, `client.beta` — each mapping to a logical API surface. This resource decomposition is a Stainless convention: the same pattern appears in OpenAI's SDK and other Stainless-generated clients. What varies per API company is the resource tree itself, not the structural approach. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

```python
# anthropic-sdk-python: resource-based access
client = Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

Each resource lives in its own module file. In the Python SDK, `anthropic/resources/messages.py` defines `Messages` and `AsyncMessages`. In the TypeScript SDK, `src/resources/messages.ts` mirrors the same structure. This one-file-per-resource rule keeps individual files focused and navigable. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

## Mirrored SDK Layouts

Anthropic maintains structural parity between the Python and TypeScript SDKs. The directory trees are intentionally parallel:

```
anthropic-sdk-python/              anthropic-sdk-typescript/
  src/anthropic/                     src/
    _client.py                         client.ts
    resources/                         resources/
      messages.py                        messages.ts
      completions.py                     completions.ts
      beta/                              beta/
        ...                                ...
    types/                             types/
      message.py                         message.ts
      message_create_params.py           message-create-params.ts
    _streaming.py                      streaming.ts
    _exceptions.py                     error.ts
```

This parity is a strategic choice for an API company: it lets Anthropic write documentation, migration guides, and conceptual explanations once, with language-specific details as the only variable. When a user reads a Python guide and switches to TypeScript, the resource hierarchy, method names, and type structures map directly. Commit messages confirm intentional synchronization: "mirror messages.create streaming from python SDK." [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

## Explicit Export Surfaces

The Python SDK defines `__all__` in every public module, creating a strict boundary between public API and internal implementation. The root `__init__.py` re-exports from submodules, building a curated top-level namespace. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

```python
# anthropic/__init__.py (simplified)
from .._client import Anthropic, AsyncAnthropic
from ..types import Message, MessageParam, ContentBlock
from .._exceptions import APIError, AuthenticationError, RateLimitError
from .._streaming import Stream, AsyncStream

__all__ = [
    "Anthropic",
    "AsyncAnthropic",
    "Message",
    "MessageParam",
    "ContentBlock",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "Stream",
    "AsyncStream",
]
```

Internal modules are prefixed with underscore (`_client.py`, `_streaming.py`, `_exceptions.py`) to signal they should not be imported directly. No public API lives in an underscore-prefixed module. See [[naming-conventions]] for the full prefix system.

## Types Directory as Schema Mirror

Both SDKs maintain a `types/` directory that mirrors the API schema. Each API object has a corresponding type definition file: `Message` in `types/message.py`, `MessageCreateParams` in `types/message_create_params.py`. These are generated from the OpenAPI spec via Stainless, ensuring the SDK always reflects the current API surface. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

The types directory is flat (no nested subdirectories for most resources) with one file per type. File name matches type name in snake_case — finding any API object's definition is a trivial lookup.

## Cookbook as Standalone Examples

The `anthropic-cookbook` follows a different structural philosophy: each recipe is a self-contained directory with its own README, dependencies, and runnable scripts. No shared library code across recipes. [f2b8c41](https://github.com/anthropics/anthropic-cookbook/commit/f2b8c41)

```
anthropic-cookbook/
  misc/
    prompt_caching.ipynb
    tool_use.ipynb
  third_party/
    langchain/
      README.md
      langchain_tool_use.ipynb
    ...
```

This "self-contained recipe" pattern prioritizes copy-paste usability over DRY. Each notebook can be run in isolation, and recipes never rot when other recipes change. The isolation also mirrors how SDK users actually work: they grab one example, not the whole cookbook.

## Courses as Progressive Modules

The `courses` repository organizes educational content as numbered modules that build on each other but remain independently runnable. Each module contains a README, Jupyter notebooks, and supporting Python files. This progressive structure reveals Anthropic's pedagogical approach: start with basic API calls, layer in streaming, then tool use, then agents — mirroring the SDK's own complexity gradient. [a9c1d47](https://github.com/anthropics/courses/commit/a9c1d47)

The connection between courses and SDK design is worth noting: course examples use the SDK's native patterns (context-managed streams, typed content blocks, keyword-only arguments) rather than simplified wrappers. Students learn the real API surface from the start, which means the SDK's ergonomic choices — like making `messages.create()` the primary entry point — directly shape the learning experience.

## No Deep Nesting

Across all repositories, maximum directory depth is 3-4 levels. The SDKs use `src/anthropic/resources/beta/` as the deepest path. When a new feature area emerges (e.g., beta endpoints), it gets a single subdirectory, not a parallel hierarchy. This flatness is partly a Stainless design choice and partly Anthropic's own preference for navigability. [b5e7f93](https://github.com/anthropics/anthropic-sdk-python/commit/b5e7f93)
