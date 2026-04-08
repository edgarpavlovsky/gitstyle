---
title: Naming Conventions
category: dimension
confidence: 0.95
source_repos:
  - torvalds/1590A
  - torvalds/AudioNoise
  - torvalds/GuitarPedal
  - torvalds/HunspellColorize
  - torvalds/linux
  - torvalds/pesconvert
  - torvalds/test-tlb
  - torvalds/uemacs
last_updated: 2026-04-08
---
The developer demonstrates highly consistent naming conventions across multiple languages, with a strong preference for snake_case and clear, descriptive names that indicate purpose and subsystem origin.

## Core Patterns

The developer follows traditional C naming conventions with remarkable consistency:
- **Functions and variables**: Always lowercase with underscores (snake_case) [6a6daef2, f434a0e2, 1c3e8c3b, 316f2559]
- **Constants and macros**: Always uppercase with underscores [1c1b25ef, 1cdcf9df, 3036cd0d, 86782c16]
- **Struct names**: Used without typedef, following Linux kernel style [6a6daef2, f434a0e2]

## Language-Specific Conventions

### C and System Programming
The developer strictly adheres to Linux kernel naming conventions [3036cd0d, 86782c16, 66d64899]. Functions use descriptive names with subsystem prefixes (e.g., `bnxt_`, `mlx5_`, `ice_`, `mshv_`, `enetc_`) [86782c16, bfe62a45, f8f5627a, abacaf55]. Hardware register definitions and bit masks consistently use uppercase with underscores (e.g., `MAC_TCR_SS_INDEX`, `ENETC4_POR`) [abacaf55, f8f5627a, 453a4a5f].

### Python
The developer follows PEP 8 conventions consistently, using snake_case for all identifiers [4e524250, a63ddd7a, 15bd3c10]. This alignment with [[python]] idioms shows attention to language-specific standards.

### Build Systems and Configuration
In [[cmake]] files, the developer uses CamelCase for board/project names while maintaining snake_case for source files [0a363123, d999fef1, c9098c2c]. Tag naming for releases follows a consistent format: `v7.0-rc[N]` for versions and `subsystem-YYYY-MM-DD` for dated releases [abacaf55, f8f5627a, 453a4a5f].

## Descriptive Naming Philosophy

The developer prioritizes clarity over brevity. Function names clearly indicate their purpose:
- Domain-specific: `flanger_step`, `biquad_notch_filter` [c9098c2c, 2f3c1c07]
- Action-oriented: `parse_pes_stitches`, `output_cairo`, `randomize_map` [7a7221a3, cea02218]
- Module-prefixed: `phaser_init`, `biquad_step` matching their module names [1c3e8c3b, 316f2559]

This naming approach aligns with the developer's [[code-structure]] practices, where clear module boundaries are reflected in naming prefixes.

## Cross-Language Consistency

Remarkably, the developer maintains consistent conventions across diverse languages including [[c]], [[assembly]], [[shell]], and [[python]]. Even in domain-specific languages like [[openscad]], the developer uses descriptive, function-based naming (e.g., `DaisySeed`, `Buffered`, `Plain` for boards) [e3660495, eb0d867a].

The consistency extends to [[commit-hygiene]], where subsystem prefixes in commit messages (e.g., 'MPTCP:', 'NFC:', 'DRM DRIVERS') follow uppercase conventions [a1d9d8e8, 1c9982b4, abacaf55].
