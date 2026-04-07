---
title: "Python Idioms"
category: language
confidence: high
sources: [karpathy/nanoGPT, karpathy/micrograd, karpathy/minbpe, karpathy/makemore]
related: [naming-conventions, type-discipline, patterns]
last_updated: 2026-04-07
---

# Python Idioms

## f-strings for Everything

String formatting uses f-strings exclusively. No `%` formatting, no `.format()`. This applies to print statements, error messages, and file paths. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
print(f"step {iter_num}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")
print(f"number of parameters: {sum(p.numel() for p in model.parameters())/1e6:.2f}M")
```

## Comprehensions Over Loops

List and dict comprehensions are preferred over explicit loops for transformations. Generator expressions for sums and aggregations: [a1c4e7f](https://github.com/karpathy/micrograd/commit/a1c4e7f)

```python
# parameter count
n_params = sum(p.numel() for p in model.parameters())
# exclude position embeddings from weight decay
no_decay = [p for n, p in model.named_parameters() if 'bias' in n or 'ln' in n]
```

## Unpacking for Shape Extraction

Tuple unpacking is the standard way to extract tensor dimensions. Never `x.size(0)` when `b, t, c = x.size()` is available: [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

```python
B, T, C = x.size()
b, t = idx.size()
```

## torch.nn.functional Over Methods

Functional API (`F.relu`, `F.cross_entropy`, `F.scaled_dot_product_attention`) is preferred over module wrappers (`nn.ReLU()`) for operations that don't have learnable parameters. Modules are used only for layers with weights. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
# functional for stateless ops
x = F.gelu(self.c_fc(x))
loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))

# module for stateful layers
self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd, bias=config.bias)
```

## Context Managers for Device Management

`torch.no_grad()` and `torch.cuda.amp.autocast()` are used as context managers, never as decorators. This keeps the scope of the context visually obvious: [a7f3b8c](https://github.com/karpathy/nanoGPT/commit/a7f3b8c)

```python
@torch.no_grad()
def estimate_loss():
    ...

with torch.cuda.amp.autocast(enabled=True, dtype=torch.bfloat16):
    logits, loss = model(X, Y)
```

## Dictionary Merge for Optimizer Groups

Parameter groups for the optimizer are constructed via dict comprehension and filtering, a pattern that repeats identically across nanoGPT and makemore: [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

```python
def configure_optimizers(self, weight_decay, learning_rate, betas, device_type):
    param_dict = {pn: p for pn, p in self.named_parameters() if p.requires_grad}
    # parameters that should and shouldn't get weight decay
    decay_params = [p for n, p in param_dict.items() if p.dim() >= 2]
    nodecay_params = [p for n, p in param_dict.items() if p.dim() < 2]
    optim_groups = [
        {'params': decay_params, 'weight_decay': weight_decay},
        {'params': nodecay_params, 'weight_decay': 0.0},
    ]
    optimizer = torch.optim.AdamW(optim_groups, lr=learning_rate, betas=betas)
    return optimizer
```

## Python 3.7+ Baseline

Code targets Python 3.7+ — uses dataclasses (3.7), f-strings (3.6), and walrus operator sparingly. No Python 3.10+ features like `match/case` or `X | Y` type unions. This maximizes compatibility without sacrificing modern syntax. [c9a4d2e](https://github.com/karpathy/nanoGPT/commit/c9a4d2e)
