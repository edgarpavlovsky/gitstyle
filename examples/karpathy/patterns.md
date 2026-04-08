---
title: Patterns
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
The developer demonstrates a strong preference for well-established software design patterns while maintaining pragmatic simplicity. Their approach consistently favors clarity and maintainability over architectural complexity.

## Core Architectural Patterns

The developer extensively implements **repository patterns** for data access, particularly evident in their Go work where they encapsulate database operations within App structs containing DB references and methods [a8101e25, 38406bcc]. This separation of concerns extends to web applications where they implement **MVC-like architectures** with clear boundaries between Flask routes (controllers), Jinja2 templates (views), and database access functions (models) [759f7e73, 33b2b018].

For performance-critical features, the developer consistently employs **materialized view patterns**, particularly for trending posts functionality with background goroutines handling periodic rebuilds [9a458854, eed8b1b9]. This pattern appears across multiple projects, demonstrating a systematic approach to optimization.

## Data Processing Pipelines

The developer favors **pipeline architectures** with distinct, independently executable stages. This is evident in their LLM council system implementing a clear 3-stage pipeline (collection → ranking → synthesis) [eb0eb26f, 87b4a178] and their data processing workflows following patterns like scrape → process → score → visualize [0fbf597b, 7fa0be64]. They consistently implement **caching patterns** using JSON or pickle files for intermediate results [e9345a4b, 739f1013], optimizing performance while maintaining debuggability.

## Object-Oriented Patterns

The developer demonstrates sophisticated use of OOP patterns, particularly in [[python]] where they implement:
- **Factory patterns** with `from_pretrained()` classmethods for model initialization [803f3880, acaadacd]
- **Abstract base classes** with concrete implementations, especially for neural network generators (LSTMGenerator, RNNGenerator) [2c99eac2, f399811c]
- **Extensive operator overloading** for mathematical operations (`__add__`, `__mul__`, `__pow__`) [315a2cb3, 5bb63920]
- **Configuration-driven design** using dataclasses for structured config objects [6e6a5281, ebc28b95]

## JavaScript Module Patterns

In [[javascript]], the developer consistently uses **IIFE (Immediately Invoked Function Expression)** patterns for namespace management and module encapsulation [6d6a4754, 88ae38ee, 46b290ea]. They prefer **prototype-based object construction** over ES6 classes [08d2030d, 53bf4862], and implement **game loop patterns** with init/update/draw lifecycle methods for interactive applications [1d8c733d, f3d83d85].

## Error Handling and Defensive Programming

The developer implements robust **defensive programming patterns** including:
- Platform-specific checks with graceful fallbacks for hardware features [eba36e84, 0d8fbd11]
- Automatic fallback mechanisms for resource allocation (e.g., falling back to managed memory when device allocation fails) [e6856bc5, 8c586f91]
- Atomic file operations using temporary files to prevent race conditions [8ce4543c]

## Data Serialization

A consistent pattern emerges in their approach to **binary file formats**, implementing versioned headers with magic numbers and metadata [4c84bc74, 9740a652, 16635d41]. This pattern appears across [[c]], [[cplusplus]], and [[python]] implementations, showing language-agnostic design thinking.

## Web Development Patterns

For web applications, the developer implements:
- **Cursor-based pagination** consistently across endpoints with appropriate cursor types (ID vs rank) [88750810, 9a458854]
- **CSS custom properties** for theming with dark mode support using `prefers-color-scheme` [ca230d95, ce5c0c0a]
- **Progressive enhancement** by checking element existence before rendering React components [759f7e73]
- **Feature flags** through URL parameters rather than configuration files [48a7e01a, 33b2b018]

## Educational and Research Patterns

The developer follows distinct patterns for educational content:
- **Incremental complexity** building from simple concepts to advanced implementations (bigrams → MLP → backprop → CNN → GPT) [56eda75e, 4c355970]
- **Documentation by example** through demo scripts (demo1.py, demo2.py, demo3.py) [c7940cf8]
- **Research reproduction** with explicit tracking of computational complexity and careful documentation of deviations [51c54e0f, 1ee2ac98]

Their preference for **simplicity over complexity** is evident throughout, often implementing custom solutions rather than relying on heavy frameworks [e569b59f, 1076f970]. This pragmatic approach extends to using simple file-based persistence over complex database solutions when appropriate [8ce4543c, c6d566a6].
