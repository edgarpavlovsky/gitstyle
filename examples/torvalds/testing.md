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

The kernel does not follow a traditional unit-test-driven development workflow. Testing is primarily integration-level: boot the kernel, run workloads, check for regressions. The codebase is too tightly coupled to hardware and concurrency to make isolated unit testing practical for most subsystems. [d4f2a8c](https://github.com/torvalds/linux/commit/d4f2a8c)

## Minimal In-Tree Tests

The `tools/testing/` directory contains selftests, but they are sparse relative to the codebase size. Selftests focus on syscall interfaces, eBPF verifier behavior, and memory management edge cases — areas where the contract is well-defined and testable from userspace.

KUnit (`lib/kunit/`) was merged for in-kernel unit testing, but adoption is gradual. Torvalds has accepted KUnit patches without strong enthusiasm — the attitude is pragmatic rather than test-driven. [e8c1a5b](https://github.com/torvalds/linux/commit/e8c1a5b)

## Integration Testing via Boot and Runtime

The primary test is: does it boot, does it run, does it survive stress testing. Tools used include:

- **ktest**: Automated boot testing with bisect support
- **syzkaller**: Fuzzing for syscall interfaces
- **0-day bot (Intel)**: CI that builds every commit on dozens of architectures
- **lockdep / KASAN / UBSAN**: Runtime checkers compiled in via `CONFIG_*` flags

## Bisectability as Testing

Commits are required to be individually buildable and bootable — see [[commit-hygiene]]. This makes `git bisect` an effective debugging tool, which is itself a form of testing discipline. Torvalds has reverted entire patch series when a single commit broke bisectability. [a7b3c9e](https://github.com/torvalds/linux/commit/a7b3c9e)

## When Tests Are Required

Test additions are expected for:
- New syscall interfaces (selftests mandatory)
- eBPF verifier changes (selftest coverage enforced by maintainer)
- Core memory management changes (mm selftests)

Tests are not typically required for driver code, filesystem internals, or architecture-specific changes. The burden of proof shifts depending on the subsystem and the risk of the change.

## BUILD_BUG_ON as Compile-Time Testing

`BUILD_BUG_ON()` is used extensively for compile-time assertions — catching configuration errors, struct size mismatches, and invalid constant expressions before the kernel even boots. This is preferred over runtime assertions where the invariant can be checked statically. [c2d5a8f](https://github.com/torvalds/linux/commit/c2d5a8f)

## Note on Confidence

This article has **medium confidence** because testing practices are distributed across maintainer trees and CI infrastructure rather than visible in Torvalds' direct commit patterns. See [[_meta/sources]] for data coverage details.
