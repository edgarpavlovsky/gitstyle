---
title: "Data Sources"
category: meta
last_updated: 2026-04-07
---

# Data Sources

## Repositories Analyzed

| Repository | Commits Fetched | Commits Sampled | Primary Language |
|------------|----------------|-----------------|------------------|
| karpathy/nanoGPT | 95 | 82 | Python |
| karpathy/llm.c | 142 | 120 | C |
| karpathy/micrograd | 34 | 34 | Python |
| karpathy/minbpe | 41 | 38 | Python |
| karpathy/makemore | 47 | 42 | Python |

## Sampling Notes

- **nanoGPT**: Most active Python repository. Training loop and model definition provide the strongest signal for Python style conventions
- **llm.c**: Primary source for C idioms. Very active with 500+ commits; sampled recent 142 focused on the core `train_gpt2.c` implementation
- **micrograd**: Small but high-signal — every commit is authored by Karpathy with clear style intent
- **minbpe**: Clean BPE tokenizer implementation. Good signal for class hierarchy decisions and testing patterns
- **makemore**: Progression of language models (bigram → MLP → RNN → transformer). Shows how code structure scales

## Excluded Repositories

- **nn-zero-to-hero**: Course materials (notebooks), not standalone code
- **build-nanogpt**: YouTube walkthrough code, closely mirrors nanoGPT
- **char-rnn**: Legacy Lua code, not representative of current style

## Coverage Gaps

- **Private repositories**: None known; Karpathy works entirely in public
- **Collaborative work**: Tesla/OpenAI work is not on personal GitHub — only solo educational projects are analyzed
- **Notebooks**: Jupyter notebooks in nn-zero-to-hero were excluded; style may differ in notebook-first workflows

## Confidence Impact

Articles grounded in nanoGPT + llm.c (e.g., [[code-structure]], [[naming-conventions]], [[dependencies]]) have the highest confidence. Articles extrapolating from smaller repos (e.g., [[testing]]) have medium confidence.

**Total commits fetched:** 359
**Total commits sampled:** 316
**Unique files touched:** 187
**Date range:** 2022-11 to 2026-03
