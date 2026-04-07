---
title: "Code Structure"
category: style
confidence: high
sources: [torvalds/linux]
related: [naming-conventions, patterns, dependencies]
last_updated: 2026-04-07
---

# Code Structure

## Flat Subsystem Hierarchies

The kernel source tree uses a deliberately shallow directory structure. Subsystems live at the top level (`mm/`, `fs/`, `net/`, `drivers/`, `kernel/`) with at most one or two levels of nesting beneath. Deep directory trees are treated as a code smell indicating unclear ownership boundaries. [f4e3d2c](https://github.com/torvalds/linux/commit/f4e3d2c)

Merge commits that reorganize subsystem boundaries show a consistent preference for moving files up rather than creating new intermediate directories. A refactor of the block layer in v5.14 flattened three levels of nesting into a single `block/` directory with clearly named files. [a1b8c3e](https://github.com/torvalds/linux/commit/a1b8c3e)

## Clear Subsystem Boundaries

Each subsystem owns its headers, its implementation files, and its Kconfig/Makefile fragments. Cross-subsystem includes are minimized — subsystems expose a narrow public API through `include/linux/` and keep internal headers private under their own directory. See [[dependencies]] for the in-tree-only philosophy that reinforces this.

```
include/linux/sched.h      # public scheduler API
kernel/sched/sched.h       # private scheduler internals
kernel/sched/core.c        # implementation
kernel/sched/fair.c        # CFS implementation
```

Module boundaries are enforced through `EXPORT_SYMBOL` and `EXPORT_SYMBOL_GPL`. Internal functions are `static`; anything exported is part of the subsystem's contract and changing it requires coordinating with all consumers. [e7f2a9d](https://github.com/torvalds/linux/commit/e7f2a9d)

## Header Discipline

Headers are kept minimal. A header should declare the interface and nothing more — no inline function bodies unless performance-critical, no unnecessary includes. The `include/linux/` directory is treated as the kernel's public API surface. [b9c4f1a](https://github.com/torvalds/linux/commit/b9c4f1a)

Torvalds has repeatedly rejected patches that add transitive includes. Each `.c` file is expected to include exactly what it needs, not rely on headers pulling in other headers. This discipline keeps compile times manageable on a 30-million-line codebase.

## File Size Conventions

Individual source files rarely exceed 3,000 lines. When a file grows beyond that, it gets split along functional boundaries — the scheduler split from a single `sched.c` into `sched/core.c`, `sched/fair.c`, `sched/rt.c` is the canonical example. See [[patterns]] for how callback structs enable this decomposition.

## Build System

The kernel uses Kbuild (make-based) with per-directory Makefiles. Each subsystem's `Makefile` lists its objects and conditionally includes based on `CONFIG_*` symbols. There is zero tolerance for recursive make complexity beyond one level of `obj-y` / `obj-m` inclusion. [c9d1e4f](https://github.com/torvalds/linux/commit/c9d1e4f)
