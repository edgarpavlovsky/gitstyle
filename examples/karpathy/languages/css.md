---
title: CSS Style Guide
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
The developer demonstrates a pragmatic, compatibility-focused approach to CSS that prioritizes simplicity and browser support over cutting-edge features.

## Core Philosophy

The CSS codebase reveals a clear preference for straightforward, vanilla CSS without preprocessors or complex modern features. This approach emphasizes browser compatibility and predictability, as evidenced by the consistent use of standard CSS properties without vendor prefixes or experimental features (60b1084a, 1552519d, fdeb562c, ed8a8bf8).

## Styling Patterns

### Modern Yet Conservative

While the developer avoids bleeding-edge CSS features, they do embrace well-established modern practices. The codebase includes flexbox layouts, system font stacks, and responsive design considerations (eb0eb26f, 87b4a178). Additionally, modern conveniences like border-radius, box-sizing, and web fonts are utilized appropriately (74b4fa86, 3c8d9093).

### Custom Properties Evolution

Interestingly, there's evidence of evolution in the developer's approach. Earlier commits show extensive use of CSS custom properties for theming with semantic [[naming-conventions]] like '--ai-bg', '--ai-border', and '--ai-text' (ca230d95, 3cc3390f). However, the majority of the codebase follows a more traditional approach without custom properties, focusing on direct value assignments (d7a303b4, 759f7e73, c3cb157c).

## Value and Unit Preferences

The developer strongly prefers explicit pixel values and simple units over relative units or complex calculations. This pattern prioritizes predictability over responsiveness (759f7e73, c3cb157c, 33b2b018, 68e4e0f3). Style adjustments typically involve simple value changes to padding, margins, and font-sizes rather than complex CSS features like animations, transforms, or advanced selectors (c8a2ab52, 60b1084a, 1552519d, ed8a8bf8).

## Code Organization

The CSS follows standard property ordering conventions and makes appropriate use of shorthand properties. For example, 'margin: 5px' is preferred over separate margin properties (fe474d24, 419d6be2, 495a2a4a, 633fcf2d). This demonstrates attention to [[code-structure]] while maintaining readability.

## Context-Specific Styling

For blog-specific styling adjustments, the developer isn't afraid to use inline CSS, particularly for typography (font-size, font-family) and code block appearance (757d5da4, 456889df, 1f2a878e). This pragmatic approach suggests a focus on getting the job done efficiently when appropriate.

## Overall Assessment

The CSS style reflects a developer who values stability, compatibility, and maintainability over showcasing the latest CSS features. This conservative yet modern approach ensures broad browser support while still leveraging established [[patterns]] that improve developer experience. The code demonstrates solid understanding of CSS fundamentals with a practical mindset toward real-world deployment.
