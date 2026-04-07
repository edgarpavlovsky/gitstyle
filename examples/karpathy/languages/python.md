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

String formatting uses f-strings exclusively. No `%` formatting, no `.format()`. This applies to print statements, error messages, and file paths: [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
print(f"step {iter_num}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")
print(f"number of parameters: {sum(p.numel() for p in model.parameters())/1e6:.2f}M")
```

## Comprehensions Over Loops

List and dict comprehensions are preferred over explicit loops for transformations. Generator expressions for sums and aggregations: [a1c4e7f](https://github.com/karpathy/micrograd/commit/a1c4e7f)

```python
# from micrograd — MLP parameter collection via nested comprehension
def parameters(self):
    return [p for layer in self.layers for p in layer.parameters()]
```

## Unpacking for Shape Extraction

Tuple unpacking is the standard way to extract tensor dimensions. Never `x.size(0)` when `b, t, c = x.size()` is available. This makes the dimensionality of every tensor visible at the point of use: [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

```python
B, T, C = x.size()
b, t = idx.size()
```

## torch.nn.functional Over Methods

Functional API (`F.relu`, `F.cross_entropy`, `F.scaled_dot_product_attention`) is preferred over module wrappers (`nn.ReLU()`) for operations that don't have learnable parameters. Modules are reserved for layers with weights: [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
# functional for stateless ops
x = F.gelu(self.c_fc(x))
loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))

# module for stateful layers
self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd, bias=config.bias)
```

This distinction creates a visual signal: if you see `F.something`, there are no learned parameters; if you see `self.something(x)`, there are.

## Context Managers for Device Management

`torch.no_grad()` and `torch.cuda.amp.autocast()` are used as context managers, keeping the scope visually obvious: [a7f3b8c](https://github.com/karpathy/nanoGPT/commit/a7f3b8c)

```python
@torch.no_grad()
def estimate_loss():
    ...

with torch.cuda.amp.autocast(enabled=True, dtype=torch.bfloat16):
    logits, loss = model(X, Y)
```

## Dictionary Merge for Optimizer Groups

Parameter groups for the optimizer are constructed via dict comprehension and filtering. This pattern repeats identically across nanoGPT and makemore, separating weight-decay parameters (matrices) from no-decay parameters (biases, layer norms): [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

```python
def configure_optimizers(self, weight_decay, learning_rate, betas, device_type):
    param_dict = {pn: p for pn, p in self.named_parameters() if p.requires_grad}
    decay_params = [p for n, p in param_dict.items() if p.dim() >= 2]
    nodecay_params = [p for n, p in param_dict.items() if p.dim() < 2]
    optim_groups = [
        {'params': decay_params, 'weight_decay': weight_decay},
        {'params': nodecay_params, 'weight_decay': 0.0},
    ]
    return torch.optim.AdamW(optim_groups, lr=learning_rate, betas=betas)
```

The `p.dim() >= 2` heuristic is the key insight: weight matrices are 2D, biases and layer norm parameters are 1D. This avoids maintaining an explicit list of parameter names.

## Closures for Deferred Computation

In micrograd, closures capture the backward pass logic at the time each operation is constructed. Each operator overload creates a `_backward` closure that references the operands via Python's lexical scoping: [c7a2d1b](https://github.com/karpathy/micrograd/commit/c7a2d1b)

```python
def __add__(self, other):
    out = Value(self.data + other.data, (self, other), '+')
    def _backward():
        self.grad += out.grad
        other.grad += out.grad
    out._backward = _backward
    return out
```

This is an elegant use of Python's closure semantics — the `_backward` function captures `self`, `other`, and `out` from the enclosing scope. The entire autograd engine is built on this pattern, which is idiomatic Python but would require explicit function pointers and data structures in C.

## No Classes Where Functions Suffice

Helper logic is implemented as module-level functions, not utility classes. In minbpe, `get_stats` and `merge` are standalone functions that operate on plain lists, not methods on a tokenizer class: [b7c1d5e](https://github.com/karpathy/minbpe/commit/b7c1d5e)

```python
def get_stats(ids):
    counts = {}
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair, 0) + 1
    return counts

def merge(ids, pair, idx):
    newids = []
    i = 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i+1] == pair[1]:
            newids.append(idx)
            i += 2
        else:
            newids.append(ids[i])
            i += 1
    return newids
```

This keeps the functions testable, reusable, and readable without the cognitive overhead of class instantiation. Classes appear only when there is state to manage.

## Python 3.7+ Baseline

Code targets Python 3.7+ — uses dataclasses (3.7), f-strings (3.6), and walrus operator sparingly. No Python 3.10+ features like `match/case` or `X | Y` type unions. This maximizes compatibility without sacrificing modern syntax. [c9a4d2e](https://github.com/karpathy/nanoGPT/commit/c9a4d2e)
