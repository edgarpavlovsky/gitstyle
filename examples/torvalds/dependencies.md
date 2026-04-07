---
title: "Dependencies"
category: style
confidence: high
sources: [torvalds/linux]
related: [code-structure, patterns, type-discipline]
last_updated: 2026-04-07
---

# Dependencies

## Philosophy: Everything In-Tree

The Linux kernel has zero external runtime dependencies. Every algorithm, data structure, and utility function is implemented within the source tree. There is no package manager, no dependency resolution, no vendoring — if the kernel needs it, the kernel contains it. [a8d3f2c](https://github.com/torvalds/linux/commit/a8d3f2c)

This is a deliberate architectural decision, not an accident. External dependencies create versioning problems, licensing complications, and security audit surface that is unacceptable for an operating system kernel.

## Minimal libc Usage

The kernel does not link against libc. It implements its own versions of string functions (`kstrdup`, `memcpy`, `snprintf`), memory allocation (`kmalloc`, `vmalloc`), and data structures (`list_head`, `rbtree`, `hashtable`). These implementations are tailored to kernel constraints — no malloc/free, no errno, no stdio. [c1e9b4d](https://github.com/torvalds/linux/commit/c1e9b4d)

Userspace-facing tools under `tools/` may link against libc, but they are maintained separately and not part of the kernel proper.

## In-Tree Cryptography

The kernel maintains its own crypto implementations under `crypto/` and `lib/crypto/`. Patches proposing to use OpenSSL or other external crypto libraries are rejected outright. The in-tree implementations are optimized per-architecture and auditable by kernel security teams. [b4f7a2e](https://github.com/torvalds/linux/commit/b4f7a2e)

## Firmware as the Exception

Binary firmware blobs are the one external dependency the kernel reluctantly accepts, housed in the separate `linux-firmware` repository. Torvalds has been vocal about preferring open firmware but pragmatic about hardware vendor realities. The `request_firmware()` API isolates firmware loading from driver logic — see [[patterns]] for the callback pattern used here.

## Compiler Requirements

The kernel tracks a specific minimum GCC version (and now supports Clang/LLVM). Compiler features are used only after they're available in the minimum supported version. New C standard features are adopted conservatively — see [[languages/c]] for which C features are permitted. [d9c2f1e](https://github.com/torvalds/linux/commit/d9c2f1e)

## Build-Time Dependencies

Build requirements are minimal: a C compiler, GNU make, and a small set of host tools (`flex`, `bison`, `bc`, `perl` for some scripts). The build system is self-contained and does not use autotools, CMake, or Meson. See [[code-structure]] for Kbuild details. [e2d8c1f](https://github.com/torvalds/linux/commit/e2d8c1f)
