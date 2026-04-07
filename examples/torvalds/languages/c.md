---
title: "C Idioms"
category: language
confidence: high
sources: [torvalds/linux]
related: [naming-conventions, patterns, type-discipline]
last_updated: 2026-04-07
---

# C Idioms

## Linux Kernel C Style

The kernel uses C11 with GNU extensions. The coding style is defined in `Documentation/process/coding-style.rst` and enforced through review.

## Indentation

Tabs, 8 characters wide. This is non-negotiable in the kernel. The rationale: if your indentation level pushes code past 80 columns, your function is too deeply nested and should be refactored.

## Brace Placement

K&R style: opening brace on the same line as the statement, except for function definitions where it goes on the next line.

```c
if (condition) {
    do_something();
} else {
    do_other();
}

static int
my_function(int arg)
{
    return arg + 1;
}
```

## Goto for Cleanup

`goto` is idiomatic for error handling cleanup paths. Labels are named for what they clean up (`err_free_buffer`, `err_unlock`, `out`). See [[patterns]] for the full error handling pattern.

## Container_of Macro

The `container_of()` macro is used extensively to navigate from an embedded struct member back to the containing struct. This is the kernel's primary mechanism for generic data structure support:

```c
struct my_device {
    struct device dev;
    int my_data;
};

// From a device pointer, get the containing my_device
struct my_device *md = container_of(dev, struct my_device, dev);
```

## Likely/Unlikely Branch Hints

`likely()` and `unlikely()` macros hint branch prediction for performance-critical paths. Used judiciously in hot paths, not sprinkled everywhere.

## Memory Barriers

Explicit memory barriers (`smp_rmb()`, `smp_wmb()`, `smp_mb()`) are used in lockless algorithms. The developer is meticulous about correct memory ordering — incorrect barrier usage is treated as a serious bug.
