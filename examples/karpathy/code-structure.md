---
title: Code Structure
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
The developer demonstrates a strong preference for modular, well-organized code structures with clear separation of concerns, though the specific approach varies by project type and language.

## General Patterns

The developer tends to organize code into focused modules with single responsibilities. In Go projects, handlers, database operations, API logic, and middleware are separated into distinct files within an `internal/app` package structure `[a8101e25, 9a458854, 88750810]`. Similarly, in Python web applications, the developer separates concerns into distinct modules like `serve.py` for web serving, `analyze.py` for ML processing, and dedicated daemon scripts for background tasks `[7d5030b2, b0eccba7, 633fcf2d]`.

Functions are consistently kept small and focused, typically under 50 lines with clear single responsibilities `[38406bcc, eed8b1b9, 88750810]`. This pattern holds across languages, with JavaScript event handlers typically under 10 lines `[9f400b91, c030afbe]` and MATLAB functions ranging from 50-200 lines `[f7903a1e, d07d3fb5]`.

## Language-Specific Approaches

### Python Projects
For educational or experimental projects, the developer strongly prefers single-file implementations. The GPT implementation is kept to ~300 lines in a single file `[5af9e5c5, 803f3880]`, and training scripts often contain model definition, data loading, and training loops all in one file `[8018ed2c, ba2554ac]`. However, for production applications, the developer adopts proper modular architecture with clear separation between components `[eb0eb26f, 7d5030b2]`.

The developer frequently uses dataclasses for data modeling with clear hierarchical structures `[e9345a4b, 739f1013, 64960f99]` and maintains hyperparameters as module-level constants at the top of files `[28ef2875, 83f7d22b]`.

### JavaScript/Web Projects
Web applications follow a standard structure with clear separation between frontend and backend. Static assets (JavaScript, CSS) are organized in dedicated directories separate from templates and backend code `[fe474d24, 8e52b8ba]`. The developer often starts with inline JavaScript and CSS in HTML files but refactors them into separate files as projects mature `[72b4719f, 0310f7e8]`.

For JavaScript libraries, the developer uses the module pattern with IIFE (Immediately Invoked Function Expression) for encapsulation `[6d6a4754, 88ae38ee, 2b1113e6]`, maintaining single-file libraries with clear internal organization.

### Low-Level Languages
In C/CUDA projects, the developer maintains modular organization with clear separation between utilities, kernels, and main logic. Header files are used for shared functionality `[e33402f7, cb445113]`, and different implementations are kept in separate files (e.g., `run.c` for float32, `runq.c` for int8 quantization) `[d9862069, 5186b505]`.

## Evolution and Refactoring

The developer shows a clear pattern of starting with monolithic implementations and refactoring into modular structures as projects mature. This is evident in the progression from single-file notebooks to organized module structures `[e720fb1b, ac30aa07]` and the extraction of inline scripts into separate JavaScript modules `[72b4719f]`.

Interestingly, the developer explicitly prefers "explicit, direct control over abstractions" and tends to remove 'magic' features like autocast in favor of explicit management `[1076f970, e569b59f]`. This philosophy extends to preferring configuration through Python files rather than YAML/JSON `[9755682b, 8aeea6d9]`.

## Documentation and Organization

The developer maintains consistent file organization patterns across projects. Blog posts follow Jekyll standards with date-prefixed naming `[757d5da4, 08dc797b]`, while educational content uses progressive, modular structures with each lecture building on previous ones `[56eda75e, 4c355970]`. Documentation files are organized in flat structures with descriptive names and dedicated image directories `[2ed34806, 5c17572e]`.

For [[commit-hygiene]], this structured approach facilitates clear, focused commits. The modular architecture also supports the developer's [[testing]] practices by enabling isolated unit testing. The organization choices reflect strong [[language-idioms]] awareness, adapting structure to each language's conventions.
