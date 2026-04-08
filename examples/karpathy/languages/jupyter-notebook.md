---
title: Jupyter Notebook Style
category: language
confidence: 0.82
source_repos:
  - karpathy/EigenLibSVM
  - karpathy/KarpathyTalk
  - karpathy/LLM101n
  - karpathy/Random-Forest-Matlab
  - karpathy/arxiv-sanity-lite
  - karpathy/arxiv-sanity-preserver
  - karpathy/autoresearch
  - karpathy/build-nanogpt
  - karpathy/calorie
  - karpathy/char-rnn
  - karpathy/convnetjs
  - karpathy/covid-sanity
  - karpathy/cryptos
  - karpathy/deep-vector-quantization
  - karpathy/find-birds
  - karpathy/forestjs
  - karpathy/hn-time-capsule
  - karpathy/jobs
  - karpathy/karpathy
  - karpathy/karpathy.github.io
  - karpathy/lecun1989-repro
  - karpathy/llama2.c
  - karpathy/llm-council
  - karpathy/llm.c
  - karpathy/makemore
  - karpathy/micrograd
  - karpathy/minGPT
  - karpathy/minbpe
  - karpathy/nanoGPT
  - karpathy/nanochat
  - karpathy/neuraltalk
  - karpathy/neuraltalk2
  - karpathy/ng-video-lecture
  - karpathy/nipspreview
  - karpathy/nn-zero-to-hero
  - karpathy/notpygamejs
  - karpathy/paper-notes
  - karpathy/pytorch-normalizing-flows
  - karpathy/randomfun
  - karpathy/reader3
  - karpathy/recurrentjs
  - karpathy/reinforcejs
  - karpathy/rendergit
  - karpathy/researchlei
  - karpathy/researchpooler
  - karpathy/rustbpe
  - karpathy/scholaroctopus
  - karpathy/svmjs
  - karpathy/tf-agent
  - karpathy/tsnejs
  - karpathy/twoolpy
  - karpathy/ulogme
last_updated: 2026-04-08
---
The developer demonstrates consistent patterns in their Jupyter Notebook usage, particularly around visualization setup and reproducibility practices.

## Visualization Configuration

The developer consistently uses matplotlib's inline mode across notebooks, employing the `%matplotlib inline` magic command as a standard practice (26675947, 2fb6f76d, df9135da, 328942c7, da02f899). This [[language-idioms]] pattern ensures plots are displayed directly within the notebook interface, which is essential for interactive data analysis workflows.

## Import Conventions

When working with deep learning libraries, the developer follows community-standard [[naming-conventions]] for module aliases. They consistently import PyTorch's functional module as `F` and matplotlib's pyplot as `plt` (56eda75e, 4c355970, d5b5bfda, 44cfac7e, 74aac39a). These abbreviated aliases align with widely adopted conventions in the data science and machine learning communities.

## Reproducibility Practices

A notable pattern is the consistent use of random seed initialization across notebooks (26675947, 2fb6f76d, df9135da, 328942c7, da02f899). This practice demonstrates attention to reproducibility, ensuring that experiments can be reliably repeated with consistent results. This approach reflects professional [[patterns]] in scientific computing where reproducibility is paramount.

The combination of these practices suggests a developer who values both interactive exploration and scientific rigor, using Jupyter notebooks as a primary environment for machine learning experimentation while maintaining professional standards for code reproducibility and visualization.
