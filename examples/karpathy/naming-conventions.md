---
title: "Naming Conventions"
category: style
confidence: high
sources: [karpathy/nanoGPT, karpathy/micrograd, karpathy/llm.c, karpathy/minbpe]
related: [code-structure, type-discipline, languages/python, languages/c]
last_updated: 2026-04-07
---

# Naming Conventions

## Math-Aligned Variable Names

Variables that represent mathematical quantities use names from the paper or standard notation. Tensor dimensions are single letters: `B` (batch), `T` (sequence length), `C` (channels/embedding dimension). Weight matrices are `w`, biases are `b`, with qualifiers: `wte` (word token embeddings), `wpe` (word position embeddings). [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
# from micrograd/engine.py — variable names match calculus notation
out = Value(self.data + other.data, (self, other), '+')
def _backward():
    self.grad += out.grad    # d(a+b)/da = 1
    other.grad += out.grad   # d(a+b)/db = 1
out._backward = _backward
```

This convention bridges the gap between paper and implementation. A reader who knows that `B, T, C` means batch, time, channels can read `x.view(B, T, C)` the same way they read the paper's tensor diagrams. The rationale is explicit in comments: "match the notation in Attention Is All You Need." [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

## Descriptive Config Names

Configuration parameters use full descriptive names with underscores: `block_size`, `n_layer`, `n_head`, `n_embd`, `vocab_size`, `learning_rate`, `max_iters`. The `n_` prefix follows PyTorch convention for counts. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

The same pattern holds in minbpe, where tokenizer configuration uses `vocab_size`, `num_merges`, `pattern` — no abbreviations, no cryptic shorthand.

## No Abbreviation in Functions

Function and method names are spelled out: `configure_optimizers`, `generate`, `crop_block_size`, `estimate_loss`. No `cfg_opt()` or `gen()`. The one exception is universally understood abbreviations like `init` and `fwd`. [a1c4e7f](https://github.com/karpathy/nanoGPT/commit/a1c4e7f)

This creates a two-tier system: variables in hot numerical code use terse math notation (`B`, `T`, `C`, `q`, `k`, `v`), while function names and configuration parameters are fully spelled out. The split maps to the reader's needs — you scan function names to find what you're looking for, but you read numerical code with the paper open beside you.

## Loop Variables Are Explicit

Loop iterators are descriptive rather than `i`/`j`/`k` when the loop body is non-trivial. `for step in range(max_iters)`, `for name, param in model.named_parameters()`, `for token in tokens`. Single-letter iterators appear only in tight numerical loops: `for i in range(n_layer)`. [c9a4d2e](https://github.com/karpathy/nanoGPT/commit/c9a4d2e)

## C Naming (llm.c)

In C code, the convention shifts to all-lowercase with underscores: `gpt2_forward`, `encoder_forward`, `matmul_forward`, `attention_forward`. Struct names are `typedef`'d to `PascalCase`: `GPT2`, `GPT2Config`, `ParameterTensors`. This mirrors the Python class names while respecting C idiom. See [[languages/c]] for details. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
// function prefix creates a pseudo-namespace — the "class" the function belongs to
void gpt2_forward(GPT2 *model, int* inputs, int* targets, int B, int T);
void gpt2_backward(GPT2 *model);
void gpt2_update(GPT2 *model, float learning_rate, float beta1, float beta2, float eps, float weight_decay, int t);
void gpt2_free(GPT2 *model);
```

The math-aligned convention transfers directly across languages: `B`, `T`, `C`, `V`, `L` appear identically in both the Python and C implementations, so a reader familiar with one codebase can navigate the other immediately.

## Repository Names as Naming Convention

The repositories themselves follow a naming pattern: compound lowercase words that communicate scope and intent. `micrograd` = micro + autograd. `nanoGPT` = nano + GPT. `minbpe` = minimal + BPE. `makemore` = a verb phrase describing what the model does. `llm.c` = LLM + the file extension, declaring both subject and language in three characters. Each name sets expectations about the project's ambition: these are intentionally small implementations of well-known algorithms.
