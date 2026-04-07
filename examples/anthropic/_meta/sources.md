---
title: "Data Sources"
category: meta
last_updated: 2026-04-07
---

# Data Sources

## Repositories Analyzed

| Repository | Commits Fetched | Commits Sampled | Primary Language |
|------------|----------------|-----------------|------------------|
| anthropics/anthropic-sdk-python | 412 | 340 | Python |
| anthropics/anthropic-sdk-typescript | 387 | 310 | TypeScript |
| anthropics/anthropic-cookbook | 156 | 128 | Python (notebooks) |
| anthropics/courses | 73 | 65 | Python (notebooks) |
| anthropics/claude-code | 241 | 195 | TypeScript |

## Sampling Notes

- **anthropic-sdk-python**: Primary source for Python patterns, type discipline, and SDK architecture. Highest signal-to-noise ratio — nearly every commit is a deliberate API design decision
- **anthropic-sdk-typescript**: Primary source for TypeScript idioms. Structural parity with Python SDK makes cross-language pattern extraction reliable
- **anthropic-cookbook**: Source for documentation patterns and integration examples. Each recipe is self-contained; sampled for code style within examples rather than repo-level architecture
- **courses**: Educational content with progressive module structure. Lower weight in style extraction — notebook code is less representative of production conventions
- **claude-code**: CLI agent implementation. Source for TypeScript application architecture patterns distinct from SDK library patterns

## Excluded Repositories

- **anthropics/anthropic-quickstarts**: Starter templates — too thin to extract meaningful style patterns
- **anthropics/prompt-eng-interactive-tutorial**: Tutorial-focused, style is pedagogical rather than production
- **Forks and mirrors**: Excluded all forked repositories

## Coverage Gaps

- **Private repositories**: Anthropic's core model training and infrastructure code is private. This wiki covers only the public developer-facing surface
- **Internal tooling**: Build systems, deployment pipelines, and internal libraries are not represented
- **Model research code**: Research experiment code (if any is open-sourced) may follow different conventions than SDK code

## Confidence Impact

Articles grounded in both SDKs (e.g., [[code-structure]], [[naming-conventions]], [[type-discipline]], [[patterns]]) have the highest confidence — the same patterns are validated across two independent codebases. Articles that rely on cookbook or course code (e.g., [[comments-and-docs]]) have slightly lower confidence since example code may prioritize clarity over organizational convention.

The org framing is strongest for SDK-derived patterns. Cookbook and course patterns reflect Anthropic's recommended external style, which may differ from internal production conventions.

**Total commits fetched:** 1,269
**Total commits sampled:** 1,038
**Unique files touched:** 743
**Date range:** 2023-03 to 2026-03
