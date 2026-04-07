---
title: "Testing"
category: style
confidence: medium
sources: [torvalds/linux]
related: [patterns, code-structure]
last_updated: 2026-04-07
---

# Testing

## Kernel Testing Framework

The kernel uses KUnit (`lib/kunit/`) for unit testing and kselftest (`tools/testing/selftests/`) for integration-level tests. The developer merges patches that add test coverage for new features and regressions.

## Test-Alongside-Code

KUnit tests live alongside the code they test (often in the same directory), following the principle that tests should be close to what they exercise. Selftests are organized by subsystem under `tools/testing/selftests/`.

## Regression-Driven

Many test additions are driven by bug fixes — when a bug is found and fixed, a test is added to prevent regression. This is a pattern visible in merge commits that combine a fix with its corresponding test.

## Build-Time Assertions

`BUILD_BUG_ON()` is used extensively for compile-time assertions, catching configuration and type errors before runtime. This is preferred over runtime assertions where possible.
