---
title: "Comments & Documentation"
category: style
confidence: high
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-sdk-typescript, anthropics/anthropic-cookbook, anthropics/courses]
related: [naming-conventions, code-structure, type-discipline]
last_updated: 2026-04-07
---

# Comments & Documentation

## Docstrings on Every Public Method

Anthropic's Python SDK provides docstrings on all public methods. These docstrings describe the API operation, list parameters with their types and meanings, and note any special behaviors (streaming, pagination, beta status). The style is Google-format with `Args:` and `Returns:` sections. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

```python
def create(
    self,
    *,
    model: str,
    max_tokens: int,
    messages: Iterable[MessageParam],
    **kwargs,
) -> Message:
    """Create a message.

    Send a structured list of input messages with text and/or image
    content, and the model will generate the next message in the
    conversation.

    Args:
        model: The model that will complete your prompt (e.g.
            ``"claude-sonnet-4-20250514"``).
        max_tokens: The maximum number of tokens to generate before
            stopping.
        messages: Input messages. Each message has a ``role`` and
            ``content``.

    Returns:
        A Message object containing the model's response.
    """
```

This is in sharp contrast to internal modules (prefixed with `_`), which often have no docstrings at all. The documentation boundary aligns exactly with the public API boundary. See [[code-structure]] for how `__all__` exports define this boundary.

## TypeScript JSDoc Mirrors Python Docstrings

The TypeScript SDK uses JSDoc comments that closely mirror the Python docstrings. The same parameter descriptions, the same caveats, the same examples appear in both languages. This is likely generated from a shared source or manually synchronized. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

```typescript
/**
 * Create a message.
 *
 * Send a structured list of input messages with text and/or image
 * content, and the model will generate the next message in the
 * conversation.
 *
 * @param params - The message creation parameters.
 * @returns A Message object containing the model's response.
 */
async create(params: MessageCreateParams): Promise<Message> {
```

## Inline Comments for Protocol Details

Where the code implements HTTP or SSE protocol behavior, inline comments explain the protocol semantics — not the code mechanics. Comments like "SSE spec requires a trailing newline after data" or "retry-after is seconds per RFC 7231" appear at the protocol boundary. [b2d6e78](https://github.com/anthropics/anthropic-sdk-python/commit/b2d6e78)

```python
# SSE spec: event streams are delimited by double newlines
# Each event has optional "event:" and required "data:" fields
for line in response.iter_lines():
    if line.startswith("event: "):
        event_type = line[7:]
    elif line.startswith("data: "):
        data = json.loads(line[6:])
        yield _make_event(event_type, data)
    elif line == "":
        # empty line signals end of event
        event_type = None
```

## Cookbook as Narrative Documentation

The `anthropic-cookbook` repository treats each notebook as narrative documentation. Cells alternate between markdown explanation and runnable code. The markdown cells explain _why_ a pattern is used, _what_ the API behavior is, and _when_ to use one approach over another. [f2b8c41](https://github.com/anthropics/anthropic-cookbook/commit/f2b8c41)

```markdown
## Prompt Caching

Prompt caching allows you to reduce costs and latency for prompts with
shared prefixes. When you send a request with prompt caching enabled,
the API caches the prompt prefix and reuses it for subsequent requests
that share the same prefix.

### When to use prompt caching
- Long system prompts that are reused across many requests
- Multi-turn conversations where the context grows incrementally
```

This narrative style makes cookbooks usable both as tutorials (read top-to-bottom) and as reference (search for a specific pattern). Code examples are complete and runnable, not snippets.

## README as Quick-Start, Not Full Reference

SDK READMEs focus on installation and a minimal working example — typically under 200 lines of markdown. They do not attempt to document every method or parameter. The README points users to the API documentation site for comprehensive reference. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

```markdown
## Installation

```sh
pip install anthropic
```

## Usage

```python
from anthropic import Anthropic

client = Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
print(message.content)
```
```

The pattern is: README gets you from zero to "hello world" in under a minute. Everything beyond that is in the docs site or cookbook.

## CHANGELOG for Release Communication

Both SDKs maintain a `CHANGELOG.md` following Keep a Changelog format. Each release entry lists additions, changes, fixes, and deprecations. Changelog entries are written from the user's perspective — "Added streaming support for tool use" rather than "Refactored streaming handler to support tool blocks." [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

## No Inline TODO/FIXME in Released Code

A search for `TODO` and `FIXME` in released SDK code yields near-zero results. Unfinished work is tracked in GitHub issues, not in source comments. This keeps the published codebase clean — users reading the source should not encounter breadcrumbs of internal development state. [b5e7f93](https://github.com/anthropics/anthropic-sdk-python/commit/b5e7f93)

## Type Annotations as Documentation

The comprehensive type annotations serve double duty as documentation. IDE hover information derived from the type signatures is often sufficient to understand a method's contract without reading the docstring. The combination of typed parameters, `Literal` types for valid values, and `Optional` for nullable fields makes the function signature itself a concise API reference. See [[type-discipline]] for the full typing philosophy. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)
