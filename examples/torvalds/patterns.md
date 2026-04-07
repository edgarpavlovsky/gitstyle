---
title: "Patterns & Architecture"
category: style
confidence: high
sources: [torvalds/linux]
related: [code-structure, type-discipline, naming-conventions]
last_updated: 2026-04-07
---

# Patterns & Architecture

## Error Handling

The kernel uses integer return codes exclusively: `0` for success, negative `errno` values for failure. This is enforced rigorously — every function that can fail returns an `int` or a pointer (using `ERR_PTR`/`IS_ERR`/`PTR_ERR` for pointer-returning functions).

```c
// Standard error pattern
int ret = some_operation();
if (ret < 0)
    return ret;
```

`goto`-based cleanup is the standard pattern for functions with multiple resources to release:

```c
int complex_init(struct device *dev)
{
    ret = alloc_resource_a();
    if (ret)
        goto err_a;
    ret = alloc_resource_b();
    if (ret)
        goto err_b;
    return 0;

err_b:
    free_resource_a();
err_a:
    return ret;
}
```

## Encapsulation via Opaque Structs

Data hiding is achieved through opaque struct pointers. Headers declare `struct foo;` without the definition, forcing users through accessor functions. This is the kernel's version of OOP.

## Callback-Based Polymorphism

The kernel's "object-oriented" pattern uses structs of function pointers (e.g., `struct file_operations`, `struct device_driver`). This provides runtime polymorphism without language-level OOP features. See [[type-discipline]] for how types support this.

## Locking Discipline

Explicit locking with `spin_lock`, `mutex_lock`, and careful documentation of which lock protects which data. Lock ordering is documented in comments to prevent deadlocks.
