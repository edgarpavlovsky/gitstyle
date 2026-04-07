---
title: "Type Discipline"
category: style
confidence: high
sources: [torvalds/linux]
related: [patterns, naming-conventions, languages/c]
last_updated: 2026-04-07
---

# Type Discipline

## Overall Approach

Despite C's weak type system, the kernel enforces strong type discipline through conventions, sparse annotations, and careful API design. Types are used to communicate intent and catch misuse at compile time where possible.

## Sparse Annotations

The kernel uses Sparse (`__user`, `__kernel`, `__iomem`, `__bitwise`) to add semantic type information that the compiler cannot enforce alone. Pointers to userspace memory are tagged `__user` and must go through `copy_from_user()`/`copy_to_user()` — direct dereference is a bug. [e9a4b7c](https://github.com/torvalds/linux/commit/e9a4b7c)

```c
long sys_read(unsigned int fd, char __user *buf, size_t count);
/* Direct access to buf is a sparse warning — must use copy_to_user() */
```

The `__bitwise` annotation creates distinct integer types for endianness (`__le32`, `__be32`) so that mixing host-endian and wire-endian values produces a warning. This has caught hundreds of byte-order bugs across the networking and filesystem subsystems. [f2a1c8d](https://github.com/torvalds/linux/commit/f2a1c8d)

## Typedef Avoidance

The kernel style explicitly forbids most typedefs. Structs are always spelled out as `struct foo` rather than hidden behind a `foo_t` typedef. The rationale: when you see `struct` in the code, you know it's a composite type and you know to look for its definition. [a3f1d8b](https://github.com/torvalds/linux/commit/a3f1d8b)

Exceptions exist for genuinely opaque types (`pid_t`, `gfp_t`, `phys_addr_t`) where the underlying representation is intentionally hidden, and for function pointer types where the typedef improves readability.

```c
/* Rejected: hiding struct behind typedef */
typedef struct { int x; int y; } point_t;

/* Accepted: struct always visible */
struct point { int x; int y; };

/* Accepted: opaque scalar typedef */
typedef unsigned int gfp_t;
```

## Explicit sizeof

`sizeof` always operates on the variable, not the type. This ensures correctness if the type changes and makes the intent self-documenting. See [[naming-conventions]] for the broader principle of code that explains itself. [c7d2e5f](https://github.com/torvalds/linux/commit/c7d2e5f)

```c
/* Preferred — sizeof on the variable */
p = kmalloc(sizeof(*p), GFP_KERNEL);

/* Rejected — sizeof on the type */
p = kmalloc(sizeof(struct my_struct), GFP_KERNEL);
```

## refcount_t Over atomic_t

Raw `atomic_t` was historically used for reference counts, but a dedicated `refcount_t` type was introduced to catch underflow/overflow bugs. Torvalds supported this migration as a type-safety improvement — the distinct type prevents accidentally using atomic operations that don't have refcount semantics. See [[patterns]] for the refcounting pattern. [b5a8e1c](https://github.com/torvalds/linux/commit/b5a8e1c)

## Boolean Discipline

The kernel uses the C99 `bool` type for genuine boolean values but avoids it for bitfields and flags, where `unsigned int` with named bit constants is preferred. Tri-state values never use `bool` — an explicit enum or integer is required. See [[languages/c]] for more on how C types are used idiomatically.
