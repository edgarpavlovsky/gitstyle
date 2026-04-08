---
title: JavaScript Style Guide
category: language
confidence: 0.87
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
The developer demonstrates a diverse JavaScript coding style that spans from traditional patterns to modern ES6+ features, reflecting experience across different eras of JavaScript development.

## Modern JavaScript Adoption

The developer shows strong familiarity with modern JavaScript [[language-idioms]], consistently using ES6+ features including:
- Async/await for asynchronous operations (eb0eb26f, 87b4a178)
- Arrow functions and template literals (9f400b91, c030afbe, 921f8c43, 81e4de70)
- Const/let declarations over var (1552519d, fdeb562c)
- Destructuring and spread operators (eb0eb26f, 87b4a178)
- Promises for asynchronous flow control (0310f7e8, 74b4fa86)

## Framework and Library Usage

For React development, the developer favors functional components with hooks over class components (d7a303b4, 759f7e73, 33b2b018), aligning with modern React [[patterns]].

In legacy codebases, the developer demonstrates proficiency with jQuery and D3.js, following common patterns of that era including inline event handlers and global variables (fe474d24, 1682975c, 495a2a4a).

## Object-Oriented Patterns

The developer shows flexibility in object creation [[patterns]]:
- Prefers object literals for simple data structures (1d8c733d, 0fd906aa, b94827ec)
- Uses constructor functions with prototype methods in pre-ES6 code (3e62bba1, 84d69349, f480d05e, 88ae38ee)
- Employs the 'new' keyword pattern for object instantiation
- Utilizes options objects for configuration (f480d05e, b75b7128, 0e47c3af)

## Defensive Programming

The developer consistently implements defensive programming techniques:
- Type checking with typeof operators (5284e9b8, ea9d6a97)
- Default parameter handling (7b71356d)
- hasOwnProperty checks for object iteration (6d6a4754)
- Utility functions for assertions and validation

## Code Organization

The [[code-structure]] varies based on context:
- Uses IIFE (Immediately Invoked Function Expressions) for encapsulation in traditional JavaScript (6d6a4754, 88ae38ee)
- Writes code compatible with both browser and Node.js environments (88ae38ee, f480d05e)
- Follows a procedural/imperative style in some codebases with minimal functional programming (0b9315a6, 53bf4862)

## Iteration Patterns

The developer shows a preference for for-in loops over traditional for loops when iterating arrays (1d8c733d, b94827ec, 0fd906aa), though this practice is generally discouraged for arrays in modern JavaScript.

## Array Handling

Uses both modern and traditional array initialization:
- new Array() constructor for specific use cases (0e47c3af, 2b1113e6)
- Array literals in most contexts

The developer's JavaScript style reflects adaptability across different project requirements and JavaScript evolution, from jQuery-era patterns to modern React and ES6+ features.
