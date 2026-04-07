---
title: "Dependencies"
category: style
confidence: high
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-sdk-typescript, anthropics/anthropic-cookbook, anthropics/claude-code]
related: [code-structure, patterns, languages/python, languages/typescript]
last_updated: 2026-04-07
---

# Dependencies

## httpx as the HTTP Foundation (Python)

Anthropic's Python SDK is built on `httpx`, not `requests`. This is a deliberate choice: httpx provides native async support (`httpx.AsyncClient`), HTTP/2, and streaming response iteration — all requirements for an SDK that is async-first and streaming-first. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

```python
# from _base_client.py
import httpx

class SyncHttpxClientWrapper:
    _client: httpx.Client

class AsyncHttpxClientWrapper:
    _client: httpx.AsyncClient
```

The httpx client is wrapped but not abstracted away — the SDK's transport layer is thin enough that httpx idioms (timeouts, transport configuration, proxy settings) pass through to users who need them.

## Pydantic for Data Modeling (Python)

All API response types are Pydantic v2 `BaseModel` subclasses. Anthropic uses Pydantic for runtime validation, JSON serialization/deserialization, and schema generation. The dependency on Pydantic is deep — it is not a thin wrapper but the foundation of the type system. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

```python
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Literal

class Message(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    type: Literal["message"]
    role: Literal["assistant"]
    content: List[ContentBlock]
    model: str
    stop_reason: Optional[StopReason]
    usage: Usage
```

The `extra="allow"` config is standard across all response models, enabling forward compatibility — when the API adds new fields, existing SDK versions continue to work.

## Minimal Dependency Surface (Python)

The Python SDK's runtime dependencies are intentionally few: `httpx`, `pydantic`, `typing-extensions`, `distro`, `sniffio`, `anyio`, and `tokenizers` (optional). There are no utility grab-bag dependencies like `requests`, `urllib3`, `click`, or `attrs`. Each dependency serves a specific, non-overlapping purpose. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

| Dependency | Purpose |
|------------|---------|
| httpx | HTTP transport (sync + async) |
| pydantic | Response modeling and validation |
| typing-extensions | Backport type constructs (`Required`, `override`) |
| anyio | Async runtime compatibility (asyncio + trio) |
| sniffio | Detect current async library |
| distro | OS identification for user-agent string |
| tokenizers | Optional: client-side token counting |

## node-fetch and TypeScript Ecosystem

The TypeScript SDK depends on `node-fetch` for HTTP in Node.js environments and uses the native `fetch` in edge runtimes. Dependencies include `@anthropic-ai/sdk` internal packages, `web-streams-polyfill` for streaming in older Node versions, and `abort-controller` for request cancellation. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

The TypeScript dependency footprint is similarly minimal — no Express, no Axios, no lodash. The SDK is designed to work in Node.js, Deno, Bun, and Cloudflare Workers without pulling in environment-specific frameworks.

## typing-extensions for Backport Support

The Python SDK depends on `typing-extensions` to use modern type constructs on older Python versions. Key imports include `Required` (for TypedDict fields), `override` (decorator signaling method overrides), `Literal`, and `TypeGuard`. This enables writing modern typed code while supporting Python 3.8+. [f4a1c39](https://github.com/anthropics/anthropic-sdk-python/commit/f4a1c39)

```python
from typing_extensions import Required, override, Literal, TypeGuard
```

## No Framework Dependencies in Cookbook

Cookbook examples install only the `anthropic` SDK plus whatever third-party integration is being demonstrated (e.g., `langchain`, `llama-index`). There is no shared cookbook framework or utility library. Each recipe's `requirements.txt` is self-contained and minimal. [f2b8c41](https://github.com/anthropics/anthropic-cookbook/commit/f2b8c41)

```
# typical cookbook recipe requirements.txt
anthropic>=0.30.0
```

When a recipe demonstrates a third-party integration, that integration's package is the only addition. No kitchen-sink requirements.

## Rye/uv for Python Project Management

Anthropic's Python repositories use modern Python project management tooling. The SDK uses `pyproject.toml` with Hatch as the build backend. Development dependencies (pytest, mypy, pyright, ruff) are specified in `[project.optional-dependencies]` rather than a separate `requirements-dev.txt`. [b5e7f93](https://github.com/anthropics/anthropic-sdk-python/commit/b5e7f93)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "anthropic"
dependencies = [
    "httpx>=0.23.0,<1",
    "pydantic>=1.9.0,<3",
    "typing-extensions>=4.7,<5",
    "anyio>=3.5.0,<5",
    "distro>=1.7.0,<2",
    "sniffio",
]
```

## Version Pinning Strategy

Runtime dependencies use lower-bound pins with upper-bound major version constraints: `httpx>=0.23.0,<1`, `pydantic>=1.9.0,<3`. This balances stability (known minimum working version) with flexibility (users aren't forced to match exact versions). Development dependencies are pinned more tightly. [a7e3b14](https://github.com/anthropics/anthropic-sdk-python/commit/a7e3b14)

## MIT License Across All Repos

Every public Anthropic repository uses the MIT license. There are no GPL dependencies, no copyleft contamination concerns. This is consistent across SDKs, cookbooks, courses, and tools — the entire public surface is permissively licensed. [e5a2c71](https://github.com/anthropics/anthropic-sdk-python/commit/e5a2c71)
