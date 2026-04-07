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

The flatness serves a practical purpose beyond aesthetics: maintainer ownership maps cleanly to top-level directories. The `MAINTAINERS` file uses path patterns to assign reviewers, and shallow hierarchies make those patterns simpler and less ambiguous.

## Clear Subsystem Boundaries

Each subsystem owns its headers, its implementation files, and its Kconfig/Makefile fragments. Cross-subsystem includes are minimized — subsystems expose a narrow public API through `include/linux/` and keep internal headers private under their own directory. See [[dependencies]] for the in-tree-only philosophy that reinforces this.

```
include/linux/sched.h      # public scheduler API
kernel/sched/sched.h       # private scheduler internals
kernel/sched/core.c        # implementation
kernel/sched/fair.c        # CFS implementation
```

Module boundaries are enforced through `EXPORT_SYMBOL` and `EXPORT_SYMBOL_GPL`. Internal functions are `static`; anything exported is part of the subsystem's contract and changing it requires coordinating with all consumers. The `_GPL` variant restricts usage to GPL-licensed modules, creating a two-tier API surface that reflects both technical and legal boundaries. [e7f2a9d](https://github.com/torvalds/linux/commit/e7f2a9d)

## Header Discipline

Headers are kept minimal. A header should declare the interface and nothing more — no inline function bodies unless performance-critical, no unnecessary includes. The `include/linux/` directory is treated as the kernel's public API surface. [b9c4f1a](https://github.com/torvalds/linux/commit/b9c4f1a)

Torvalds has repeatedly rejected patches that add transitive includes. Each `.c` file is expected to include exactly what it needs, not rely on headers pulling in other headers. This discipline keeps compile times manageable on a 30-million-line codebase. Forward declarations (`struct foo;`) are preferred over `#include` when only a pointer to the type is needed.

## File Size Conventions

Individual source files rarely exceed 3,000 lines. When a file grows beyond that, it gets split along functional boundaries — the scheduler split from a single `sched.c` into `sched/core.c`, `sched/fair.c`, `sched/rt.c` is the canonical example. See [[patterns]] for how callback structs enable this decomposition without breaking interfaces.

The split criterion is functional cohesion, not arbitrary line counts. A 4,000-line file that implements a single coherent algorithm (like some crypto implementations) is acceptable; a 2,000-line file that mixes unrelated concerns is not.

## Build System

The kernel uses Kbuild (make-based) with per-directory Makefiles. Each subsystem's `Makefile` lists its objects and conditionally includes based on `CONFIG_*` symbols. There is zero tolerance for recursive make complexity beyond one level of `obj-y` / `obj-m` inclusion. [c9d1e4f](https://github.com/torvalds/linux/commit/c9d1e4f)

Kconfig files define the configuration space, and the build system guarantees that any valid `.config` produces a buildable kernel. This constraint — every configuration must compile — is enforced by CI across hundreds of architecture/config combinations. See [[testing]] for how automated build testing catches violations.

## init/exit Lifecycle

Code that runs only during module initialization is annotated `__init` and placed in a special memory section that is freed after boot completes. Similarly, `__exit` marks code needed only during module unload. This convention turns the compiler and linker into memory management tools — hundreds of kilobytes of initialization code are automatically reclaimed once the system is running. See [[languages/c]] for the GCC attributes that implement this.

Calling an `__init` function after init completes is a bug — the memory has been freed. The `__ref` annotation exists for the rare cases where post-init code must call init-time functions, and the build system warns on suspicious cross-section references.
