---
title: "Type Discipline"
category: style
confidence: high
sources: [torvalds/linux]
related: [patterns, naming-conventions, languages/c]
last_updated: 2026-04-07
---

# Type Discipline

## Typedef Policy

Typedefs are used sparingly and only for specific purposes: opaque handles (`typedef struct _foo *foo_t`), architecture-specific types (`u8`, `u16`, `u32`, `u64`), and function pointer types. Struct types are always referred to as `struct foo`, never hidden behind typedefs.

## Fixed-Width Types

The kernel defines and uses `u8`/`u16`/`u32`/`u64` (and signed variants `s8`-`s64`) for all fixed-width integer usage. Standard C `int` is used only when the exact width doesn't matter.

## Type Safety Through Structs

The developer enforces type safety by wrapping related data in structs even when a simpler type would suffice. This prevents mixing up semantically different values (e.g., a page frame number vs. a byte offset). See [[patterns]] for how structs enable encapsulation.

## Const Correctness

Pointer parameters that aren't modified are marked `const`. This is enforced as a matter of style, providing both documentation and compiler-checked guarantees:

```c
int validate_header(const struct packet_header *hdr);
```
