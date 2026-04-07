---
title: "Dependencies"
category: style
confidence: high
sources: [torvalds/linux]
related: [code-structure, patterns]
last_updated: 2026-04-07
---

# Dependencies

## No External Dependencies

The Linux kernel has zero external runtime dependencies. Everything is self-contained, including its own implementations of standard library functions (`lib/string.c`, `lib/sort.c`). This is both a philosophical and practical choice — the kernel cannot depend on userspace libraries.

## Vendored Implementations

When the kernel needs functionality typically provided by libraries, it implements its own version. Examples: `lib/crypto/`, `lib/zlib_deflate/`, `lib/lzo/`. These are maintained in-tree and adapted to kernel constraints.

## Build Dependencies

Build dependencies are kept minimal: GCC or Clang, GNU Make, and a handful of host tools. The developer has pushed for reducing build-time dependencies over the years.

## Toolchain Compatibility

The kernel maintains compatibility with multiple compiler versions and architectures. Changes that require bleeding-edge compiler features are generally rejected unless the benefit is substantial.
