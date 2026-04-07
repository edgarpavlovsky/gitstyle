---
title: "Testing"
category: style
confidence: medium
sources: [karpathy/nanoGPT, karpathy/micrograd, karpathy/llm.c, karpathy/minbpe]
related: [patterns, commit-hygiene, comments-and-docs]
last_updated: 2026-04-07
---

# Testing

## The Pedagogical Testing Philosophy

None of the analyzed repositories use pytest, unittest, or any testing framework. There are no `test_*.py` files following standard conventions (with one exception noted below). This reflects a deliberate stance about what "correctness" means for educational code. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

The implicit contract is: the reader _is_ the test suite. When someone clones nanoGPT and runs `python train.py`, they are simultaneously learning the material and verifying the implementation. If the loss converges and the generated text looks reasonable, the code is correct. If it does not, the reader has a debugging exercise that teaches them more than any passing test would.

This inverts the standard relationship between tests and users. In production code, tests protect users from regressions. In educational code, the user's act of running and understanding the code _is_ the verification.

The approach also reflects the nature of the audience. Someone working through micrograd or nanoGPT is learning backpropagation or transformer training — they benefit from understanding _why_ something went wrong, not from seeing a red/green test result. A failing training run is a more valuable learning experience than a failing test case.

## Validation Scripts

Where automated verification does exist, it takes the form of standalone scripts that run the implementation end-to-end and print results for human inspection. `llm.c` has `test_gpt2.c` which loads a checkpoint, runs a forward pass, and prints loss values that should match the Python reference: [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
// in test_gpt2.c — the "test" is a human comparing two numbers
// expected loss at step 0: 5.2700
// expected loss at step 10: 4.0600
// if your loss is very different, something is wrong
```

The "test" is comparing printed output against known-good values documented in comments. This is manual regression testing — but it teaches the reader what the expected behavior looks like, which an automated test would hide behind a green checkmark.

## Reference Implementation Comparison

The primary testing strategy across projects is cross-validation against a reference. `llm.c` validates against PyTorch outputs. `minbpe` validates against OpenAI's tiktoken. `micrograd` validates against PyTorch autograd. The pattern: implement from scratch, then verify outputs match the established library to within floating-point tolerance. [c7a2d1b](https://github.com/karpathy/micrograd/commit/c7a2d1b)

```python
# from micrograd test — verify gradient correctness against PyTorch
x = Value(-4.0)
z = 2*x + 2 + x
# ... operations ...
xpt = torch.Tensor([-4.0]).double()
# ... same operations with PyTorch ...
assert abs(x.grad - xpt.grad.item()) < 1e-6
```

micrograd is the one exception that does have a `test/` directory with proper assertions. The reason is telling: gradient correctness requires numerical verification because a wrong gradient produces silently wrong training, not an obvious crash. The test exists precisely where visual inspection fails.

Similarly, minbpe validates its output against tiktoken byte by byte — because a tokenizer that silently encodes one wrong token will produce garbled model behavior that would be nearly impossible to diagnose downstream.

## Training Loss as Test Signal

For neural network code, the primary correctness indicator is training loss convergence. If loss goes down, the implementation is likely correct. README files document expected loss curves: "after 5000 iterations you should see a loss of ~1.48." This turns every training run into an integration test. [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

This is more powerful than it first appears. A converging loss exercises the full pipeline — data loading, forward pass, loss computation, gradient computation, optimizer step. A bug in any of these stages almost always manifests as diverging or stuck loss.

## Print-Based Debugging

`print()` statements are the debugging tool. Training scripts print loss, learning rate, and throughput metrics every N steps. Sample generation is interleaved with training to provide qualitative output inspection: [a7f3b8c](https://github.com/karpathy/nanoGPT/commit/a7f3b8c)

```python
if iter_num % eval_interval == 0:
    losses = estimate_loss()
    print(f"step {iter_num}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")
if iter_num % sample_interval == 0:
    context = torch.zeros((1, 1), dtype=torch.long, device=device)
    print(decode(model.generate(context, max_new_tokens=200)[0].tolist()))
```

There is no logging framework, no structured log output, no log levels. The output is designed for a human watching the terminal — the qualitative text samples let you _see_ the model learning in real time, which serves both as debugging and as pedagogy.

## The Spectrum Across Repos

The testing philosophy is not uniform — it calibrates to the stakes. micrograd, where a gradient bug is silent and catastrophic, has the most formal testing. nanoGPT, where bugs manifest as bad loss curves, relies on training convergence. `llm.c`, where the C implementation must match the Python reference exactly, uses cross-implementation comparison. minbpe validates against tiktoken's output. Each project tests at the level where bugs would otherwise be invisible.

This reveals a principled rule: write formal tests only where the failure mode is silent. If a bug produces an obvious symptom (diverging loss, garbled text, compilation error), the educational context provides its own feedback loop.

## What This Rules Out

The absence of formal tests has a specific consequence: there is no CI, no pre-commit hooks, no automated gate between writing code and pushing it. This is viable because the projects are single-author and the audience is learners, not dependents. See [[commit-hygiene]] for how the direct-to-main workflow connects to this.
