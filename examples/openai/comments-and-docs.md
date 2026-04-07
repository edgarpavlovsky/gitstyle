---
title: "Comments & Documentation"
category: style
confidence: high
sources: [openai/openai-python, openai/openai-node, openai/tiktoken, openai/whisper, openai/CLIP, openai/openai-cookbook]
related: [naming-conventions, type-discipline, code-structure]
last_updated: 2026-04-07
---

# Comments & Documentation

## SDK: Generated Docstrings from OpenAPI Spec

SDK resource methods carry comprehensive docstrings generated from the OpenAPI specification. Each parameter is documented with its type, description, and allowed values. These are not hand-written — Stainless generates them from the API spec and keeps them in sync with API changes. This makes them the densest documentation anywhere in the org. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```python
def create(
    self,
    *,
    messages: Iterable[ChatCompletionMessageParam],
    model: Union[str, ChatModel],
    ...
) -> ChatCompletion:
    """Create a chat completion.

    Args:
        messages: A list of messages comprising the conversation so far.
        model: ID of the model to use. See the model endpoint compatibility
            table for details on which models work with the Chat API.
        frequency_penalty: Number between -2.0 and 2.0. Positive values
            penalize new tokens based on their existing frequency.
        ...
    """
```

## SDK: Sparse Inline Comments

Despite heavy docstrings, SDK implementation code has minimal inline comments. The code is expected to be self-explanatory through naming and type annotations. Comments appear only for non-obvious decisions — retry logic, SSE parsing edge cases, header manipulation. [b5d3a72](https://github.com/openai/openai-python/commit/b5d3a72)

```python
# _streaming.py — comments only where behavior is surprising
def _iter_events(self) -> Iterator[ServerSentEvent]:
    buf = b""
    for chunk in self._response.iter_bytes():
        buf += chunk
        # SSE spec: events are separated by blank lines
        # but some proxies strip trailing newlines, so we
        # also split on double \n within the buffer
        while b"\n\n" in buf:
            event_data, buf = buf.split(b"\n\n", 1)
            yield self._parse_event(event_data)
```

## Research Code: Paper-Reference Comments

Whisper and CLIP include comments referencing their respective papers by section or equation number, connecting implementation to academic work. This makes the code navigable for researchers reproducing results. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38) [e7f2c83](https://github.com/openai/CLIP/commit/e7f2c83)

```python
# whisper/model.py
class ResidualAttentionBlock(nn.Module):
    """Corresponds to Section 2.1 of the Whisper paper.
    Multi-head attention with residual connection and layer norm.
    """
    def forward(self, x, xa=None, mask=None):
        # pre-norm formulation (Ba et al., 2016)
        x = x + self.attn(self.attn_ln(x), mask=mask)
        if self.cross_attn:
            x = x + self.cross_attn(self.cross_attn_ln(x), xa)
        x = x + self.mlp(self.mlp_ln(x))
        return x
```

## tiktoken: The Educational Module as Living Documentation

tiktoken's most distinctive documentation choice is `_educational.py` — a pure-Python reimplementation of the BPE algorithm written for clarity, not performance. The production Rust code has minimal comments; the educational module _is_ the documentation. This dual-implementation approach (fast Rust + readable Python) is rare in open source and makes tiktoken's algorithm more accessible than any amount of prose documentation could. [a4e2f91](https://github.com/openai/tiktoken/commit/a4e2f91)

```python
# tiktoken/_educational.py
def byte_pair_encode(mergeable_ranks, input_bytes):
    """This is a reference implementation of BPE.

    It's written for clarity, not performance. The Rust implementation
    in _tiktoken.so is ~100x faster.

    The algorithm:
    1. Start with individual bytes as tokens
    2. Find the most frequent adjacent pair
    3. Merge that pair into a new token
    4. Repeat until no more merges are possible
    """
    parts = list(input_bytes)
    while True:
        min_rank = None
        min_idx = None
        for i in range(len(parts) - 1):
            pair = parts[i] + parts[i + 1]
            rank = mergeable_ranks.get(pair)
            if rank is not None and (min_rank is None or rank < min_rank):
                min_rank = rank
                min_idx = i
        if min_idx is None:
            break
        parts = parts[:min_idx] + [parts[min_idx] + parts[min_idx + 1]] + parts[min_idx + 2:]
    return parts
```

This pattern — shipping a pedagogical reimplementation alongside production code — is arguably tiktoken's most significant engineering decision. It means anyone trying to understand BPE tokenization can read real, runnable Python instead of reverse-engineering Rust or reading a paper. The educational module has become a widely-cited reference for BPE implementations in the broader ML community. See [[code-structure]] for how it fits into tiktoken's directory layout.

## Cookbook: Narrative Documentation

The openai-cookbook uses Jupyter notebooks as its documentation medium. Each notebook tells a complete story with markdown cells explaining motivation, approach, and interpretation of results between code cells. The writing style is tutorial-oriented — second person, step-by-step, expected output descriptions. This is the most user-facing writing in the org, distinctly different in voice from the terse SDK docstrings. [c1d4e87](https://github.com/openai/openai-cookbook/commit/c1d4e87)

## README Quality Varies by Category

SDK READMEs are comprehensive: installation, quickstart, error handling, retries, timeouts, migration guides. Research READMEs focus on model description, setup, and inference commands. Gym's README is the most extensive research README, serving as the primary reference for the `Env` interface. [f8a2c64](https://github.com/openai/openai-python/commit/f8a2c64)

## No Generated API Docs

None of the repositories use Sphinx, MkDocs, or other documentation generators. SDK API reference lives on platform.openai.com (generated from the OpenAPI spec, not from code). Research repos rely solely on READMEs and inline comments. Triton is the only repo with Apache-2.0 per-file license headers, following LLVM convention. [b8c4d19](https://github.com/openai/openai-python/commit/b8c4d19) [b3d7e14](https://github.com/openai/triton/commit/b3d7e14)
