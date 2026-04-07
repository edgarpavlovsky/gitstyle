---
title: "Naming Conventions"
category: style
confidence: high
sources: [torvalds/linux]
related: [code-structure, comments-and-docs]
last_updated: 2026-04-07
---

# Naming Conventions

## C Naming Style

Strictly follows the Linux kernel coding style (Documentation/process/coding-style.rst):

- `snake_case` for all functions and variables
- `SCREAMING_SNAKE_CASE` for macros and constants
- No Hungarian notation
- Short but meaningful names preferred

```c
// Typical naming
static int nr_free_pages;
void flush_tlb_range(struct vm_area_struct *vma, unsigned long start, unsigned long end);
```

## Function Naming

Functions follow a `subsystem_verb_object` pattern that makes their origin and purpose clear without needing to check headers:

```c
// Clear subsystem prefixes
sched_fork()           // scheduler subsystem
mm_alloc()             // memory management
vfs_read()             // virtual filesystem
net_rx_action()        // networking
```

## Type Names

Struct types use `snake_case` without a `_t` suffix (which is reserved for POSIX types in kernel convention). Typedefs are used sparingly and only for specific cases like opaque handles.

## Local Variables

Local variables can be short (1-3 characters) when the scope is small and the meaning is obvious: `i` for iterators, `p` for pointers, `ret` for return values. This is a deliberate style choice, not laziness — longer scopes get longer names.
