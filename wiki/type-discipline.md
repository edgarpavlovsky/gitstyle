---
title: "Type Discipline"
category: style
confidence: medium
sources: [karpathy/nanoGPT, karpathy/micrograd, karpathy/minbpe, karpathy/llm.c]
related: [naming-conventions, patterns, languages/python, languages/c]
last_updated: 2026-04-07
---

# Type Discipline

## Dataclasses Over Dicts

Configuration and structured data use Python dataclasses with type annotations. `GPTConfig` in nanoGPT, `TrainConfig` fields in makemore — all dataclass-based with explicit types. This provides IDE completion and self-documenting parameter lists without the overhead of Pydantic or attrs. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

```python
@dataclass
class GPTConfig:
    block_size: int = 1024
    vocab_size: int = 50304
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
```

Configuration dicts (`{"n_layer": 12}`) do not appear in any of the analyzed repositories. When a function needs to accept configuration, it takes the dataclass directly.

## No Type Annotations on Functions

Despite using dataclasses with types, function signatures do not carry type annotations. This applies consistently across all Python repositories — no `def forward(self, x: torch.Tensor) -> torch.Tensor`. The code relies on clear naming and inline comments for type documentation rather than formal annotations. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
def forward(self, idx, targets=None):
    device = idx.device
    b, t = idx.size()
    ...
```

The pragmatic interpretation: type annotations add visual noise to educational code without adding runtime behavior. The shapes are documented in comments instead. See [[comments-and-docs]].

## Shape Comments as Type Documentation

Where formal type annotations are absent, tensor shape comments fill the gap. These appear as inline comments after tensor operations, documenting the shape transformation: [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

```python
tok_emb = self.transformer.wte(idx)  # (B, T, C)
pos_emb = self.transformer.wpe(pos)  # (T, C)
x = tok_emb + pos_emb               # (B, T, C)
```

This convention appears in nanoGPT, makemore, and micrograd. It serves the same purpose as type annotations but is more informative for numerical code — shape is more important than `torch.Tensor`.

## C Type Discipline

In `llm.c`, typing is strict by necessity. Struct definitions use `typedef` for clean names. Pointer arithmetic is explicit and well-commented. There is no `void*` casting — data types are concrete throughout. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
typedef struct {
    float* wte;  // (V, C)
    float* wpe;  // (T, C)
    float* ln1w; // (L, C)
    float* ln1b; // (L, C)
    ...
} ParameterTensors;
```

Shape comments carry over directly from the Python convention — the same `(B, T, C)` notation appears in both languages.

## Assert-Based Validation

Input validation uses bare `assert` statements rather than explicit `if`/`raise`. This is consistent across projects — `assert` serves as both documentation and a runtime check: [a7f3b8c](https://github.com/karpathy/nanoGPT/commit/a7f3b8c)

```python
assert vocab_size is not None
assert block_size is not None
assert t <= self.config.block_size, f"sequence length {t} > block_size {self.config.block_size}"
```

Assertions are treated as executable specifications rather than error handling. They document invariants that should never be violated, not user-facing error conditions.
