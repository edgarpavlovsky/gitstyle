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

Configuration and structured data use Python dataclasses with type annotations, never loose dictionaries. `GPTConfig` in nanoGPT, `TrainConfig` fields in makemore — all dataclass-based with explicit types. This provides IDE completion and self-documenting parameter lists without the overhead of Pydantic or attrs. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

Configuration dicts (`{"n_layer": 12}`) do not appear in any of the analyzed repositories. When a function needs to accept configuration, it takes the dataclass directly. The dataclass is the single source of truth for what parameters exist and what their defaults are — there is no second place to look.

## No Type Annotations on Functions

Despite using dataclasses with types, function signatures do not carry type annotations. This applies consistently across all Python repositories — no `def forward(self, x: torch.Tensor) -> torch.Tensor`. The code relies on clear naming and inline comments for type documentation rather than formal annotations. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
# from minbpe — no annotations, but the argument names are self-documenting
def encode(self, text):
    tokens = list(text.encode("utf-8"))
    while len(tokens) >= 2:
        stats = get_stats(tokens)
        pair = min(stats, key=lambda p: self.merges.get(p, float("inf")))
        if pair not in self.merges:
            break
        idx = self.merges[pair]
        tokens = merge(tokens, pair, idx)
    return tokens
```

The pragmatic interpretation: type annotations add visual noise to educational code without adding runtime behavior. For numerical code, the shape is more important than the type — knowing something is `torch.Tensor` tells you less than knowing it is `(B, T, C)`. See [[comments-and-docs]].

## Shape Comments as Type Documentation

Where formal type annotations are absent, tensor shape comments fill the gap. These appear as inline comments after tensor operations, documenting the shape transformation: [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

```python
tok_emb = self.transformer.wte(idx)  # (B, T, C)
pos_emb = self.transformer.wpe(pos)  # (T, C)
x = tok_emb + pos_emb               # (B, T, C)
```

This convention appears in nanoGPT, makemore, and micrograd. It serves the same purpose as type annotations but is more informative for numerical code — the reader can trace how dimensions flow through the network, catching broadcasting and reshaping errors by inspection.

## C Type Discipline

In `llm.c`, typing is strict by necessity. Struct definitions use `typedef` for clean names. Pointer arithmetic is explicit and well-commented. There is no `void*` casting — data types are concrete throughout. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
// activation tensors — each pointer is a view into one contiguous allocation
typedef struct {
    float* encoded;   // (B, T, C)
    float* ln1;       // (L, B, T, C)
    float* ln1_mean;  // (L, B, T)
    float* ln1_rstd;  // (L, B, T)
    float* qkv;       // (L, B, T, 3*C)
    float* atty;      // (L, B, T, C)
    ...
} ActivationTensors;
```

Shape comments carry over directly from the Python convention — the same `(B, T, C)` notation appears in both languages. This creates a Rosetta Stone effect: a reader who understands the nanoGPT Python implementation can navigate the llm.c C implementation by following the shape annotations.

## Assert-Based Validation

Input validation uses bare `assert` statements rather than explicit `if`/`raise`. This is consistent across projects: [a7f3b8c](https://github.com/karpathy/nanoGPT/commit/a7f3b8c)

```python
assert vocab_size is not None
assert block_size is not None
assert t <= self.config.block_size, f"sequence length {t} > block_size {self.config.block_size}"
```

Assertions serve as executable specifications — they document invariants that should never be violated, not user-facing error conditions. For educational code where the author controls the call sites, this is sufficient. Production code would need proper error handling; educational code needs clarity about what the preconditions are.

## Implicit Typing Through Convention

Across the codebase, type information is communicated through a consistent set of conventions rather than through the type system. Variable names signal types: `idx` is always integer indices, `x` is always a float tensor, `config` is always a dataclass. The `n_` prefix always means an integer count. These conventions are reliable enough across all five repositories that a reader who learns them in micrograd can apply them in nanoGPT without additional documentation. See [[naming-conventions]] for the full vocabulary.
