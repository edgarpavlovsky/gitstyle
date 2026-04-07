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

Despite C's weak type system, the kernel enforces strong type discipline through conventions, sparse annotations, and careful API design. Types are used to communicate intent and catch misuse at compile time where possible. Where the compiler cannot help, runtime checkers fill the gap — see [[testing]] for the verification infrastructure.

## Sparse Annotations

The kernel uses Sparse (`__user`, `__kernel`, `__iomem`, `__bitwise`, `__rcu`) to add semantic type information that the compiler cannot enforce alone. These annotations create distinct address spaces in the type system, catching an entire class of bugs at static-analysis time. [e9a4b7c](https://github.com/torvalds/linux/commit/e9a4b7c)

**`__user`** marks pointers to userspace memory. Direct dereference is a bug — all access must go through `copy_from_user()` / `copy_to_user()` or the `get_user()` / `put_user()` primitives. A bare dereference of a `__user` pointer is a security vulnerability (it bypasses SMAP on x86 and similar protections on other architectures).

```c
long sys_read(unsigned int fd, char __user *buf, size_t count);
/* Direct access to buf is a sparse warning — must use copy_to_user() */
```

**`__iomem`** marks memory-mapped I/O pointers. These must be accessed through `readl()` / `writel()` and friends, never by direct pointer dereference. The hardware may reorder or cache MMIO accesses differently than normal memory. [d3a8f1c](https://github.com/torvalds/linux/commit/d3a8f1c)

**`__rcu`** marks pointers managed by RCU (see [[patterns]]). Access must use `rcu_dereference()` inside an RCU read-side critical section or `rcu_assign_pointer()` for updates. Sparse catches missing RCU annotations before they become data races.

The **`__bitwise`** annotation creates distinct integer types for endianness (`__le32`, `__be32`, `__le16`, `__be16`) so that mixing host-endian and wire-endian values produces a warning. This has caught hundreds of byte-order bugs across the networking and filesystem subsystems. [f2a1c8d](https://github.com/torvalds/linux/commit/f2a1c8d)

## Typedef Avoidance

The kernel style explicitly forbids most typedefs. Structs are always spelled out as `struct foo` rather than hidden behind a `foo_t` typedef. The rationale: when you see `struct` in the code, you know it's a composite type and you know to look for its definition. [a3f1d8b](https://github.com/torvalds/linux/commit/a3f1d8b)

Exceptions exist for genuinely opaque types (`pid_t`, `gfp_t`, `phys_addr_t`, `sector_t`) where the underlying representation is intentionally hidden, and for function pointer types where the typedef improves readability.

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

Raw `atomic_t` was historically used for reference counts, but a dedicated `refcount_t` type was introduced to catch underflow/overflow bugs. The `refcount_t` operations (`refcount_inc`, `refcount_dec_and_test`) include saturation semantics — an underflow does not wrap to a large positive value but instead triggers a warning and clamps. This prevents use-after-free exploits where an attacker deliberately overflows a refcount. [b5a8e1c](https://github.com/torvalds/linux/commit/b5a8e1c)

Torvalds supported this migration as a type-safety improvement: the distinct type prevents accidentally using atomic operations that lack refcount semantics (e.g., `atomic_add` when `refcount_inc` should be used). See [[patterns]] for the refcounting pattern.

## Boolean Discipline

The kernel uses the C99 `bool` type for genuine boolean values but avoids it for bitfields and flags, where `unsigned int` with named bit constants is preferred. Tri-state values never use `bool` — an explicit enum or integer is required. See [[languages/c]] for more on how C types are used idiomatically.

## Fixed-Width Integer Types

The kernel uses explicit-width types (`u8`, `u16`, `u32`, `u64` and their signed variants `s8`, `s16`, `s32`, `s64`) for hardware interfaces, protocol parsing, and any context where the exact bit width matters. The generic C types (`int`, `long`) are used for computation where the exact width is not part of the contract. Mixing the two — using `int` where a hardware register requires exactly 32 bits — is caught in review. [a1c7d4e](https://github.com/torvalds/linux/commit/a1c7d4e)

For userspace-facing APIs (syscall arguments, ioctl structures), the `__u32`/`__s32` variants are used in UAPI headers to avoid namespace pollution — the `u32` short forms are internal to the kernel.

## Const Discipline

The `const` qualifier is used aggressively on operations tables (see [[patterns]]), string literals, and function parameters that are not modified. Mutable global state is minimized, and when it exists, its locking requirements are documented. The `const` on operations tables is a security measure — placing function pointers in read-only memory prevents control-flow hijacking attacks.
