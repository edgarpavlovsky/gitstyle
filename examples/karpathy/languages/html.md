---
title: HTML Style Guide
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
The developer demonstrates a pragmatic approach to HTML development, favoring inline styles and modern web standards while prioritizing simplicity over strict separation of concerns.

## Semantic Markup and Modern Standards

The codebase consistently uses HTML5 doctype and semantic markup (0b9315a6, 08af2a2f, 32706e14). This adherence to modern [[language-idioms]] shows a commitment to web standards while maintaining practical simplicity. The developer frequently uses inline event handlers directly in HTML elements (80e61f4c), choosing convenience over the traditional separation of behavior from structure.

## Inline Styling Philosophy

A distinctive pattern emerges in the developer's approach to styling. Rather than maintaining separate CSS files, inline styles are heavily utilized (1d0e49b6, dde802a7). This [[code-structure]] choice trades modularity for immediacy and context-locality. When custom styling is needed for specific content like blog posts, the developer embeds `<style>` tags directly within the HTML (757d5da4, 456889df, 1f2a878e), keeping related styles close to their usage.

## Modern CSS Integration

Despite the preference for inline styles, the developer leverages modern CSS features effectively. CSS Grid and Flexbox layouts appear throughout for responsive design (95be95e6, 6f808a87), along with CSS variables and transition effects (ce5c0c0a). This demonstrates proficiency with current CSS [[patterns]] while maintaining the inline approach.

## JavaScript Integration

The HTML files incorporate modern JavaScript features, including Promises and ES6 syntax (74b4fa86, 0310f7e8, 8824c908). This integration follows the same philosophy of keeping related code together, often embedding [[javascript]] directly in HTML files rather than external scripts.

The overall HTML style reflects a developer who values practicality and locality over strict architectural separation, creating self-contained, immediately understandable components.
