---
title: "Code Structure"
category: style
confidence: high
sources: [torvalds/linux]
related: [naming-conventions, patterns, dependencies]
last_updated: 2026-04-07
---

# Code Structure

## Kernel-Scale Organization

The Linux kernel uses a deeply structured directory hierarchy organized by subsystem. Each subsystem (`drivers/`, `fs/`, `net/`, `mm/`, `arch/`) is largely self-contained with its own Makefiles and Kconfig files.

## Header-Source Separation

Strict separation between headers (`include/`) and implementation files. Public kernel APIs live in `include/linux/`, architecture-specific headers in `include/asm-generic/` and `arch/*/include/`. This is enforced by convention and build system.

## File Size

Individual source files can be large (1000+ lines) when they represent a complete subsystem component. However, the developer regularly merges patches that split oversized files into logical units. The preference is for files that cover a coherent concept rather than arbitrary size limits.

## Build System

Kconfig + Makefile-based build system. Every directory has its own Makefile fragment. Configuration is hierarchical — subsystems define their own config options that compose into the top-level `.config`.

## Module Boundaries

Strong module boundaries enforced through the kernel's `EXPORT_SYMBOL` mechanism. Internal functions are `static`, exported APIs are explicitly marked. This creates a clear public/private API distinction at the source level. See [[patterns]] for more on encapsulation.
