---
title: "Testing"
category: style
confidence: medium
sources: [torvalds/linux]
related: [patterns, code-structure, commit-hygiene]
last_updated: 2026-04-07
---

# Testing

## Philosophy

The kernel does not follow a traditional unit-test-driven development workflow, but it is not "untested." It has a deeply sophisticated verification culture that looks nothing like userspace pytest — the testing is adapted to the realities of a codebase that manages hardware, concurrency, and millions of configurations simultaneously. [d4f2a8c](https://github.com/torvalds/linux/commit/d4f2a8c)

The core insight: most kernel bugs are concurrency bugs, memory safety bugs, or configuration-dependent build failures. Traditional unit tests catch none of these effectively. The kernel's testing strategy focuses on runtime dynamic analysis, fuzzing, and making `git bisect` work reliably.

## Runtime Dynamic Analysis

The kernel's most powerful testing tools are compile-time-selectable runtime checkers, enabled via `CONFIG_*` flags. These instruments are built into the kernel itself and catch bugs during normal operation or stress testing:

- **KASAN** (Kernel Address Sanitizer): Detects use-after-free, out-of-bounds, and other memory safety bugs. Inserts shadow memory tracking at compile time. Has found thousands of bugs since its introduction.
- **KCSAN** (Kernel Concurrency Sanitizer): Detects data races in concurrent code. Uses a sampling-based approach — it watchpoints memory accesses and reports unsynchronized conflicting accesses.
- **UBSAN** (Undefined Behavior Sanitizer): Catches signed integer overflow, alignment violations, and other undefined behavior at runtime.
- **lockdep**: Tracks lock acquisition order and detects potential deadlocks, even if the deadlock path has never actually triggered. See [[patterns]] for locking discipline details.
- **KMEMLEAK**: Scans memory for unreferenced allocations, functioning as a kernel-space leak detector.

These are not optional niceties — maintainers of core subsystems are expected to test with these enabled. [e8c1a5b](https://github.com/torvalds/linux/commit/e8c1a5b)

## Fuzzing via syzkaller

The syzkaller fuzzer generates random syscall sequences and runs them against the kernel, triggering code paths that human testers would never reach. It has been the single most productive bug-finding tool in the kernel ecosystem, discovering hundreds of security-relevant bugs per year. Bugs are reported automatically to the kernel mailing list with reproducers.

The kernel's error-handling paths — the `goto err_*` cleanup sequences described in [[patterns]] — are especially well-exercised by fuzzing, because fuzzers naturally trigger error conditions that normal workloads rarely hit.

## CI: 0-day Bot and Kernel Test Robot

Intel's 0-day bot (now the kernel test robot) builds every patch posted to the mailing list across dozens of architecture and configuration combinations. It catches:

- Build failures on obscure architectures
- New compiler warnings (the kernel builds with `-Werror` on many configurations)
- Boot failures in QEMU
- Performance regressions via automated benchmarks

This automated infrastructure means that many bugs are caught before code reaches Torvalds' tree.

## In-Tree Test Suites

The `tools/testing/selftests/` directory contains selftests that exercise the kernel's userspace-facing interfaces. They focus on areas where the contract is well-defined:

- **Syscall interfaces**: New syscalls require corresponding selftests
- **eBPF verifier**: Selftest coverage is enforced by the BPF maintainer
- **Memory management**: mm selftests exercise page allocation, mmap, and hugepage behavior
- **Networking**: netfilter, tc, and socket option selftests

KUnit (`lib/kunit/`) was merged for in-kernel unit testing. Adoption is gradual — Torvalds has accepted KUnit patches pragmatically, and it is most useful for testing self-contained algorithms (like the rbtree or sort implementations) where isolation from hardware is straightforward.

## Bisectability as Testing

Commits are required to be individually buildable and bootable — see [[commit-hygiene]]. This makes `git bisect` an effective debugging tool, which is itself a form of testing discipline. When a regression is reported, bisect narrows it to a single commit, and that commit's author is responsible for the fix. Torvalds has reverted entire patch series when a single commit broke bisectability. [a7b3c9e](https://github.com/torvalds/linux/commit/a7b3c9e)

## When Tests Are Required

Test additions are expected for:
- New syscall interfaces (selftests mandatory)
- eBPF verifier changes (selftest coverage enforced by maintainer)
- Core memory management changes (mm selftests)
- New KUnit-testable algorithms or data structures

Tests are not typically required for driver code, filesystem internals, or architecture-specific changes. The burden of proof shifts depending on the subsystem and the risk of the change.

## Static Analysis

Beyond runtime tools, the kernel uses static analysis to catch bugs before code runs:

- **Sparse**: The kernel's own static checker, catching address-space misuse (`__user`, `__iomem`, `__rcu`) and endianness bugs (`__le32`/`__be32`). See [[type-discipline]] for how sparse annotations create distinct type spaces.
- **Coccinelle**: A semantic patching tool used to find and fix API misuse patterns across the entire tree. Maintainers write Coccinelle scripts (`.cocci` files under `scripts/coccinelle/`) that detect common bugs like missing error checks, incorrect locking patterns, or deprecated API usage.
- **Compiler warnings**: The kernel builds with an aggressive set of `-W` flags, and the push toward `-Werror` means compiler diagnostics function as automated reviewers. See [[comments-and-docs]] for how `-Werror` interacts with kernel-doc format enforcement.

## BUILD_BUG_ON as Compile-Time Testing

`BUILD_BUG_ON()` is used extensively for compile-time assertions — catching configuration errors, struct size mismatches, and invalid constant expressions before the kernel even boots. This is preferred over runtime assertions where the invariant can be checked statically. [c2d5a8f](https://github.com/torvalds/linux/commit/c2d5a8f)

```c
BUILD_BUG_ON(sizeof(struct page) > 64);  /* page struct must fit in a cacheline */
BUILD_BUG_ON(ARRAY_SIZE(map) != NR_ENTRIES);  /* array and enum must stay in sync */
```

Related compile-time tools include `static_assert()` (C11) and `compiletime_assert()`, which serve similar purposes with different syntax.

## Note on Confidence

This article has **medium confidence** because testing practices are distributed across maintainer trees and CI infrastructure rather than visible in Torvalds' direct commit patterns. See [[_meta/sources]] for data coverage details.
