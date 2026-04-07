---
title: "Testing"
category: style
confidence: medium
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-sdk-typescript, anthropics/claude-code]
related: [patterns, commit-hygiene, type-discipline]
last_updated: 2026-04-07
---

# Testing

## pytest as the Standard Framework

Anthropic's Python repositories use pytest exclusively. There is no unittest usage, no nose, no custom test runners. Test files follow the `test_*.py` convention and live in a top-level `tests/` directory mirroring the `src/` structure. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

```
tests/
  api_resources/
    test_messages.py
    test_completions.py
    beta/
      test_tools.py
  test_client.py
  test_streaming.py
  test_models.py
```

The TypeScript SDK uses Jest (later migrating toward vitest in newer repositories), following the same directory-mirroring convention with `*.test.ts` files. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

## Mock HTTP Layer, Not the API

Tests mock at the HTTP transport layer rather than mocking the client methods. The Python SDK tests use `httpx`'s transport mocking to inject fake responses, so the full request serialization and response parsing path is exercised. [e7c2a49](https://github.com/anthropics/anthropic-sdk-python/commit/e7c2a49)

```python
@pytest.fixture
def client() -> Anthropic:
    return Anthropic(
        api_key="test-api-key",
        _strict_response_validation=True,
    )

def test_messages_create(client: Anthropic, respx_mock):
    respx_mock.post("/v1/messages").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello!"}],
                "model": "claude-sonnet-4-20250514",
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 10, "output_tokens": 5},
            },
        )
    )
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hi"}],
    )
    assert message.content[0].text == "Hello!"
    assert message.stop_reason == "end_turn"
```

This approach tests the full SDK stack — serialization, transport, deserialization, type coercion — without making real API calls. It catches regressions in Pydantic model changes, header construction, and URL assembly.

## Parametrized Error Testing

Error handling is tested via `@pytest.mark.parametrize` over the full error hierarchy. Each HTTP status code maps to a specific exception class, and tests verify the mapping is correct. [c9b4d15](https://github.com/anthropics/anthropic-sdk-python/commit/c9b4d15)

```python
@pytest.mark.parametrize(
    "status_code,expected_error",
    [
        (400, anthropic.BadRequestError),
        (401, anthropic.AuthenticationError),
        (403, anthropic.PermissionDeniedError),
        (404, anthropic.NotFoundError),
        (422, anthropic.UnprocessableEntityError),
        (429, anthropic.RateLimitError),
        (500, anthropic.InternalServerError),
    ],
)
def test_error_mapping(client, respx_mock, status_code, expected_error):
    respx_mock.post("/v1/messages").mock(
        return_value=httpx.Response(status_code, json={"error": {"message": "test"}})
    )
    with pytest.raises(expected_error):
        client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1, messages=[])
```

This parametrized pattern is the standard Anthropic approach for testing any mapping table — status codes to errors, event types to models, content block types to classes.

## Streaming Replay Fixtures

Streaming tests use recorded SSE fixtures — files containing raw SSE event streams that are replayed through the SDK's streaming parser. This avoids both real API calls and the complexity of mocking a streaming connection. [b2d6e78](https://github.com/anthropics/anthropic-sdk-python/commit/b2d6e78)

```python
def test_streaming_message(client, respx_mock):
    respx_mock.post("/v1/messages").mock(
        return_value=httpx.Response(
            200,
            content=b"event: message_start\ndata: {\"type\":\"message_start\",...}\n\n"
                    b"event: content_block_delta\ndata: {\"type\":\"content_block_delta\",...}\n\n"
                    b"event: message_stop\ndata: {\"type\":\"message_stop\"}\n\n",
            headers={"content-type": "text/event-stream"},
        )
    )
    with client.messages.stream(model="claude-sonnet-4-20250514", max_tokens=1024, messages=[...]) as stream:
        events = list(stream.events())
        assert events[0].type == "message_start"
```

Fixture files are stored in `tests/fixtures/` and named after the scenario: `streaming_message.sse`, `streaming_tool_use.sse`.

## Strict Response Validation in Tests

Tests enable `_strict_response_validation=True` on the client, which makes Pydantic reject unknown fields and enforce all type constraints. Production clients use relaxed validation (extra fields allowed) for forward compatibility, but tests verify the SDK's understanding of the current API schema is exact. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

## Type Checking as Testing

Both SDKs run static type checkers as part of CI. The Python SDK runs mypy and pyright in strict mode. The TypeScript SDK runs `tsc --noEmit`. Type errors are treated as test failures — a PR that introduces a type error cannot merge. [b5e7f93](https://github.com/anthropics/anthropic-sdk-python/commit/b5e7f93)

```yaml
# from CI configuration
- run: mypy src/anthropic
- run: pyright src/anthropic
- run: pytest tests/ -x --timeout=30
```

This means the type annotations documented in [[type-discipline]] are not just documentation — they are continuously verified.

## No Integration Tests in Public CI

Public repositories do not include integration tests that hit the live Anthropic API. All tests are hermetic and run against mocked HTTP responses. This ensures tests pass without API keys and avoids rate limit or cost concerns in CI. [a7e3b14](https://github.com/anthropics/anthropic-sdk-python/commit/a7e3b14)

Cookbook examples serve as informal integration tests — they demonstrate real API usage patterns and are expected to work against the live API, but they are not wired into CI.

## Snapshot Testing for Serialization

Pydantic model serialization is verified via snapshot tests. A model instance is serialized to JSON and compared against a stored fixture. This catches unintentional changes to the wire format — if a field name changes or a default value shifts, the snapshot diff surfaces it. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)
