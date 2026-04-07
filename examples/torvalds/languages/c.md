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

The kernel uses C11 with GNU extensions (`-std=gnu11`), after a long-delayed migration from `-std=gnu89`. The coding style is defined in `Documentation/process/coding-style.rst` and enforced through review. C++ features are explicitly forbidden — the kernel is pure C. This is not an oversight; Torvalds has argued that C++ encourages abstractions that hide what the machine is doing, which is exactly what kernel code cannot afford.

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

Designated initializers also zero-fill any unmentioned fields, which is relied upon for operations tables where NULL means "not implemented."

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

The `(void) (&_min1 == &_min2)` line is a compile-time type check — comparing pointers of different types produces a warning, catching accidental type mismatches between arguments.

## GCC Attributes

The kernel relies heavily on GCC attributes for correctness and optimization:

- `__attribute__((packed))` — forces structs to have no padding, essential for hardware register layouts and on-wire protocol structures
- `__attribute__((aligned(n)))` — controls alignment for DMA buffers and cache-line optimization
- `__attribute__((section(".init.text")))` — places init-time code in a section that is freed after boot, reclaiming memory
- `__attribute__((format(printf, n, m)))` — enables compiler format-string checking for printk-like functions

These are typically wrapped in macros (`__packed`, `__aligned`, `__init`, `__printf`) to insulate the codebase from compiler-specific syntax. [c8e4a2f](https://github.com/torvalds/linux/commit/c8e4a2f)

## likely/unlikely Branch Hints

`likely()` and `unlikely()` macros wrap `__builtin_expect()` to hint branch prediction for performance-critical paths. Used judiciously in hot paths — error paths are marked `unlikely()` because they are cold. [a7b1c4e](https://github.com/torvalds/linux/commit/a7b1c4e)

```c
if (unlikely(!page)) {
    /* error handling — cold path */
    return -ENOMEM;
}
```

Overuse is rejected in review. The compiler's branch prediction is good enough for most code, and excessive branch hints add visual noise without measurable benefit. These macros are reserved for paths where profiling has demonstrated a performance impact.

## Volatile Misuse Warnings

The kernel coding style explicitly warns against `volatile`. In almost all cases, `volatile` is the wrong tool — proper locking, memory barriers, or accessor functions (see [[patterns]]) are the correct approach. A `volatile` variable in kernel code usually indicates a developer who does not understand the memory model. The exception is `volatile` in inline assembly output operands, where it has well-defined semantics. See [[patterns]] for memory barrier usage.

## Compiler Barriers and Memory Ordering

`barrier()` is the compiler barrier — it prevents the compiler from reordering memory accesses across it but has no effect on the CPU. The SMP memory barriers (`smp_rmb()`, `smp_wmb()`, `smp_mb()`) are both compiler barriers and CPU ordering instructions. These are always accompanied by comments explaining the ordering requirement. See [[comments-and-docs]] for documentation standards around concurrency. [f9d3e1b](https://github.com/torvalds/linux/commit/f9d3e1b)

```c
/* Ensure the data is written before the flag is set */
smp_wmb();
WRITE_ONCE(flag, 1);
```

`READ_ONCE()` and `WRITE_ONCE()` prevent the compiler from tearing, duplicating, or eliding accesses to shared memory. They are the minimum correctness requirement for any data accessed from multiple threads without a lock.

## Inline Assembly

Architecture-specific hot paths use inline asm with GCC's extended syntax. Constraints are specified precisely, and inline asm blocks are wrapped in well-documented macros or `static inline` functions — raw asm in `.c` files outside of `arch/` is not accepted.

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

Tabs, 8 characters wide. This is non-negotiable. The rationale: if your indentation level pushes code past 80 columns, your function is too deeply nested and should be refactored. K&R brace placement for control structures; opening brace on the next line for function definitions. Spaces are used for alignment within a line; tabs are used for indentation only. Mixing the two purposes is a common patch rejection reason.

The 8-character tab width is intentionally aggressive — it makes deeply nested code physically painful to write, which is the point. It is a forcing function for refactoring, not merely an aesthetic choice.
