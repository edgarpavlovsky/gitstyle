---
title: "C Idioms"
category: language
confidence: high
sources: [torvalds/linux]
related: [naming-conventions, patterns, type-discipline]
last_updated: 2026-04-07
---

# C Idioms

## Language Standard

The kernel uses C11 with GNU extensions (`-std=gnu11`). The coding style is defined in `Documentation/process/coding-style.rst` and enforced through review. C++ features are explicitly forbidden — the kernel is pure C.

## Designated Initializers

Struct initialization uses designated initializers exclusively. Positional initializers are rejected because they're fragile — adding a field to the struct silently shifts values. This is especially critical for operations tables (see [[patterns]]). [e3a1f7c](https://github.com/torvalds/linux/commit/e3a1f7c)

```c
/* Required: designated initializers */
static const struct file_operations my_fops = {
    .owner   = THIS_MODULE,
    .open    = my_open,
    .read    = my_read,
    .release = my_release,
};

/* Rejected: positional initialization */
static const struct file_operations my_fops = {
    THIS_MODULE, my_open, my_read, NULL, my_release  /* fragile */
};
```

## Compound Literals

Compound literals are used for constructing temporary structs inline, particularly for passing one-off arguments to functions that take struct pointers. [b4c2d8a](https://github.com/torvalds/linux/commit/b4c2d8a)

```c
/* Compound literal avoids a named temporary */
err = kern_path_create(AT_FDCWD, pathname,
                       &(struct path){}, LOOKUP_DIRECTORY);
```

## Statement Expressions

GNU statement expressions (`({ ... })`) are used in macros to evaluate arguments exactly once while returning a value. This avoids the classic macro double-evaluation bug. The `min()` and `max()` macros are the canonical examples. See [[type-discipline]] for how these enforce type safety. [d1f8a3e](https://github.com/torvalds/linux/commit/d1f8a3e)

```c
#define min(x, y) ({            \
    typeof(x) _min1 = (x);     \
    typeof(y) _min2 = (y);     \
    (void) (&_min1 == &_min2); \
    _min1 < _min2 ? _min1 : _min2; })
```

The `(void) (&_min1 == &_min2)` line is a compile-time type check — it produces a warning if `x` and `y` have different types.

## Inline Assembly

Architecture-specific hot paths use inline asm with GCC's extended syntax. Constraints are specified precisely, and inline asm blocks are wrapped in well-documented macros or `static inline` functions — raw asm in `.c` files outside of `arch/` is not accepted. [c8e4a2f](https://github.com/torvalds/linux/commit/c8e4a2f)

```c
static inline void native_cpuid(unsigned int *eax, unsigned int *ebx,
                                unsigned int *ecx, unsigned int *edx)
{
    asm volatile("cpuid"
        : "=a" (*eax), "=b" (*ebx), "=c" (*ecx), "=d" (*edx)
        : "0" (*eax), "2" (*ecx)
        : "memory");
}
```

## Indentation and Braces

Tabs, 8 characters wide. This is non-negotiable. The rationale: if your indentation level pushes code past 80 columns, your function is too deeply nested and should be refactored. K&R brace placement for control structures; opening brace on the next line for function definitions. [a7b1c4e](https://github.com/torvalds/linux/commit/a7b1c4e)

## likely/unlikely Branch Hints

`likely()` and `unlikely()` macros hint branch prediction for performance-critical paths. Used judiciously in hot paths, not sprinkled everywhere. Overuse is rejected in review — the compiler's branch prediction is good enough for most code. See [[naming-conventions]] for the macro naming convention these follow.

## Memory Barriers

Explicit memory barriers (`smp_rmb()`, `smp_wmb()`, `smp_mb()`) are used in lockless algorithms. Incorrect barrier usage is treated as a serious bug — these are always accompanied by comments explaining the ordering requirement. See [[comments-and-docs]] for documentation standards around concurrency. [f9d3e1b](https://github.com/torvalds/linux/commit/f9d3e1b)
