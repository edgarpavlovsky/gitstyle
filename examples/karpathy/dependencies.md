---
title: Dependencies
category: dimension
confidence: 0.9
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
The developer demonstrates a strong minimalist philosophy toward dependencies, consistently preferring to implement functionality from scratch rather than relying on external libraries. This pattern is most evident in their explicit comments about removing dependencies for security and simplicity [a445144d, 03be9536, e569b59f].

## Core Philosophy

The developer actively works to minimize external dependencies, often implementing complex functionality from scratch. In JavaScript projects, they achieve zero runtime dependencies, creating self-contained libraries [6d6a4754, 88ae38ee, f480d05e]. In Python projects, they frequently rely only on the standard library, implementing cryptographic primitives [948711d1, db4e27d9] and neural networks [f1addd3a] from scratch rather than using established libraries.

## Language-Specific Patterns

### Python
In [[python]] projects, the developer uses modern dependency management with `pyproject.toml` and `uv.lock` [b11d6f28, 9c383a8c], but keeps dependencies minimal. They typically rely on the scientific Python stack (NumPy, Matplotlib, PyTorch) only when necessary [26675947, 333e0441]. The developer actively removes dependencies when possible, replacing scipy with PyTorch equivalents [cae0006f].

### JavaScript
For [[javascript]] projects, the developer maintains zero runtime dependencies in core libraries [88ae38ee, f480d05e], though they use jQuery and jQuery UI for demo interfaces [72b4719f, 3e62bba1]. They prefer vanilla implementations over frameworks [9f400b91].

### Go
In [[go]] projects, the developer uses only well-established libraries like goldmark for markdown and modernc.org/sqlite for database functionality [a8101e25], preferring standard library solutions elsewhere.

### C/C++/CUDA
For low-level [[c]], [[cplusplus]], and [[cuda]] code, the developer relies primarily on standard libraries (stdio.h, stdlib.h, math.h) and platform-specific headers only when necessary [d9862069, b233b770]. They use CUDA libraries (cublas, cudnn) for GPU operations [cb445113, 17872103].

## Dependency Management Practices

The developer provides graceful fallbacks for optional dependencies, particularly for GPU libraries in [[lua]] projects [ef0373f0, 9cb025b1]. They document dependencies clearly in comments with pip install instructions [69cb21f0, a108c323] and maintain requirements.txt files [8d071865].

When dependencies are necessary, the developer chooses performance-focused options like ahash for hashing and rayon for parallelism in [[rust]] [7772a98a], and prefers self-hosting resources over external CDNs for privacy [3c8d9093].

## Cross-Platform Considerations

The developer carefully manages platform-specific dependencies with conditional compilation [cb445113, e6856bc5] and separate implementations for different operating systems [de780a83, b6676ecc]. This attention to portability aligns with their minimalist approach, ensuring code can run in various environments with minimal external requirements.
