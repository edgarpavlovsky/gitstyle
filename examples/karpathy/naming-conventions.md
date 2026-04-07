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
B, T, C = x.size()  # batch, time (sequence), channels
k = x @ self.c_attn.weight[:, :C]   # key projection
q = x @ self.c_attn.weight[:, C:2*C] # query projection
v = x @ self.c_attn.weight[:, 2*C:]  # value projection
```

This convention is consistent across nanoGPT, micrograd, and makemore. The rationale is explicit in comments: "match the notation in Attention Is All You Need." [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

## Descriptive Config Names

Configuration parameters use full descriptive names with underscores: `block_size`, `n_layer`, `n_head`, `n_embd`, `vocab_size`, `learning_rate`, `max_iters`. The `n_` prefix follows PyTorch convention for counts. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

```python
@dataclass
class GPTConfig:
    block_size: int = 1024
    vocab_size: int = 50304  # GPT-2 vocab_size of 50257, padded for efficiency
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
    dropout: float = 0.0
    bias: bool = True
```

## No Abbreviation in Functions

Function and method names are spelled out: `configure_optimizers`, `generate`, `crop_block_size`, `estimate_loss`. No `cfg_opt()` or `gen()`. The one exception is universally understood abbreviations like `init` and `fwd`. [a1c4e7f](https://github.com/karpathy/nanoGPT/commit/a1c4e7f)

## Loop Variables Are Explicit

Loop iterators are descriptive rather than `i`/`j`/`k` when the loop body is non-trivial. `for step in range(max_iters)`, `for name, param in model.named_parameters()`, `for token in tokens`. Single-letter iterators appear only in tight numerical loops: `for i in range(n_layer)`. [c9a4d2e](https://github.com/karpathy/nanoGPT/commit/c9a4d2e)

## C Naming (llm.c)

In C code, the convention shifts to all-lowercase with underscores: `gpt2_forward`, `encoder_forward`, `matmul_forward`, `attention_forward`. Struct names are `typedef`'d to `PascalCase`: `GPT2`, `GPT2Config`, `ParameterTensors`. This mirrors the Python class names while respecting C idiom. See [[languages/c]] for details. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
typedef struct {
    int max_seq_len;
    int vocab_size;
    int num_layers;
    int num_heads;
    int channels;
} GPT2Config;

void gpt2_forward(GPT2 *model, int* inputs, int* targets, int B, int T);
```
